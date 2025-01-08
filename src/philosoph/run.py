import socket
import json
import time
import logging
import os
from mqtt.mqtt_wrapper import MQTTWrapper


ID = os.environ.get('ID')
logging.basicConfig(format=f'PH{ID}: %(message)s', level=logging.INFO)
NUMBER_PHILOSOPHERS = int(os.environ.get('NUMBER_PHILOSOPHERS'))

STATE_TOPIC = "State"

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


class Philosopher:
    def __init__(self, id):
        self.id = int(id)
        self.fork_port = 8080
        left, right = self.get_forks(NUMBER_PHILOSOPHERS)
        self.right_handed = False if self.id % 2 != 0 else True
        self.times_eaten = 0

        if self.right_handed:
            self.dominant_side_fork = MyRpc(right, self.fork_port)
            self.weak_side_fork = MyRpc(left, self.fork_port)
        else:
            self.dominant_side_fork = MyRpc(left, self.fork_port)
            self.weak_side_fork = MyRpc(right, self.fork_port)

        self.mqtt = MQTTWrapper('mqttbroker', 1883, name= f'phi_{self.id}')


    def publish(self, state):
        data = {
            "ID":           self.id,
            "state":        state,
            "times_eaten":  self.times_eaten
            }
        self.mqtt.loop_start()
        self.mqtt.publish(STATE_TOPIC, json.dumps(data))
        self.mqtt.stop()
            

    def get_forks(self, NUMBER_PHILOSOPHERS):
        
        right = f"f{self.id - 1}"
        left = f"f{self.id}"

        if self.id == 1:
            right = f"f{NUMBER_PHILOSOPHERS}"

        return left, right
    


    def think(self):
        self.publish("Thinking")
        time.sleep(4)


    def eat(self):
        self.publish("Eating")
        time.sleep(4)
        self.times_eaten += 1
        

    def try_to_eat(self):
        self.publish("Trying_to_eat")
        if self.dominant_side_fork.reserve(self.times_eaten):

            if self.weak_side_fork.reserve(self.times_eaten):
                self.eat()
                self.dominant_side_fork.free(self.times_eaten)
                self.weak_side_fork.free(self.times_eaten)
                return True
            else:
                self.dominant_side_fork.free(self.times_eaten)
                return False
        else:
            return False
        

    def live(self, cycles=5):
        counter = 0
        while counter != cycles:
            counter += 1
            self.think()
            if self.try_to_eat():
                counter = 0
                
        self.publish("Dead")


if __name__ == "__main__":
    philosopher = Philosopher(ID)
    philosopher.live()

    


