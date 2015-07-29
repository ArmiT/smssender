# -*- coding: utf-8 -*-
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
import config

# default parameters
HTTP_HOST = "192.168.0.175"
HTTP_PORT = 8080
APP_LOG = "app.log"
SERIAL_PORT = "COM12"
BAUDRATE = 9600
KEY_PARAM = "access-token"

if __name__ == "__main__":

    config.CONFIG = config.init(".config")  # Don't know right way

    HTTP_HOST = config.CONFIG.get('HTTP').get('host', HTTP_HOST)
    HTTP_PORT = int(config.CONFIG.get('HTTP').get('port', HTTP_PORT))
    APP_LOG = config.CONFIG.get('LOG').get('file', APP_LOG)
    SERIAL_PORT = config.CONFIG.get('SERIAL').get('port', SERIAL_PORT)
    BAUDRATE = int(config.CONFIG.get('SERIAL').get('baudrate', BAUDRATE))

    logger.init(os.path.dirname(__file__), APP_LOG)
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

