
from django.conf import settings
from time import sleep
from xmlrpclib import Fault, ProtocolError

if len(settings.BUNDLE_SERVICE_URL) > 0:
    from codalab.client.remote_bundle_client import RemoteBundleClient

    def _call_with_retries(f, retry_count=0):
        try:
            return f()
        except (Fault, ProtocolError) as e:
            if retry_count < 2:
                sleep(0.1)
                return _call_with_retries(f, retry_count=retry_count+1)
            raise e

    class BundleService():

        def __init__(self):
            self.client = RemoteBundleClient(settings.BUNDLE_SERVICE_URL)

        def items(self):
            return _call_with_retries(lambda: self.client.search())

        def item(self, uuid):
            return _call_with_retries(lambda: self.client.info(uuid))

        def worksheets(self):
            return _call_with_retries(lambda: self.client.list_worksheets())

        def worksheet(self, uuid):
            return _call_with_retries(lambda: self.client.worksheet_info(uuid))

else:

    class BundleService():

        def items(self):
            return []
