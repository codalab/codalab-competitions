import re

from codalab.common import State
from codalab.objects.bundle import Bundle


class UploadedBundle(Bundle):
  METADATA_TYPES = {
    'name': basestring,
    'description': basestring,
    'tags': set,
  }
  NAME_REGEX = '[a-zA-Z_][a-zA-Z0-9_]*'

  @classmethod
  def construct(cls, data_hash, metadata):
    return cls({
      'bundle_type': cls.BUNDLE_TYPE,
      'data_hash': data_hash,
      'state': State.READY,
      'is_current': True,
      'metadata': metadata,
    })

  def validate(self):
    super(UploadedBundle, self).validate()
    class_name = self.__class__.__name__
    if not self.metadata.name:
      raise ValueError('%ss must have non-empty names' % (class_name,))
    if not re.match(self.NAME_REGEX, self.metadata.name):
      raise ValueError(
        "%s names must match %s, was '%s'" %
        (class_name, self.NAME_REGEX, self.metadata.name)
      )
    if not self.metadata.description:
      raise ValueError('%ss must have non-empty description' % (class_name,))
