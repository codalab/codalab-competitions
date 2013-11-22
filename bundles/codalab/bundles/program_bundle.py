from codalab.bundles.uploaded_bundle import UploadedBundle


class ProgramBundle(UploadedBundle):
  BUNDLE_TYPE = 'program'
  METADATA_TYPES = dict(UploadedBundle.METADATA_TYPES)
  METADATA_TYPES['architecture'] = set


from codalab.objects.metadata import Metadata
metadata = Metadata(
  name='my_name',
  description='my_description',
  tags=['my_tag_1', 'my_tag_2'],
  architecture=[],
)
bundle = ProgramBundle.construct('my_data_hash', metadata)
bundle.validate()
print bundle

serialized_bundle = bundle.to_dict()
deserialized_bundle = ProgramBundle(serialized_bundle)
deserialized_bundle.validate()
print deserialized_bundle
