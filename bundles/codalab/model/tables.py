# TODO(skishore): Add various indices once we know how we're querying the db.
# TODO(skishore): Write these in a MySQL-compatible form.
create_table_statements = [
  '''
    CREATE TABLE bundle (
      id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
      bundle_type VARCHAR(63) NOT NULL,
      status VARCHAR(63) NOT NULL,
      is_active TINYINT NOT NULL,
      data_hash VARCHAR(63) NOT NULL
    )
  ''',
  '''
    CREATE TABLE bundle_metadata (
      id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
      bundle_id INTEGER NOT NULL,
      metadata_key VARCHAR(63) NOT NULL,
      metadata_value VARCHAR(63) NOT NULL,
      FOREIGN KEY (bundle_id) REFERENCES bundle(id)
    )
  ''',
  '''
    CREATE TABLE dependency (
      id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
      dependency_type VARCHAR(63) NOT NULL,
      child_bundle_id INT(11) NOT NULL,
      parent_bundle_id INT(11) NOT NULL,
      parent_subpath MEDIUMTEXT NOT NULL,
      FOREIGN KEY (child_bundle_id) REFERENCES bundle(id),
      FOREIGN KEY (parent_bundle_id) REFERENCES bundle(id)
    )
  ''',
]
