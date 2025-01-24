import socket
import json
import threading
import os
from mqtt.mqtt_wrapper import MQTTWrapper

STATE_TOPIC = "State"
mqtt = MQTTWrapper('mqttbroker', 1883, name=f'presentation')


def publish(id, state, times_eaten):
    global mqtt, STATE_TOPIC

    data = {
        "ID": id,
        "state": state,
        "times_eaten": times_eaten
    }
    mqtt.loop_start()
    mqtt.publish(STATE_TOPIC, json.dumps(data))
    mqtt.stop()

def receiving_thread():
    IP = os.environ.get('IP')
    IP = "20.0.1.200"
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((IP, 42888))
        server_socket.listen(1)
        print(f"Server listening on {IP}:42888")

    except Exception as e:
        print(f"Error binding server socket on IP {IP}: {e}")
        return

    while True:
        try:
            conn, addr = server_socket.accept()
            data = conn.recv(1024).decode()
            update = json.loads(data)
            #data extract
            '''
            {
            "ID":   int,
            "state": string,
            "times_eaten": int
            }
            '''
            publish(update.get("ID"), update.get("state"), update.get("times_eaten"))

            response = {"status": "success"}
            conn.sendall(json.dumps(response).encode())

        except Exception as e:
            print(f"Error handling connection: {e}")

        finally:
            conn.close()


def main():
    client_thread = threading.Thread(target=receiving_thread)
    client_thread.start()


if __name__ == "__main__":
    main()