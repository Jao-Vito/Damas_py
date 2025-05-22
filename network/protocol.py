import socket
import threading

class NetworkHandler:
    def __init__(self, is_server, host='localhost', port=5555):
        self.is_server = is_server
        self.host = host
        self.port = port
        self.conn = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener = None

    def start(self):
        if self.is_server:
            self.sock.bind((self.host, self.port))
            self.sock.listen(1)
            print("Aguardando conexão...")
            self.conn, _ = self.sock.accept()
            print("Cliente conectado.")
        else:
            self.sock.connect((self.host, self.port))
            self.conn = self.sock
            print("Conectado ao servidor.")

    def send(self, message):
        if self.conn:
            self.conn.sendall((message + '\n').encode())

    def receive(self):
        data = b''
        while not data.endswith(b'\n'):
            part = self.conn.recv(1024)
            if not part:
                break
            data += part
        return data.decode().strip()

    def start_listener(self, callback):
        def listen():
            while True:
                try:
                    msg = self.receive()
                    if msg:
                        callback(msg)
                except:
                    break
        self.listener = threading.Thread(target=listen, daemon=True)
        self.listener.start()

    def close(self):
        if self.conn:
            self.conn.close()
        self.sock.close()
