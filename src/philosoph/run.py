import socket
import json
import time
import random
import logging
import os


ID = os.environ.get('ID')
logging.basicConfig(format=f'PH{ID}: %(message)s', level=logging.INFO)
NUMBER_PHILOSOPHERS = int(os.environ.get('NUMBER_PHILOSOPHERS'))

class MyRpc:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def reserve(self):
        return self.call("reserve")

    def free(self):
        return self.call("free")

    def call(self, method):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((self.host, self.port))
                request = {"method": method}
                client_socket.sendall(json.dumps(request).encode())
                response = client_socket.recv(1024).decode()
                response = json.loads(response)
                return response
        except Exception as e:
            logging.error(f"Error calling {method} on {self.host}:{self.port} - {e}")
            return {"status": "error", "message": str(e)}


class Philosopher:
    def __init__(self, id):
        self.id = int(id)  #2
        self.fork_port = 8080
        left, right = self.get_forks(NUMBER_PHILOSOPHERS)
        self.left_fork = MyRpc(left, self.fork_port)
        self.right_fork = MyRpc(right, self.fork_port)
        self.right_handed = False if self.id % 2 != 0 else True


    def get_forks(self, NUMBER_PHILOSOPHERS):
        
        right = f"f{self.id - 1}"
        left = f"f{self.id}"

        if self.id == 1:
            right = f"f{NUMBER_PHILOSOPHERS}"

        return left, right
    


    def think(self):
        logging.info(f"thinking.")
        time.sleep(random.uniform(1, 3))  # Denkt für 1-3 Sekunden


    def eat(self):
        logging.info(f"eating.")
        time.sleep(random.uniform(5, 10))  # Isst für 1-2 Sekunden
        logging.info(f"finished eating.")
        
    def start_with_right(self):
        right_response = self.right_fork.reserve()
        if right_response.get("status") == "success":
            logging.info(f"reserved the first fork.")
            left_response = self.left_fork.reserve()
            if left_response.get("status") == "success":
                logging.info(f"reserved the second fork.")
                self.eat()
                self.left_fork.free()
                logging.info(f"freed the second fork.")
                self.right_fork.free()
                logging.info(f"freed the first fork.")
                return True
            else:
                logging.info(f"could not reserve the second fork.")
                self.right_fork.free()
                logging.info(f"freed the first fork.")
                return False
        else:
            logging.info(f"could not reserve the first fork.")
            return False
        
    
    def start_with_left(self):
        left_response = self.left_fork.reserve()
        if left_response.get("status") == "success":
            logging.info(f"reserved the first fork.")
            right_response = self.right_fork.reserve()
            if right_response.get("status") == "success":
                logging.info(f"reserved the second fork.")
                self.eat()
                self.right_fork.free()
                logging.info(f"freed the second fork.")
                self.left_fork.free()
                logging.info(f"freed the first fork.")
                return True
            else:
                logging.info(f"could not reserve the second fork.")
                self.left_fork.free()
                logging.info(f"freed the first fork.")
                return False
        else:
            logging.info(f"could not reserve the first fork.")
            return False
    
    
    
    def try_to_eat(self):
        logging.info(f"trying to eat.")
        if self.right_handed:
            return self.start_with_right()
        else:
            return self.start_with_left()

    def live(self, cycles=5):
        counter = 0
        while counter != cycles:
            counter += 1
            self.think()
            if self.try_to_eat():
                counter = 0
                
        logging.info("--------------------im dead-------------------")


if __name__ == "__main__":
    philosopher = Philosopher(ID)
    philosopher.live()
