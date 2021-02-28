import os, time
from abc import abstractmethod

boundary = '--boundarydonotcross'

def request_headers():
    return {
        'Cache-Control': 'no-store, no-cache, must-revalidate, pre-check=0, post-check=0, max-age=0',
        'Connection': 'close',
        'Content-Type': 'multipart/x-mixed-replace;boundary=%s' % boundary,
        'Expires': 'Mon, 1 Jan 2030 00:00:00 GMT',
        'Pragma': 'no-cache',
		'Access-Control-Allow-Origin': '*' # CORS
    }


class Image:
    def image_headers(self, mimetype='image/jpeg'):
        return {
            'X-Timestamp': time.time(),
            'Content-Length': self.get_content_length(),
            'Content-Type': mimetype,
        }
    @abstractmethod
    def get_content_length(self):
        raise NotImplementedError()

    @abstractmethod
    def get_byte_generator(self):
        raise NotImplementedError()


class FileImage(Image):
    def __init__(self, filename):
        self.filename = filename

    def image_headers(self):
        ext = self.filename.split('.')[-1].lower()
        if ext in ('jpg', 'jpeg'):
            return super().image_headers(mimetype='image/jpeg')
        else:
            raise NotImplementedError("Only implemented for jpeg for now")

    def get_content_length(self):
        return os.path.getsize(self.filename)

    def get_byte_generator(self):
        with open(self.filename, "rb") as f:
            # for byte in f.read(1) while/if byte ?
            byte = f.read(1)
            while byte:
                yield byte
                # Next byte
                byte = f.read(1)


class BytesImage(Image):
    def __init__(self, bytes: list):
        self.bytes = bytes

    def get_content_length(self):
        return len(self.bytes)

    def get_byte_generator(self):
        for byte in self.bytes:
            yield byte
