import socket
import logging
import setup

def left_client(name):
    LEFT_PORT = 8080

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((name, LEFT_PORT))
    s.sendall(b'REQUEST')
    data = s.recv(1024)

    logging.info('cl: antwort: %s', data)

    if data == b'ACK':
            
        return True
    
    if data == b'NACK':
        return False
    
    
def right_client(name):

    RIGHT_PORT = 8081

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((name, RIGHT_PORT))
    s.sendall(b'REQUEST')
    data = s.recv(1024)

    logging.info('cr: antwort: %s', data)

    if data == b'ACK':
        return True
    
    if data == b'NACK':
        return False
    
    

    