# TODO(skishore): Write tests for this using an in-memory SQLite database.
from sqlalchemy.orm import sessionmaker

from codalab.model.tables import (
  bundle as cl_bundle,
  bundle_metadata as cl_bundle_metadata,
  db_metadata,
)


class BundleModel(object):
  def __init__(self, engine):
    '''
    Initialize a BundleModel with the given SQLAlchemy engine.
    '''
    self.engine = engine
    self.session = sessionmaker(bind=engine)

  def create_tables(self):
    '''
    Create all Codalab bundle tables if they do not already exist.
    '''
    db_metadata.create_all(self.engine)

  def _execute(self, query):
    return self.session.execute(query)

  def _execute_ac(self, query):
    result = self.session.execute(query)
    self.session.commit()
    return result

  def save_bundle(self, bundle):
    '''
    Save a bundle. On success, set the Bundle object's id from the result.
    '''
    bundle_value = bundle.to_dict()
    bundle_metadata_values = bundle_value.pop('metadata')
    bundle_id = self._execute(cl_bundle.insert().values(bundle_value)).lastrowid
    for value in bundle_metadata_values:
      value['bundle_id'] = bundle_id
    self._execute_ac(cl_bundle_metadata.insert().values(bundle_metadata_values))
    bundle.id = bundle_id
