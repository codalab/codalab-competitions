import os

from codalab.model.sqlite_model import SQLiteModel


home_directory = os.path.expanduser('~')
model = SQLiteModel(home_directory)


from codalab.bundles.dataset_bundle import DatasetBundle
from codalab.objects.metadata import Metadata
model.create_tables()
metadata = Metadata(
  name='my_name',
  description='my_description',
  tags=list('tags'),
)
bundle = DatasetBundle.construct(data_hash='my_data_hash', metadata=metadata)
bundle.validate()
