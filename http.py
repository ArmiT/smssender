__author__ = 'ArmiT'

import BaseHTTPServer
import urlparse
import time
import json
import logging


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

    #def log_error(self, format, *args):
        #logging.warning(format)

    def handle_error(self, message):
        self.send_response(500)
        self.send_header("Content-type", "text/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}))

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/json")
        self.end_headers()

    def do_GET(self):

        params = urlparse.parse_qs(
            urlparse.urlparse(self.path).query
        )

        cmd = params.get("c", "status")
        attrs = params.get("params", "")

        try:

            response = self.call_handler(ServerHandler.sender_handler, cmd[0], attrs[0])
            self.send_response(200)
            self.send_header("Content-type", "text/json")
            self.end_headers()
            self.wfile.write(response)

        except BaseException as e:
            self.handle_error(e.message)

    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-type", "text/json")
        self.end_headers()

        self.wfile.write("this is post req")

    def call_handler(self, handler, command, params):
        params = json.loads(params)
        method = getattr(handler, command)
        return method(params)
