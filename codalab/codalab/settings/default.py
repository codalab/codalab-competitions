from .base import DevBase
import os

__all__ = ['Dev','Prod','Test','Staging']

class NotImp(object):
   def __init__(self):
      raise NotImplementedError

class Dev(DevBase):
   pass

class Prod(NotImp):
   pass

class Test(NotImp):
   pass

class Staging(NotImp):
   pass
