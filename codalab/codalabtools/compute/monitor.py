import os

from bottle import request, route, run, template

directory = os.path.dirname(os.path.realpath(__file__))
password = open(os.path.join(directory, 'password.txt'), 'r').read().strip()


@route('/')
def index():
    if 'pass' not in request.query:
        return False
    if request.query['pass'] != password:
        return False
    return '<pre>%s</pre>' % open(os.path.join(directory, 'worker.log')).read()


run(host='0.0.0.0', port=8000)
