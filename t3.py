import cv2, json, numpy
import socket
from collections import deque
from threading import Thread, Lock
import face_recognition
from database import *
import sys, os
import base64
import requests

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
            print("Recieved: ", job_heap[-1]["frame"])
            lock.release()

            i += length
            length = 0
            f = 0
            continue
        elif f:
            length = 10 * length + int(data[i])
        i += 1


# Thread n - Workers Incoming
def recieveJobs(conn, lock):
    while True:
        data = conn.recv(4096)
        # print(data)
        if not data:
            lock.acquire()
            job_heap.append("")
            lock.release()
            break
        formatData(data.decode(), lock)
    print("done")


# Thread 1 - Incoming
def multipleClients(lock):
    HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
    PORT = int(sys.argv[1])  # Port to listen on (non-privileged ports are > 1023)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(num_conn)

        temp = num_conn
        while temp:
            conn, addr = s.accept()
            print("t3 Connected by", addr)
            t = Thread(
                target=recieveJobs,
                args=(
                    conn,
                    lock,
                ),
            )
            t.start()
            temp = temp - 1
        print("end")


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


# Thread 2 - Face Location
def locateAndSend(lock_j, lock_s):
    i = 0
    dbOb = Database()
    dir_input = "temp\\"
    count_empty = 0
    while 1:
        if job_heap:

            lock_j.acquire()
            job = job_heap.popleft()
            lock_j.release()

            if not job:
                count_empty += 1
                if count_empty == num_conn:
                    lock_s.acquire()
                    sendFrames.append("")
                    lock_s.release()
                    break
                continue

            label = job["label"]
            frame = job["frame"]
            encoded = job["encoded"]

            uploading = 0
            if label == 1 or logic(encoded):
                print(frame)
                dbOb.saveImageDb(cv2.imread(dir_input + frame + ".png"), label)
                if label == 0:
                    lock_s.acquire()
                    uploading = 1
                    sendFrames.append(dir_input + frame + ".png")
                    lock_s.release()

            if not uploading:
                try:
                    os.remove(dir_input + frame + ".png")
                except:
                    print("Failed to delete :", dir_input + frame + ".png")

            i += 1


# Thread 3 - Uploading to Cloud
def uploadOnAws(lock):
    k = 0
    while 1:
        if sendFrames:

            lock.acquire()
            k += 1
            picname = sendFrames.popleft()
            lock.release()

            if not picname:
                break

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

            try:
                os.remove(picname)
            except:
                print("Failed to delete :", picname)

            print(response.json())


if __name__ == "__main__":
    confFile = open("conf.json", "r")
    conf = json.load(confFile)
    num_conn = len(conf["workers"])
    lock_j = Lock()
    lock_s = Lock()
    task1 = Thread(target=multipleClients, args=(lock_j,))
    task2 = Thread(target=locateAndSend, args=(lock_j, lock_s))
    task3 = Thread(target=uploadOnAws, args=(lock_s,))
    task1.start()
    task2.start()
    task3.start()
    task1.join()
    task2.join()
    task3.join()
