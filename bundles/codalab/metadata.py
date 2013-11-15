import inspect


class Metadata(object):
  BASE_METADATA_KEYS = {
    'name': basestring,
    'description': basestring,
    'tags': set,
  }

  def __init__(self, **kwargs):
    '''
    The constructor for a Metadata subclass takes its keys as keyword arguments.
    '''
    for (key, value) in kwargs.iteritems():
      self.set_metadata_key(key, value)

  def set_metadata_key(self, key, value):
    '''
    Perform validation, then set this Metadata object's value for a given key.
    '''
    if key not in self.METADATA_KEYS:
      raise ValueError('Unexpected metadata key: %s' % (key,))
    metadata_type = self.METADATA_KEYS[key]
    if (metadata_type == set and
        any(not isinstance(subvalue, basestring) for subvalue in value)):
      raise ValueError(
        'List-type metadata key %s had non-string entries: %s' %
        (key, value)
      )
    elif not isinstance(value, metadata_type):
      raise ValueError(
        'Metadata key %s should have values of type %s, was %s' %
        (key, metadata_type, value)
      )
    setattr(self, key, value)

  @staticmethod
  def get_metadata_subclass(bundle_type):
    '''
    Return the Metadata subclass associated with a given bundle type.
    '''
    subclass_name = '%sMetadata' % (bundle_type.title(),)
    return Metadata.METADATA_SUBCLASSES[subclass_name]

  @staticmethod
  def get_type_constructor(metadata_type):
    '''
    Return the type constructor for each type of metadata.
    Note that basestrings cannot be instantiated, so we return unicode instead.
    '''
    return unicode if metadata_type == basestring else metadata_type

  @staticmethod
  def from_dicts(bundle_type, rows):
    '''
    Construct a Metadata object given a bundle type and a denormalized list of
    metadata dicts. These dicts may either be those returned by from_dicts or
    sqlalchemy Row objects from the metadata table.
    '''
    subclass = Metadata.get_metadata_subclass(bundle_type)
    metadata = {}
    for (key, metadata_type) in subclass.METADATA_KEYS.iteritems():
      if metadata_type == set:
        metadata[key] = set()
    for row in rows:
      (key, value) = (row['metadata_key'], row['metadata_value'])
      metadata_type = subclass.METADATA_KEYS[key]
      if metadata_type == set:
        metadata[key].add(value)
      else:
        if key in metadata:
          raise ValueError(
            'Got duplicate values %s and %s for key %s' %
            (metadata[key], value, key)
          )
        metadata[key] = Metadata.get_type_constructor(metadata_type)(value)
    return subclass(**metadata)

  def to_dicts(self, bundle_id):
    '''
    Serialize this metadata object and return a list of dicts that can be saved
    to a MySQL table. These dicts should have the following keys:
      bundle_id
      metadata_key
      metadata_value
    '''
    result = []
    for (key, metadata_type) in self.METADATA_KEYS.iteritems():
      value = getattr(self, key, self.get_type_constructor(metadata_type)())
      values = value if metadata_type == set else (value,)
      for value in values:
        result.append({
          'bundle_id': bundle_id,
          'metadata_key': key,
          'metadata_value': unicode(value),
        })
    return result


class ProgramMetadata(Metadata):
  METADATA_KEYS = dict(Metadata.BASE_METADATA_KEYS)
  METADATA_KEYS['architectures'] = set


class DatasetMetadata(Metadata):
  METADATA_KEYS = dict(Metadata.BASE_METADATA_KEYS)


class MacroMetadata(Metadata):
  METADATA_KEYS = dict(Metadata.BASE_METADATA_KEYS)


Metadata.METADATA_SUBCLASSES = {
  cls.__name__: cls for cls in locals().itervalues()
  if inspect.isclass(cls) and issubclass(cls, Metadata) and cls != Metadata
}
