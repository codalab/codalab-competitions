import mock
from sqlalchemy import create_engine
from sqlalchemy.engine.reflection import Inspector
import unittest

from codalab.model.bundle_model import (
  BundleModel,
  db_metadata,
)


def metadata_to_dicts(uuid, metadata):
  return [
    {
      'bundle_uuid': uuid,
      'metadata_key': key,
      'metadata_value': value,
    }
    for (key, value) in metadata.iteritems()
  ]


def canonicalize(metadata_dicts):
  '''
  Convert a list of metadata dicts (which may be computed in-memory by
  calling metadata_to_dicts, or which may come from SQLAlchemy) into a
  canonical form for comparison.
  '''
  # Strip out any 'id' columns coming from the database.
  return sorted(
    sorted((k, v) for (k, v) in dict(metadata_dict).iteritems() if k != 'id')
    for metadata_dict in metadata_dicts
  )


class MockBundle(object):
  _fields = {
    'uuid': 'my_uuid',
    'bundle_type': 'my_bundle_type',
    'data_hash': 'my_data_hash',
    'state': 'my_state',
    'is_current': False,
    'metadata': {'key_1': 'value_1', 'key_2': 'value_2'},
  }

  def __init__(self, row=None):
    if row:
      for (field, value) in self._fields.iteritems():
        if field == 'metadata':
          actual_value = canonicalize(row[field])
          expected_value = canonicalize(
            metadata_to_dicts(self._fields['uuid'], self._fields['metadata'])
          )
          self._tester.assertEqual(actual_value, expected_value)
        else:
          self._tester.assertEqual(row[field], value)
    for (field, value) in self._fields.iteritems():
      setattr(self, field, value)

  def validate(self):
    self._validate_called = True

  def to_dict(self):
    result = dict(self._fields)
    result['metadata'] = metadata_to_dicts(result['uuid'], result['metadata'])
    return result


class BundleModelTest(unittest.TestCase):
  def setUp(self):
    MockBundle._tester = self
    self.engine = create_engine('sqlite://', strategy='threadlocal')
    self.model = BundleModel(self.engine)
    # We'll test the result of this schema creation step in test_create_tables.
    self.model.create_tables()

  def tearDown(self):
    self.model = None
    self.engine = None

  def test_create_tables(self):
    inspector = Inspector.from_engine(self.engine)
    tables = set(inspector.get_table_names())
    for table in db_metadata.tables:
      self.assertIn(table, tables)

  def test_save_and_get_bundle(self):
    bundle = MockBundle()
    self.model.save_bundle(bundle)
    self.assertTrue(bundle._validate_called)

    get_bundle_subclass_path = 'codalab.model.bundle_model.get_bundle_subclass'
    with mock.patch(get_bundle_subclass_path, lambda bundle_type: MockBundle):
      retrieved_bundle = self.model.get_bundle(bundle.uuid)
    self.assertTrue(isinstance(retrieved_bundle, MockBundle))
    self.assertTrue(retrieved_bundle._validate_called)
