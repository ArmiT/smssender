__author__ = 'ArmiT'

# https://docs.python.org/2/library/threading.html#semaphore-objects
# http://stackoverflow.com/questions/2031394/python-logging-over-multiple-files
# https://docs.python.org/2/howto/logging-cookbook.html
# https://docs.python.org/2/howto/logging.html

from http import Observer
from handler import SmsHandler
import logging
import logger
import os


HTTP_HOST = "127.0.0.1"
HTTP_PORT = 8080
ERROR_LOG = "app.log"
SERIAL_PORT = "COM4"
BAUDRATE = 9600

"""
Usage:
http://<service IP>:<port>/?c=sendsms&params={"phone":"+79233054392", "text": "this is sms text..."}
"""


if __name__ == "__main__":

    logger.init(os.path.dirname(__file__), ERROR_LOG)
    log = logging.getLogger(logger.NAME)

    try:

        log.info("Session started")

        handler = SmsHandler(SERIAL_PORT, BAUDRATE)

        observer = Observer()
        observer.set_handler(handler)
        observer.listen(HTTP_HOST, HTTP_PORT)

    except BaseException as e:
        log.critical("Server fail with message: %s" % e.message)
        exit(1)

