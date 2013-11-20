import os
import sqlite3

from codalab.model.bundle_model import BundleModel


class SQLiteModel(BundleModel):
  SQLITE_DB_FILE_NAME = 'bundles.db'

  def __init__(self, root):
    sqlite_db_path = os.path.join(root, self.SQLITE_DB_FILE_NAME)
    sqlite_db = sqlite3.connect(sqlite_db_path)
    super(SQLiteModel, self).__init__(sqlite_db.cursor())
