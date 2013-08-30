#!/usr/bin/env python

"""
This is a prototype command-line utility for CodaLab.
"""

import os, sys, yaml, sqlite3, time, tempfile

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
  def __init__(self, bundleId):
    self.bundleId = bundleId
    self.path = os.path.join(bundlesPath, str(bundleId))
    if not os.path.exists(self.path):
      raise Exception('Bundle path doesn\'t exist: ' + self.path)

  def __str__(self): return str(self.bundleId)

############################################################

def truncate(s, n=20):
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

  def parseBundle(self, s):
    # TODO: handle search by title too
    bundleId = int(s)
    cur = self.bundlesDb.cursor()
    #cur.execute("SELECT * From Bundles WHERE Id = ?", str(bundleId))
    #print cur.fetchall()
    bundle = Bundle(bundleId)
    return bundle

  def stringRepn(self, bundleId, title, description, command, deps):
    # Find a string representation of this Bundle
    items = [str(bundleId)]
    if title: items.append('['+title+']')
    if command: items.append('command('+command+')')
    if deps: items.append('{' + self.depsToString(deps) + '}')
    return ' '.join(items)

  def depsToString(self, deps):
    return ','.join([key+':'+str(sourceBundle.bundleId)+'/'+sourceKey for key, (sourceBundle, sourceKey) in sorted(deps.items())])

  # Return the Bundle object and whether it was new or not.
  def createBundle(self, title, description, command, deps, bundleHash=None):
    if not bundleHash:
      bundleHash = (command or '') + ';' + self.depsToString(deps)
    # If hash exists, don't recreate the Bundle.
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
    if command:
      cur.execute('UPDATE Bundles SET Status = ? WHERE Id = ?', ('ready', bundleId))
    self.bundlesDb.commit()

    # Create the directory
    os.mkdir(os.path.join(bundlesPath, str(bundleId)))
    bundle = Bundle(bundleId)

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

  def upload(self, path):
    sizeKb = int(os.popen('du -s %s | cut -f 1' % path).read())
    bundleHash = os.popen('find %s -type f -exec md5sum {} + | awk \'{print $1}\' | sort | md5sum | cut -f 1 -d " "' % path).read().strip()
    print >>sys.stderr, '%s: %s KB, hash is %s' % (path, sizeKb, bundleHash)

    metadataPath = os.path.join(path, 'metadata')
    if os.path.exists(metadataPath):
      metadata = readYaml(metadataPath)
    else:
      metadata = {}

    # Give a default title if it doesn't exist
    if 'title' not in metadata:
      metadata['title'] = os.path.abspath(path)

    bundle, isNew = self.createBundle(metadata.get('title'), metadata.get('description'), metadata.get('command'), metadata.get('deps'), bundleHash)
    if isNew:
      if os.path.isfile(path):
        self.system('cp %s %s' % (path, bundle.path))
      else:
        self.system('cp -a %s/* %s' % (path, bundle.path))
    return bundle

  def make(self, command, deps):
    bundle, isNew = self.createBundle(None, None, command, deps)
    return bundle

  def download(self, bundle, outPath):
    inPath = bundle.path
    if os.path.exists(outPath):
      print >>sys.stderr, 'Directory %s already exists' % outPath
    else:
      self.system('cp -a %s %s' % (inPath, outPath))
      print >>sys.stderr, 'Downloaded bundle %s to %s' % (bundle, outPath)

  def delete(self, bundle):
    # TODO: warn user about downstream dependencies
    cur = self.bundlesDb.cursor()
    cur.execute('DELETE FROM Bundles WHERE Id = ?', (bundle.bundleId,))
    self.system('rm -r %s' % bundle.path)
    print >>sys.stderr, 'Permanently deleted %s' % bundle.bundleId

  def showBundles(self, arg, verbose):
    cur = self.bundlesDb.cursor()
    # TODO: make search more general
    if arg == None:
      cur.execute('SELECT * FROM Bundles')
    else:
      bundleId = int(' '.join(args))
      cur.execute('SELECT * FROM Bundles WHERE Id = ?', (bundleId,))

    rows = []
    for entry in cur.fetchall():
      bundleId, title, description, command, bundleHash, status = entry
      bundle = Bundle(bundleId)
      if not verbose:
        title = truncate(title)
        description = truncate(description)
        command = truncate(command)
      cur2 = self.bundlesDb.cursor()
      cur2.execute('SELECT * FROM Deps WHERE Id = ?', (bundleId,))
      deps = ['%s:%s/%s' % (key, sourceId, sourceKey) for (_, key, sourceId, sourceKey) in cur2.fetchall()]
      if verbose:
        print '=========================='
        print 'id:', bundleId
        if title: print 'title:', title
        if description: print 'description:', description
        if command: print 'command:', command
        if status: print 'status:', status
        if deps: print 'deps:', ' '.join(deps)
        stdoutPath = os.path.join(bundle.path, 'stdout')
        if os.path.exists(stdoutPath):
          stdout = open(stdoutPath).read()
          if len(stdout) > 0: print "--- stdout ---\n" + stdout,
      else:
        rows.append([str(x) if x else '-' for x in [bundleId, title, description, command, status, ' '.join(deps)]])
    if len(rows) > 0:
      numCols = len(rows[0])
      maxWidths = [max(len(row[j]) for row in rows) for j in range(numCols)]
      fmt = ' '.join(['%%-%ds' % maxWidths[j] for j in range(numCols)])
      for row in rows:
        print fmt % tuple(row)

  def system(self, command):
    #print >>sys.stderr, command
    if os.system(command) != 0:
      print >>sys.stderr, 'FAILED: %s' % command
      sys.exit(1)

  def installDependencies(self, bundleId, runPath):
    cur = self.bundlesDb.cursor()
    cur.execute('SELECT * FROM Deps WHERE Id = ?', (bundleId,))
    for (_, key, sourceId, sourceKey) in cur.fetchall():
      self.system('cp -a %s %s' % (os.path.join(bundlesPath, str(sourceId), sourceKey), os.path.join(runPath, key)))
      # source could also depend on other things
      # TODO: make this work for general sourceKey
      if sourceKey == '':
        self.installDependencies(sourceId, os.path.join(runPath, key))

  def run(self, bundle):
    cur = self.bundlesDb.cursor()

    cur.execute("SELECT * From Bundles WHERE Id = ?", (bundle.bundleId,))
    entry = cur.fetchall()[0]
    bundleId, title, description, command, bundleHash, status = entry

    # Setup a scratch directory
    runPath = tempfile.mkdtemp(prefix='run-', dir='.')
    self.installDependencies(bundle.bundleId, runPath)

    # Update program
    command = command.replace("$", runPath + '/') # for $program, $input, etc.

    print
    print "BEGIN %s ====== run(%s) ======" % (bundleId, command)
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
    print open(stdoutPath).read(),
    print open(stderrPath).read(),

    print "END %s ====== run(%s) ====== [exitCode %s, %.4f seconds]" % (bundleId, command, exitCode, elapsedTime)

    # Copy output files back
    # TODO: copy back stderr/stdout incrementally as the process is running
    for filename in ['stderr', 'stdout', 'output']:
      self.system('cp -a %s %s' % (os.path.join(runPath, filename), bundle.path))

    # Update status
    status = 'done' if exitCode == 0 else 'failed'
    cur.execute('UPDATE Bundles SET Status = ? WHERE Id = ?', (status, bundle.bundleId))
    self.bundlesDb.commit()

    self.system('rm -r %s' % runPath)

    return exitCode == 0

  def workerLoop(self):
    print "Running worker loop..."
    cur = self.bundlesDb.cursor()
    while True:
      cur.execute('SELECT * FROM Bundles')
      for entry in cur.fetchall():
        bundleId, title, description, command, bundleHash, status = entry
        if (not command) or status != 'ready': continue
        self.run(self.parseBundle(bundleId))
      time.sleep(1)

############################################################

main = os.path.basename(sys.argv[0])
usage = """
Usage: %s <command> [<args>]

Convention:
  <bundle>: either the integer id or /<search keywords>

Commands:
  login
  logout
  upload <directory>
  make <key>:<bundle>[/<directory>]* [command:<command string (e.g., "$program/run $input $output")>]
  run <program> <input bundle> <script file in $program> [args]
  download <bundle>
  list <bundle>
  info <bundle>
  delete <bundle>

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

# TODO: do error checking on usage
# TODO: maintain consistency between the metadata file and the database
# TODO: update title, description of a bundle
# TODO: print out things that use a particular bundle
# TODO: display size of dataset

if command == 'upload':
  for arg in args:
    bundle = server.upload(arg)
    print bundle.bundleId
elif command == 'make' or command == 'run':
  if command == 'run':  # run is a special case of make
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
  bundle = server.make(command, deps)
  print bundle.bundleId
elif command == 'list' or command == 'info':
  if len(args) == 0:
    server.showBundles(None, command == 'info')
  else:
    for arg in args:
      server.showBundles(arg, command == 'info')
elif command == 'delete':
  for arg in args:
    bundle = server.parseBundle(arg) 
    server.delete(bundle)
elif command == 'download':
  bundle = server.parseBundle(args[0]) 
  server.download(bundle, str(bundle.bundleId))
elif command == 'worker':
  server.workerLoop()
else:
  print "Invalid command: " + command
  sys.exit(1)

server.finish()
