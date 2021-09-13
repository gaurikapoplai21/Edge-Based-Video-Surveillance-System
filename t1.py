import cv2, json, numpy
import socket
from collections import deque
from threading import Thread, Lock
import random

# Global Job heap
job_heap = deque()
conf = None


def recieveJobs(lock):
    HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
    PORT = 5000  # Port to listen on (non-privileged ports are > 1023)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print("Connected by", addr)
            while True:
                data = conn.recv(1024)
                # print(data)
                lock.acquire()
                job_heap.append(data)
                lock.release()
                if not data:
                    break
            print("done")


def sendTasks(lock):
    HOST = "127.0.0.1"  # The server's hostname or IP address
    i = 0
    connections = []
    for w in conf["workers"]:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, w["port"]))
        connections.append(s)

    while 1:
        if job_heap:
            print("Writing..." + str(i))
            lock.acquire()
            job = job_heap.popleft()
            lock.release()

            # Write:
            # cv2.imwrite(
            #     "output/nmsk/" + str(i) + ".png",
            #     cv2.cvtColor(
            #         numpy.float32(numpy.array(json.loads(job.decode())["frame"])),
            #         cv2.COLOR_BGR2GRAY,
            #     ),
            # )

            worker = random_scheduler(conf["workers"])
            connections[worker["id"] - 1].send(job)
            i += 1


def random_scheduler(workers):
    return random.choice(workers)


if __name__ == "__main__":
    confFile = open("conf.json", "r")
    conf = json.load(confFile)
    lock = Lock()
    task1 = Thread(target=recieveJobs, args=(lock,))
    task2 = Thread(target=sendTasks, args=(lock,))
    task1.start()
    task2.start()
    task1.join()
    task2.join()
