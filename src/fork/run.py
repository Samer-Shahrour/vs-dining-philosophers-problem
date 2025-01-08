import socket
import json
import os
import time
from enum import Enum
import threading
import logging

class State(Enum):
    FREE = 1
    RESERVED = 2

class Fork:
    def __init__(self, ip, port):
        self.port = int(port)
        self.state = State.FREE
        logging.info(f"my ip is: {ip}")
        logging.info(f"my port is: {self.port}")
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((ip, self.port))
        self.server_socket.listen(3)
        self.requests = []
        self.requests_lock = threading.Lock()
        self.state_lock = threading.Lock()

    def reserve(self):
        with self.state_lock:
            if self.state == State.RESERVED:
                return {"status": "fail", "message": "Fork already reserved"}
            else:
                self.state = State.RESERVED
                return {"status": "success", "message": "Fork reserved"}

    def free(self):
        with self.state_lock:
            if self.state == State.RESERVED:
                self.state = State.FREE
                return {"status": "success", "message": "Fork freed"}
            else:
                return {"status": "fail", "message": "Fork is not reserved"}


    def handle_request(self, conn, request):
        method = request.get("method")

        if method == "reserve":
            with self.requests_lock:
                self.requests.append((conn, request.get("timestamp")))

        else:
            try:
                if method == "free":
                    response = self.free()
                else:
                    response = {"status": "error", "message": f"Unknown method: {method}"}

                conn.sendall(json.dumps(response).encode())

            finally:
                conn.close()
            

    def handle_client(self, conn, addr):
        try:
            data = conn.recv(1024).decode()
            request = json.loads(data)
            self.handle_request(conn, request)
        
        except Exception as e:
            logging.error(f"Error: {e}")

    def start(self):
        client_thread = threading.Thread(target=self.thread)
        client_thread.start()
        while True:
            conn, addr = self.server_socket.accept()
            self.handle_client(conn, addr)
            

    def thread(self):
        while True:
            time.sleep(1)
            with self.requests_lock:

                if not self.requests:
                    continue
                
                try:
                    self.requests.sort(key=lambda x: x[1])
                    conn, _ = self.requests.pop(0)
                    
                    response = self.reserve()
                    conn.sendall(json.dumps(response).encode())

                finally:
                    conn.close()

                for conn, _ in self.requests:
                    try:
                        response = {"status": "fail", "message": "Fork already reserved"}
                        conn.sendall(json.dumps(response).encode())
                    finally:
                        conn.close()

                self.requests.clear()

                    


if __name__ == "__main__":
    ID = os.environ.get('ID')
    IP = os.environ.get('IP')
    PORT = os.environ.get('PORT')

    if not ID:
        ID = "ID"

    logging.basicConfig(format=f'F{ID}: %(message)s', level=logging.INFO)

    fork = Fork(IP, PORT)
    fork.start()
