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
                return response.get("status") == "success"
        except Exception as e:
            logging.error(f"Error calling {method} on {self.host}:{self.port} - {e}")
            return False


class Philosopher:
    def __init__(self, id):
        self.id = int(id)
        self.fork_port = 8080
        left, right = self.get_forks(NUMBER_PHILOSOPHERS)
        self.right_handed = False if self.id % 2 != 0 else True

        if self.right_handed:
            self.dominant_side_fork = MyRpc(right, self.fork_port)
            self.weak_side_fork = MyRpc(left, self.fork_port)
        else:
            self.dominant_side_fork = MyRpc(left, self.fork_port)
            self.weak_side_fork = MyRpc(right, self.fork_port)


    def get_forks(self, NUMBER_PHILOSOPHERS):
        
        right = f"f{self.id - 1}"
        left = f"f{self.id}"

        if self.id == 1:
            right = f"f{NUMBER_PHILOSOPHERS}"

        return left, right
    


    def think(self):
        logging.info(f"thinking.")
        time.sleep(random.uniform(1, 3))
        logging.info(f"finished thinking.")


    def eat(self):
        logging.info(f"eating.")
        time.sleep(random.uniform(5, 10))
        logging.info(f"finished eating.")
        

    
    def try_to_eat(self):
        logging.info(f"trying to eat.")
        if self.dominant_side_fork.reserve():
            logging.info(f"reserved the first fork.")

            if self.weak_side_fork.reserve():
                logging.info(f"reserved the second fork.")
                self.eat()
                self.dominant_side_fork.free()
                logging.info(f"freed the second fork.")
                self.weak_side_fork.free()
                logging.info(f"freed the first fork.")
                return True
            else:
                logging.info(f"could not reserve the second fork.")
                self.dominant_side_fork.free()
                logging.info(f"freed the first fork.")
                return False
        else:
            logging.info(f"could not reserve the first fork.")
            return False
        

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
