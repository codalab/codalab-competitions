import uuid

from codalab.model.database_object import DatabaseObject
from codalab.model.tables import bundle as cl_bundle
from codalab.objects.metadata import Metadata


class Bundle(DatabaseObject):
  TABLE = cl_bundle

  # Bundle subclasses should have a string BUNDLE_TYPE and a METADATA_TYPES
  # dictionary mapping metadata keys -> value types.
  BUNDLE_TYPE = None
  METADATA_TYPES = None

  @classmethod
  def construct(cls, *args, **kwargs):
    raise NotImplementedError

  def validate(self):
    assert(self.BUNDLE_TYPE is not None), \
      'Initialized abstract bundle class %s' % (self.__class__.__name__,)
    if self.bundle_type != self.BUNDLE_TYPE:
      raise ValueError(
        'Mismatched bundle types: %s vs %s' %
        (self.bundle_type, self.BUNDLE_TYPE)
      )
    self.metadata.validate(self.METADATA_TYPES)

  def __repr__(self):
    return '%s(uuid=%r, name=%r)' % (
      self.__class__.__name__,
      self.uuid,
      self.metadata.name,
    )

  def update_in_memory(self, row):
    metadata = row.pop('metadata')
    if 'uuid' not in row:
      row['uuid'] = str(uuid.uuid4())
    super(Bundle, self).update_in_memory(row)
    if isinstance(metadata, dict):
      metadata = Metadata(**metadata)
    elif isinstance(metadata, (list, tuple)):
      metadata = Metadata.from_dicts(self.METADATA_TYPES, metadata)
    self.metadata = metadata
  
  def to_dict(self):
    result = super(Bundle, self).to_dict()
    result['metadata'] = self.metadata.to_dicts(self.METADATA_TYPES)
    for metadata_row in result['metadata']:
      metadata_row['bundle_uuid'] = self.uuid
    return result
