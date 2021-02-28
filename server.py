# FIXME: Make a Python Unit test
import socket

import pymjpeg
from glob import glob
import sys
import logging

from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(level=logging.DEBUG)


class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        logging.debug('GET response code: 200')
        self.send_response(200)
        # Response headers (multipart)
        for k, v in pymjpeg.request_headers().items():
            self.send_header(k, v)
            logging.debug('GET response header: ' + k + '=' + v)
        # Multipart content
        for filename in glob('img/*.jpg'):
            image = pymjpeg.FileImage(filename)
            logging.debug('GET response image: ' + filename)
            # Part boundary string
            self.end_headers()
            self.wfile.write(bytes(pymjpeg.boundary, 'utf-8'))
            self.end_headers()
            # Part headers
            for k, v in image.image_headers().items():
                self.send_header(k, v)
                # logging.debug('GET response header: %s = %s' % (k, v))
            self.end_headers()
            # Part binary
            # logging.debug('GET response image: ' + filename)
            for chunk in image.get_byte_generator():
                try:
                    self.wfile.write(chunk)
                except (ConnectionResetError, ConnectionAbortedError):
                    return

    def log_message(self, format, *args):
        return


class MJPEGServer:
    def __init__(self, port=8001, handler=MyHandler):
        ipaddress = socket.gethostbyname(socket.gethostname())
        address = "http://%s:%s" % (ipaddress, port)
        logging.info('Listening on port %d ...  address: %s' % (port, address))
        self.httpd = HTTPServer(('', port), handler)

    def start(self):
        self.httpd.serve_forever()

    def stop(self):
        self.httpd.shutdown()


if __name__ == '__main__':
    server = MJPEGServer()
    server.start()

