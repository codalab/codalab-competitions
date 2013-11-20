import errno
import hashlib
import mock
import os
import unittest

from codalab.bundle_store import BundleStore


class BundleStoreTest(unittest.TestCase):
  unnormalized_test_root = 'random string that normalizes to test_root'
  test_root = '/tmp/codalab_tests'

  directories = [
    test_root,
    os.path.join(test_root, BundleStore.DATA_SUBDIRECTORY),
    os.path.join(test_root, BundleStore.TEMP_SUBDIRECTORY),
  ]
  mkdir_calls = [[(directory,), {}] for directory in directories]

  class MockBundleStore(BundleStore):
    @staticmethod
    def normalize_path(path):
      assert(path == BundleStoreTest.unnormalized_test_root)
      return BundleStoreTest.test_root

  @mock.patch('codalab.bundle_store.os')
  @mock.patch('codalab.bundle_store.shutil', new_callable=lambda: None)
  def test_init(self, mock_shutil, mock_os):
    '''
    Check that __init__ calls normalize path and then creates the directories.
    '''
    mock_os.path.join = os.path.join
    self.MockBundleStore(self.unnormalized_test_root)
    self.assertEqual(mock_os.mkdir.call_args_list, self.mkdir_calls)

  @mock.patch('codalab.bundle_store.os')
  @mock.patch('codalab.bundle_store.shutil', new_callable=lambda: None)
  def test_init_with_existing_directories(self, mock_shutil, mock_os):
    '''
    Check that __init__ still works if store directories already exist.
    '''
    mock_os.path.join = os.path.join
    failures = [0]
    def mkdir_when_directory_exists(path):
      if path == self.directories[1]:
        failures[0] += 1
        error = OSError()
        error.errno = errno.EEXIST
        raise error
    mock_os.mkdir.side_effect = mkdir_when_directory_exists
    self.MockBundleStore(self.unnormalized_test_root)
    self.assertEqual(mock_os.mkdir.call_args_list, self.mkdir_calls)
    self.assertEqual(failures[0], 1)

  @mock.patch('codalab.bundle_store.os')
  @mock.patch('codalab.bundle_store.shutil', new_callable=lambda: None)
  def test_init_with_failures(self, mock_shutil, mock_os):
    '''
    Check that __init__ fails when mkdir fails with OS errors other than EEXIST.
    '''
    mock_os.path.join = os.path.join
    def mkdir_with_other_failure(path):
      if path == self.directories[1]:
        raise OSError()
    mock_os.mkdir.reset_mock()
    mock_os.mkdir.side_effect = mkdir_with_other_failure
    self.assertRaises(
      OSError,
      lambda: self.MockBundleStore(self.unnormalized_test_root),
    )
    self.assertEqual(mock_os.mkdir.call_args_list, self.mkdir_calls[:2])

  @mock.patch('codalab.bundle_store.os', new_callable=lambda: None)
  @mock.patch('codalab.bundle_store.shutil', new_callable=lambda: None)
  def test_get_relative_path(self, mock_shutil, mock_os):
    '''
    Test that get_relative_path checks if the root is a prefix of the path,
    and if so, returns the path's suffix.
    '''
    # The path is a prefix, so get_relative_path should return the suffix.
    self.assertEqual(
      BundleStore.get_relative_path('asdf', 'asdfblah'),
      'blah',
    )
    # The path is not a prefix, so get_relative_path should raise ValueError.
    self.assertRaises(
      ValueError,
      lambda: BundleStore.get_relative_path('asdfg', 'asdfblah'),
    )

  @mock.patch('codalab.bundle_store.os', new_callable=mock.Mock)
  @mock.patch('codalab.bundle_store.shutil', new_callable=mock.Mock)
  def run_upload_trial(self, mock_shutil, mock_os, new):
    '''
    Test that upload takes the following actions, in order:
      - Copies the bundle into the temp directory
      - Sets permissions for the bundle to 755
      - Hashes the directory
      - Moves the directory into data (if new) or deletes it (if old)
    '''
    tester = self
    check_isdir_called = [False]
    temp_directory = []
    mock_os.path = mock.Mock()
    mock_os.path.join = os.path.join

    unnormalized_bundle_path = 'random thing that will normalize to bundle path'
    bundle_path = 'bundle path'
    test_root = 'test_root'
    test_data = os.path.join(test_root, 'data')
    test_temp = os.path.join(test_root, 'temp')
    test_directory_hash = 'directory-hash'
    final_directory = os.path.join(test_data, test_directory_hash)

    def os_path_exists(path):
      self.assertEqual(path, final_directory)
      return not new
    mock_os.path.exists = os_path_exists

    class MockBundleStore(BundleStore):
      def __init__(self, root):
        self.root = root
        self.data = os.path.join(root, 'data')
        self.temp = os.path.join(root, 'temp')
      @classmethod
      def normalize_path(cls, path):
        tester.assertEqual(path, unnormalized_bundle_path)
        return bundle_path
      @classmethod
      def check_isdir(cls, path, message):
        tester.assertEqual(path, bundle_path)
        check_isdir_called[0] = True
      @classmethod
      def set_permissions(cls, path, permissions):
        tester.assertTrue(path.startswith(test_temp))
        tester.assertEqual(permissions, 0o755)
        tester.assertFalse(temp_directory)
        temp_directory.append(path)
      @classmethod
      def hash_directory(cls, path):
        tester.assertTrue(path, temp_directory[0])
        return test_directory_hash
    bundle_store = MockBundleStore(test_root)
    self.assertFalse(check_isdir_called[0])
    bundle_store.upload(unnormalized_bundle_path)
    self.assertTrue(check_isdir_called[0])
    if new:
      mock_os.rename.assert_called_with(temp_directory[0], final_directory)
    else:
      mock_shutil.rmtree.assert_called_with(temp_directory[0])

  def test_new_upload(self):
    self.run_upload_trial(new=True)

  def test_old_upload(self):
    self.run_upload_trial(new=False)

  @mock.patch('codalab.bundle_store.os', new_callable=lambda: None)
  @mock.patch('codalab.bundle_store.shutil', new_callable=lambda: None)
  def test_hash_directory(self, mock_shutil, mock_os):
    '''
    Test the two-level hashing scheme, mocking out all filesystem operations.
    '''
    tester = self
    check_isdir_called = [False]

    unnormalized_bundle_path = 'random thing that will normalize to bundle path'
    bundle_path = 'bundle path'
    directories = ['asdf', 'blah', 'this', 'is', 'not', 'sorted']
    files = ['foo', 'bar']
    relative_prefix = 'relative-'
    contents_hash_prefix = 'contents-hash-'

    # Compute the result of the the two-level hashing scheme on this bundle.
    directory_hash = hashlib.sha1()
    for directory in sorted(directories):
      path_hash = hashlib.sha1(relative_prefix + directory).hexdigest()
      directory_hash.update(path_hash)
    file_hash = hashlib.sha1()
    for file_name in sorted(files):
      name_hash = hashlib.sha1(relative_prefix + file_name).hexdigest()
      file_hash.update(name_hash)
      file_hash.update(contents_hash_prefix + file_name)
    overall_hash = hashlib.sha1()
    overall_hash.update(directory_hash.hexdigest())
    overall_hash.update(file_hash.hexdigest())
    expected_hash = overall_hash.hexdigest()

    # Mock out all file system operations in BundleStore. For operations
    # that require reading files to get content hashes, take the filename and
    # prepend it with a prefix instead.
    class MockBundleStore(BundleStore):
      @classmethod
      def normalize_path(cls, path):
        tester.assertEqual(path, unnormalized_bundle_path)
        return bundle_path
      @classmethod
      def check_isdir(cls, path, message):
        tester.assertEqual(path, bundle_path)
        check_isdir_called[0] = True
      @classmethod
      def recursive_ls(cls, path):
        tester.assertEqual(path, bundle_path)
        return (directories, files)
      @classmethod
      def get_relative_path(cls, root, path):
        tester.assertEqual(root, bundle_path)
        return relative_prefix + path
      @classmethod
      def hash_file_contents(cls, path):
        tester.assertIn(path, files)
        return contents_hash_prefix + path

    actual_hash = MockBundleStore.hash_directory(unnormalized_bundle_path) 
    self.assertTrue(check_isdir_called[0])
    self.assertEqual(actual_hash, expected_hash)
