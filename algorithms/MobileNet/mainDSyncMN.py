from numpy.lib.function_base import _ARGUMENT_LIST
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from imutils.video import VideoStream
import numpy as np
import imutils
import time
import cv2
import os
import sys
import asyncio
from concurrent.futures import ThreadPoolExecutor
from multiprocessing.pool import ThreadPool as Pool
import subprocess
import json
import boto3
from tensorflow.python.keras.backend import GraphExecutionFunction
import socket
from collections import deque
from threading import Thread, Lock

print("MobileNet Algorithm started")
print("_" * 100)

k = 0
s3 = boto3.resource(
    service_name="s3",
    region_name="us-east-1",
    aws_access_key_id="AKIARN4QT2VHYCU5XH7P",
    aws_secret_access_key="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",
)


def uploadOnAws(picname):
    global k
    k += 1
    s3.Bucket("frames-from-the-edge").upload_file(Filename=picname, Key=str(k) + ".jpg")
    print("done")


def getParentDirectory(levels):
    cur = os.path.dirname(__file__)
    for _ in range(0, levels):
        cur = os.path.dirname(cur)
    return os.path.realpath(cur)


grandparentDir = getParentDirectory(2)
sys.path.append(grandparentDir)
exit_code = 0

from database import Database


def detect_and_predict_mask(frame, faceNet, maskNet):
    # grab the dimensions of the frame and then construct a blob
    # from it
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 1.0, (224, 224), (104.0, 177.0, 123.0))

    # pass the blob through the network and obtain the face detections
    faceNet.setInput(blob)
    detections = faceNet.forward()
    # print(detections.shape)

    # initialize our list of faces, their corresponding locations,
    # and the list of predictions from our face mask network
    faces = []
    locs = []
    preds = []

    # loop over the detections
    for i in range(0, detections.shape[2]):
        # extract the confidence (i.e., probability) associated with
        # the detection
        confidence = detections[0, 0, i, 2]

        # filter out weak detections by ensuring the confidence is
        # greater than the minimum confidence
        if confidence > 0.5:
            # compute the (x, y)-coordinates of the bounding box for
            # the object
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # ensure the bounding boxes fall within the dimensions of
            # the frame
            (startX, startY) = (max(0, startX), max(0, startY))
            (endX, endY) = (min(w - 1, endX), min(h - 1, endY))

            # extract the face ROI, convert it from BGR to RGB channel
            # ordering, resize it to 224x224, and preprocess it
            face = frame[startY:endY, startX:endX]
            # picname = "picture" + str(i) + ".png"
            # cv2.imwrite(picname,face)
            face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
            face = cv2.resize(face, (224, 224))
            face = img_to_array(face)
            face = preprocess_input(face)
            # cv2.imwrite("picture.jpg",face)

            # add the face and bounding boxes to their respective
            # lists
            faces.append(face)
            locs.append((startX, startY, endX, endY))
            # i += 1

    # only make a predictions if at least one face was detected
    if len(faces) > 0:
        # for faster inference we'll make batch predictions on *all*
        # faces at the same time rather than one-by-one predictions
        # in the above `for` loop
        faces = np.array(faces, dtype="float32")
        preds = maskNet.predict(faces, batch_size=32)

    # return a 2-tuple of the face locations and their corresponding
    # locations

    return (locs, preds)


def checkStopSignal():
    global exit_code, stop_conn
    HOST = "127.0.0.1"
    PORT = 6969

    stop_conn.bind((HOST, PORT))

    try:
        data, _ = stop_conn.recvfrom(1024)
        stop_conn.close()
        if data:
            exit_code = 1
    except:
        print("Explicitely Stopped!")


def saveAndSendTask(lock):
    global frame_heap, frame_number
    while 1:
        if frame_heap:
            lock.acquire()
            frame = frame_heap.popleft()
            frame_number += 1
            lock.release()

            if frame is None:
                break

            label, only_face_color = frame

            cv2.imwrite(
                grandparentDir + r"\\temp\\" + str(frame_number) + ".png",
                only_face_color,
            )
            label01 = 1 if label == "Mask" else 0
            data_to_send = json.dumps(
                {
                    "label": label01,
                    "frame": str(frame_number),
                }
            )
            data_to_send = "%" + str(len(data_to_send)) + data_to_send
            socket_conn.send(data_to_send.encode())
    socket_conn.shutdown(1)


def getInputStreamMN(lock):
    global frame_heap, exit_code
    i = 0
    # loop over the frames from the video stream
    while True:
        # grab the frame from the threaded video stream and resize it
        # to have a maximum width of 400 pixels
        # frame = vs.read()
        ret, frame = cap.read()
        print(i)

        # Terminate if frame is None
        if frame is None:
            break

        if i % 1 == 0:

            # detect faces in the frame and determine if they are wearing a
            # face mask or not
            (locs, preds) = detect_and_predict_mask(frame, faceNet, maskNet)

            # loop over the detected face locations and their corresponding
            # locations
            for (box, pred) in zip(locs, preds):
                # unpack the bounding box and predictions
                (startX, startY, endX, endY) = box
                (mask, withoutMask) = pred

                # determine the class label and color we'll use to draw
                # the bounding box and text
                label = "Mask" if mask > withoutMask else "No Mask"
                # color = (0, 255, 0) if label == "Mask" else (0, 0, 255)
                expansion = 10
                only_face_color = frame[
                    startY - expansion : endY + expansion,
                    startX - expansion : endX + expansion,
                ]

                lock.acquire()
                frame_heap.append([label, only_face_color])
                lock.release()

        i += 1

        cv2.imshow("Frame", frame)
        # show the output frame
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

        if exit_code:
            break

    lock.acquire()
    frame_heap.append(None)
    lock.release()

    # do a bit of cleanup
    stop_conn.close()
    cv2.destroyAllWindows()

    print("Finished!!!")


if __name__ == "__main__":
    dir_ = getParentDirectory(0)
    HOST = "127.0.0.1"  # The server's hostname or IP address
    PORT = 5001  # The port used by the server

    # load our serialized face detector model from disk
    prototxtPath = dir_ + r"\face_detector\deploy.prototxt"
    weightsPath = dir_ + r"\face_detector\res10_300x300_ssd_iter_140000.caffemodel"
    faceNet = cv2.dnn.readNet(prototxtPath, weightsPath)

    # load the face mask detector model from disk
    maskNet = load_model(
        dir_ + r"\mask_detector.model",
        compile=False,
    )

    # initialize the video stream
    print("[INFO] starting video stream...")
    # cap = VideoStream(src=0).start()
    cap = cv2.VideoCapture(grandparentDir + r"\mmsk.mp4")
    output_path = grandparentDir + r"\output\\"
    socket_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_conn.connect((HOST, PORT))

    lock = Lock()
    # Frame Collection -> Shared by both threads
    frame_heap = deque()
    frame_number = 0

    # Check stop
    exit_code = 0
    stop_conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    task1 = Thread(target=getInputStreamMN, args=(lock,))
    task2 = Thread(target=saveAndSendTask, args=(lock,))
    task3 = Thread(target=checkStopSignal, args=())

    task1.start()
    task2.start()
    task3.start()

    task1.join()
    task2.join()
    task3.join()