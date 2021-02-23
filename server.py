# FIXME: Make a Python Unit test

import pymjpeg
from glob import glob
import sys
import logging

from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(level = logging.DEBUG)

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
            logging.debug('GET response image: ' + filename)
            # Part boundary string
            self.end_headers()
            self.wfile.write(bytes(pymjpeg.boundary, 'utf-8'))
            self.end_headers()
            # Part headers
            for k, v in pymjpeg.image_headers(filename).items():
                self.send_header(k, v)
                # logging.debug('GET response header: ' + k + '=' + v)
            self.end_headers()
            # Part binary
            # logging.debug('GET response image: ' + filename)
            for chunk in pymjpeg.image(filename):
                self.wfile.write(chunk)
    def log_message(self, format, *args):
        return

logging.info('Listening on port 8001...')
httpd = HTTPServer(('', 8001), MyHandler)
httpd.serve_forever()
