import os, sys, yaml, time, re

# This file provides the interface for working with Bundles and Worksheets.
# Currently, everything is just run locally.  Currently this is just a
# prototype which needs to be refactored.

# The base directory where all the Bundles are stored.
bundlesPath = "."

# For visualization
htmlOutPath = 'html_out'

# These keys are produced in a run
producedRunKeys = ['output', 'status', 'stdout', 'stderr']

# If we generate a Bundle with some specification, then we cache it, so we
# don't generate duplicates.
bundleCache = {}  # Map from specification to Bundle

# A Bundle is an immutable directory with files and subdirectories.
# Some of these files are YAML files, which conceptually represent
# directories.
#
# A Bundle has a metadata file which contains the following keys:
#  - description
#  - any key-value pairs that reference other Bundles
#
# Programs, Datasets, and Runs are Bundles with different mandatory keys
# (files):
#  - Program: command
#  - Dataset: format
#  - Run: program/macro, input, produced keys (output, status, stdout, stderr)
#
# In a Program's command, the following variables will be substituted:
#  - $program: path to the program.
#  - $input: path to the input (read everything from this directory).
#  - $ouput: path to the output (write everything to this directory).
#  - $tmp: path to output temporary files.
class Bundle:
  def __init__(self, name):
    self.name = name
    self.path = os.path.join(bundlesPath, name.replace('/', os.path.sep))
    self.metadataPath = os.path.join(self.path, 'metadata')
    if not os.path.exists(self.path):
      raise Exception('Bundle path doesn\'t exist: ' + self.path)
    if os.path.exists(self.metadataPath):
      self.metadata = readYaml(self.metadataPath)
    else:
      self.metadata = {}
  def __str__(self): return self.name

############################################################
# Main functions:
#   - getBundle: Return an existing bundle with this name.
#   - createBundle: Creates a new bundle by combining parts of other
#     bundles.
#   - runProgram: Creates a new bundle by running a program.
#   - runMacro: Creates a new bundle by running a macro.

# Return the bundle with this name.
def getBundle(name): return Bundle(name)

# Helper function: find a fresh bundle directory (this is inefficient!)
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

def getSpec(metadata):
  filteredMetadata = {}
  for key, value in metadata.items():
    if key not in producedRunKeys:
      filteredMetadata[key] = value
  # TODO: make invariant to order of map
  return yaml.dump(filteredMetadata)

# Load all the existing Bundles into cache so that we can check for duplicates.
def loadBundlesIntoCache():
  print 'Loading all bundles into cache'
  generatedPath = os.path.join(bundlesPath, 'generated')
  if os.path.exists(generatedPath):
    for i in os.listdir(generatedPath):
      name = 'generated/'+i
      bundle = Bundle(name)
      spec = getSpec(bundle.metadata)
      bundleCache[spec] = bundle

# Given the metadata, create and the corresponding Bundle.
def createBundle(metadata):
  spec = getSpec(metadata)
  if spec in bundleCache: return bundleCache[spec]
  bundle = Bundle(reserveNewBundleName())
  bundleCache[spec] = bundle

  # Write metadata
  if len(bundle.metadata) != 0: raise Exception("Not empty")
  bundle.metadata = metadata
  writeYaml(bundle.metadata, bundle.metadataPath)

  # Set up dependencies
  installDependencies(bundle)

  return bundle

def installDependencies(bundle):
  # Set up dependencies
  for key, value in bundle.metadata.items():
    installDir(os.path.join(bundlesPath, value),
               os.path.join(bundle.path, key))

def getExitCode(bundle):
  status = readYaml(os.path.join(bundle.path, 'status'))
  return status.get('exitCode')
def wasRunSuccessful(bundle):
  return getExitCode(bundle) == 0
def wasRunStarted(bundle):  # Either started, or finishing
  return os.path.exists(os.path.join(bundle.path, 'output'))

# Execute this run Bundle.  Return whether it was successful.
def runProgram(bundle):
  if wasRunStarted(bundle):
    return wasRunSuccessful(bundle)
  # TODO: create a scratch directory.  For now, just use the same
  # directory.

  runPath = bundle.path 
  programPath = os.path.join(runPath, 'program')
  inputPath = os.path.join(runPath, 'input')
  outputPath = os.path.join(runPath, 'output')
  tmpPath = runPath

  # Read the command from the Program's metadata.
  metadataPath = os.path.join(bundle.path, 'program', 'metadata')
  command = readYaml(metadataPath).get('command')
  if not command:
    raise Exception("Metadata %s does not have a command" % metadataPath)
  command = command.replace("$program", programPath)
  command = command.replace("$input", inputPath)
  command = command.replace("$output", outputPath)
  command = command.replace("$tmp", tmpPath)

  os.mkdir(outputPath)

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
  print "END ====== runProgram(%s) ====== [%.4f seconds]" % (command, elapsedTime)
  return exitCode == 0

# A Macro is just a worksheet where some variables are unspecified.
def runMacro(bundle):
  print 'BEGIN ===== runMacro(%s) ===== ' % bundle.metadata

  # Instantiate the worksheet
  worksheet = Worksheet(bundle.metadata['macro'])
  overrideVarToName = {}
  inputBundle = Bundle(bundle.metadata['input'])
  for key in os.listdir(inputBundle.path):
    overrideVarToName[key] = inputBundle.name + '/' + key

  # Execute the worksheet
  ok = True
  if not worksheet.execute(overrideVarToName):
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
# Functions for loading and running worksheets.

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
  def resolveReferences(self, overrideVarToName, value):
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
  def execute(self, overrideVarToName={}):
    for block in self.blocks:
      if not isinstance(block, BundleBlock): continue

      if block.name: # Load existing bundle
        block.bundle = getBundle(block.name)
      else:  # Create new bundle
        # Substitute variables (begin with ^) with blocks
        info = {}
        for key, value in block.contents.items():
          value = self.resolveReferences(overrideVarToName, value)
          info[key] = value

        block.bundle = createBundle(info)

        # Execute stuff
        if block.program:
          if not runProgram(block.bundle): return False
        if block.macro:
          if not runMacro(block.bundle): return False
      print 'execute', block.bundle, block.contents
      self.returnBundle = block.bundle

    return True

  # This is a dirt simple visualization of the Worksheet.
  # |path| is directory to put all the HTML files.
  def generateHtml(self):
    def rowStr(key, value):
      return '<tr valign="top"><td><b>' + key + '</b></td><td>' + value + '</td>'

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

    if not os.path.exists(htmlOutPath): os.mkdir(htmlOutPath)
    htmlPath = os.path.join(htmlOutPath, self.name.replace('/', '-') + '.html')
    out = open(htmlPath, 'w')
    print >>out, '<h1>' + self.name + '</h1>'
    print >>out, '<p><i>' + self.description + '</i></p>'
    print >>out, '<hr/>'
    for block in self.blocks:
      if isinstance(block, TextBlock):
        print >>out, '<p><i><font color="brown">' + block.contents + '</font></i></p>'
      elif isinstance(block, BundleBlock):
        print >>out, '<p>[<b><font color="green">' + block.var + '</font></b>]<br/>'
        print >>out, '<table>'
        hitKeys = set()

        # Print name
        print >>out, rowStr('name', block.bundle.name)
        hitKeys.add('name')

        # Print keys in metadata
        for key, value in block.bundle.metadata.items():
          if key in producedRunKeys: continue
          generalValue = block.contents.get(key)
          if os.path.isfile(os.path.join(bundlesPath, value)):
            value = pathToValue(os.path.join(bundlesPath, value))
          if generalValue and generalValue != value:
            renderedValue = value + ' [<font color="green">' + generalValue[1:] + '</font>]'
          else:
            renderedValue = value
          print >>out, rowStr(key, renderedValue)

        # Print keys in files
        for key in os.listdir(block.bundle.path):
          if key not in producedRunKeys: continue
          path = os.path.join(block.bundle.path, key)
          value = pathToValue(path)
          print >>out, rowStr(key, value)

        print >>out, '</table></p>'
      else:
        raise Exception('Internal error')
    out.close()

############################################################
# Helper functions

def installDir(sourcePath, destPath):
  if not os.path.exists(sourcePath):
    return
    #raise Exception("Does not exist: " + sourcePath)
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

loadBundlesIntoCache()

w = Worksheet('pliang/csv_to_arff')
w.execute()
w.generateHtml()

w = Worksheet('pliang/basic_ml')
w.execute()
w.generateHtml()

w = Worksheet('pliang/standard_ml_programs')
w.execute()
w.generateHtml()
