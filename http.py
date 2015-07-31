# -*- coding: utf-8 -*-
__author__ = 'ArmiT'

import BaseHTTPServer
import urlparse
import time
import json
import logging
import logger
from AuthException import AuthException
from AppException import AppException
import config

log = logging.getLogger(logger.NAME)


class Observer:
    """
    Facade for BaseHTTPServer
    """

    def __init__(self):
        self.server = BaseHTTPServer.HTTPServer
        self.request_handler = None

    def set_handler(self, handler):
        self.request_handler = handler

    def listen(self, host, port):

        handler = ServerHandler
        handler.set_call_handler(self.request_handler)

        httpd = self.server((host, port), handler)
        print time.asctime(), "Server starts - %s:%s" % (host, port)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()

        print time.asctime(), "Server stops - %s:%s" % (host, port)


class ServerHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    sender_handler = None

    def __init__(self, request, client_address, server):

        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, request, client_address, server)
        self.sender_handler = None

    @staticmethod
    def set_call_handler(handler):
        ServerHandler.sender_handler = handler

    # def log_message(self, format, *args):
    #     log.info(format % args)

    def log_error(self, format, *args):
        log.error(format % args)

    def handle_error(self, e, http_code=500):
        """
        Sends error http response and adds record to the log
        :param e: AppException
        :param http_code: int
        :return:
        """

        self.send_response(http_code)
        self.send_header("Content-type", "text/json")
        self.end_headers()

        self.wfile.write(json.dumps({"error": e.message, "code": e.code}))
        log.error("processing: %s:%s" % (e.message, e.code))

    def do_GET(self):
        """
        It serves GET requests
        :return:
        """

        params = urlparse.parse_qs(
            urlparse.urlparse(self.path).query
        )

        key_param = config.CONFIG.get('AUTH').get('key_param')

        key = params.get(key_param, [""])[0]
        cmd = params.get("c", ["nothing"])
        attrs = params.get("params", ["{}"])

        log.info("%s[%s] - %s: %s" % (self.address_string(), self.client_address, "".join(cmd), "".join(attrs)))

        try:

            if not self.check_auth(key):
                raise AuthException(message="Authenticate error", code=41)

            log_key = key[:5]
            log_key += "*" * 27
            log.info("auth success [%s]" % log_key)

            response = self.call_handler(ServerHandler.sender_handler, cmd[0], attrs[0])

        except AuthException as e:
            self.handle_error(e, 401)

        except AppException as e:
            self.handle_error(e)

        else:
            self.send_response(200)
            self.send_header("Content-type", "text/json")
            self.end_headers()
            self.wfile.write(json.dumps({"response": response, "code": 0}))

    def call_handler(self, handler, command, params):
        """
        Calls the requested command of a handler with given parameters
        :param handler: instance of a hanвдук class
        :param command: string
        :param params: dictionary
        :return:
        """
        try:
            params = json.loads(params)
            method = getattr(handler, command)

        except AttributeError as e:
            raise AppException(e.message, 40)
        else:
            return method(params)

    def check_auth(self, key):
        """
        Checks authority
        :param key:
        :return:
        """
        keys = config.CONFIG.get('AUTH').get('keys')
        keys = json.loads(keys)

        for item in keys:
            if item.get('key') == key:
                return True

        return False
