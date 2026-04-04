import http.server
import socketserver
import threading as thrd
import time, io

PORT = 8000

class simpleServer:
    def __init__(self,port=PORT):
        self.port=port
        self.httpd=None
        self.thread=None

    def start(self):
        handler = http.server.SimpleHTTPRequestHandler
        self.httpd = socketserver.TCPServer(("", self.port), handler)
        print(f"Web Server start at port {self.port}")
        self.thread=thrd.Thread(target=self.httpd.serve_forever)
        self.thread.start()

    def stop(self):
        if self.httpd:
            self.httpd.shutdown()
            self.thread.join()
            print("Web Server stop.")


########################################################################

PAGE = """\
<html>
<head>
<title>picamera2 MJPEG streaming demo</title>
</head>
<body>
<h1>Picamera2 MJPEG Streaming Demo</h1>
<img src="stream.mjpg" width="640" height="480" />
</body>
</html>
"""

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = thrd.Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


class StreamingHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    global outStream
                    with outStream.condition:
                        outStream.condition.wait()
                        frame = outStream.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                print('Removed streaming client %s: %s' % (self.client_address, str(e)))
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


class pageServer:
    def __init__(self,output,port=PORT):
        global outStream
        self.port=port
        outStream=output
        self.server = None
        self.thread=None


    def start(self):
        address = ('', self.port)
        self.server = StreamingServer(address, StreamingHandler)
        print(f"Page Server start at port {self.port}")
        self.thread=thrd.Thread(target=self.server.serve_forever)
        self.thread.start()


    def stop(self):
        if self.server:
            self.server.shutdown()
            self.thread.join()
            print("Page Server stop.")
