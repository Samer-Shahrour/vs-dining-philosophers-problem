import logging
import threading
import os
import time
import random
import setup
from communication import left_client, right_client
import socket
import threading
from enum import Enum

NAME = os.environ.get('NAME')
logging.basicConfig(format=f'{NAME}: %(message)s', level=logging.INFO)

NUMBER_PHILOSOPHERS = int(os.environ.get('NUMBER_PHILOSOPHERS'))

MY_ID = int(NAME[2:])
DOMINANT_HAND_RIGHT = False if MY_ID % 2 != 0 else True
NAME_RIGHT_PARTNER, NAME_LEFT_PARTNER = setup.set_partners(MY_ID, NUMBER_PHILOSOPHERS)
counter_eat = 0
counter_try_eat = 0
counter_think = 0

class State(Enum):
    EATING = 1
    THINKING = 2
    TRYING_TO_EAT = 3

state = State.THINKING

mutex = threading.Lock()

def right_server():
    global state
    RIGHT_PORT = 8080
    HOST = '0.0.0.0'         
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, RIGHT_PORT))
    s.listen()
   
    while True:
        conn, _ = s.accept()
        data = conn.recv(1024)
        if data == b'REQUEST':
            
            mutex.acquire()
           
            if state == State.EATING or state == State.TRYING_TO_EAT:
                conn.sendall(b'NACK')
            else:
                conn.sendall(b'ACK')
                
                   
            mutex.release()
        
        conn.close()

    
def left_server():
    global state
    LEFT_PORT = 8081
    HOST = '0.0.0.0'         
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, LEFT_PORT))
    s.listen()
    while True:
        conn, _ = s.accept()
        data = conn.recv(1024)
        if data == b'REQUEST':

            mutex.acquire()

            if state == State.EATING or state == State.TRYING_TO_EAT:
                conn.sendall(b'NACK')
            else:
                conn.sendall(b'ACK')
    
            mutex.release()

        conn.close()


def think():
    global state,counter_think
    mutex.acquire()
    state = State.THINKING
    mutex.release()
    counter_think +=1
    sleep_time = random.randint(3, 7)
    logging.info("thinking for: %s s", sleep_time)
    time.sleep(sleep_time)
    logging.info("thinking ended")
    

def try_to_eat():
    global state, counter_eat, counter_try_eat
    mutex.acquire()
    state = State.TRYING_TO_EAT
    mutex.release()
    counter_try_eat += 1
    if DOMINANT_HAND_RIGHT:
        if right_client(NAME_RIGHT_PARTNER):
            if left_client(NAME_LEFT_PARTNER):
                counter_eat += 1
                mutex.acquire()
                state = State.EATING
                mutex.release()
                
                sleep_time = random.randint(1, 7)
                logging.info("eating for: %s", sleep_time)
                time.sleep(sleep_time)
                
    else:
        if left_client(NAME_LEFT_PARTNER):
            if right_client(NAME_RIGHT_PARTNER):
                
                mutex.acquire()
                state = State.EATING
                mutex.release()
                sleep_time = random.randint(1, 10)
                logging.info("eating for: %s", sleep_time)
                time.sleep(sleep_time)
                
    logging.info("eating ended")


t1 = threading.Thread(target=right_server)
t1.start()

t2 = threading.Thread(target=left_server)
t2.start()

counter = 0
while True:
    think()
    try_to_eat()
    if counter == 4:
        logging.info("counter eat %d", counter_eat)
        logging.info("counter try eat %d", counter_try_eat)
        logging.info("counter think %d", counter_think)
        logging.info("effizienz in prozent %d", int((counter_eat/(counter_eat+counter_try_eat))*100))
        counter = 0
    counter += 1

