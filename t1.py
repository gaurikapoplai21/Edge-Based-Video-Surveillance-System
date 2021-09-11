import cv2, json, numpy
import socket
from collections import deque
from threading import Thread, Lock


# Global Job heap
job_heap = deque()


def formImage(full_data, data, lock):
    idx = data.find(b"|")
    if idx == -1:
        return full_data + data
    else:
        job = json.loads((full_data + data[:idx]).decode())
        job["frame"] = numpy.array(job["frame"])

        lock.acquire()
        job_heap.append(job)
        lock.release()
        return data[idx + 1 :]


def recieveJobs(lock):
    HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
    PORT = 5000  # Port to listen on (non-privileged ports are > 1023)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print("Connected by", addr)
            full_data = b""
            while True:
                data = conn.recv(4096)
                full_data = formImage(full_data, data, lock)
                if not data:
                    break
            print("done")


def sendTasks(lock):
    HOST = "127.0.0.1"  # The server's hostname or IP address
    PORT = 5001  # The port used by the server
    i = 0
    while 1:
        if job_heap:
            print("Writing..." + str(i))
            lock.acquire()
            job = job_heap.popleft()
            lock.release()

            # Write:
            cv2.imwrite("output/nmsk/" + str(i) + ".png", job["frame"])
            i += 1


if __name__ == "__main__":
    lock = Lock()
    task1 = Thread(target=recieveJobs, args=(lock,))
    task2 = Thread(target=sendTasks, args=(lock,))
    task1.start()
    task2.start()
    task1.join()
    task2.join()
