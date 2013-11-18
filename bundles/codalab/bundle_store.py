# TODOs:
# - Deal with permissions bits / ownership
# - Deal with symlinks
# - Add a method to clean up the temp directory based on mtimes
# - Tests! Need to be careful, as this changes the filesystem...
import errno
import hashlib
import os
import shutil
import uuid


class BundleStore(object):
  DATA_SUBDIRECTORY = 'data'
  TEMP_SUBDIRECTORY = 'temp'
  BLOCK_SIZE = 0x40000

  def __init__(self, root):
    self.root = self.normalize_path(root)
    self.data = os.path.join(self.root, self.DATA_SUBDIRECTORY)
    self.temp = os.path.join(self.root, self.TEMP_SUBDIRECTORY)
    self.make_directories()

  def make_directories(self):
    '''
    Create the root, data, and temp directories for this BundleStore.
    '''
    for path in (self.root, self.data, self.temp):
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
    This path is returned in a "canonical form", without .'s or ..'s.
    '''
    if not os.path.isabs(path):
      path = os.path.join(os.getcwd(), path)
    return os.path.normpath(path)

  @staticmethod
  def check_isdir(path, fn_name):
    '''
    Raise ValueError if the given path does not point to a directory.
    '''
    if not os.path.isdir(path):
      raise ValueError('%s called with non-directory: %s' % (fn_name, path))

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
    # Hash the contents of the temporary directory, and then if there is no
    # data with this hash value, move this directory into the data directory.
    data_hash = self.hash_directory(temp_path)
    final_path = os.path.join(self.data, data_hash)
    if os.path.exists(final_path):
      shutil.rmtree(temp_path)
    else:
      os.rename(temp_path, final_path)
    # After this operation there should always be a directory at the final path.
    assert(os.path.isdir(final_path)), 'Uploaded to %s failed!' % (final_path,)
    return data_hash

  @classmethod
  def hash_directory(cls, path):
    '''
    Return the hash of the contents of the folder at the given path.
    This hash is independent of the path itself - if you were to move the
    directory and call get_hash again, you would get the same result.
    '''
    absolute_path = cls.normalize_path(path)
    cls.check_isdir(absolute_path, 'get_directory_hash')
    overall_hash = hashlib.sha1()
    for (root, _, files) in os.walk(absolute_path):
      assert(os.path.isabs(root)), 'Got relative root in os.walk: %s' % (root,)
      for file_name in files:
        # For each file, we will update the overall hash with the hash of the
        # file subpath and the hash of the file contents. It is important that
        # we hash twice, so that we call update with a fixed-length string for
        # each file - otherwise, a sequence of hash updates might be ambiguous.
        file_path = os.path.join(root, file_name)
        if not file_path.startswith(root):
          raise ValueError('file_path %s not under root %s' % (file_path, root))
        # Update the overall hash with the hash of the file subpath.
        relative_path = file_path[len(root):]
        overall_hash.update(hashlib.sha1(relative_path).hexdigest())
        # Update the overall hash with the hash of the file contents.
        overall_hash.update(cls.hash_file_contents(file_path))
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
