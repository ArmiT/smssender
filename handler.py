# -*- coding: utf-8 -*-
__author__ = 'ArmiT'

from modem import Modem
import logging
import logger
import re
from AppException import AppException


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
        """
        Checks phone format
        :param phone: string
        :return: bool
        """
        pattern = re.compile("^((\+?7|8)(?!95[4-79]|99[08]|907|94[^0]|336|986)([348]\d|9[0-6789]|7[0247])\d{8}|\+?(99[^4568]\d{7,11}|994\d{9}|9955\d{8}|996[57]\d{8}|9989\d{8}|380[34569]\d{8}|375[234]\d{8}|372\d{7,8}|37[0-4]\d{8}))$")
        return pattern.match(phone)

    @staticmethod
    def check_text(text):
        """
        Checks sms text
        Errors range: 2x
        :param text: string
        :return:
        """
        if len(text) <= 0:
            raise AppException("The text should not be an empty string", 21)

        if Validator.is_ascii(text):
            if len(text) > 160:
                raise AppException("The text should not be longer than 160 characters to ascii", 22)
        else:
            if len(text) > 70:
                raise AppException("The text should not be longer than 70 characters for not ascii", 23)


class SmsHandler:

    def __init__(self, serial_port, baudrate):
        self.connection = Modem(serial_port, baudrate)

    def send_sms(self, params={}):
        """
        Sends the sms in the PDU mode
        Errors range: 3x
        :param params: json {phone:"", text: ""}
        :return:
        """
        if not params.get('phone'):
            raise AppException("phone number is required", 30)

        if not Validator.check_phone(params.get('phone')):
            raise AppException("phone number has invalid format [%s]" % params.get('phone'), 31)

        if not params.get('text'):
            raise AppException("payload is required", 32)

        Validator.check_text(params.get('text'))

        result = self.connection.send_sms_pdu(str(params.get('phone')), params.get('text'))

        if not result:
            raise AppException("internal modem error. The message not sended", 33)

        log = logging.getLogger(logger.NAME)
        log.info("Sms successfully send")

        return "success"

    def get_balance(self, params={}):
        """
        Request balance and parses response
        Errors range: 4x
        :param params: void
        :return:
        """

        result = self.connection.check_balance()
        if not result:
            raise AppException("internal modem error. Balance does not received", 40)

        log = logging.getLogger(logger.NAME)
        log.info("Balance successfully received [%s]" % result)

        return result

    def nothing(self, params={}):
        """
        dummy
        Errors range: 1x
        :param params: void
        :return:
        """
        raise AppException("command is required", 10)
