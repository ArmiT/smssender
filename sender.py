__author__ = 'ArmiT'

# https://docs.python.org/2/library/threading.html#semaphore-objects
# http://stackoverflow.com/questions/2031394/python-logging-over-multiple-files
# https://docs.python.org/2/howto/logging-cookbook.html
# https://docs.python.org/2/howto/logging.html

from http import Observer
from handler import SmsHandler
import logging

HOST = "127.0.0.1"
PORT = 8080
ERROR_LOG = "app.log"

"""
Usage:
http://<service IP>:<port>/?c=sendsms&params={"phone":"+79233054392", "text": "this is sms text..."}
"""
if __name__ == "__main__":

    observer = Observer()
    observer.set_handler(SmsHandler)
    observer.listen(HOST, PORT)

