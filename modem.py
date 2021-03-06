# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

__author__ = 'ArmiT'

from serial import Serial
import time
from messaging.sms import SmsSubmit
import base64
import re

"""
Resources:
# https://pypi.python.org/pypi/pyserial - install windows over installer
# https://github.com/makerbot/pyserial/blob/develop/examples/wxTerminal.py
# https://tungweilin.wordpress.com/2015/01/04/python-serial-port-communication/
# http://www.diafaan.com/sms-tutorials/gsm-modem-tutorial/at-cmgs-text-mode/
# http://www.diafaan.com/sms-tutorials/gsm-modem-tutorial/online-sms-pdu-decoder/

# https://github.com/pmarti/python-messaging - install this lib
# https://github.com/pmarti/python-messaging/blob/master/doc/tutorial/sms.rst - tutorial for sending
# http://www.minimoesfuerzo.org/blog/python-messaging-sms-encoderdecoder-masses/ - questions and answers from author
#  (multipart sending)
# http://www.linux.org.ru/forum/linux-hardware/6403426#comment-6403454 create CUSD
"""


class Modem:
    """
    Implements communication with GSM modem (Huawei e3131) in the serial mode.
    Can:
    - Initialize connection with selected boudrate on selected port
    - Reload modem in the software
    - Send sms in the text mode
    - Send sms in the PDU mode
    - Request balance for the SIM card
    :example
    m = Modem("COM4")
    print m.send_sms_text("+79203080806", "test this is")
    print m.send_sms_pdu("+79203080806", "Ваша заявка №123 принята. См. http://d3.ru/wfv13kgt")

    dependecy:
    Serial - https://pypi.python.org/pypi/pyserial
    python-messaging - https://github.com/pmarti/python-messaging

    """

    def __init__(self, port, baudrate=9600):
        """
        Initialize the serial connection with selected baudrate over the port, which pointed
        :param port: string - Name of selected port. Required. Ex. "COM4" 4 win or "/dev/ttyS0" for *nix
        :param baudrate: integer - Selected boudrate 4 connection (default 9600)
        :return: void
        """

        self.connection = Serial(port, baudrate)
        time.sleep(2)
        self.reload()

    def reload(self):
        """
        Reload modem
        :return: void
        """

        self.connection.write("AT+CFUN=1\r")
        self.connection.readline()  # read CFUN report for clear RX buffer

    def check_response(self):
        """
        Reads response from the modem after sending sms. Parses output and defines result for sending.
        :return: boolean - Returns True if sending successfully. False if Failure or exceeded buffer size
        """

        response = ""
        max_lines_count = 1000
        i = 0
        #  wait response from modem - read 1000 lines max
        while i <= max_lines_count:

            append = self.connection.readline()
            if len(append):
                i += 1
                response += append

            if response.find("+CMGS:") != -1: return True  # todo possible - if "+CMGS:" in response:
            if response.find("+CMS ERROR:") != -1: return False

        return False

    def send_sms_text(self, phone, text):
        """
        Sends sms, that contains text to the phone in the text mode. Payload must contain only ascii range and length,
        that less or equal 160 symbols. Method does not have validation!
        :param phone: string - receiver phone number
        :param text: string - payload
        :return: boolean - Returns a True if message sent successfully, otherwise False
        """
        self.connection.write("AT+CMGF=1\r")
        time.sleep(1)
        self.connection.write("AT+CMGS=\"%s\"\x0D%s\x1A" % (phone, text))

        return self.check_response()

    def send_sms_pdu(self, phone, text):
        """
        Sends sms, that contains text, to the phone in the PDU mode. Payload can contain utf-8 range and length,
        that less or equal 70 symbols. If payload contain only ascii range, then length may be less or equal 160 symbols
        Attention! Method does not have validation!
        :param phone: string - receiver phone number
        :param text: string - payload
        :return: boolean - Returns a True if message sent successfully, otherwise False
        """

        # sms = SmsSubmit(phone, text.decode("utf-8"))
        sms = SmsSubmit(phone, text)
        pdu = sms.to_pdu()[0]
        time.sleep(2)
        self.connection.write("AT+CMGF=0\x0D")  # enter pdu mode
        self.connection.readline()
        time.sleep(2)
        self.connection.write("AT+CMGS=%s\x0D%s\x1A" % (pdu.length, pdu.pdu))

        return self.check_response()

    def check_balance(self):
        """
        Gets balance of SIM card
        Sends a USSD request to the *100# and parses the response
        :return: string
        """
        time.sleep(3)
        self.connection.write("AT+CMGF=0\x0D")
        time.sleep(2)
        self.connection.write('AT+CUSD=1,"' + self.to7bit('*100#') + '",15\x0D')
        time.sleep(1)

        response = ''
        max_lines_count = 1000
        i = 0

        #  wait response from modem - read 1000 lines max
        while i <= max_lines_count:
            append = self.connection.readline()
            if len(append):
                i += 1
                response += append
            if "ERROR" in response:
                return False

            entry = re.search('\+CUSD: 0,"([0-9A-Z]+)",', response)

            if entry:
                answer = base64.b16decode(entry.group(1)).decode('utf-16-be')
                return re.search(ur'(\-?\d+(.\d+)?)(.*)', answer).group(1)  # for megafon ussd only!

            # start_pos = response.find("+CUSD:")
            #
            # if start_pos != -1:
            #     end_pos = response.find('",', start_pos)
            #
            #     if end_pos == -1:
            #         return False
            #
            #     answer = response[start_pos: end_pos]
            #     return base64.b16decode(answer[10:]).decode('utf-16-be')

            # if "+CUSD:" in response:

        return False

    def __del__(self):
        """
        It destroys the connection and all associated resources
        :return: void
        """
        if isinstance(self.connection, Serial):
            self.connection.close()

    def to7bit(self, src):
        """
        Converts to the 7bit
        :param src:
        :return:
        """
        result, count, last = [], 0, 0
        for c in src:
            this = ord(c) << (8 - count)
            if count:
                result.append('%02X' % ((last >> 8) | (this & 0xFF)))
            count = (count + 1) % 8
            last = this

        result.append('%02x' % (last >> 8))
        return ''.join(result)

if __name__ == '__main__':
    pass
    # import base64
    # import re
    # l = '12333 +CUSD: 0,"002D003100300031002E003200300440002E0423044104420430043D043E04320438044204350020044804430442043A044300200441043E002004410432043E0438043C00200438043C0435043D0435043C0020043D04300020043304430434043A043800210020002A00350035003100230020",72 werwer'
    #
    # entry = re.search('\+CUSD: 0,"([0-9A-Z]+)",', l)
    # # print str(entry.group(1)).decode('utf-16-be')
    # print entry

    # print(base64.b16decode(entry.group(1)).decode('utf-16-be'))
    # print(base64.b16decode(l[10:l.rfind('"')]).decode('utf-16-be'))

    # print ('AT+CUSD=1,' + to7bit('*100#') + ',15')
    # answer = '-102.40р."Обещанный платёж" 300р. на 3 дня: *106*1#  (20р.)'
    # print re.search(ur'(\-?\d+(.\d+)?)(.*)', answer).group(1)
    # print re.search(ur'\u0440+.', answer)

    # m = Modem("COM11")
    # print m.check_balance()

    # print m.send_sms_text("+79203048606", "test this is")
    # print m.send_sms_pdu("+79203048606", "Ваша заявка №123 принята. См. http://d3.ru/wfv13kgt")

###
# s = Serial('COM4', baudrate=9600)
#
# sms = SmsSubmit("+79203048606", "проверка боем".decode("utf-8"))
# pdu = sms.to_pdu()[0]
# envelope = pdu.pdu
# envelope_len = pdu.length
#
# time.sleep(2)
# s.write("AT+CMGF=0\x0D")
# time.sleep(2)
# s.write("AT+CMGS=%s\x0D%s\x1A" % (envelope_len, envelope))
# while True:
#     print s.read(2000)
#
# s.close()
