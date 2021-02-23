import os, time

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

def image_headers(filename):
    return {
        'X-Timestamp': time.time(),
        'Content-Length': os.path.getsize(filename),
        #FIXME: mime-type must be set according file content
        'Content-Type': 'image/jpeg',
    }

# FIXME: should take a binary stream
def image(filename):
    with open(filename, "rb") as f:
        # for byte in f.read(1) while/if byte ?
        byte = f.read(1)
        while byte:
            yield byte
            # Next byte
            byte = f.read(1)
