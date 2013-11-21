import os
from sqlalchemy import create_engine

from codalab.model.bundle_model import BundleModel


class SQLiteModel(BundleModel):
  SQLITE_DB_FILE_NAME = 'bundle.db'

  def __init__(self, root):
    if not os.path.isabs(root):
      root = os.path.join(os.getcwd(), root)
    normalized_root = os.path.normpath(root)
    sqlite_db_path = os.path.join(normalized_root, self.SQLITE_DB_FILE_NAME)
    engine = create_engine('sqlite:///%s' % (sqlite_db_path,))
    super(SQLiteModel, self).__init__(engine)
