import socket
import json
import logging

class MyRpc:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def reserve(self, times_eaten):
        return self.call("reserve", times_eaten)

    def free(self, times_eaten):
        return self.call("free", times_eaten)

    def call(self, method, times_eaten):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((self.host, self.port))
                request = {"method": method, "timestamp": times_eaten}
                client_socket.sendall(json.dumps(request).encode())

                response = client_socket.recv(1024).decode()
                response = json.loads(response)
                return response.get("status") == "success"

        except Exception as e:
            logging.error(f"Error calling {method} on {self.host}:{self.port} - {e}")
            return False



class PresentationRpc:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def update(self, id, state, times_eaten):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((self.host, self.port))
                request = {"ID": id, "state": state, "times_eaten": times_eaten}
                client_socket.sendall(json.dumps(request).encode())

                response = client_socket.recv(1024).decode()
                response = json.loads(response)
                return response.get("status") == "success"

        except Exception as e:
            logging.error(f"Error calling update on {self.host}:{self.port} - {e}")
            return False