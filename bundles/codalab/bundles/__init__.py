from codalab.bundles.dataset_bundle import DatasetBundle
from codalab.bundles.program_bundle import ProgramBundle


BUNDLE_SUBCLASSES = (
  DatasetBundle,
  ProgramBundle,
)

BUNDLE_TYPE_MAP = {cls.BUNDLE_TYPE: cls for cls in BUNDLE_SUBCLASSES}
assert(len(BUNDLE_TYPE_MAP) == len(BUNDLE_SUBCLASSES)), \
  'bundle_type collision: %s' % (BUNDLE_TYPE_MAP,)


def get_bundle_subclass(bundle_type):
  return BUNDLE_TYPE_MAP[bundle_type]
