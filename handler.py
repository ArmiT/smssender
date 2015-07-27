__author__ = 'ArmiT'

from modem import Modem
import time
import logging
import logger
import random


class SmsHandler:

    def __init__(self, serial_port, baudrate):
        self.connection = Modem(serial_port, baudrate)
        self.log = logging.getLogger(logger.NAME)
        self.t = random.randint(1, 1000)

    def send_sms(self, params = {}):
        self.log.info("command [send_sms]: ")
        return "send sms..."

    def status(self, params = {}):
        self.log.info("command [status]: ")
        return "status..."

    def test(self, params = {}):
        self.log.info("command [test]: ")
        print self.t
        time.sleep(20)
