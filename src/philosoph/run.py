import logging
import socket
import threading
import os
import time

NAME = os.environ.get('NAME')
PORT = 8080


logging.basicConfig(format=f'{NAME}: %(message)s', level=logging.INFO)

def client():
    if NAME == "ph1":
        PARTNERHOST = "ph2"  
    else:
        PARTNERHOST = "ph1"

    logging.info("my partner is -> %s", PARTNERHOST)
               
    time.sleep(1)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((PARTNERHOST, PORT))
    s.sendall(b'Client: Hallo')
    data = s.recv(1024)

    logging.info('c: antwort - %s', data)


def server():
    HOST = '0.0.0.0'   
    PORT = 8080        

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()
    conn, _ = s.accept()
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            logging.info('s: vom Client - %s', data)
            conn.sendall(b'Server: habe deine Anforderung bearbeitet')


if NAME == "ph1":
    t1 = threading.Thread(target=client)
    t1.start()
    t1.join()
    
if NAME == "ph2":
    t2 = threading.Thread(target=server)
    t2.start()
    t2.join()
