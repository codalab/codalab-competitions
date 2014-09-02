import sys, getopt
from subprocess import call

if len(sys.argv) != 2:
	print '\n  Usage: python build.py <closure compiler jar>'
	print '\n  Download and extract the compiler from http:/dl.google.com/closure-compiler/compiler-latest.zip'
	sys.exit(2)

files = [
	"js/app.js",
	"js/bundle.js",
	"js/competition.js",
	"js/main.js",
	# "app/js/app.js",  # moved to worksheet/index.html
	# "app/js/services/worksheetsapi.js",
	# "app/js/controllers/root.js",
	# "app/js/controllers/worksheets.js",
	# "app/js/controllers/worksheet.js",
	# "app/js/directives/shortcut.js",
	# "app/js/directives/setfocus.js",
	# "app/js/directives/scrollintoview.js",
	]

# Run JSLint
call(["gjslint", "--disable", "110", "414", "424", ] + files)

# Minify js files
call(["java", "-jar", sys.argv[1], "--js"] + files + ["--js_output_file", "codalab.min.js", "--create_source_map", "codalab.min.map", "--output_wrapper", "%output%//# sourceMappingURL=/static/codalab.min.map"])

# To allow debugging in browsers that don't support source maps, create a single JS file
with open('codalab.js', 'w') as outfile:
    for file in files:
        with open(file) as infile:
            for line in infile:
                outfile.write(line)
