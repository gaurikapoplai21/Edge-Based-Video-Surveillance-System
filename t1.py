import cv2, json, numpy
import subprocess
import socket

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print("Connected by", addr)
        img = b""
        arr = []
        while True:
            data = conn.recv(4096)
            idx = data.find(b"|")
            if idx == -1:
                img += data
            else:
                arr.append(img + data[:idx])
                img = data[idx + 1 :]
            if not data:
                break
        for i in range(len(arr)):
            cv2.imwrite(
                "output/nmsk/" + str(i) + ".png",
                numpy.array(json.loads(arr[i].decode())),
            )
        print("done")
