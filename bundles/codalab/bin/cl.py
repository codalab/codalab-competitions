#!/usr/bin/env python
import argparse
import sys

from codalab.client.local_bundle_client import LocalBundleClient


class BundleCLI(object):
  '''
  Each CodaLab bundle command corresponds to a function on this class.
  This function should take a list of arguments and perform the action.
  '''
  DESCRIPTIONS = {
    'help': 'Show a usage message for cl.py or for a particular command.',
    'upload': 'Create a bundle from an existing directory.',
    'info': 'Show detailed information about an existing bundle.',
    'ls': 'List the contents of a bundle.',
  }
  COMMON_COMMANDS = ('upload', 'info', 'ls')

  def __init__(self, client):
    self.client = client

  def exit(self, message, error_code=1):
    if not error_code:
      raise ValueError('exit called with error_code=0')
    print >> sys.stderr, message
    sys.exit(error_code)

  def do_command(self, argv):
    if len(sys.argv) < 2:
      self.do_help_command(['help'])
    else:
      (command, remaining_args) = (argv[1], argv[1:])
      command_fn = getattr(self, 'do_%s_command' % (command,), None)
      if not command_fn:
        self.exit("'%s' is not a codalab command. %s" % (command, self.USAGE))
      parser = argparse.ArgumentParser(description=self.DESCRIPTIONS[command])
      command_fn(remaining_args, parser)

  def do_help_command(self, argv, parser):
    print 'Usage: ./cl.py <command> <arguments>'
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
    pass


if __name__ == '__main__':
  cli = BundleCLI(LocalBundleClient())
  cli.do_command(sys.argv)
