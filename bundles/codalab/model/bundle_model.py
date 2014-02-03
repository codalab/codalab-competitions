from codalab.bundles import get_bundle_subclass
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

  def create_tables(self):
    '''
    Create all Codalab bundle tables if they do not already exist.
    '''
    db_metadata.create_all(self.engine)

  def get_bundle(self, uuid):
    '''
    Retrieve a bundle from the database given its uuid.
    '''
    with self.engine.begin() as connection:
      bundle_row = connection.execute(cl_bundle.select().where(
        cl_bundle.c.uuid == uuid
      )).fetchone()
      if not bundle_row:
        raise ValueError('Could not find bundle with uuid %s' % (uuid,))
      metadata_rows = connection.execute(cl_bundle_metadata.select().where(
        cl_bundle_metadata.c.bundle_uuid == uuid
      )).fetchall()
    bundle_value = dict(bundle_row, metadata=metadata_rows)
    bundle = get_bundle_subclass(bundle_value['bundle_type'])(bundle_value)
    bundle.validate()
    return bundle

  def save_bundle(self, bundle):
    '''
    Save a bundle. On success, sets the Bundle object's id from the result.
    '''
    bundle.validate()
    bundle_value = bundle.to_dict()
    bundle_metadata_values = bundle_value.pop('metadata')
    with self.engine.begin() as connection:
      result = connection.execute(cl_bundle.insert().values(bundle_value))
      connection.execute(cl_bundle_metadata.insert(), bundle_metadata_values)
      bundle.id = result.lastrowid
