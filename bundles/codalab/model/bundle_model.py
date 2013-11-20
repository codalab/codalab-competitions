from codalab.model.tables import create_table_statements


class BundleModel(object):
  def __init__(self, cursor):
    self.cursor = cursor

  def init_schema(self):
    for statement in create_table_statements:
      self.cursor.execute(statement)
