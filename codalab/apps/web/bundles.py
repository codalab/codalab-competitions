
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

    fake_results = [
        {'bundle_type': 'dataset',
         'data_hash': '0x8c6917ce3d...1ac58a4a52fa1',
         'hard_dependencies': [],
         'metadata': {
            'name': 'Test Bundle 1',
            'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean ligula ipsum, pretium et porta sed, tempor a nibh. Vestibulum tellus ipsum, faucibus non faucibus at, consequat at nulla. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Vivamus pellentesque ultrices venenatis. Aliquam lobortis adipiscing diam, id venenatis dui laoreet vitae.',
            'created': 1391045308,
            'data_size': 12622,
            'tags': [] }, 
         'state': 'ready', 
         'uuid': '0x4a09904179c947f79e25936cb26c8d2b'},
        {'bundle_type': 'dataset',
         'data_hash': '0x8c6917ce3d...1ac58a4a52fa1',
         'hard_dependencies': [],
         'metadata': {
            'name': 'census_popuplation',
            'description': 'Census population data',
            'created': 1391045308,
            'data_size': 12622,
            'tags': [] }, 
         'state': 'staged', 
         'uuid': '0x4a09904179c947f79e25936cb26c8d2c'},
        {'bundle_type': 'dataset',
         'data_hash': '0x8c6917ce3d...1ac58a4a52fa1',
         'hard_dependencies': [],
         'metadata': {
            'name': 'census_popuplation',
            'description': 'Census population data',
            'created': 1391045308,
            'data_size': 12622,
            'tags': [] }, 
         'state': 'failed', 
         'uuid': '0x4a09904179c947f79e25936cb26c8d2d'}]

    class BundleService():

        def items(self):
            return fake_results

        def item(self, uuid):
            return [ result for result in fake_results if result['uuid'] == uuid ][0]
