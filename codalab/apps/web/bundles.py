
from django.conf import settings

if settings.BUNDLE_SERVICE_ENABLED:
    from codalab.client.remote_bundle_client import RemoteBundleClient

    class BundleService():

        def __init__(self):
            self.client = RemoteBundleClient(settings.BUNDLE_SERVICE_URL)

        def items(self):
            results = self.client.search()
            return results

else:

    class BundleService():

        def items(self):
            return []
