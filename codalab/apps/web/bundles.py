import base64
from time import sleep
import mimetypes
import os

from django.conf import settings
from django.template.defaultfilters import slugify
from django.utils.encoding import smart_str

from xmlrpclib import Fault, ProtocolError

if len(settings.BUNDLE_SERVICE_URL) > 0:

    from apps.authenz.oauth import get_user_token
    #imports from command line interface
    from codalab.bundles.make_bundle import MakeBundle
    from codalab.bundles.run_bundle import RunBundle
    from codalab.bundles.uploaded_bundle import UploadedBundle
    from codalab.bundles import get_bundle_subclass
    from codalab.client.remote_bundle_client import RemoteBundleClient
    from codalab.common import UsageError, PermissionError
    from codalab.lib import worksheet_util, bundle_cli, metadata_util, spec_util
    from codalab.objects.permission import permission_str, group_permissions_str
    from codalab.lib.codalab_manager import CodaLabManager
    from codalab.server.rpc_file_handle import RPCFileHandle
    from codalab.lib import file_util

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
            ## def get_bundle_infos(self, uuids, get_children=False, get_host_worksheets=False, get_permissions=False):
            bundle_info = _call_with_retries(lambda: self.client.get_bundle_info(uuid, True, True, True))
            # format permission data
            bundle_info['permission_str'] = permission_str(bundle_info['permission'])
            # format each groups as well
            for group_permission in bundle_info['group_permissions']:
                group_permission['permission_str'] = permission_str(group_permission['permission'])

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

        def get_worksheet_bundles(self, worksheet_uuid):
            worksheet_info = self.client.get_worksheet_info(worksheet_uuid, True, True)
            bundle_info_list = []
            for (bundle_info, subworksheet_info, value_obj, item_type) in worksheet_info['items']:
                if item_type == worksheet_util.TYPE_BUNDLE:
                    bundle_info_list.append(bundle_info)
            return bundle_info_list

        def worksheets(self):
            return _call_with_retries(lambda: self.client.list_worksheets())

        def search_worksheets(self, keywords, worksheet_uuid=None):
            return _call_with_retries(lambda: self.client.search_worksheets(keywords))

        def create_worksheet(self, name):
            return _call_with_retries(lambda: self.client.new_worksheet(name, None))

        def get_worksheet_uuid(self, spec):
            uuid = None
            spec = smart_str(spec)  # generic clean up just in case
            try:
                if(spec_util.UUID_REGEX.match(spec)): # generic function sometimes get uuid already just return it.
                    uuid = spec
                else:
                    uuid = worksheet_util.get_worksheet_uuid(self.client, None, spec)
            except UsageError, e:
                #TODO handle Found multiple worksheets with name
                raise e
            return uuid

        def get_bundle_uuid(self, bundle_spec, worksheet_uuid=None):
            uuid = None
            spec = smart_str(spec)  # generic clean up just in case
            try:
                if(spec_util.UUID_REGEX.match(spec)):  # generic function sometimes get uuid already just return it.
                    uuid = spec
                else:
                    uuid = worksheet_util.get_bundle_uuid(client, worksheet_uuid, bundle_spec)
            except UsageError, e:
                #TODO handle Found multiple worksheets with name
                raise e
            return uuid


        def worksheet(self, uuid, interpreted=False, fetch_items=True, get_raw=True):
            try:
                worksheet_info  = self.client.get_worksheet_info(
                                            uuid,
                                            fetch_items,  # fetch_items
                                            True,  # get_permissions
                                )
            except PermissionError:
                raise UsageError # forces a not found
            if get_raw:
                worksheet_info['raw'] = worksheet_util.get_worksheet_lines(worksheet_info)
            # set permissions
            worksheet_info['edit_permission'] = False
            if worksheet_info['permission'] == GROUP_OBJECT_PERMISSION_ALL:
                worksheet_info['edit_permission'] = True

            worksheet_info['permission_str'] = permission_str(worksheet_info['permission'])
            # format each groups as well
            for group_permission in worksheet_info['group_permissions']:
                group_permission['permission_str'] = permission_str(group_permission['permission'])


            if interpreted:
                interpreted_items = worksheet_util.interpret_items(
                                    worksheet_util.get_default_schemas(),
                                    worksheet_info['items']
                                )
                worksheet_info['items'] = self.client.resolve_interpreted_items(interpreted_items['items'])
                # Currently, only certain fields are base64 encoded.
                for item in worksheet_info['items']:
                    if item['mode'] in ['html', 'contents']:
                        # item['name'] in ['stdout', 'stderr']
                        if item['interpreted'] is None:
                            item['interpreted'] = ['MISSING']
                        else:
                            item['interpreted'] = map(base64.b64decode, item['interpreted'])
                    elif item['mode'] == 'table':
                        for row_map in item['interpreted'][1]:
                            for k, v in row_map.iteritems():
                                if v is None:
                                     row_map[k] = 'MISSING'
                    elif 'bundle_info' in item:
                        for bundle_info in item['bundle_info']:
                            try:
                                ## sometimes bundle_info is a string. when item['mode'] is image
                                if isinstance(bundle_info, dict) and bundle_info.get('bundle_type', None) == 'run':
                                    if 'stdout' in bundle_info.keys():
                                        bundle_info['stdout'] = base64.b64decode(bundle_info['stdout'])
                                    if 'stderr' in bundle_info.keys():
                                        bundle_info['stderr'] = base64.b64decode(bundle_info['stderr'])
                            except Exception, e:
                                print e
                                import ipdb; ipdb.set_trace()


                return worksheet_info
            else:
                return worksheet_info

        # TODO: remove this, not necessary
        def create_run_bundle(self, args, worksheet_uuid):
            cli = self._create_cli(worksheet_uuid)
            parser = cli.create_parser('run')
            parser.add_argument('target_spec', help=cli.TARGET_SPEC_FORMAT, nargs='*')
            parser.add_argument('command', help='Command-line')
            metadata_util.add_arguments(RunBundle, set(), parser)
            metadata_util.add_edit_argument(parser)
            args = parser.parse_args(args)
            metadata = metadata_util.request_missing_metadata(RunBundle, args)
            targets = cli.parse_key_targets(self.client, worksheet_uuid, args.target_spec)

            new_bundle_uuid = self.client.derive_bundle('run', targets, args.command, metadata, worksheet_uuid)
            return new_bundle_uuid


        def upload_bundle(self, source_file, bundle_type, worksheet_uuid):
            '''
            Upload |source_file| (a stream) to |worksheet_uuid|.
            '''
            # Construct info for creating the bundle.
            bundle_subclass = get_bundle_subclass(bundle_type) # program or data
            metadata = metadata_util.request_missing_metadata(bundle_subclass, {}, initial_metadata={'name': source_file.name, 'description': 'Upload ' + source_file.name})
            info = {'bundle_type': bundle_type, 'metadata': metadata}

            # Upload it by creating a file handle and copying source_file to it (see RemoteBundleClient.upload_bundle in the CLI).
            remote_file_uuid = self.client.open_temp_file()
            dest = RPCFileHandle(remote_file_uuid, self.client.proxy)
            file_util.copy(source_file, dest, autoflush=False, print_status='Uploading %s' % info['metadata']['name'])
            dest.close()

            # Then tell the client that the uploaded file handle is there.
            new_bundle_uuid = self.client.upload_bundle_zip(remote_file_uuid, info, worksheet_uuid, False, True)
            return new_bundle_uuid

        def add_worksheet_item(self, worksheet_uuid, bundle_uuid):
            self.client.add_worksheet_item(worksheet_uuid, worksheet_util.bundle_item(bundle_uuid))

        def parse_and_update_worksheet(self, uuid, lines):
            worksheet_info = self.client.get_worksheet_info(uuid, True)
            new_items, commands = worksheet_util.parse_worksheet_form(lines, self.client, worksheet_info['uuid'])
            self.client.update_worksheet_items(
                                worksheet_info,
                                new_items
                        )


        def get_target_info(self, target, depth=1):
            return _call_with_retries(lambda: self.client.get_target_info(target, depth))

        def resolve_interpreted_items(self, interpreted_items):
            return _call_with_retries(lambda: self.client.resolve_interpreted_items(('test', 'test')))

        def delete_worksheet(self, worksheet_uuid):
            return _call_with_retries(lambda: self.client.delete_worksheet(worksheet_uuid, False))

        # Create an instance of a CLI.
        def _create_cli(self, worksheet_uuid):
            manager = CodaLabManager(temporary=True, clients={settings.BUNDLE_SERVICE_URL: self.client})
            manager.set_current_worksheet_uuid(self.client, worksheet_uuid)
            cli = bundle_cli.BundleCLI(manager, headless=True)
            return cli

        def general_command(self, worksheet_uuid, command):
            cli = self._create_cli(worksheet_uuid)
            args = worksheet_util.string_to_tokens(command)
            def do_command():
                from cStringIO import StringIO
                import sys
                real_stdout = sys.stdout
                sys.stdout = StringIO()
                stdout_str = None

                real_stderr = sys.stderr
                sys.stderr = StringIO()
                stderr_str = None

                exception = None
                try:
                    cli.do_command(args)
                    success = True
                except SystemExit as e:
                    pass  # stderr will will tell the user the error
                except BaseException as e:
                    exception = smart_str(e)
                    success = False
                stdout_str = sys.stdout.getvalue()
                sys.stdout.close()
                sys.stdout = real_stdout


                stderr_str = sys.stderr.getvalue()
                sys.stderr.close()
                sys.stderr = real_stderr

                print '>>> general_command on worksheet %s: %s' % (worksheet_uuid, command)
                print stdout_str
                print stderr_str
                return {'stdout': stdout_str, 'stderr': stderr_str, 'exception': str(exception) if exception else None}
            return _call_with_retries(do_command)

        MAX_BYTES = 1024*1024
        def read_target(self, target):
            '''
            Given target (bundle uuid, path), return (stream, name, content_type).
            '''
            uuid, path = target
            bundle_info = self.client.get_bundle_info(uuid, False, False, False)
            if path == '':
                name = bundle_info['metadata']['name']
            else:
                name = os.path.basename(path)

            target_info = self.client.get_target_info(target, 0)
            if target_info['type'] == 'file':
                # Is a file, Don't need to zip it up
                content_type = mimetypes.guess_type(name)[0]
                if not content_type: content_type = 'text/plain'
                source_uuid = self.client.open_target(target)
                delete = False
            else:
                # Is a directory, need to zip it up
                content_type = 'zip'
                source_uuid, _ = self.client.open_target_zip(target, False)
                name += '.zip'
                delete = True

            def read_file():
                try:
                    while True:
                        bytes = self.client.read_file(source_uuid, BundleService.MAX_BYTES)
                        yield bytes.data
                        if len(bytes.data) < BundleService.MAX_BYTES:
                            break
                finally:
                    self.client.finalize_file(source_uuid, delete)

            print 'Downloading bundle uuid %s => %s %s' % (uuid, name, content_type)
            return read_file(), name, content_type

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

