class DatabaseObject(object):
  # To use this class, subclass it and set TABLE to a SQLAlchemy table object.
  TABLE = None

  def __init__(self, row):
    self.columns = tuple(
      column.name for column in self.TABLE.c if column.name != 'id'
    )
    self.update_in_memory(row)

  def update_in_memory(self, row):
    '''
    Initialize the attributes on this object from the data in the row.
    The attributes of the row are inferred from the table columns.
    '''
    for column in self.columns:
      if column not in row:
        raise ValueError('Row %s is missing column: %s' % (row, column))
    for (key, value) in row.iteritems():
      if not hasattr(self.TABLE.c, key):
        raise ValueError('Unexpected column in update: %s' % (key,))
      setattr(self, key, value)

  def to_dict(self):
    '''
    Return a JSON-serializable and database-uploadable dictionary that
    represents this object.
    '''
    return {column: getattr(self, column) for column in self.columns}
