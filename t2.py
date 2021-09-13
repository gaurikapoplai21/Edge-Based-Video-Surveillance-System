import cv2, json, numpy
import socket
from collections import deque
from threading import Thread, Lock
import face_recognition
import sys

# Global Job heap
job_heap = deque()
encoded = deque()


def formatData(data, lock):
    length = 0
    i = 0
    f = 0
    while i < len(data):
        if data[i] == "%":
            f = 1
        elif data[i] == "{":
            lock.acquire()
            job_heap.append(json.loads(data[i : i + length]))
            lock.release()
            i += length
            length = 0
            f = 0
            continue
        elif f:
            length = 10 * length + int(data[i])
        i += 1


def recieveJobs(lock):
    HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
    PORT = int(sys.argv[1])  # Port to listen on (non-privileged ports are > 1023)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print("Connected by", addr)
            full_data = b""
            while True:
                data = conn.recv(1024)
                # print(data)
                formatData(data.decode(), lock)
                if not data:
                    break
            print("done")


def encodeFaces(lock_job, lock_enc):
    i = 0
    while 1:
        if job_heap:
            print("Encoding..." + str(i))
            lock_job.acquire()
            job = job_heap.popleft()
            lock_job.release()

            print(job)

            frameEncoding = face_recognition.face_encodings(
                cv2.imread(r"temp\\images\\" + job["frame"] + ".png")
            )
            if frameEncoding == []:
                continue
            job["encoded"] = frameEncoding[0].tolist()

            lock_enc.acquire()
            encoded.append(job)
            lock_enc.release()

            i += 1


def sendTasks(lock):
    HOST = "127.0.0.1"  # The server's hostname or IP address
    PORT = int(sys.argv[2])  # The port used by the server
    i = 0
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        while 1:
            if encoded:

                print("Sending..." + str(i))

                lock.acquire()
                encodedFrame = encoded.popleft()
                lock.release()

                data_to_send = json.dumps(encodedFrame)
                data_to_send = "%" + str(len(data_to_send)) + data_to_send
                s.send(data_to_send.encode())
                i += 1


if __name__ == "__main__":
    lock_job = Lock()
    lock_enc = Lock()
    task1 = Thread(target=recieveJobs, args=(lock_job,))
    task2 = Thread(
        target=encodeFaces,
        args=(
            lock_job,
            lock_enc,
        ),
    )
    task3 = Thread(target=sendTasks, args=(lock_enc,))
    task1.start()
    task2.start()
    task3.start()
    task1.join()
    task2.join()
    task3.join()
