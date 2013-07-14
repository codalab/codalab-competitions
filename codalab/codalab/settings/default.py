from .base import Base
import os

class Dev(Base):
   OPTIONAL_APPS = ('debug_toolbar','django_extensions',)
   INTERNAL_IPS = ('127.0.0.1',)
   DEBUG_TOOLBAR_CONFIG = {
      'SHOW_TEMPLATE_CONTEXT': True,

      'ENABLE_STACKTRACES' : True,
      }

   HAYSTACK_CONNECTIONS = {
      'default': {
          'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
          'PATH': os.path.join(Base.PROJECT_DIR, 'whoosh_index'),
      },
   }
