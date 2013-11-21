from codalab.bundles.named_bundle import NamedBundle


class ProgramBundle(NamedBundle):
  BUNDLE_TYPE = 'program'
  METADATA_TYPES = dict(NamedBundle.METADATA_TYPES)
  METADATA_TYPES['architecture'] = set
