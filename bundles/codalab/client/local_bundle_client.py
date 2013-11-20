import os
import sqlite3

# TODO(skishore): Get some sort of virtualenv / package system working.
from codalab.bundle_client import BundleClient
# TODO(skishore): There is no BundleModel...
from codalab.bundle_model import BundleModel


class LocalBundleClient(BundleClient):
  BUNDLES_DB_NAME = 'bundle.db'

  def __init__(self, home, model):
    # CodaLab data structures will live in a home directory that this client
    # needs to know the location of. This directory defaults to $HOME/.codalab.
    self.home = home
    bundles_db_path = os.path.join(self.home, self.BUNDLES_DB_NAME)
    # Ugh, should be initializing the model to point to either a MySQL server
    # (with some url) or a sqlite3 file (with some path) based on config.
    self.bundles_db = sqlite3.connect(bundles_db_path)
    self.cursor = self.bundles_db.cursor()
    self.model = BundleModel(self.cursor)

  # TODO(skishore): Add a basic implementation of the BundleClient interface.
