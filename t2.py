import cv2, json, numpy
import socket
from collections import deque
from threading import Thread, Lock
import face_recognition

# Global Job heap
job_heap = deque()
encoded = deque()


def formImage(full_data, data, lock):
    idx = data.find(b"|")
    if idx == -1:
        return full_data + data
    else:
        job = json.loads((full_data + data[:idx]).decode())
        # print(job["frame"])
        # job["frame"] = numpy.array(job["frame"])
        job["frame"] = numpy.array(job["frame"]).astype(numpy.uint8)
        lock.acquire()
        job_heap.append(job)
        lock.release()
        return data[idx + 1 :]


def recieveJobs(lock):
    HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
    PORT = 5001  # Port to listen on (non-privileged ports are > 1023)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print("Connected by", addr)
            full_data = b""
            while True:
                data = conn.recv(4096)
                # print("came")
                full_data = formImage(full_data, data, lock)
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

            # print(face_recognition.face_encodings(job["frame"]))
            frameEncoding = face_recognition.face_encodings(job["frame"])
            if frameEncoding == []:
                continue
            job["frame"] = job["frame"].tolist()
            job["encoded"] = frameEncoding[0].tolist()

            lock_enc.acquire()
            encoded.append(job)
            lock_enc.release()

            i += 1


def sendTasks(lock):
    HOST = "127.0.0.1"  # The server's hostname or IP address
    PORT = 5002  # The port used by the server
    i = 0
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        while 1:
            if encoded:

                print("Sending..." + str(i))

                lock.acquire()
                encodedFrame = encoded.popleft()
                lock.release()

                s.sendall(json.dumps(encodedFrame).encode() + b"|")
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
