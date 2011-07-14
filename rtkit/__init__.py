# -*- coding: utf-8 -

version_info = (0, 0, 1)
__version__ =  ".".join(map(str, version_info))

try:
    from resource import RTResource
    from error import *
except ImportError:
    import traceback
    traceback.print_exc()

import restkit
if restkit.__version__.split('.') < (3,3,1):
    import warnings
    warnings.warn("Attachment features will raise AttributeError", FutureWarning)

import logging

LOG_LEVELS = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG
}

def set_logging(level, handler=None):
    if not handler:
        handler = logging.StreamHandler()
    format = r'[%(levelname)s] %(message)s'
    handler.setFormatter(logging.Formatter(format))
    loggers = [
        logging.getLogger('rtkit'),
        logging.getLogger('restkit'),
    ]
    for logger in loggers:
        logger.setLevel(LOG_LEVELS.get(level, logging.INFO))
        logger.addHandler(handler)