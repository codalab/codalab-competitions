class Metadata(object):
  def __init__(self, **kwargs):
    self._metadata_keys = set()
    for (key, value) in kwargs.iteritems():
      self.set_metadata_key(key, value)

  def validate(self, metadata_types):
    '''
    Check that this metadata has the correct metadata keys and that it has
    metadata values of the correct types.
    '''
    for key in self._metadata_keys:
      if key not in metadata_types:
        raise ValueError('Unexpected metadata key: %s' % (key,))
    for (key, value_type) in metadata_types.iteritems():
      if key not in self._metadata_keys:
        raise ValueError('Missing metadata key: %s' % (key,))
      value = getattr(self, key)
      if not isinstance(value, value_type):
        raise ValueError(
          'Metadata value for %s should be of type %s, was %s' %
          (key, value_type, type(value))
        )

  def set_metadata_key(self, key, value):
    '''
    Set this Metadata object's key to be the given value. Record the key.
    '''
    self._metadata_keys.add(key)
    if isinstance(value, (set, list, tuple)):
      value = set(value)
    setattr(self, key, value)

  @staticmethod
  def get_type_constructor(value_type):
    '''
    Return the type constructor for each type of metadata.
    Note that basestrings cannot be instantiated, so we return unicode instead.
    '''
    return unicode if value_type == basestring else value_type 

  @classmethod
  def from_dicts(cls, metadata_types, rows):
    '''
    Construct a Metadata object given a denormalized list of metadata dicts.
    These dicts may either be those returned by from_dicts or sqlalchemy Row objects from the metadata table.
    '''
    metadata_dict = {}
    for (key, value_type) in metadata_types.iteritems():
      metadata_dict[key] = cls.get_type_constructor(value_type)()
    for row in rows:
      (maybe_unicode_key, value) = (row['metadata_key'], row['metadata_value'])
      # If the key is Unicode text (which is the case if it was extracted from a
      # database), cast it to a string. This operation encodes it with UTF-8.
      key = str(maybe_unicode_key)
      value_type = metadata_types[key]
      if value_type == set:
        metadata_dict[key].add(value)
      else:
        if metadata_dict.get(key):
          raise ValueError(
            'Got duplicate values %s and %s for key %s' %
            (metadata_dict[key], value, key)
          )
        metadata_dict[key] = cls.get_type_constructor(value_type)(value)
    return Metadata(**metadata_dict)

  def to_dicts(self, metadata_types):
    '''
    Serialize this metadata object and return a list of dicts that can be saved
    to a MySQL table. These dicts should have the following keys:
      metadata_key
      metadata_value
    '''
    result = []
    for (key, value_type) in metadata_types.iteritems():
      value = getattr(self, key, self.get_type_constructor(value_type)())
      values = value if value_type == set else (value,)
      for value in values:
        result.append({
          'metadata_key': unicode(key),
          'metadata_value': unicode(value),
        })
    return result

  def to_dict(self):
    '''
    Serialize this metadata to human-readable JSON format. This format is NOT
    an appropriate one to save to a database.
    '''
    items = [(key, getattr(self, key)) for key in self._metadata_keys]
    return {
      key: list(value) if isinstance(value, (list, set, tuple)) else value
      for (key, value) in items
    }
