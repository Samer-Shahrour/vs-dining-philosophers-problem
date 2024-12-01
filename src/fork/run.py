import socket
import json
import logging
import os
from enum import Enum
#from threading import Lock


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
        #self.lock = Lock()
        logging.info(f"Fork server listening on port {port}")

    def reserve(self):
        response = None
        #self.lock.acquire()
        
        if self.state == State.RESERVED:
            response = {"status": "fail", "message": "Fork already reserved"}
        else:
            self.state = State.RESERVED
            response = {"status": "success", "message": "Fork reserved"}
        
        #self.lock.release()
        return response

    def free(self):
        response = None
        #self.lock.acquire()

        if self.state == State.RESERVED:
            self.state = State.FREE
            response = {"status": "success", "message": "Fork freed"}
        else:
            response = {"status": "fail", "message": "Fork is not reserved"}
            
        #self.lock.release()
        return response
    

    def handle_request(self, request):

        method = request.get("method")

        logging.info("received method = %s", method)
        if method == "reserve":
            return self.reserve()
        elif method == "free":
            return self.free()
        else:
            return {"status": "error", "message": f"Unknown method: {method}"}
        

    def handle_client(self, conn, addr):
        logging.info(f"Connection established with {addr}")
        try:
            data = conn.recv(1024).decode()
            request = json.loads(data)
            logging.info(f"Received request: {request}")
            response = self.handle_request(request)
            conn.sendall(json.dumps(response).encode())
        except Exception as e:
            logging.error(f"Error: {e}")
        finally:
            conn.close()
            logging.info(f"Connection with {addr} closed")



    def start(self):
        while True:
            conn, addr = self.server_socket.accept()
            self.handle_client(conn, addr)


if __name__ == "__main__":
    ID = os.environ.get('ID')
    if not ID:
        ID = "ID"
        
    logging.basicConfig(format=f'{ID}: %(message)s', level=logging.INFO)


    fork = Fork()
    fork.start()