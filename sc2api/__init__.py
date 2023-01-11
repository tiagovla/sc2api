__version__ = "0.1.3"

import logging

from .api import Sc2Api
from .const import League, QueueID, Region, TeamType
from .error import Sc2ApiAuthenticationError

__all__ = [
    "Sc2Api",
    "League",
    "QueueID",
    "Region",
    "TeamType",
    "Sc2ApiAuthenticationError",
]

from logging import NullHandler
logging.getLogger(__name__).addHandler(NullHandler())
