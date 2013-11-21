from codalab.model.database_object import DatabaseObject
from codalab.model.tables import bundle as cl_bundle
from codalab.objects.metadata import Metadata


class Bundle(DatabaseObject):
  COLUMNS = tuple(column for column in cl_bundle if column != 'id')

  # Bundle subclasses should have a string BUNDLE_TYPE and a METADATA_TYPES
  # dictionary mapping metadata keys -> value types.
  BUNDLE_TYPE = None
  METADATA_TYPES = None

  @classmethod
  def construct(*args, **kwargs):
    raise NotImplementedError

  def validate(self):
    assert(self.BUNDLE_TYPE is not None), \
      'Initialized abstract bundle class %s' % (self.__class__.__name__,)
    if self.bundle_type != self.BUNDLE_TYPE:
      raise ValueError(
        'Mismatched bundle types: %s vs %s' %
        (self.bundle_type, self.BUNDLE_TYPE)
      )
    # TODO(skishore): Validate state against a list of states.
    self.metadata.validate(self.METADATA_TYPES)

  def __repr__(self):
    id_str = 'id=%d' % (self.id,) if hasattr(self, 'id') else ''
    return '%s(%sname=%s, data_hash=%s)' % (
      self.__class__.__name__,
      self.bundle_type.title(),
      id_str,
      repr(self.metadata.name),
      repr(self.data_hash),
    )

  def update_in_memory(self, row):
    super(Bundle, self).update_in_memory(row)
    self.metadata = Metadata.from_dicts(self.METADATA_TYPES, row['metadata'])
  
  def to_dict(self):
    result = super(Bundle, self).to_dict()
    result['metadata'] = self.metadata.to_dicts(self.METADATA_TYPES)
