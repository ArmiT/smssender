# -*- coding: utf-8 -*-
__author__ = 'ArmiT'

from modem import Modem
import logging
import logger
import re


class Validator:

    def __init__(self):
        pass

    @staticmethod
    def is_ascii(text):
        try:
            text.decode('ascii')
        except UnicodeDecodeError:
            return False
        except UnicodeEncodeError:
            return False
        else:
            return True


    @staticmethod
    def check_phone(phone):
        pattern = re.compile("^((\+?7|8)(?!95[4-79]|99[08]|907|94[^0]|336|986)([348]\d|9[0-6789]|7[0247])\d{8}|\+?(99[^4568]\d{7,11}|994\d{9}|9955\d{8}|996[57]\d{8}|9989\d{8}|380[34569]\d{8}|375[234]\d{8}|372\d{7,8}|37[0-4]\d{8}))$")
        return pattern.match(phone)

    @staticmethod
    def check_text(text):

        if len(text) <= 0:
            raise BaseException("the text should not be an empty string")

        if Validator.is_ascii(text):
            if len(text) > 160:
                raise BaseException("The text should not be longer than 160 characters to ascii")
        else:
            if len(text) > 70:
                raise BaseException("The text should not be longer than 70 characters for not ascii")


class SmsHandler:

    def __init__(self, serial_port, baudrate):
        self.connection = Modem(serial_port, baudrate)

    def send_sms(self, params={}):

        if not params.get('phone'):
            raise BaseException("phone number is required")

        if not Validator.check_phone(params.get('phone')):
            raise BaseException("phone number has invalid format [%s]" % params.get('phone'))

        if not params.get('text'):
            raise BaseException("payload is required")

        Validator.check_text(params.get('text'))

        result = self.connection.send_sms_pdu(str(params.get('phone')), params.get('text'))

        if not result:
            raise BaseException("internal modem error. The message not sended")

        log = logging.getLogger(logger.NAME)
        log.info("Sms successfully send")

        return "success"

    def nothing(self, params={}):
        raise BaseException("command is required")
