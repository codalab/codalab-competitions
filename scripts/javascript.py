import os, sys
from subprocess import call

if len(sys.argv) != 2:
	print '\n  Usage: python ' + sys.argv[0] + ' <closure compiler jar>'
	print '\n  Download and extract the compiler from http:/dl.google.com/closure-compiler/compiler-latest.zip'
	sys.exit(1)

base_path = os.path.join(os.path.dirname(sys.argv[0]), '..', 'codalab', 'apps', 'web', 'static')

def P(path):
    return os.path.join(base_path, path)

input_paths = [
	P("js/app.js"),
	P("js/Competition.js"),
	P("js/main.js"),
]

# Run JSLint
call(["gjslint", "--disable", "110", "414", "424"] + input_paths)

# Minify js
call(["java", "-jar", sys.argv[1], "--js"] + input_paths + [
    "--js_output_file", P("codalab.min.js"),
    "--create_source_map", P("codalab.min.map"),
    "--output_wrapper", "%output%//# sourceMappingURL=/static/codalab.min.map"])

# To allow debugging in browsers that don't support source maps, create a single JS file
with open(P('codalab.js'), 'w') as outfile:
    print >>outfile, '//// THIS FILE IS AUTO-GENERATED - DO NOT EDIT!'
    for path in input_paths:
        print >>outfile, '\n//// ' + path
        with open(path) as infile:
            for line in infile:
                outfile.write(line)
