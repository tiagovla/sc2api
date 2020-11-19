__version__ = '0.1.3'

import logging

from .api import RequestHandler, Sc2Api
from .const import League, QueueID, Region, TeamType
from .error import Sc2ApiAuthenticationError

try:
    from logging import NullHandler
except ImportError:

    class NullHandler(logging.Handler):
        def emit(self, record):
            pass


logging.getLogger(__name__).addHandler(NullHandler())
