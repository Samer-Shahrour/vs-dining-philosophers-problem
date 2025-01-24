import socket
import json
import time
import logging
import os
#from mqtt.mqtt_wrapper import MQTTWrapper
from RPC import MyRpc, PresentationRpc



class Philosopher:
    def __init__(self, id, ip, port, presentationIP):
        self.id = int(id)
        self.ip = ip
        self.port = int(port)
        self.presentation = PresentationRpc(presentationIP, 42888)
        left_ip, right_ip, left_port, right_port = self.get_forks(NUMBER_PHILOSOPHERS)
        logging.info(f"my id: {self.id}")
        logging.info(f"my right ip: {right_ip}, and my left ip: {left_ip}")
        logging.info(f"my right port: {right_port}, and my left port: {left_port}")
        self.right_handed = False if self.id % 2 != 0 else True
        self.times_eaten = 0

        if self.right_handed:
            self.dominant_side_fork = MyRpc(ip, right_port)
            self.weak_side_fork = MyRpc(ip, left_port)
        else:
            self.dominant_side_fork = MyRpc(ip, left_port)
            self.weak_side_fork = MyRpc(ip, right_port)

        #self.mqtt = MQTTWrapper('mqttbroker', 1883, name= f'phi_{self.id}')


    '''
    def publish(self, state):
        
        data = {
            "ID":           self.id,
            "state":        state,
            "times_eaten":  self.times_eaten
            }
        #self.mqtt.loop_start()
        #self.mqtt.publish(STATE_TOPIC, json.dumps(data))
        #self.mqtt.stop() 
        
        print("TODO")
     '''

            

    def get_forks(self, NUMBER_PHILOSOPHERS):
        right_ip = self.ip + '.' + str(self.id + 1)
        left_ip = self.ip + '.' + str(self.id + 2)
        
        right_port = self.port + self.id - 1
        left_port = self.port + self.id 
        
        if self.id == NUMBER_PHILOSOPHERS:
            left_ip = self.ip + '.2'
            left_port = self.port

        return left_ip, right_ip, left_port, right_port      

    def think(self):
        #self.publish("Thinking")
        self.presentation.update(self.id, "Thinking", self.times_eaten)
        time.sleep(4)


    def eat(self):
        #self.publish("Eating")
        self.presentation.update(self.id, "Eating", self.times_eaten)
        time.sleep(4)
        self.times_eaten += 1
        

    def try_to_eat(self):
        #self.publish("Trying_to_eat")
        self.presentation.update(self.id, "Trying_to_eat", self.times_eaten)

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

        self.presentation.update(self.id, "Dead", self.times_eaten)
        #self.publish("Dead")


if __name__ == "__main__":
    ID = os.environ.get('ID')
    IP = os.environ.get('BASE_IP')
    IP = os.environ.get('FORKS_IP')
    PORT = os.environ.get('BASE_PORT')
    PresentationIP = os.environ.get('PRS_IP')
    logging.basicConfig(format=f'PH{ID}: %(message)s', level=logging.INFO)
    NUMBER_PHILOSOPHERS = int(os.environ.get('NUMBER_PHILOSOPHERS'))

    #STATE_TOPIC = "asdfasdadsfasdf"
    philosopher = Philosopher(ID, IP, PORT, PresentationIP)
    philosopher.live()