# django-configurations is the right way to go
# but still need local overrrides of some sort
# local.py will override the whatever is in default
# and will need to be created by build/deploy process

import logging
logger = logging.getLogger(__name__)

from .default import *
try:
    from .local import *
except ImportError as e:
    logger.info("No local configuration found")
