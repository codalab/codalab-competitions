# TODO(skishore): Add code to clean up the temp directory based on mtimes.
import errno
import hashlib
import itertools
import os
import shutil
import uuid


class BundleStore(object):
  DATA_SUBDIRECTORY = 'data'
  TEMP_SUBDIRECTORY = 'temp'
  BLOCK_SIZE = 0x40000

  def __init__(self, codalab_home):
    self.codalab_home = self.normalize_path(codalab_home)
    self.data = os.path.join(self.codalab_home, self.DATA_SUBDIRECTORY)
    self.temp = os.path.join(self.codalab_home, self.TEMP_SUBDIRECTORY)
    self.make_directories()

  def make_directories(self):
    '''
    Create the root, data, and temp directories for this BundleStore.
    '''
    for path in (self.codalab_home, self.data, self.temp):
      try:
        os.mkdir(path)
      except OSError, e:
        if e.errno != errno.EEXIST:
          raise
      self.check_isdir(path, 'make_directories')

  @staticmethod
  def normalize_path(path):
    '''
    Return the absolute path of the location specified by the given path.
    This path is returned in a "canonical form", without ~'s, .'s, ..'s.
    '''
    return os.path.abspath(os.path.expanduser(path))

  @staticmethod
  def check_isdir(path, fn_name):
    '''
    Raise ValueError if the given path does not point to a directory.
    '''
    if not os.path.isdir(path):
      raise ValueError('%s called with non-directory: %s' % (fn_name, path))

  def get_location(self, data_hash):
    '''
    Returns the on-disk location of the bundle with the given data hash.
    '''
    return os.path.join(self.data, data_hash)

  def upload(self, path):
    '''
    Copy the contents of the directory at path into the data subdirectory,
    in a subfolder named by a hash of the contents of the new data directory.

    Return the name of the new subfolder, that is, the data hash.
    '''
    absolute_path = self.normalize_path(path)
    self.check_isdir(absolute_path, 'upload')
    # Recursively copy the directory into a new BundleStore temp directory.
    temp_directory = str(uuid.uuid4())
    temp_path = os.path.join(self.temp, temp_directory)
    shutil.copytree(absolute_path, temp_path)
    # Recursively list the directory just once as an optimization.
    dirs_and_files = self.recursive_ls(temp_path)
    self.check_for_symlinks(temp_path, dirs_and_files)
    self.set_permissions(temp_path, 0o755, dirs_and_files)
    # Hash the contents of the temporary directory, and then if there is no
    # data with this hash value, move this directory into the data directory.
    data_hash = self.hash_directory(temp_path, dirs_and_files)
    final_path = os.path.join(self.data, data_hash)
    if os.path.exists(final_path):
      shutil.rmtree(temp_path)
    else:
      os.rename(temp_path, final_path)
    # After this operation there should always be a directory at the final path.
    assert(os.path.isdir(final_path)), 'Uploaded to %s failed!' % (final_path,)
    return data_hash

  @classmethod
  def recursive_ls(cls, path):
    '''
    Return two lists (directories, files) of files under the given path.
    All subpaths are given as absolute paths under the directory.
    '''
    absolute_path = cls.normalize_path(path)
    cls.check_isdir(absolute_path, 'recursive_ls')
    (directories, files) = ([], [])
    for (root, _, file_names) in os.walk(absolute_path):
      assert(os.path.isabs(root)), 'Got relative root in os.walk: %s' % (root,)
      directories.append(root)
      for file_name in file_names:
        files.append(os.path.join(root, file_name))
    return (directories, files)

  @staticmethod
  def get_relative_path(root, path):
    if not path.startswith(root):
      raise ValueError('Path %s was not under root %s' % (path, root))
    return path[len(root):]

  @classmethod
  def check_for_symlinks(cls, root, dirs_and_files=None):
    '''
    Raise ValueError if there are any symlinks under the given path.
    '''
    (directories, files) = dirs_and_files or cls.recursive_ls(root)
    for path in itertools.chain(directories, files):
      if os.path.islink(path):
        raise ValueError('Found symlink %s under %s' % (path, root))

  @classmethod
  def set_permissions(cls, root, permissions, dirs_and_files=None):
    '''
    Sets the permissions bits for all directories and files under the path.
    '''
    (directories, files) = dirs_and_files or cls.recursive_ls(root)
    for path in itertools.chain(directories, files):
      os.chmod(path, permissions)

  @classmethod
  def hash_directory(cls, path, dirs_and_files=None):
    '''
    Return the hash of the contents of the folder at the given path.
    This hash is independent of the path itself - if you were to move the
    directory and call get_hash again, you would get the same result.
    '''
    absolute_path = cls.normalize_path(path)
    cls.check_isdir(absolute_path, 'get_directory_hash')
    (directories, files) = dirs_and_files or cls.recursive_ls(absolute_path)
    # Sort and then hash all directories and then compute a hash of the hashes.
    # This two-level hash is necessary so that the overall hash is unambiguous -
    # if we updated directory_hash with the directory names themselves, then
    # we'd be hashing the concatenation of these names, which could be generated
    # in multiple ways.
    directory_hash = hashlib.sha1()
    for directory in sorted(directories):
      relative_path = cls.get_relative_path(absolute_path, directory)
      directory_hash.update(hashlib.sha1(relative_path).hexdigest())
    # Use a similar two-level hashing scheme for all files, but incorporate a
    # hash of both the file name and contents.
    file_hash = hashlib.sha1()
    for file_name in sorted(files):
      relative_path = cls.get_relative_path(absolute_path, file_name)
      file_hash.update(hashlib.sha1(relative_path).hexdigest())
      file_hash.update(cls.hash_file_contents(file_name))
    # Return a hash of the two hashes.
    overall_hash = hashlib.sha1(directory_hash.hexdigest())
    overall_hash.update(file_hash.hexdigest())
    return overall_hash.hexdigest()

  @classmethod
  def hash_file_contents(cls, file_path):
    '''
    Return the hash of the file's contents, read in blocks of size BLOCK_SIZE.
    '''
    if not os.path.isabs(file_path):
      raise ValueError('hash_file called with relative path: %s' % (file_path,))
    contents_hash = hashlib.sha1()
    with open(file_path, 'rb') as file_handle:
      while True:
        data = file_handle.read(cls.BLOCK_SIZE)
        if not data:
          break
        contents_hash.update(data)
    return contents_hash.hexdigest()
