from codalab.bundles.uploaded_bundle import UploadedBundle


class ProgramBundle(UploadedBundle):
  BUNDLE_TYPE = 'program'
  METADATA_TYPES = dict(UploadedBundle.METADATA_TYPES)
  METADATA_TYPES['architecture'] = set
