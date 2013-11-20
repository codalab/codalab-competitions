class BundleClient(object):
  '''
  Abstract base class that describes the BundleClient interface.

  There are three categories of BundleClient commands:
    basic operations: creating, browsing, and downloading bundles
    sharing operations: permissions and group administration
    remote operations: commands that link a local CodaLab instance to a remote

  There will be several implementations of this class. Each derived
  implementation supports more commands.
    RpcBundleClient:
      Supports the basic and sharing operations, but shells out to a remote
      CodaLab instance to actually perform them.
    LocalBundleClient:
      Supports all operations. Basic operations are performed locally.
      The sharing and remote are shelled out to a remote instance.
    RemoteBundleClient:
      Supports all operations. Sharing operations happen locally.

  Class heirarchy (A -> B means B subclasses A):
    BundleClient -> RpcBundleClient -> LocalBundleClient -> RemoteBundleClient
  '''

  # Commands for creating bundles: upload, update, make, and run.

  def upload(self, path, metadata):
    '''
    Create a new bundle with a copy of the directory at the given path in the
    local filesystem. Return its id. If the path leads to a file, the new bundle
    will only contain only that file.
    '''
    # TODO(skishore): This function should handle symlinks in the directory
    # being uploaded, either by realizing them or erroring out if they exist.
    raise NotImplementedError

  def update(self, bundle_id, metadata):
    '''
    Update a bundle's metadata with the given data. Overwrite old metadata.
    '''
    raise NotImplementedError

  def make(self, targets):
    '''
    Create a new bundle with dependencies on the given targets. Return its id.
    targets should be a dict mapping target keys to (bundle_id, path) pairs.
    Each of the targets will by symlinked into the new bundle at its key.
    '''
    # TODO(skishore): How will metadata be inferred for this bundle type?
    # TODO(skishore): Figure out if this method will call run or vice-versa.
    raise NotImplementedError

  def run(self, program_bundle_id, targets, command):
    '''
    Run the given program bundle, create bundle of output, and return its id.
    The program and input bundles are symlinked in as dependencies at runtime,
    but are NOT included in the final result.
    '''
    # TODO(skishore): Figure out how the command should be parametrized.
    raise NotImplementedError

  # Commands for browsing bundles: info, ls, cat, grep, and search.

  def info(self, bundle_id):
    '''
    Return a dict containing detailed information about a given bundle:
      bundle_type: one of (program, dataset, macro, make, run)
      location: its physical location on the filesystem
      metadata: its metadata object
      status: a description of the bundle's status
    '''
    raise NotImplementedError

  def ls(self, target):
    '''
    Return a directory listing of the target, which is a (bundle_id, path) pair.
    This listing should include the same information as ls -la.
    '''
    # TODO(skishore): Need to decide on an output format for this method.
    raise NotImplementedError

  def cat(self, target):
    '''
    Print the contents of the target file at to stdout.
    Raise a ValueError if the target is not a file.
    '''
    raise NotImplementedError

  def grep(self, target, pattern):
    '''
    Grep the contents of the target bundle, directory, or file for the pattern.
    '''
    raise NotImplementedError

  def search(self, query):
    '''
    Run a search on bundle metadata and return the ids of all bundles that
    are returned by the query.
    '''
    raise NotImplementedError

  # Various utility commands for pulling bundles back out of the system.

  def download(self, bundle_id, path):
    '''
    Download the contents of the given bundle to the given local path.
    '''
    # TODO(skishore): What are we going to do about dependencies here?
    # We should probably realize them. This isn't too bad, because derived
    # bundles will not include their dependencies in their final value.
    raise NotImplementedError

  def wait(self, bundle_id):
    '''
    Block on the execution of the given bundle. Return SUCCESS or FAILED
    based on whether it was computed successfully.
    '''
    raise NotImplementedError
