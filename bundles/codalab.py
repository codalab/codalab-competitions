#!/usr/bin/env python

"""
This is a prototype command-line utility for CodaLab.
"""

import re, os, sys, yaml, sqlite3, time, tempfile, random

# The base directory where all the Bundles are stored.
bundlesPath = os.path.join(os.path.dirname(__file__), 'bundles.fs')
bundlesDbPath = os.path.join(os.path.dirname(__file__), 'bundles.db')

"""
A Bundle is an immutable directory with files and subdirectories.

A Bundle has a metadata YAML file which contains the following keys:
 - type: either Program, Dataset, or Run
 - title: free text
 - description: free text
 - tags: space separated list of identifiers
Programs, Datasets, and Runs are Bundles with the following mandatory
 - Program: command (metadata)
 - Dataset: n/a
 - Run: program (metadata), input (metadata), status, stdout, stderr (directories)

Things stored in the database:
 - (everything in the metadata file)
 - user, creation date

In a Program's command, the following variables will be substituted:
 - $program: path to the program.
 - $input: path to the input (read everything from this directory).
 - $ouput: path to the output (write everything to this directory).
"""
class Bundle:
  def __init__(self, arg):
    if isinstance(arg, int):
      # Just comes with the Bundle id
      self.bundleId = arg
    else:
      # An entry read from the database
      self.bundleId, self.title, self.description, self.command, self.bundleHash, self.status = arg
      
    self.path = os.path.join(bundlesPath, str(self.bundleId))
    if not os.path.exists(self.path):
      raise Exception('Bundle path doesn\'t exist: ' + self.path)

  def __str__(self): return str(self.bundleId)

"""
Represents a dependency of the key of a Bundle on the key of a source Bundle.
(behaves like a symlink)
"""
class Dep:
  def __init__(self, entry):
    self.bundleId, self.key, self.sourceBundleId, self.sourceKey = entry
  def __str__(self): return '%s:%s/%s' % (self.key, self.sourceBundleId, self.sourceKey)

############################################################
# General utilities

def truncate(s, n):
  if not s: return s
  if len(s) > n:
    return s[0:n-3] + '...'
  return s

def readYaml(path):
  f = open(path)
  result = yaml.load(f)
  f.close()
  return result

def writeYaml(info, path):
  f = open(path, "w")
  f.write(yaml.dump(info, default_flow_style=False))
  f.close()

def systemOrDie(command):
  #print >>sys.stderr, command
  if os.system(command) != 0:
    print >>sys.stderr, 'FAILED: %s' % command
    sys.exit(1)

############################################################
# The main functionality

class BundleServer:
  def __init__(self):
    self.bundlesDb = sqlite3.connect(bundlesDbPath)
    if not os.path.exists(bundlesPath): os.mkdir(bundlesPath)
    cur = self.bundlesDb.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS Bundles(
      Id INTEGER PRIMARY KEY AUTOINCREMENT,
      Title TEXT,
      Description TEXT,
      Command TEXT,
      Hash TEXT,
      Status TEXT);
    """)
    cur.execute("""CREATE TABLE IF NOT EXISTS Deps(
      Id INTEGER,
      Key TEXT,
      SourceId INTEGER,
      SourceKey TEXT,
      FOREIGN KEY(Id) REFERENCES Bundles(Id),
      FOREIGN KEY(SourceId) REFERENCES Bundles(Id));
    """)

  def finish(self):
    self.bundlesDb.commit()
    self.bundlesDb.close()

  # Return a list of Bundles based on the query
  # query is either:
  # - None (return everything)
  # - Integer (return the bundle with that id)
  # - String (return latest Bundle with a matching title)
  def parseBundles(self, query):
    cur = self.bundlesDb.cursor()
    conditions = self.getBundleQueryConditions(query)
    #print conditions
    if len(conditions) > 0:
      cur.execute("SELECT * From Bundles WHERE %s" % ' AND '.join(conditions))
    else:
      cur.execute('SELECT * FROM Bundles')
    entries = cur.fetchall()
    return [Bundle(entry) for entry in entries]

  def getBundleQueryConditions(self, query):
    if query == None: return []
    if re.search(r'^\d+$', query): return ["Id = %s" % query]
    m = re.search(r'^(\d+)-(\d+)$', query)
    if m: return ["Id >= " + m.group(1), "Id <= " + m.group(2)]
    if query == 'runs': return ['Command IS NOT NULL']
    m = re.search(r'^(\w+)(=|!=|<|>|<=|>=|LIKE)(.+)$', query)
    if m:
      return ["%s %s '%s'" % (m.group(1).capitalize(), m.group(2), m.group(3))]
    # Default
    return ["Title LIKE '%%%s%%'" % query]

  # Return a single query (fail if we can't).
  def parseBundle(self, query):
    bundles = self.parseBundles(query)
    if len(bundles) == 0:
      print >>sys.stderr, 'No bundles matching "%s"' % query
      sys.exit(1) # This might be a bit harsh
    if len(bundles) > 1:
      print >>sys.stderr, '%d bundles matching "%s"' % (len(bundles), query)
    return bundles[-1]

  def stringRepn(self, bundleId, title, description, command, deps):
    # Find a string representation of this Bundle
    items = [str(bundleId)]
    if title: items.append('['+title+']')
    if command: items.append('command('+command+')')
    if deps: items.append('{' + self.depsToString(deps) + '}')
    return ' '.join(items)

  # Return a string representing the dependencies
  def depsToString(self, deps):
    return ','.join([key+':'+str(sourceBundle.bundleId)+'/'+sourceKey for key, (sourceBundle, sourceKey) in sorted(deps.items())])

  # Helper function.
  # Return the Bundle object and whether it was new or not.
  def createBundle(self, title, description, command, deps, bundleHash=None):
    if title: title = str(title)
    if description: description = str(description)
    if command: command = str(command)

    if not bundleHash:
      bundleHash = (command or '') + ';' + self.depsToString(deps)
    # If a Bundle with the same hash already exists, don't recreate the Bundle.
    memoize = True
    if memoize:
      cur = self.bundlesDb.cursor()
      cur.execute("SELECT * FROM Bundles WHERE Hash = ?", (bundleHash,))
      for entry in cur.fetchall():
        bundleId = entry[0]
        print >>sys.stderr, 'Reusing existing bundle %s' % self.stringRepn(bundleId, title, description, command, deps)
        return (Bundle(bundleId), False)

    # Write to the database
    cur = self.bundlesDb.cursor()
    cur.execute("INSERT INTO Bundles(Title, Description, Command, Hash) VALUES (?,?,?,?);", (title, description, command, bundleHash))
    bundleId = cur.lastrowid
    if deps:
      for key, (sourceBundle, sourceKey) in deps.items():
        cur.execute("INSERT INTO Deps(Id, Key, SourceId, SourceKey) VALUES (?,?,?,?)", (bundleId, key, sourceBundle.bundleId, sourceKey))
    self.bundlesDb.commit()

    # Create the directory
    os.mkdir(os.path.join(bundlesPath, str(bundleId)))
    bundle = Bundle(bundleId)

    if command: self.updateStatus(bundle, 'ready')

    # Write metadata
    metadata = {}
    if title: metadata['title'] = title
    if description: metadata['description'] = description
    if command: metadata['command'] = command
    if deps:
      metadataDeps = metadata['deps'] = {}
      for key, (sourceBundle, sourceKey) in deps.items():
        metadataDeps[key] = str(sourceBundle.bundleId) + '/' + sourceKey
    writeYaml(metadata, os.path.join(bundle.path, 'metadata'))

    print >>sys.stderr, 'Created new bundle %s' % self.stringRepn(bundleId, title, description, command, deps)
    return (bundle, True)

  def uploadBundle(self, path):
    # Compute statistics of the local directory
    sizeKb = int(os.popen('du -s %s | cut -f 1' % path).read())
    bundleHash = os.popen('find %s -type f -exec md5sum {} + | awk \'{print $1}\' | sort | md5sum | cut -f 1 -d " "' % path).read().strip()
    print >>sys.stderr, '%s: %s KB, hash is %s' % (path, sizeKb, bundleHash)

    # Read the metadata 
    metadataPath = os.path.join(path, 'metadata')
    if os.path.exists(metadataPath):
      metadata = readYaml(metadataPath)
    else:
      metadata = {}

    # Give a default title if it doesn't exist
    if 'title' not in metadata:
      metadata['title'] = os.path.basename(os.path.abspath(path))

    bundle, isNew = self.createBundle(metadata.get('title'), metadata.get('description'), metadata.get('command'), metadata.get('deps'), bundleHash)
    if isNew:
      if os.path.isfile(path):
        systemOrDie('cp %s %s' % (path, bundle.path))
      else:
        systemOrDie('cp -a %s/* %s' % (path, bundle.path))
    return bundle

  def makeBundle(self, command, deps):
    bundle, isNew = self.createBundle(None, None, command, deps)
    return bundle

  def noteBundle(self, message):
    # Put it in the title for now
    bundle, isNew = self.createBundle(message, None, None, {}, "%032x" % random.getrandbits(128))
    return bundle

  # Download the Bundle into the outPath.
  def downloadBundle(self, bundle, outPath):
    inPath = bundle.path
    if os.path.exists(outPath):
      print >>sys.stderr, 'Directory %s already exists' % outPath
    else:
      systemOrDie('cp -a %s %s' % (inPath, outPath))
      print >>sys.stderr, 'Downloaded bundle %s to %s' % (bundle, outPath)

  # Wait, printing out status for the Bundle to finish
  def waitBundle(self, bundle):
    while True:
      bundle = self.parseBundle(str(bundle.bundleId))  # TODO: do this more directly
      if bundle.status in ['done', 'failed']:
        return
      time.sleep(1)

  # Print out the contents of <bundle>/<key> to stdout.
  def catFile(self, bundle, key):
    keyPath = os.path.join(bundle.path, key)
    if os.path.isfile(keyPath):
      systemOrDie('cat %s' % keyPath)
    else:
      systemOrDie('ls -l %s' % keyPath)

  # Delete Bundles matching this query.
  def deleteBundle(self, bundle):
    # TODO: warn user about downstream dependencies
    cur = self.bundlesDb.cursor()
    cur.execute('DELETE FROM Bundles WHERE Id = ?', (bundle.bundleId,))
    systemOrDie('rm -rf %s' % bundle.path)
    print >>sys.stderr, 'Permanently deleted %s' % bundle.bundleId

  def getDeps(self, bundle):
    cur = self.bundlesDb.cursor()
    cur.execute('SELECT * FROM Deps WHERE Id = ?', (bundle.bundleId,))
    return [Dep(entry) for entry in cur.fetchall()]

  # Display Bundles matching this query.
  def showBundles(self, bundles, verbose):
    rows = []
    for bundle in bundles:
      maxLen = 1000000 if verbose else 30
      title = truncate(bundle.title, maxLen)
      command = truncate(bundle.command, maxLen)
      deps = server.getDeps(bundle)
      if deps: deps = ' '.join([str(dep) for dep in deps])
      if verbose:
        print '=========================='
        print 'id:', bundle.bundleId
        if title: print 'title:', title
        if bundle.description: print 'description:', bundle.description
        if command: print 'command:', command
        if bundle.status: print 'status:', bundle.status
        if deps: print 'deps:', deps
        for filename in ['stdout', 'stderr']:
          stdoutPath = os.path.join(bundle.path, filename)
          if os.path.exists(stdoutPath):
            stdout = open(stdoutPath).read()
            if len(stdout) > 0: print "--- " + filename + " ---\n" + stdout,
        print '--- files ---'
        os.system('ls -l %s' % bundle.path)
      else:
        rows.append([str(x) if x else '-' for x in [bundle.bundleId, title, command, bundle.status, deps]])
    if len(rows) > 0:
      numCols = len(rows[0])
      maxWidths = [max(len(row[j]) for row in rows) for j in range(numCols)]
      fmt = ' '.join(['%%-%ds' % maxWidths[j] for j in range(numCols)])
      for row in rows:
        print fmt % tuple(row)

  # Helper function for the worker:
  def installDependencies(self, bundle, outPath):
    for dep in server.getDeps(bundle):
      sourceBundle = Bundle(dep.sourceBundleId)
      keyInPath = os.path.join(sourceBundle.path, dep.sourceKey)
      keyOutPath = os.path.join(outPath, dep.key)
      if not os.path.exists(keyInPath):
        # TODO: pass this message up
        print >>sys.stderr, 'installDependencies: path does not exist: %s' % keyInPath
        return False
      systemOrDie('cp -a %s %s' % (keyInPath, keyOutPath))
      # TODO: make this work for general sourceKey
      if dep.sourceKey == '':
        if not self.installDependencies(sourceBundle, keyOutPath):
          return False
    return True

  # Helper method
  def updateStatus(self, bundle, status):
    cur = self.bundlesDb.cursor()
    cur.execute('UPDATE Bundles SET Status = ? WHERE Id = ?', (status, bundle.bundleId))
    self.bundlesDb.commit()

  def run(self, bundle):
    # Setup a scratch directory
    runPath = tempfile.mkdtemp(prefix='run-', dir='.')

    self.updateStatus(bundle, 'running')
    success = self.runInPath(bundle, runPath)
    status = 'done' if success else 'failed'
    self.updateStatus(bundle, status)

    systemOrDie('rm -rf %s' % runPath)

  def runInPath(self, bundle, runPath):
    if not self.installDependencies(bundle, runPath):
      return False

    # Update command-line with the real paths
    command = bundle.command.replace("$", runPath + '/') # for $program, $input, etc.

    print
    print "BEGIN %s ====== run(%s) ======" % (bundle.bundleId, bundle.command)
    stdoutPath = os.path.join(runPath, 'stdout')
    stderrPath = os.path.join(runPath, 'stderr')
    outputPath = os.path.join(runPath, 'output')
    os.mkdir(outputPath)

    startTime = time.time()
    exitCode = os.system(command+' >'+stdoutPath+' 2>'+stderrPath) # Run it!
    endTime = time.time()
    elapsedTime = endTime - startTime

    status = {}
    status['exitCode'] = exitCode
    status['elapsedTime'] = elapsedTime
    status['maxMemoryUsed'] = 100 # TODO
    writeYaml(status, os.path.join(runPath, 'status'))
    sys.stdout.write(open(stdoutPath).read())
    sys.stdout.write(open(stderrPath).read())

    print "END %s ====== run(%s) ====== [exitCode %s, %.4f seconds]" % (bundle.bundleId, bundle.command, exitCode, elapsedTime)

    # Copy output files back
    # TODO: copy back stderr/stdout incrementally as the process is running
    for filename in ['status', 'stderr', 'stdout', 'output']:
      systemOrDie('cp -a %s %s' % (os.path.join(runPath, filename), bundle.path))

    return exitCode == 0

  def workerLoop(self):
    print "Running worker loop..."
    while True:
      for bundle in self.parseBundles('status=ready'):
        self.run(bundle)
      time.sleep(1)

############################################################
# Main entry point

main = os.path.basename(sys.argv[0])
usage = """
Usage: %s <command> [<args>]

Convention:
  <bundle>: either the integer id or /<search keywords>

Commands that return bundles:
  upload <directory>
  make <key>:<bundle>[/<directory>]* [command:<command string (e.g., "$program/run $input $output")>]
  run <program bundle> <input bundle> <command string>
  note <text>: write a note
  wait <bundle>: wait until bundle is done

  download <bundle>
  list <bundle>
  info <bundle>
  delete <bundle>
  cat <bundle>[/<directory>]

  worker: runs the worker loop

Quick example (in bash):
  weka=$(%s upload pliang/weka)
  data=$(%s upload pliang/uci_arff/vote)
  %s run $weka $data '$program/split $input $output 4'
""" % (main, main, main, main)

if len(sys.argv) == 1:
  print usage
  sys.exit(1)
command = sys.argv[1]
args = sys.argv[2:]
server = BundleServer()

# TODO: maintain consistency between the metadata file and the database
# TODO: commands to update title, description, tags of a bundle
# TODO: print out things that use a particular bundle
# TODO: display date created
# TODO: display size of bundles
# TODO: implement tagging system
# TODO: implement versioning system (backpointers)
# TODO: ascii tree w/ immediate children & parents for each bundle

if command == 'up' or command == 'upload':
  for arg in args:
    bundle = server.uploadBundle(arg)
    print bundle.bundleId
elif command == 'make' or command == 'run':
  if command == 'run':  # run is a special case of make
    if len(args) == 2: args.append('-run') # Default way to run
    if len(args) < 3:
      print >>sys.stderr, 'Missing arguments, usage is: <program> <input> [<command>]'
      sys.exit(1)
    if args[2].startswith('-'): # Just provide the name of the program to invoke
      args[2] = '$program/' + args[2][1:] + ' $input $output'
    args = ['program:' + args[0], 'input:' + args[1], 'command:'+' '.join(args[2:])]

  command = None
  deps = {}
  for s in args:
    # Format: each s is <key>:<sourceBundle>/<sourceKey>
    if ':' not in s:
      raise Exception('Bad argument: %s' % s)
    key, value = s.split(':', 1)
    if key == 'command':
      command = value
    else:
      values = value.split('/', 1)
      sourceBundle = server.parseBundle(values[0])
      sourceKey = values[1] if len(values) > 1 else ''
      deps[key] = (sourceBundle, sourceKey)
  bundle = server.makeBundle(command, deps)
  print bundle.bundleId
elif command == 'list' or command == 'info':
  if len(args) == 0: args.append(None)
  for arg in args:
    bundles = server.parseBundles(arg)
    server.showBundles(bundles, command == 'info')
elif command == 'rm' or command == 'delete':
  for arg in args:
    for bundle in server.parseBundles(arg):
      server.deleteBundle(bundle)
elif command == 'download':
  for arg in args:
    for bundle in server.parseBundles(arg):
      server.downloadBundle(bundle, str(bundle.bundleId))
elif command == 'note':
  bundle = server.noteBundle(' '.join(args))
  print bundle.bundleId
elif command == 'wait':
  for arg in args:
    for bundle in server.parseBundles(arg):
      server.waitBundle(bundle)
      print bundle.bundleId
elif command == 'cat':
  for arg in args:
    if '/' not in arg: arg += '/'
    bundleId, key = arg.split('/', 1)
    bundle = server.parseBundle(bundleId)
    server.catFile(bundle, key)
elif command == 'worker':
  server.workerLoop()
else:
  print "Invalid command: " + command
  sys.exit(1)

server.finish()
