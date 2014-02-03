import os


CODALAB_HOME = os.path.expanduser('~/.codalab')


class State(object):
  '''
  An enumeration of states that a bundle can be in.
  '''
  READY = 'ready'

  OPTIONS = set(
    READY,
  )
