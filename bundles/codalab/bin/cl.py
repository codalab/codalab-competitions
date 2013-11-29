#!/usr/bin/env python
import argparse
import platform
import sys

from codalab.bundles import get_bundle_subclass
from codalab.client.local_bundle_client import LocalBundleClient


class BundleCLI(object):
  '''
  Each CodaLab bundle command corresponds to a function on this class.
  This function should take a list of arguments and perform the action.
  '''
  DESCRIPTIONS = {
    'help': 'Show a usage message for cl.py or for a particular command.',
    'upload': 'Create a bundle by uploading an existing directory.',
    'info': 'Show detailed information about an existing bundle.',
    'ls': 'List the contents of a bundle.',
  }
  COMMON_COMMANDS = ('upload', 'info', 'ls')

  def __init__(self, client, verbose):
    self.client = client
    self.verbose = verbose

  def exit(self, message, error_code=1):
    if not error_code:
      raise ValueError('exit called with error_code=0')
    print >> sys.stderr, message
    sys.exit(error_code)

  def hack_formatter(self, parser):
    '''
    Screw with the argparse default formatter to improve help formatting.
    '''
    formatter_class = parser.formatter_class
    if type(formatter_class) == type:
      def mock_formatter_class(*args, **kwargs):
        return formatter_class(max_help_position=30, *args, **kwargs)
      parser.formatter_class = mock_formatter_class

  def do_command(self, argv):
    if not argv:
      self.do_help_command(['help'])
    else:
      (command, remaining_args) = (argv[0], argv[1:])
      command_fn = getattr(self, 'do_%s_command' % (command,), None)
      if not command_fn:
        self.exit("'%s' is not a codalab command. %s" % (command, self.USAGE))
      parser = argparse.ArgumentParser(
        prog='./cl.py %s' % (command,),
        description=self.DESCRIPTIONS[command],
      )
      self.hack_formatter(parser)
      if self.verbose:
        command_fn(remaining_args, parser)
      else:
        try:
          return command_fn(remaining_args, parser)
        except Exception, e:
          self.exit('%s: %s' % (e.__class__.__name__, e))

  def do_help_command(self, argv, parser):
    if argv:
      self.do_command([argv[0], '-h'])
    print 'usage: ./cl.py <command> <arguments>'
    print '\nThe most commonly used codalab commands are:'
    max_length = max(len(command) for command in self.DESCRIPTIONS)
    indent = 2
    for command in self.COMMON_COMMANDS:
      print '%s%s%s%s' % (
        indent*' ',
        command,
        (indent + max_length - len(command))*' ',
        self.DESCRIPTIONS[command],
      )

  def do_upload_command(self, argv, parser):
    parser.add_argument('bundle_type', help='bundle type: [program|dataset]')
    parser.add_argument('path', help='path of the directory to upload')
    parser.add_argument('--name', help='name: [a-zA-Z0-9_]+)')
    parser.add_argument(
      '--desc',
      dest='description',
      help='human-readable description',
      metavar='DESC',
    )
    parser.add_argument('--tags', help='list of search tags', nargs='+')
    this_machine = platform.machine()
    default_architecture = [this_machine] if this_machine else []
    parser.add_argument(
      '--arch',
      default=default_architecture,
      dest='architecture',
      help='viable architectures (for programs)',
      metavar='ARCH',
      nargs='+',
    )
    args = parser.parse_args(argv)
    bundle_subclass = get_bundle_subclass(args.bundle_type)
    metadata = {k: getattr(args, k) for k in bundle_subclass.METADATA_TYPES}
    print metadata
    print self.client.upload(args.bundle_type, args.path, metadata)


if __name__ == '__main__':
  cli = BundleCLI(LocalBundleClient(), verbose=False)
  cli.do_command(sys.argv[1:])
