import cv2, json, numpy
from face_recognition.api import face_locations
import socket
from collections import deque
from threading import Thread, Lock
import face_recognition
from database import *
import sys
import base64
import requests
import boto3

# Global Job heap
job_heap = deque()
encodedFrames = []
sendFrames = deque()


def formatData(data, lock):
    length = 0
    i = 0
    f = 0
    while i < len(data):
        if data[i] == "%":
            f = 1
        elif data[i] == "{":
            job = json.loads(data[i : i + length])
            job["encoded"] = numpy.array(job["encoded"])
            lock.acquire()
            job_heap.append(job)
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
            while True:
                data = conn.recv(4096)
                # print(data)
                formatData(data.decode(), lock)
                if not data:
                    break
            print("done")


def checkUnique(res):
    # True: Unique Frame
    # False: Frame Match Found
    if res == []:
        return True
    for x in res:
        if x:
            return False
    return True


def logic(encoded):
    # True: Frame Added
    # False: Frame Discarded
    res = face_recognition.compare_faces(encodedFrames, encoded)
    if checkUnique(res):
        encodedFrames.append(encoded)
        return True
    return False


def uploadOnAws(lock):
    k = 0
    while 1:
        if sendFrames:

            lock.acquire()
            k += 1
            picname = sendFrames.popleft()
            lock.release()

            print("Picname : " + picname)

            with open(picname, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())

            response = requests.post(
                "https://w1vz8j0cqk.execute-api.us-east-1.amazonaws.com/prod/demo-lambda",
                json={
                    "name": "dumped/" + str(k) + ".png",
                    "file": encoded_string.decode(),
                },
            )
            print(response.json())


def locateAndSend(lock_j, lock_s):
    i = 0
    dbOb = Database()
    dir_output = "output\\nmsk\\"
    dir_input = "temp\\"
    while 1:
        if job_heap:
            # print("Writing..." + str(i))

            lock_j.acquire()
            job = job_heap.popleft()
            lock_j.release()

            label = job["label"]
            frame = job["frame"]
            encoded = job["encoded"]
            # print(label)
            if label == 1 or logic(encoded):
                print(frame)
                # cv2.imwrite(dir_output + frame + ".png", frame)
                dbOb.saveImageDb(cv2.imread(dir_input + frame + ".png"), label)
                if label == 0:
                    lock_s.acquire()
                    sendFrames.append(dir_input + frame + ".png")
                    lock_s.release()

            # print(job)

            i += 1


if __name__ == "__main__":
    lock_j = Lock()
    lock_s = Lock()
    task1 = Thread(target=recieveJobs, args=(lock_j,))
    task2 = Thread(target=locateAndSend, args=(lock_j, lock_s))
    task3 = Thread(target=uploadOnAws, args=(lock_s,))
    task1.start()
    task2.start()
    task3.start()
    task1.join()
    task2.join()
    task3.join()
