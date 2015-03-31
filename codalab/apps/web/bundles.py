from time import sleep

from django.conf import settings
from django.template.defaultfilters import slugify

from xmlrpclib import Fault, ProtocolError

if len(settings.BUNDLE_SERVICE_URL) > 0:

    from apps.authenz.oauth import get_user_token
    #imports from command line interface
    from codalab.bundles.make_bundle import MakeBundle
    from codalab.bundles.run_bundle import RunBundle
    from codalab.bundles.uploaded_bundle import UploadedBundle
    from codalab.client.remote_bundle_client import RemoteBundleClient
    from codalab.common import UsageError, PermissionError
    from codalab.lib import worksheet_util, bundle_cli, metadata_util

    from codalab.model.tables import (
        GROUP_OBJECT_PERMISSION_ALL,
        GROUP_OBJECT_PERMISSION_READ,
    )

    from codalab.bundles import (
        get_bundle_subclass
    )


    def _call_with_retries(f, retry_count=0):
        try:
            return f()
        except (Fault, ProtocolError) as e:
            if retry_count < 2:
                sleep(0.1)
                return _call_with_retries(f, retry_count=retry_count+1)
            raise e


    class BundleService():
        def __init__(self, user=None):
            self.client = RemoteBundleClient(settings.BUNDLE_SERVICE_URL,
                                             lambda command: get_user_token(user), verbose=1)

        def items(self):
            return _call_with_retries(lambda: self.client.search())

        def get_bundle_info(self, uuid):
            bundle_info = _call_with_retries(lambda: self.client.get_bundle_info(uuid))

            metadata = bundle_info['metadata']

            cls = get_bundle_subclass(bundle_info['bundle_type'])
            # format based on specs from the cli
            for spec in cls.METADATA_SPECS:
                key = spec.key
                if key not in metadata:
                    continue
                if metadata[key] == '' or metadata[key] == []:
                    continue
                value = worksheet_util.apply_func(spec.formatting, metadata.get(key))
                # if isinstance(value, list):
                #     value = ', '.join(value)
                metadata[key] = value

            bundle_info['metadata'] = metadata

            return bundle_info
        def head_target(self, target, maxlines=100):
            return self.client.head_target(target, maxlines)

        def search_bundles(self, keywords, worksheet_uuid=None):
            bundle_uuids = self.client.search_bundle_uuids(worksheet_uuid, keywords)
            bundle_infos = self.client.get_bundle_infos(bundle_uuids)
            return bundle_infos

        def worksheets(self):
            return _call_with_retries(lambda: self.client.list_worksheets())

        def create_worksheet(self, name):
            return _call_with_retries(lambda: self.client.new_worksheet(name))

        def worksheet(self, uuid, interpreted=False):
            try:
                worksheet_info  = self.client.get_worksheet_info(
                                            uuid,
                                            True,  #fetch_items
                                            True,  # get_permissions

                                )
            except PermissionError:
                raise UsageError # forces a not found
            worksheet_info['raw'] = worksheet_util.get_worksheet_lines(worksheet_info)
            # set permissions
            worksheet_info['edit_permission'] = False
            if worksheet_info['permission'] == GROUP_OBJECT_PERMISSION_ALL:
                worksheet_info['edit_permission'] = True


            if interpreted:
                interpreted_items = worksheet_util.interpret_items(
                                    worksheet_util.get_default_schemas(),
                                    worksheet_info['items']
                                )
                worksheet_info['items'] = self.client.resolve_interpreted_items(interpreted_items['items'])
                return worksheet_info
            else:
                return worksheet_info

        def create_run_bundle(self, args, command, worksheet_uuid):
            from codalab.lib.codalab_manager import CodaLabManager
            #mimic the command line so we can parse targets and create the bundle
            manager = CodaLabManager()
            cli = bundle_cli.BundleCLI(manager)
            parser = cli.create_parser('run')
            parser.add_argument('target_spec', help=cli.TARGET_SPEC_FORMAT, nargs='*')
            parser.add_argument('command', help='Command-line')
            metadata_util.add_arguments(RunBundle, set(), parser)
            metadata_util.add_edit_argument(parser)
            args = parser.parse_args(args)

            metadata = metadata_util.request_missing_metadata(RunBundle, args)
            metadata['name'] = str(slugify(command))

            targets = cli.parse_key_targets(self.client, worksheet_uuid, args.target_spec)

            new_bundle_uuid = self.client.derive_bundle('run', targets, str(command), metadata, worksheet_uuid)
            return new_bundle_uuid


        def upload_bundle_url(self, url, info, worksheet_uuid):
            file_name = url.split("/")[-1]
            info = {
                'bundle_type': 'dataset',
                'metadata': {
                    'description': 'Upload %s' % url,
                    'tags': [],
                    'name': '%s' % file_name,
                    'license': '',
                    'source_url': '%s' % url,
                }
            }
            new_bundle_uuid = self.client.upload_bundle_url(url, info, worksheet_uuid, True)
            return new_bundle_uuid

        def add_worksheet_item(self, worksheet_uuid, bundle_uuid):
            self.client.add_worksheet_item(worksheet_uuid, worksheet_util.bundle_item(bundle_uuid))

        def parse_and_update_worksheet(self, uuid, lines):
            worksheet_info = self.client.get_worksheet_info(uuid, True)
            new_items, commands = worksheet_util.parse_worksheet_form(lines, self.client, worksheet_info['uuid'])
            self.client.update_worksheet(
                                worksheet_info,
                                new_items
                        )


        def get_target_info(self, target, depth=1):
            return _call_with_retries(lambda: self.client.get_target_info(target, depth))

        def resolve_interpreted_items(self, interpreted_items):
            return _call_with_retries(lambda: self.client.resolve_interpreted_items(('test', 'test')))

        def get_worksheet_info(self):
            return _call_with_retries(lambda: self.client.get_worksheet_info())

        def delete_worksheet(self, worksheet_uuid):
            return _call_with_retries(lambda: self.client.delete_worksheet(worksheet_uuid))

        MAX_BYTES = 1024*1024
        def read_file(self, uuid, path):
            fid = self.client.open_target((uuid, path))
            try:
                while True:
                    bytes = self.client.read_file(fid, BundleService.MAX_BYTES)
                    yield bytes.data
                    if len(bytes.data) < BundleService.MAX_BYTES:
                        break
            finally:
                self.client.close_file(fid)

        def download_target(self, uuid, return_zip=False):
            target = (uuid, '')
            result_path, container_path = self.client.download_target(target=target, follow_symlinks=True, return_zip=return_zip)
            return (result_path, container_path)

        def http_status_from_exception(self, ex):
            # This is brittle. See https://github.com/codalab/codalab/issues/345.
            if type(ex) == UsageError:
                return 404
            return 500

        def update_bundle_metadata(self, uuid, new_metadata):
            self.client.update_bundle_metadata(uuid, new_metadata)
            return


else:

    class BundleService():

        def items(self):
            return []

        def item(self, uuid):
            raise NotImplementedError

        def worksheets(self):
            return []

        def worksheet(self, uuid):
            raise NotImplementedError

        def ls(self, uuid, path):
            raise NotImplementedError

