import sys, getopt
from subprocess import call

if len(sys.argv) != 2:
	print '\n  Usage: python build.py <closure compiler jar>'
	print '\n  Download and extract the compiler from http://dl.google.com/closure-compiler/compiler-latest.zip'
	sys.exit(2)

files = [
	"js\\app.js",
	"js\\bundle.js",
	"js\\competition.js",
	"js\\main.js",
	"app\\js\\app.js",
	"app\\js\\services\\worksheetsapi.js",
	"app\\js\\controllers\\root.js",
	"app\\js\\controllers\\worksheets.js",
	"app\\js\\controllers\\worksheet.js",
	"app\\js\\directives\\shortcut.js",
	"app\\js\\directives\\setfocus.js",
	"app\\js\\directives\\scrollintoview.js",
	]

call(["gjslint", "--disable", "110"] + files)
call(["java", "-jar", sys.argv[1], "--js"] + files + ["--js_output_file", "codalab.min.js", "--create_source_map", "codalab.min.map", "--output_wrapper", "%output%//# sourceMappingURL=/static/codalab.min.map"])
