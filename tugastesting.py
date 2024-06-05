import socket
import threading
import logging
from time import gmtime, strftime

class CommandProcessor:
    @staticmethod
    def handle_time(connection):
        time_message = f"JAM {strftime('%H:%M:%S', gmtime())}\r\n"
        connection.sendall(time_message.encode())

    @staticmethod
    def handle_quit(connection):
        quit_message = "QUIT MESSAGE BERHASIL DITERIMA\n"
        connection.sendall(quit_message.encode())
        connection.close()

    @staticmethod
    def handle_unknown(connection):
        unknown_message = "WARNING: COMMAND TIDAK DIKENAL\n"
        connection.sendall(unknown_message.encode())

class ClientHandler(threading.Thread):
    def __init__(self, client_socket, client_address):
        super().__init__()
        self.client_socket = client_socket
        self.client_address = client_address

    def run(self):
        while True:
            try:
                data = self.client_socket.recv(32)
                if data:
                    command = data.decode().strip()
                    logging.warning(f"Data diterima: {command} dari {self.client_address}.")
                    if command.endswith('TIME'):
                        logging.warning(f"TIME command diterima dari {self.client_address}.")
                        CommandProcessor.handle_time(self.client_socket)
                    elif command.endswith('QUIT'):
                        logging.warning(f"QUIT command diterima dari {self.client_address}.")
                        CommandProcessor.handle_quit(self.client_socket)
                        break
                    else:
                        logging.warning(f"Perintah tidak dikenal {command} dari {self.client_address}.")
                        CommandProcessor.handle_unknown(self.client_socket)
                else:
                    break
            except OSError:
                break
        self.client_socket.close()

class TCPServer(threading.Thread):
    def __init__(self, ip='0.0.0.0', port=45000):
        super().__init__()
        self.ip = ip
        self.port = port
        self.client_threads = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(5)
        logging.warning(f"Server listening on {self.ip}:{self.port}")

        while True:
            client_socket, client_address = self.server_socket.accept()
            logging.warning(f"Connection from {client_address}")

            client_thread = ClientHandler(client_socket, client_address)
            client_thread.start()
            self.client_threads.append(client_thread)

def main():
    logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
    server = TCPServer()
    server.start()

if __name__ == "__main__":
    main()
