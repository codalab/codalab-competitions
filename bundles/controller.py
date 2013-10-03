#!/usr/bin/env python

import os, sys, yaml, time, re

# This file provides the interface for working with Bundles and Worksheets.
# Currently, everything is just run locally.  Currently this is just a
# prototype which needs to be refactored.
#
# All Bundles and Worksheets have a unique immutable name of the form:
#   <user>/<basename>

# The base directory where all the Bundles and Worksheets are stored.
# Names are paths relative to this base.
bundlesPath = "."

# For visualization.
htmlOutPath = 'html_out'

# These keys are produced in a run
producedRunKeys = ['output', 'status', 'stdout', 'stderr']

# If we generate a Bundle with some specification, then we cache it, so we
# don't generate duplicates.
bundleCache = {}  # Map from specification to Bundle

# A Bundle is an immutable directory with files and subdirectories.
#
# A Bundle has a metadata file which contains the following keys:
#  - description
#  - key-value pairs that reference other Bundles
#
# Programs, Datasets, and Runs are Bundles with different mandatory keys:
#  - Program: command
#  - Dataset: (none)
#  - Run: program/macro, input, produced keys (output, status, stdout, stderr)
#
# In a Program's command, the following variables will be substituted:
#  - $program: path to the program.
#  - $input: path to the input (read everything from this directory).
#  - $ouput: path to the output (write everything to this directory).
class Bundle:
  def __init__(self, name, metadata=None):
    self.name = name
    self.path = os.path.join(bundlesPath, name.replace('/', os.path.sep))
    if not os.path.exists(self.path):
      raise Exception('Bundle path doesn\'t exist: ' + self.path)

    # Either read or write metadata
    self.metadataPath = os.path.join(self.path, 'metadata')
    if metadata:
      self.metadata = metadata
      writeYaml(metadata, self.metadataPath)
    else:
      if os.path.exists(self.metadataPath):
        self.metadata = readYaml(self.metadataPath)
      else:
        self.metadata = {}

  def __str__(self): return self.name

############################################################
# Main functions:
#   - getBundle: Return an existing Bundle with this name.
#   - createBundle: Creates a new Bundle by combining parts of other
#     Bundles.
#   - runProgram: Creates a new Bundle by running a program.
#   - runMacro: Creates a new Bundle by running a macro.

# Return the existing Bundle with this name.
def getBundle(name): return Bundle(name)

# Helper function: find an unused Bundle directory (this is inefficient!).
# Just return the unused smallest integer.
def reserveNewBundleName():
  i = 0
  generatedName = 'generated'
  if not os.path.exists(generatedName): os.mkdir(generatedName)
  while True:
    name = os.path.join(generatedName, str(i))
    if not os.path.exists(os.path.join(bundlesPath, name)): break
    i += 1
  os.mkdir(name)
  #print "Created " + name
  return name

# Given |metadata| which specifies the construction of the Bundle, return a
# specification string which essentially serializes this metadata.
# The specification is used to check for duplicates.
def getSpec(metadata):
  # Don't include keys that could change over time (producedRunKeys - stdout)
  filteredMetadata = {}
  for key, value in metadata.items():
    if key not in producedRunKeys:
      filteredMetadata[key] = value
  # TODO: make invariant to order of map
  return yaml.dump(filteredMetadata)

# Load all the existing Bundles into cache so that we can check for duplicates.
def loadBundlesIntoCache():
  print 'Loading all bundles into cache...'
  generatedPath = os.path.join(bundlesPath, 'generated')
  if os.path.exists(generatedPath):
    for i in os.listdir(generatedPath):
      name = 'generated/'+i
      bundle = Bundle(name)
      spec = getSpec(bundle.metadata)
      bundleCache[spec] = bundle

# Given the metadata, create the corresponding Bundle,
# writing it to disk.
def createBundle(metadata):
  spec = getSpec(metadata)
  if spec in bundleCache: return bundleCache[spec]
  bundle = Bundle(reserveNewBundleName(), metadata)
  bundleCache[spec] = bundle

  # Set up dependencies
  installDependencies(bundle)

  return bundle

def getHtmlOutFile(stack, name): return '-'.join(stack + [name.replace('/', '-')]) + '.html'
def getHtmlOutPath(stack, name): return os.path.join(htmlOutPath, getHtmlOutFile(stack, name))

def rowStr(key, value):
  return '<tr valign="top"><td><b>' + key + '</b></td><td>' + value + '</td>'

# Return whether |value| is a reference (by name) to a Bundle.
def isReference(key, value):
  if key == 'macro': return False
  if key == 'command': return False
  if not isinstance(value, basestring): return False
  return True

# If a Bundle depends on another one, its metadata will contain:
#   <key>: <reference to Bundle>/<subdirectory>
# Take this information and make it an actual directory (in the future,
# installation will not be in the same directory but on the worker machine).
def installDependencies(bundle):
  for key, value in bundle.metadata.items():
    if not isReference(key, value): continue;
    installDir(os.path.join(bundlesPath, value),
               os.path.join(bundle.path, key))

# Helper functions to query about a Run.
def getExitCode(bundle):
  status = readYaml(os.path.join(bundle.path, 'status'))
  return status.get('exitCode')
def wasRunSuccessful(bundle):
  return getExitCode(bundle) == 0
def wasRunStarted(bundle):  # Either started, or finishing
  return os.path.exists(os.path.join(bundle.path, 'output'))

# Execute this Run Bundle.  Return whether it was successful.
# Currently, we are executing the Run in the same directory.
# In the future, this will be impossible since it will be on another machine.
def runProgram(bundle):
  # If already run, don't do it again.
  if wasRunStarted(bundle):
    ok = wasRunSuccessful(bundle)
    if not ok:
      print "PROGRAM FAILED:", bundle, bundle.metadata
    return ok

  # Define paths
  runPath = bundle.path 
  programPath = os.path.join(runPath, 'program')
  inputPath = os.path.join(runPath, 'input')
  outputPath = os.path.join(runPath, 'output')
  os.mkdir(outputPath)

  program = getBundle(bundle.metadata['program'])
  input = getBundle(bundle.metadata['input'])

  # Read the command from the Program's metadata.
  command = program.metadata.get('command')
  if not command:
    raise Exception("Program does not have a command: %s" % program)
  command = command.replace("$program", programPath)
  command = command.replace("$input", inputPath)
  command = command.replace("$output", outputPath)

  print
  print "BEGIN ====== runProgram(%s) ======" % command
  print command
  stdoutPath = os.path.join(runPath, 'stdout')
  stderrPath = os.path.join(runPath, 'stderr')

  startTime = time.time()
  exitCode = os.system(command+' >'+stdoutPath+' 2>'+stderrPath) # Run it!
  endTime = time.time()
  elapsedTime = endTime - startTime

  status = {}
  status['exitCode'] = exitCode
  status['elapsedTime'] = elapsedTime
  status['maxMemoryUsed'] = 100 # placeholder
  writeYaml(status, os.path.join(runPath, 'status'))
  print open(stdoutPath).read()
  print open(stderrPath).read()

  print "END ====== runProgram(%s) ====== [exitCode %s, %.4f seconds]" % (command, exitCode, elapsedTime)
  return exitCode == 0

# A Macro is just a worksheet where some variables are unspecified.
def runMacro(stack, bundle):
  print
  print 'BEGIN ===== runMacro(%s) ===== ' % bundle.metadata

  # Instantiate the worksheet
  worksheet = Worksheet(bundle.metadata['macro'])
  overrideVarToName = {}
  inputBundle = Bundle(bundle.metadata['input'])
  for key in os.listdir(inputBundle.path):
    overrideVarToName[key] = inputBundle.name + '/' + key

  # Execute the worksheet
  ok = True
  if not worksheet.execute(stack, overrideVarToName):
    ok = False
  else:
    # Copy output of the last block of the worksheet to this bundle.
    for key in producedRunKeys:
      bundle.metadata[key] = worksheet.returnBundle.name + '/' + key
    writeYaml(bundle.metadata, bundle.metadataPath)
    installDependencies(bundle)

  print 'END ===== runMacro(%s) ===== ' % bundle.metadata
  return ok

############################################################
# Functions for loading and running Worksheets.

# A basic building block of a worksheet
class Block: pass

class TextBlock(Block):
  def __init__(self, contents):
    self.contents = contents

class BundleBlock(Block):
  def __init__(self, contents):
    self.contents = contents
    self.var = contents.get('var')
    del self.contents['var']
    # For getBundle
    self.name = contents.get('name')
    # For runProgram/runMacro
    self.program = contents.get('program')
    self.macro = contents.get('macro')

class Worksheet:
  def __init__(self, name):
    self.name = name
    self.path = os.path.join(bundlesPath, name+'.yaml')
    contents = yaml.load(open(self.path))
    self.description = contents['description']
    if not self.description: raise BadFormatException('Missing description')

    self.blocks = []
    self.varToBlock = {}  # Mapping from variable to blocks
    blocks = contents.get('blocks')
    if not blocks: raise BadFormatException('Missing blocks')
    for blockContents in blocks:
      if isinstance(blockContents, basestring):
        block = TextBlock(blockContents)
      else:
        block = BundleBlock(blockContents)
        if block.var:
          if block.var in self.varToBlock:
            raise BadFormatException('Variable defined twice: ' + block.var)
          self.varToBlock[block.var] = block
      self.blocks.append(block)

  # If |value| contains ^var, then replace it with the real name.
  def resolveReferences(self, key, overrideVarToName, value):
    if not isReference(key, value): return value
    m = re.match('\\^([\w_]+)(.*)', value)
    if m:
      refVar = m.group(1)
      name = overrideVarToName.get(refVar)
      if not name:
        refBlock = self.varToBlock.get(refVar)
        if not refBlock:
          raise BadFormatException('Undefined variable reference: ' + refVar)
        name = refBlock.bundle.name
      if name:
        value = name + m.group(2)
    return value

  # If |overrideVarToName| is specified, use that to override the variables.
  # Return whether execution was successful.
  # |stack|: call stack of worksheets that lead up to this one
  def execute(self, stack=[], overrideVarToName={}):
    print
    print "BEGIN WORKSHEET =====", stack, self.name
    ok = True
    for block in self.blocks:
      if not isinstance(block, BundleBlock): continue

      if block.name: # Load existing bundle
        block.bundle = getBundle(block.name)
      else:  # Create new bundle
        # Substitute variables (begin with ^) with blocks
        info = {}
        for key, value in block.contents.items():
          value = self.resolveReferences(key, overrideVarToName, value)
          info[key] = value

        block.bundle = createBundle(info)

        # Execute stuff
        if block.program: ok = runProgram(block.bundle)
        if block.macro: ok = runMacro(stack + [block.var], block.bundle)
        if not ok: break
      print 'execute', len(stack), block.bundle, block.contents
      self.returnBundle = block.bundle
    print "END WORKSHEET =====", stack, self.name, '['+str(ok)+']'
    self.generateHtml(stack, overrideVarToName)
    return ok

  # This is a dirt simple visualization of the Worksheet.
  # |path| is directory to put all the HTML files.
  def generateHtml(self, stack, overrideVarToName):
    if not os.path.exists(htmlOutPath): os.mkdir(htmlOutPath)
    htmlPath = getHtmlOutPath(stack, self.name)
    out = open(htmlPath, 'w')
    print >>out, '<h1>' + '-'.join(stack + [self.name]) + '</h1>'
    print >>out, '<p><i>' + self.description + '</i></p>'
    print >>out, '<hr/>'
    for block in self.blocks:
      if isinstance(block, TextBlock):
        print >>out, '<p><i><font color="brown">' + block.contents + '</font></i></p>'
      elif isinstance(block, BundleBlock):
        if block.var in overrideVarToName: # Substituted bundle
          self.printBundleHtml(stack, overrideVarToName, block.var, {}, getBundle(overrideVarToName[block.var]), out)
        else:
          self.printBundleHtml(stack, overrideVarToName, block.var, block.contents, block.bundle, out)
      else:
        raise Exception('Internal error')
    out.close()


  def printBundleHtml(self, stack, overrideVarToName, var, contents, bundle, out):
    # Return a value to represent the path (directory or file)
    def pathToValue(path):
      if os.path.isdir(path):
        value = ' '.join(os.listdir(path))
      else:
        f = open(path)
        lines = []
        numLines = 5
        for i in range(0, numLines):
          line = f.readline()
          if not line: break
          lines.append(line)
          if i == numLines-1: lines.append('...')
        value = '<br>'.join(lines)
        f.close()
      return value

    if var in overrideVarToName:
      print >>out, '<p>[<b><font color="blue">' + var + '</font></b>]<br/>'
    else:
      print >>out, '<p>[<b><font color="green">' + var + '</font></b>]<br/>'
    print >>out, '<table>'
    hitKeys = set()

    # Print name
    print >>out, rowStr('name', bundle.name)
    hitKeys.add('name')

    # Print keys in metadata
    for key, value in bundle.metadata.items():
      if key in producedRunKeys: continue
      value = str(value)
      generalValue = contents.get(key)
      if generalValue: generalValue = str(generalValue)
      if os.path.isfile(os.path.join(bundlesPath, value)):
        value = pathToValue(os.path.join(bundlesPath, value))
      if generalValue and generalValue != value:
        renderedValue = value + ' [<font color="green">' + generalValue[1:] + '</font>]'
      else:
        renderedValue = value
      if key == 'macro':
        renderedValue = '<a href="'+getHtmlOutFile(stack + [var], value)+'">' + renderedValue + '</a>'
      print >>out, rowStr(key, renderedValue)

    # Print keys in files
    for key in os.listdir(bundle.path):
      if key not in producedRunKeys: continue
      path = os.path.join(bundle.path, key)
      value = pathToValue(path)
      print >>out, rowStr(key, value)

    print >>out, '</table></p>'

############################################################
# Helper functions

def installDir(sourcePath, destPath):
  if not os.path.exists(sourcePath):
    raise Exception("Does not exist: " + sourcePath)
    return
  # Future: need to copy if transferred to another machine.
  if os.path.exists(destPath):
    return
    #raise Exception('Destination already exists: ' + destPath)
  os.symlink(os.path.abspath(sourcePath), destPath)

def readYaml(path):
  f = open(path)
  result = yaml.load(f)
  f.close()
  return result

def writeYaml(info, path):
  f = open(path, "w")
  f.write(yaml.dump(info, default_flow_style=False))
  f.close()

# Error due to bad file formats.
class BadFormatException(Exception):
  def __init__(self, message):
    self.message = message
  def __str__(self): return self.message

############################################################
# Main entry point

# In the future, should have better way of doing this.
loadBundlesIntoCache()

def generateStandard():
  w = Worksheet('pliang/csv_to_arff')
  w.execute()

  w = Worksheet('pliang/basic_ml')
  w.execute()

  w = Worksheet('pliang/standard_ml_programs')
  w.execute()

generateStandard()
