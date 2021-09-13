import cv2, json, numpy
import socket
from collections import deque
from threading import Thread, Lock


# Global Job heap
job_heap = deque()


"""def formImage(data, lock):
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
        i += 1"""


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
    PORT = 5001  # The port used by the server
    i = 0
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
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

                s.send(job)
                i += 1


if __name__ == "__main__":
    lock = Lock()
    task1 = Thread(target=recieveJobs, args=(lock,))
    task2 = Thread(target=sendTasks, args=(lock,))
    task1.start()
    task2.start()
    task1.join()
    task2.join()
