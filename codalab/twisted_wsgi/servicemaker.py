'''
Run Django 1.4 using Twisted WSGI container

foreground: twistd -n --reactor=epoll rundjserver
background (demonized): twistd --reactor=epoll rundjserver

Created on Jan 22, 2012

@author: arif
'''

import os

# Replace this line with your settings module
#os.environ['DJANGO_SETTINGS_MODULE'] = 'ExampleDjangoProject.settings'

from django.conf import settings
from configurations.wsgi import get_wsgi_application

from zope.interface import implements

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.application import internet, service
from twisted.web import server, resource, wsgi, static
from twisted.python import threadpool
from twisted.internet import reactor, ssl

ADDR = ''
PORT = ''
SSL_PORT = ''

DEBUG = getattr(settings, 'DEBUG', True)
if DEBUG:
    DEFAULT_ADDR = getattr(settings, 'TWISTED_DEBUG_LISTEN_ADDR', '127.0.0.1')
    DEFAULT_PORT = getattr(settings, 'TWISTED_DEBUG_HTTP_PORT', '8000')
    DEFAULT_SSL_PORT = getattr(settings, 'TWISTED_DEBUG_HTTPS_PORT', '8001')
else:
    DEFAULT_ADDR = getattr(settings, 'TWISTED_LISTEN_ADDR', '')
    DEFAULT_PORT = getattr(settings, 'TWISTED_HTTP_PORT', '80')
    DEFAULT_SSL_PORT = getattr(settings, 'TWISTED_HTTPS_PORT', '443')

ENABLE_SSL = getattr(settings, 'TWISTED_ENABLE_SSL', False)
SSL_KEY = getattr(settings, 'TWISTED_SSL_KEY', './cert/key.pem')
SSL_CERT = getattr(settings, 'TWISTED_SSL_CERT', './cert/cert.pem')

TPSIZE_MIN = getattr(settings, 'TWISTED_THREADPOOL_MIN_SIZE', 10)
TPSIZE_MAX = getattr(settings, 'TWISTED_THREADPOOL_MAX_SIZE', 50)

if getattr(settings, 'TWISTED_SERVE_STATIC', True):
    SERVE_STATIC = 'yes'
else:
    SERVE_STATIC = 'no'

if getattr(settings, 'TWISTED_REDIRECT_TO_HTTPS', False):
    REDIRECT_TO_HTTPS = 'yes'
else:
    REDIRECT_TO_HTTPS = 'no'

class Options(usage.Options):
    optParameters = [
        ["port", "p", DEFAULT_PORT, "The port number to listen on."],
        ["sslport", "p", DEFAULT_SSL_PORT, "The port number for SSL Connection."],
        ["address", "a", DEFAULT_ADDR, "The address to listen on."],
        ["servestatic", "s", SERVE_STATIC, "Serve Static content directly from Twisted."],
        ["tohttps", "s", REDIRECT_TO_HTTPS, "Redirect all http request to https."]]

class Root(resource.Resource):
    def __init__(self, wsgi_resource):
        resource.Resource.__init__(self)
        self.wsgi_resource = wsgi_resource

    def getChild(self, path, request):
        path0 = request.prepath.pop(0)
        request.postpath.insert(0, path0)
        return self.wsgi_resource


class ThreadPoolService(service.Service):
    def __init__(self, pool):
        self.pool = pool

    def startService(self):
        service.Service.startService(self)
        self.pool.start()

    def stopService(self):
        service.Service.stopService(self)
        self.pool.stop()


def wsgi_redirector_app(environ, start_response):
    '''
    Redirect all request to https
    '''
    global SSL_PORT
    
    server = environ['SERVER_NAME']
    path = environ['PATH_INFO']
    
    if SSL_PORT == '443':
        redirect_target = 'https://%s%s' % (server, path)
    else:
        redirect_target = 'https://%s:%s%s' % (server, SSL_PORT, path)
    
    start_response('302 Found', [('Location', redirect_target)])
    return [redirect_target]


class ServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "rundjserver"
    description = "Django Application Server"
    options = Options

    def makeService(self, options):
        
        # save address and port settings
        set_http_port(options['port'])
        set_https_port(options['sslport'])
        set_address(options['address'])
        
        # make a new MultiService to hold the thread/web services
        multi = service.MultiService()
        
        # make a new ThreadPoolService and add it to the multi service
        tps = ThreadPoolService(threadpool.ThreadPool())
        tps.setServiceParent(multi)
        
        # create the WSGI resource using the thread pool and Django handler
        resource = wsgi.WSGIResource(reactor, tps.pool, get_wsgi_application())
        # create a custom 'root' resource, that we can add other things to
        root = Root(resource)
        
        # serve the static media
        if (DEBUG is False) and (options['servestatic'] == 'yes'):
            static_resource = static.File(settings.STATIC_ROOT)
            media_resource = static.File(settings.MEDIA_ROOT)
            root.putChild(settings.STATIC_URL.strip('/'), static_resource)
            root.putChild(settings.MEDIA_URL.strip('/'), media_resource)
        
        site = server.Site(root)
        
        # create redirector
        redirector_resource = wsgi.WSGIResource(reactor, tps.pool, wsgi_redirector_app)
        redirector_root = Root(redirector_resource)
        redirector_site = server.Site(redirector_root)
        
        # start the http server
        if options['tohttps'] == 'yes':
            # redirect all http request to https
            ws = internet.TCPServer(int(options['port']), redirector_site, interface=options['address'])
        else:
            ws = internet.TCPServer(int(options['port']), site, interface=options['address'])
        ws.setServiceParent(multi)
        
        # start the https server
        if ENABLE_SSL:
            sslcontext = ssl.DefaultOpenSSLContextFactory(SSL_KEY, SSL_CERT)
            ws_ssl = internet.SSLServer(int(options['sslport']), site, sslcontext, interface=options['address'])
            ws_ssl.setServiceParent(multi)
        
        return multi


def set_http_port(port):
    global PORT
    PORT = port

def set_https_port(port):
    global SSL_PORT
    SSL_PORT = port

def set_address(address):
    global ADDR
    ADDR = address
