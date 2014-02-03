import simplejson as json
import unittest

from codalab.objects.bundle import Bundle
from codalab.objects.metadata import Metadata


class MockBundle(Bundle):
  BUNDLE_TYPE = 'mock'
  METADATA_TYPES = {
    'str_metadata': basestring,
    'int_metadata': int,
    'set_metadata': set,
  }

  @classmethod
  def construct(cls, **kwargs):
    final_kwargs = dict(kwargs, bundle_type=MockBundle.BUNDLE_TYPE)
    return cls(final_kwargs)


class BundleTest(unittest.TestCase):
  columns = tuple(
    column.name for column in Bundle.TABLE.c if column.name != 'id'
  )

  str_metadata = 'my_str'
  int_metadata = 17
  set_metadata = ['value_1', 'value_2']

  bundle_type = MockBundle.BUNDLE_TYPE
  data_hash = 'my_data_hash'
  state = 'my_state'
  is_current = True

  def construct_mock_bundle(self):
    metadata = Metadata(
      str_metadata=self.str_metadata,
      int_metadata=self.int_metadata,
      set_metadata=self.set_metadata,
    )
    return MockBundle.construct(
      data_hash=self.data_hash,
      state=self.state,
      is_current=self.is_current,
      metadata=metadata,
    )

  def check_bundle(self, bundle, uuid=None):
    for (key, value_type)in MockBundle.METADATA_TYPES.iteritems():
      expected_value = getattr(self, key)
      if value_type == set:
        expected_value = set(expected_value)
      self.assertEqual(getattr(bundle.metadata, key), expected_value)
    for column in self.columns:
      if column == 'uuid':
        expected_value = uuid or getattr(bundle, column)
      else:
        expected_value = getattr(self, column)
      self.assertEqual(getattr(bundle, column), expected_value)

  def test_init(self):
    '''
    Test that initializing a Bundle works and that its fields are correct.
    '''
    bundle = self.construct_mock_bundle()
    bundle.validate()
    self.check_bundle(bundle)

  def test_to_dict(self):
    '''
    Test that serializing and deserializing a bundle recovers the original.
    '''
    bundle = self.construct_mock_bundle()
    serialized_bundle = bundle.to_dict()
    # Serialize through JSON to check that the serialized bundle can be
    # transferred over the wire or depressed into a database.
    json_bundle = json.loads(json.dumps(serialized_bundle))
    deserialized_bundle = MockBundle(json_bundle)
    self.check_bundle(deserialized_bundle, uuid=bundle.uuid)
