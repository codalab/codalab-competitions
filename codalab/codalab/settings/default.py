from .base import Base
import os

class Dev(Base):
   HAYSTACK_CONNECTIONS = {
      'default': {
          'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
          'PATH': os.path.join(Base.PROJECT_DIR, 'whoosh_index'),
      },
   }



