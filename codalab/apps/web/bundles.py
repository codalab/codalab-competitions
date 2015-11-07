'''
Defines the BundleService class, which is the gateway between the frontend and
the BundleService/CLI backend (in the codalab-cli repo).

Internally, BundleService just creates a RemoteBundleClient and wraps some of
the calls.
'''
import base64
from time import sleep
import mimetypes
import os
import shlex

from django.conf import settings
from django.template.defaultfilters import slugify
from django.utils.encoding import smart_str

from xmlrpclib import Fault, ProtocolError

if len(settings.BUNDLE_SERVICE_URL) > 0:
    from apps.authenz.oauth import get_user_token

    # Imports from codalab-cli repo.
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
    from codalab.lib import file_util, formatting

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
        # Maximum number of lines of files to show
        HEAD_MAX_LINES = 100

        def __init__(self, user=None):
            self.client = RemoteBundleClient(settings.BUNDLE_SERVICE_URL,
                                             lambda command: get_user_token(user), verbose=1)

        def items(self):
            return _call_with_retries(lambda: self.client.search())

        def get_bundle_info(self, uuid):
            bundle_info = _call_with_retries(lambda: self.client.get_bundle_info(uuid, True, True, True))

            if bundle_info is None:
                return None
            # Set permissions
            bundle_info['edit_permission'] = (bundle_info['permission'] == GROUP_OBJECT_PERMISSION_ALL)
            # Format permissions into strings
            bundle_info['permission_str'] = permission_str(bundle_info['permission'])
            for group_permission in bundle_info['group_permissions']:
                group_permission['permission_str'] = permission_str(group_permission['permission'])

            metadata = bundle_info['metadata']

            cls = get_bundle_subclass(bundle_info['bundle_type'])
            for key, value in worksheet_util.get_formatted_metadata(cls, metadata):
                metadata[key] = value

            bundle_info['metadata'] = metadata
            bundle_info['editable_metadata_fields'] = worksheet_util.get_editable_metadata_fields(cls, metadata)

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

        def basic_worksheet(self, uuid):
            return self.worksheet(uuid, fetch_items=False, get_permissions=True, interpreted=False)

        def full_worksheet(self, uuid):
            return self.worksheet(uuid, fetch_items=True, get_permissions=True, interpreted=True)

        def worksheet(self, uuid, fetch_items, get_permissions, interpreted):
            '''
            Return information about a worksheet. Calls
            - get_worksheet_info: get basic info
            - resolve_interpreted_items: get more information about a worksheet.
            In the future, for large worksheets, might want to break this up so
            that we can render something basic.
            '''
            try:
                worksheet_info = self.client.get_worksheet_info(uuid, fetch_items, get_permissions)
            except PermissionError:
                raise UsageError # forces a not found

            if fetch_items:
                worksheet_info['raw'] = worksheet_util.get_worksheet_lines(worksheet_info)

            # Set permissions
            worksheet_info['edit_permission'] = (worksheet_info['permission'] == GROUP_OBJECT_PERMISSION_ALL)
            # Format permissions into strings
            worksheet_info['permission_str'] = permission_str(worksheet_info['permission'])
            for group_permission in worksheet_info['group_permissions']:
                group_permission['permission_str'] = permission_str(group_permission['permission'])

            # Go and fetch more information about the worksheet contents by
            # resolving the interpreted items.
            if interpreted:
                interpreted_items = worksheet_util.interpret_items(
                                    worksheet_util.get_default_schemas(),
                                    worksheet_info['items'])
                worksheet_info['items'] = self.client.resolve_interpreted_items(interpreted_items['items'])
                # Currently, only certain fields are base64 encoded.
                for item in worksheet_info['items']:
                    if item['mode'] in ['html', 'contents']:
                        if item['interpreted'] is None:
                            item['interpreted'] = [formatting.contents_str(item['interpreted'])]
                        else:
                            item['interpreted'] = map(base64.b64decode, item['interpreted'])
                    elif item['mode'] == 'table':
                        for row_map in item['interpreted'][1]:
                            for k, v in row_map.iteritems():
                                if v is None:
                                     row_map[k] = formatting.contents_str(v)
                    elif 'bundle_info' in item:
                        infos = []
                        if isinstance(item['bundle_info'], list):
                            infos = item['bundle_info']
                        elif isinstance(item['bundle_info'], dict):
                            infos = [item['bundle_info']]
                        for bundle_info in infos:
                            try:
                                if isinstance(bundle_info, dict):
                                    worksheet_util.format_metadata(bundle_info.get('metadata'))
                            except Exception, e:
                                print e
                                import ipdb; ipdb.set_trace()

            return worksheet_info

        def upload_bundle(self, source_file, bundle_type, worksheet_uuid):
            '''
            Upload |source_file| (a stream) to |worksheet_uuid|.
            '''
            # Construct info for creating the bundle.
            bundle_subclass = get_bundle_subclass(bundle_type) # program or data
            metadata = metadata_util.fill_missing_metadata(bundle_subclass, {}, initial_metadata={'name': source_file.name, 'description': 'Upload ' + source_file.name})
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
            '''
            Add bundle uuid to the given worksheet.
            '''
            self.client.add_worksheet_item(worksheet_uuid, worksheet_util.bundle_item(bundle_uuid))

        def parse_and_update_worksheet(self, uuid, lines):
            '''
            Replace worksheet |uuid| with the raw contents given by |lines|.
            '''
            worksheet_info = self.client.get_worksheet_info(uuid, True)
            new_items, commands = worksheet_util.parse_worksheet_form(lines, self.client, worksheet_info['uuid'])
            self.client.update_worksheet_items(worksheet_info, new_items)
            # Note: commands are ignored

        def get_bundle_contents(self, uuid):
            '''
            If bundle is a single file, get file contents.
            Otherwise, get stdout and stderr.
            For each file, only return the first few lines.
            '''
            def get_lines(name):
                lines = self.head_target((uuid, name), self.HEAD_MAX_LINES)
                if lines is not None:
                    import base64
                    lines = ''.join(map(base64.b64decode, lines))
                return lines
                
            info = self.get_target_info((uuid, ''), 2)  # List files
            if info['type'] == 'file':
                info['file_contents'] = get_lines('')
            else:
                # Read contents of stdout and stderr.
                info['stdout'] = None
                info['stderr'] = None
                contents = info.get('contents')
                if contents:
                    for item in contents:
                        name = item['name']
                        if name in ['stdout', 'stderr']:
                            info[name] = get_lines(name)
            return info

        def get_target_info(self, target, depth=1):
            info = _call_with_retries(lambda: self.client.get_target_info(target, depth))
            contents = info.get('contents')
            # Render the sizes
            if contents:
                for item in contents:
                    if 'size' in item:
                        item['size_str'] = formatting.size_str(item['size'])
            return info

        def delete_worksheet(self, worksheet_uuid):
            return _call_with_retries(lambda: self.client.delete_worksheet(worksheet_uuid, False))

        # Create an instance of a CLI.
        def _create_cli(self, worksheet_uuid):
            manager = CodaLabManager(temporary=True, clients={settings.BUNDLE_SERVICE_URL: self.client})
            manager.set_current_worksheet_uuid(self.client, worksheet_uuid)
            cli = bundle_cli.BundleCLI(manager, headless=True)
            return cli

        def complete_command(self, worksheet_uuid, command):
            '''
            Given a command string, return a list of suggestions to complete the last token.
            '''
            cli = self._create_cli(worksheet_uuid)
            return cli.complete_command(command)

        def get_command(self, raw_command_map):
            '''
            Return a cli-command corresponding to raw_command_map contents.
            Input:
                raw_command_map: a map containing the info to edit, new_value and the action to perform
            '''
            return worksheet_util.get_worksheet_info_edit_command(raw_command_map)

        def general_command(self, worksheet_uuid, command):
            '''
            Executes an arbitrary CLI command with |worksheet_uuid| as the current worksheet.
            Basically, all CLI functionality should go through this command.
            The method currently intercepts stdout/stderr and returns it back to the user.
            TODO: check thread-safety.
            '''
            cli = self._create_cli(worksheet_uuid)
            if isinstance(command, basestring):
                args = shlex.split(command)
            else:
                args = list(command)
            if args[0] == 'cl':
                args = args[1:]

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
                structured_result = None
                try:
                    structured_result = cli.do_command(args)
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
                return {
                    'structured_result': structured_result,
                    'stdout': stdout_str, 'stderr': stderr_str,
                    'exception': str(exception) if exception else None
                }
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
                '''
                Generates a stream of strings corresponding to the contents of this file.
                '''
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

        def home_worksheet(self, username):
            return spec_util.home_worksheet(username)

else:
    # Bundle service not supported
    class BundleService():
        def __init__(self, user=None):
            pass

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
