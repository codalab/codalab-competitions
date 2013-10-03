'''
Run Django on Twisted

foreground: twistd -n --reactor=epoll rundjangoserver
background (demonized): twistd --reactor=epoll rundjangoserver

Created on Jan 22, 2012

@author: arif
'''
from twisted_wsgi import servicemaker

serviceMaker = servicemaker.ServiceMaker()
