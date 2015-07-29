# -*- coding: utf-8 -*-
__author__ = 'ArmiT'

import BaseHTTPServer
import urlparse
import time
import json
import logging
import logger
from AuthException import AuthException
import traceback
import config

log = logging.getLogger(logger.NAME)


class Observer:

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

    def handle_error(self, message, code = 500):
        self.send_response(code)
        self.send_header("Content-type", "text/json")
        self.end_headers()

        self.wfile.write(json.dumps({"error": message}))
        log.error("processing: %s" % message)

    def do_GET(self):

        params = urlparse.parse_qs(
            urlparse.urlparse(self.path).query
        )

        key_param = config.CONFIG.get('AUTH').get('key_param')

        key = params.get(key_param, [""])[0]
        cmd = params.get("c", ["status"])
        attrs = params.get("params", ["{}"])

        log.info("%s[%s] - %s: %s" % (self.address_string(), self.client_address, "".join(cmd), "".join(attrs)))

        try:

            if not self.check_auth(key):
                raise AuthException("Authenticate error")

            log_key = key[:5]
            log_key += "*" * 27
            log.info("auth success [%s]" % log_key)

            response = self.call_handler(ServerHandler.sender_handler, cmd[0], attrs[0])
            self.send_response(200)
            self.send_header("Content-type", "text/json")
            self.end_headers()
            self.wfile.write(json.dumps({"response": response}))

        except AuthException as e:
            self.handle_error(e.message, 401)

        except BaseException as e:
            self.handle_error(e.message)

    def call_handler(self, handler, command, params):
        params = json.loads(params)
        method = getattr(handler, command)
        return method(params)

    def check_auth(self, key):
        keys = config.CONFIG.get('AUTH').get('keys')
        keys = json.loads(keys)

        for item in keys:
            if item.get('key') == key:
                return True

        return False
