class DatabaseObject(object):
  # To use this class, subclass it and set the list of non-id columns.
  COLUMNS = None

  def __init__(self, row):
    self.update_in_memory(row)

  def update_in_memory(self, row):
    '''
    Initialize the attributes on this object from the data in the row.
    The attributes of the row are inferred from the table columns.
    '''
    for column in self.COLUMNS:
      setattr(self, column, row[column])

  def to_dict(self):
    '''
    Return a JSON-serializable and database-uploadable dictionary that
    represents this object.
    '''
    result = {column: getattr(self, column) for column in self.COLUMNS}
    if hasattr(self, 'id'):
      result['id'] = self.id
    return result
