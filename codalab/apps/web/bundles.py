
from django.conf import settings
from time import sleep
from xmlrpclib import Fault, ProtocolError


if len(settings.BUNDLE_SERVICE_URL) > 0:

    from codalab.common import UsageError
    from codalab.client.remote_bundle_client import RemoteBundleClient
    from apps.authenz.oauth import get_user_token
    from codalab.lib import worksheet_util

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

        def item(self, uuid):
            return _call_with_retries(lambda: self.client.get_bundle_info(uuid))

        def worksheets(self):
            return _call_with_retries(lambda: self.client.list_worksheets())

        def create_worksheet(self, name):
            return _call_with_retries(lambda: self.client.new_worksheet(name))

        def worksheet(self, uuid, interpreted=False):
            worksheet_info  = _call_with_retries(
                    lambda: self.client.get_worksheet_info(
                            uuid,
                            True
                    )
                )
            if interpreted:
                interpreted_items = worksheet_util.interpret_items(
                                    worksheet_util.get_default_schemas(),
                                    worksheet_info['items']
                                )
                worksheet_info['items'] = self.client.resolve_interpreted_items(interpreted_items['items'])
                return worksheet_info
            else:
                return worksheet_info

        def get_target_info(self, target, depth=1):
            return _call_with_retries(lambda: self.client.get_target_info(target, depth))

        def resolve_interpreted_items(self, interpreted_items):
            return _call_with_retries(lambda: self.client.resolve_interpreted_items(('test', 'test')))

        def get_worksheet_info(self):
            return _call_with_retries(lambda: self.client.get_worksheet_info())

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

