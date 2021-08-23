# FIXME: Make a Python Unit test
import logging
import queue
import socket
import time
from glob import glob
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

from pymjpeg import Image, boundary, request_headers, FileImage

logging.basicConfig(level=logging.DEBUG)


class FileImageHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        logging.debug('GET response code: 200')
        self.send_response(200)
        # Response headers (multipart)
        for k, v in request_headers().items():
            self.send_header(k, v)
            logging.debug('GET response header: ' + k + '=' + v)
        # Multipart content
        self.serve_images()

    def serve_image(self, image: Image):
        # Part boundary string
        self.end_headers()
        self.wfile.write(bytes(boundary, 'utf-8'))
        self.end_headers()
        # Part headers
        for k, v in image.image_headers().items():
            self.send_header(k, v)
            # logging.debug('GET response header: %s = %s' % (k, v))
        self.end_headers()
        # Part binary
        # logging.debug('GET response image: ' + filename)
        try:
            for chunk in image.get_byte_generator():
                self.wfile.write(chunk)
        except (ConnectionResetError, ConnectionAbortedError):
            return

    def serve_images(self):
        t_start = time.time()
        for i, filename in enumerate(glob('img/*.jpg')):
            image = FileImage(filename)
            logging.debug('GET response image: ' + filename)
            self.serve_image(image)
            fps = (i+1) / (time.time()-t_start)
            logging.debug("served image %d, overall fps: %0.3f" % (i+1, fps))

    def log_message(self, format, *args):
        return


def BytesImageHandlerFactory(q: queue.Queue):
    class BytesImageHandler(FileImageHandler):
        def __init__(self, request, client_address, server):
            self.queue = q
            super().__init__(request, client_address, server)

        def serve_images(self):
            i = 0
            t_start = time.time()
            while True:
                image = self.queue.get()
                self.serve_image(image)
                fps = (i + 1) / (time.time() - t_start)
                logging.debug("served image %d, overall fps: %0.3f" % (i + 1, fps))
                i += 1

        def add_image(self, image: Image):
            self.queue.put(image)
    return BytesImageHandler


class MJPEGServer:
    def __init__(self, port=8001, handler=FileImageHandler):
        ipaddress = socket.gethostbyname(socket.gethostname())
        address = "http://%s:%s" % (ipaddress, port)
        logging.info('Listening on port %d ...  address: %s' % (port, address))
        self.httpd = HTTPServer(('', port), handler)

    def start(self):
        self.httpd.serve_forever()


if __name__ == '__main__':
    from_files = True

    if from_files:
        # from files
        server = MJPEGServer()
        server.start()
    else:
        # from bytes; which could be coming from a bytestream or generated using e.g., opencv
        image_queue = queue.Queue(maxsize=100)
        handler_class = BytesImageHandlerFactory(q=image_queue)
        server = MJPEGServer(handler=handler_class)
        server_thread = Thread(target=server.start, daemon=True)
        server_thread.start()
        for filename in glob('img/*.jpg'):
            image = FileImage(filename)
            logging.debug('GET response image: ' + filename)
            image_queue.put(image)
        #wait until the current queue has been served before quiting
        while not image_queue.empty():
            time.sleep(1)
        server_thread.join(timeout=1)
