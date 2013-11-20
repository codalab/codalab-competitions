import os

from codalab.model.sqlite_model import SQLiteModel


home_directory = os.path.expanduser('~')
model = SQLiteModel(home_directory)
