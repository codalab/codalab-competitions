import errno
import hashlib
import os
import shutil
import stat
import unittest

from codalab.bundle_store import BundleStore


class BundleStoreFSTest(unittest.TestCase):
  # WARNING: This directory is deleted in tearDown.
  # Do not make it something important!
  test_root = '/tmp/codalab_tests'

  bundle_path = os.path.join(test_root, 'test_bundle')
  bundle_directories = [
    bundle_path,
    os.path.join(bundle_path, 'asdf'),
    os.path.join(bundle_path, 'asdf', 'craw'),
    os.path.join(bundle_path, 'blah'),
  ]
  bundle_files = [
    os.path.join(bundle_path, 'foo'),
    os.path.join(bundle_path, 'asdf', 'bar'),
    os.path.join(bundle_path, 'asdf', 'baz'),
  ]
  contents = 'random file contents'

  def setUp(self):
    self.tearDown()
    os.mkdir(self.test_root)
    for directory in self.bundle_directories:
      os.mkdir(directory)
    for file_name in self.bundle_files:
      with open(file_name, 'w') as fd:
        fd.write(self.contents)

  def tearDown(self):
    try:
      shutil.rmtree(self.test_root)
    except OSError, e:
      if e.errno != errno.ENOENT:
        raise

  def test_recursive_ls(self):
    '''
    Test that recursive_ls lists all absolute paths within a directory.
    '''
    (directories, files) = BundleStore.recursive_ls(self.bundle_path)
    self.assertEqual(set(directories), set(self.bundle_directories))
    self.assertEqual(set(files), set(self.bundle_files))

  def test_check_for_symlinks(self):
    '''
    Test that check_for_symlinks raises a ValueError iff there is a symlink
    underneat the given path.
    '''
    BundleStore.check_for_symlinks(self.bundle_path)
    symlink_path = os.path.join(self.bundle_directories[-1], 'my_symlink')
    os.symlink('/some/random/thing/to/symlink/to', symlink_path)
    self.assertRaises(
      ValueError,
      lambda: BundleStore.check_for_symlinks(self.bundle_path),
    )

  def test_set_permissions(self):
    '''
    Test that set_permissions sets permissions for all files in a directory.
    '''
    # This test will NOT work if the r and w bits for the user are not on!
    # If r is 0, stat will fail. If w is 0, tearDown will fail post the test.
    permissions = 0o723
    BundleStore.set_permissions(self.bundle_path, permissions)
    for path in self.bundle_directories + self.bundle_files:
      self.assertEqual(stat.S_IMODE(os.lstat(path).st_mode), permissions)

  def test_hash_file_contests(self):
    '''
    Test that hash_file_contents reads a file and hashes its contents.
    '''
    # TODO(skishore): Try this test with a much larger file.
    expected_hash = hashlib.sha1(self.contents).hexdigest()
    for path in self.bundle_files:
      file_hash = BundleStore.hash_file_contents(path)
      self.assertEqual(file_hash, expected_hash)
