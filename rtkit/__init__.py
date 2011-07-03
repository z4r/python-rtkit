# -*- coding: utf-8 -
#
# This file is part of RTkit released under the MIT license.
# See the NOTICE for more information.

version_info = (0, 0, 1)
__version__ =  ".".join(map(str, version_info))

try:
    from resource import RTResource
    from errors import *
except ImportError:
    import traceback
    traceback.print_exc()

import logging

LOG_LEVELS = {
    "critical": logging.CRITICAL,
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG
}

def set_logging(level, handler=None):
    if not handler:
        handler = logging.StreamHandler()

    loglevel = LOG_LEVELS.get(level, logging.INFO)
    logger = logging.getLogger('rtkit')
    logger.setLevel(loglevel)
    format = r"%(asctime)s [%(process)d] [%(levelname)s] %(message)s"
    datefmt = r"%Y-%m-%d %H:%M:%S"

    handler.setFormatter(logging.Formatter(format, datefmt))
    logger.addHandler(handler)