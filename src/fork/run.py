import socket
import json
import logging
import os
import time
import sys
from enum import Enum
import threading

class State(Enum):
    FREE = 1
    RESERVED = 2

class Fork:
    def __init__(self, port=8080):
        self.port = port
        self.state = State.FREE
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("0.0.0.0", port))
        self.server_socket.listen(3)
        self.requests = []
        self.lock = threading.Lock()
        logging.info(f"Fork server listening on port {port}")

    def reserve(self):
        if self.state == State.RESERVED:
            return {"status": "fail", "message": "Fork already reserved"}
        else:
            self.state = State.RESERVED
            return {"status": "success", "message": "Fork reserved"}

    def free(self):
        if self.state == State.RESERVED:
            self.state = State.FREE
            return {"status": "success", "message": "Fork freed"}
        else:
            return {"status": "fail", "message": "Fork is not reserved"}
               

    def handle_request(self, conn, request):
        method = request.get("method")

        logging.info("received method = %s", method)
        if method == "reserve":
            self.requests.append((conn, request.get("times_eaten")))

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
        logging.info(f"Connection established with {addr}")
        try:
            data = conn.recv(1024).decode()
            request = json.loads(data)
            logging.info(f"Received request: {request}")
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
            least = sys.maxsize
            least_conn = 0

            for i in range(len(self.requests)):
                (conn, times_eaten) = self.requests[i]
                if times_eaten < least:
                    least = times_eaten
                    least_conn = conn
            
            if least != sys.maxsize:
                try:
                    response = self.reserve()
                    least_conn.sendall(json.dumps(response).encode())
                finally:
                    conn.close()


if __name__ == "__main__":
    ID = os.environ.get('ID')
    if not ID:
        ID = "ID"

    logging.basicConfig(format=f'{ID}: %(message)s', level=logging.INFO)

    fork = Fork()
    fork.start()
