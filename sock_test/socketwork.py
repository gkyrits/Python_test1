import socket
import threading as thrd


CMD_KEY_UP   = 0x01
CMD_KEY_DOWN = 0x02
CMD_KEY_LEFT = 0x03
CMD_KEY_RIGHT = 0x04
CMD_KEY_ENTER = 0x05
CMD_KEY_1   = 0x06
CMD_KEY_2   = 0x07
CMD_KEY_3   = 0x08
CMD_KEY_4   = 0x09
CMD_KEY_5   = 0x0A


def parse_port(text):
    """Return the port as int, or None if text is not a valid TCP port (1-65535)."""
    try:
        port = int(text.strip())
    except (ValueError, AttributeError):
        return None
    return port if 1 <= port <= 65535 else None


#----------------------------------------------------
# Server socket wrapper class
#----------------------------------------------------
class ServerSock:

    def __init__(self):
        self.sock = None
        self.client_addr = None
        self.client_sock = None
        self.port = None
        self.accept_thrd = None
        self.stop_req = False
        #callback functions ...
        self.on_key_received = None
        self.on_connect = None
        self.on_disconnect = None
        self.on_error = None


    def start(self,port=8000):
        self.port = port
        self.stop_req = False
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            listener.bind(('', self.port))
            listener.listen(1)
            listener.settimeout(0.5)
        except Exception:
            listener.close()
            raise
        self.sock = listener
        print(f"Server started and listening on port {self.port}")
        self.accept_thrd = thrd.Thread(target=self._accept_thread, daemon=True)
        self.accept_thrd.start()        


    def stop(self):
        self.stop_req = True
        #take a local copy - the worker thread may set self.client_sock to None at any time
        client_sock = self.client_sock
        if client_sock:
            try:
                client_sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            client_sock.close()
        if self.sock:
            self.sock.close()
            self.sock = None
        if self.accept_thrd:
            #wait for the accept thread to exit (accept timeout is 0.5s).
            #timeout avoids a deadlock if the thread is blocked in a Tk call (root.after)
            #while the GUI thread waits here; skip if stop() is called from that thread
            if self.accept_thrd is not thrd.current_thread():
                self.accept_thrd.join(timeout=1.0)
            self.accept_thrd = None


    def started(self):
        return self.sock is not None and not self.stop_req


    def _accept_thread(self):
        listener = self.sock
        while not self.stop_req:
            print("Waiting for a connection...")
            try:
                self.client_sock, self.client_addr = listener.accept()
                print(f"Accepted connection from {self.client_addr}")
                if self.on_connect:
                    self.on_connect(self.client_addr)
                self._client_worker(self.client_sock)
                if self.stop_req:
                    break                
            except socket.timeout:
                continue
            except Exception as e:
                if self.stop_req:
                    break
                print(f"Error accepting connection: {e}")
                if self.on_error:
                    self.on_error(e)
        print("Accept thread exiting")


    def _decode_data(self, data):             
        #TCP is a byte stream - several key codes can arrive in one recv()
        print(f"receive {len(data)}bytes: {data.hex(' ')}")
        for key_code in data:
            if CMD_KEY_UP <= key_code <= CMD_KEY_5 and self.on_key_received:
                self.on_key_received(key_code)


    def _client_worker(self, client_sock):
        while not self.stop_req:
            try:
                data = client_sock.recv(1024)
            except Exception as e:
                if not self.stop_req:
                    print(f"Error receiving data from {self.client_addr}: {e}")
                    if self.on_error:
                        self.on_error(e)
                break
            if not data:
                break
            self._decode_data(data)
        print(f"Closing connection to {self.client_addr}")
        client_sock.close()
        self.client_sock = None
        self.client_addr = None
        if self.on_disconnect:
            self.on_disconnect()


#----------------------------------------------------
# Client socket wrapper class
#----------------------------------------------------
class ClientSock:

    def __init__(self):
        self.sock = None
        self.recv_thrd = None
        self.stop_req = False
        self.lock = thrd.Lock()
        self.on_disconnect = None
        self.on_error = None


    def connect(self, host='127.0.0.1', port=8000):
        self.stop_req = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((host, port))
            print(f"Connected to {host}:{port}")
        except Exception as e:
            print(f"Error connecting to {host}:{port}: {e}")
            self.sock.close()
            self.sock = None
            if self.on_error:
                self.on_error(e)            
            return False
        self.recv_thrd = thrd.Thread(target=self._receive_worker, args=(self.sock,), daemon=True)
        self.recv_thrd.start()
        return True


    def send(self, data):
        if self.sock:
            try:
                self.sock.sendall(data)
            except Exception as e:
                print(f"Error sending data: {e}")
                if self.on_error:
                    self.on_error(e)
                #the connection is broken - close it so started() reflects the real state
                self.close()
                return False
        else:
            print("Socket is not connected")
            return False
        return True


    def close(self, only_sock=None):
        #claim the socket atomically (under the lock) before shutdown wakes the receive thread,
        #so only one caller sees was_connected=True and fires on_disconnect.
        #only_sock: close only if that is still the current socket (used by the receive
        #thread so a late exit can't close a newer connection)
        with self.lock:
            if only_sock is not None and self.sock is not only_sock:
                return
            self.stop_req = True
            sock = self.sock
            self.sock = None
            recv_thrd = self.recv_thrd
            self.recv_thrd = None
        was_connected = sock is not None
        if sock:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            sock.close()
        if recv_thrd:
            #wait for the receive thread to exit; skip if called from that thread
            #timeout avoids a deadlock if the thread is blocked in a Tk call
            if recv_thrd is not thrd.current_thread():
                recv_thrd.join(timeout=1.0)
        if was_connected and self.on_disconnect:
            self.on_disconnect()


    def started(self):
        return self.sock is not None


    def _receive_worker(self, sock):
        #self.sock is not sock -> this connection was closed (and maybe replaced by a new one)
        while not self.stop_req and self.sock is sock:
            try:
                data = sock.recv(1024)
                if not data:
                    break
                print(f"Received {len(data)} bytes: {data}")
            except Exception as e:
                if not self.stop_req and self.sock is sock:
                    print(f"Error receiving data: {e}")
                    if self.on_error:
                        self.on_error(e)
                break
        print("Closing client socket")
        self.close(only_sock=sock)