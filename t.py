import socket

import cv2
import json

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server
t = 2
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while t:
        img = json.dumps(
            cv2.cvtColor(cv2.imread("output/nmsk/5.png"), cv2.COLOR_BGR2GRAY).tolist()
        ).encode()
        print(t)
        s.sendall(img + b"|")
        t -= 1
