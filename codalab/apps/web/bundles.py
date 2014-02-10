
from django.conf import settings

if len(settings.BUNDLE_SERVICE_URL) > 0:
    from codalab.client.remote_bundle_client import RemoteBundleClient

    class BundleService():

        def __init__(self):
            self.client = RemoteBundleClient(settings.BUNDLE_SERVICE_URL)

        def items(self):
            results = self.client.search()
            return results

        def item(self, uuid):
            result = self.client.info(uuid)
            return result

else:

    class BundleService():

        def items(self):
            return []
