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


    def start(self,port=8000):
        self.port = port
        self.stop_req = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('', self.port))
        self.sock.listen(1)
        print(f"Server started and listening on port {self.port}")
        self.accept_thrd = thrd.Thread(target=self._accept_thread, daemon=True)
        self.accept_thrd.start()

    def stop(self):
        self.stop_req = True
        if self.sock:
            self.sock.close()
            self.sock = None        
        if self.client_sock:
            self.client_sock.close()
            self.client_sock = None
        if self.accept_thrd:
            self.accept_thrd.join()
            self.accept_thrd = None


    def started(self):
        return self.sock is not None and not self.stop_req

    def _accept_thread(self):
        while not self.stop_req:
            print("Waiting for a connection...")
            try:
                self.client_sock, self.client_addr = self.sock.accept()
                print(f"Accepted connection from {self.client_addr}")
                self._client_worker(self.client_sock)
            except Exception as e:
                print(f"Error accepting connection: {e}")


    def _decode_data(self, data):
        #print data[0] to hex        
        print(f"receive {len(data)}bytes, data[0]={hex(data[0])}")


    def _client_worker(self, client_sock):
        while not self.stop_req:
            try:
                data = client_sock.recv(1024)
            except Exception as e:
                print(f"Error receiving data from {self.client_addr}: {e}")
                break
            if not data:
                break
            self._decode_data(data)
        print(f"Closing connection to {self.client_addr}")
        client_sock.close()
        self.client_sock = None
        self.client_addr = None


#----------------------------------------------------
# Client socket wrapper class
#----------------------------------------------------
class ClientSock:

    def __init__(self):
        self.sock = None


    def connect(self, host='127.0.0.1', port=8000):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((host, port))
            print(f"Connected to {host}:{port}")
        except Exception as e:
            print(f"Error connecting to {host}:{port}: {e}")
            self.sock = None
            return False
        self.recv_thrd = thrd.Thread(target=self._receive_worker, daemon=True)
        self.recv_thrd.start()
        return True


    def send(self, data):
        if self.sock:
            try:
                self.sock.sendall(data)
            except Exception as e:
                print(f"Error sending data: {e}")
                return False
        else:
            print("Socket is not connected")
            return False
        return True


    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None
            self.recv_thrd.join()

    def started(self):
        return self.sock is not None

    def _receive_worker(self):
        while self.sock:
            try:
                data = self.sock.recv(1024)
                if not data:
                    break
                print(f"Received {len(data)} bytes: {data}")
            except Exception as e:
                print(f"Error receiving data: {e}")
                break
        print("Closing client socket")
        self.close()