import os


class PathUtil(object):
  @staticmethod
  def expand_target(bundle_store, model, target):
    '''
    Return the on-disk location of the target (uuid, path) pair.
    '''
    (uuid, path) = target
    bundle = model.get_bundle(uuid)
    bundle_root = bundle_store.get_location(bundle.data_hash)
    final_path = os.path.join(bundle_root, path)
    if not os.path.exists(final_path):
      raise ValueError(
        'Invalid target: %s (%s does not exist!)' %
        (target, final_path)
      )
    return final_path

  @staticmethod
  def ls(path):
    if not os.path.isabs(path):
      raise ValueError('Tried to ls relative path: %s' % (path,))
    (directories, files) = ([], []) 
    for file_name in os.listdir(path):
      if os.path.isfile(os.path.join(path, file_name)):
        files.append(file_name)
      else:
        directories.append(file_name)
    return (directories, files)
