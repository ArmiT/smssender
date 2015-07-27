__author__ = 'ArmiT'

from logging.handlers import RotatingFileHandler
import logging
import os

NAME = __name__


def init(base_path, file_name):

    log = logging.getLogger(NAME)
    log.setLevel(logging.DEBUG)

    log_formatter = logging.Formatter("%(asctime)s - %(levelname)s :: %(message)s")
    log_file = os.path.join(base_path, file_name)

    handler = RotatingFileHandler(log_file, backupCount=3)
    handler.doRollover()
    handler.setFormatter(log_formatter)

    log.addHandler(handler)
