from rtkit.resource import RTResource
from rtkit.authenticators import KerberosAuthenticator
from rtkit.errors import RTResourceError
from rtkit import set_logging
import logging
import sys

def test(url):
    resource = RTResource(url, None, None, KerberosAuthenticator)
    try:
        response = resource.get(path='ticket/1')
        for r in response.parsed:
            for t in r:
                logger.info(t)
    except RTResourceError as e:
        logger.error(e.response.status_int)
        logger.error(e.response.status)
        logger.error(e.response.parsed)


if __name__ == "__main__":
    set_logging('debug')
    logger = logging.getLogger('rtkit')
    try:
        url = sys.argv[1]
    except: raise Exception("Run %s <url>" % sys.argv[0])
    test(url)
