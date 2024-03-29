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
import base64
import requests

print("MobileNet Algorithm started")
print("_" * 100)

k = 0
# s3 = boto3.resource(
#     service_name='s3',
#     region_name='us-east-1',
#     aws_access_key_id='AKIARN4QT2VHYCU5XH7P',
#     aws_secret_access_key='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'
# )
def uploadOnAws(picname):
        global k
        k += 1
#     s3.Bucket('frames-from-the-edge').upload_file(Filename='images'picname, Key=str(k) + '.jpg')
#     print("done")
    
        with open(picname, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())

        response = requests.post('https://w1vz8j0cqk.execute-api.us-east-1.amazonaws.com/prod/demo-lambda',json={'name':'dumped/' + str(k) + '.jpg','file':encoded_string.decode()})
        print(response.json())


def getParentDirectory(levels):
    cur = os.path.dirname(__file__)
    for _ in range(0, levels):
        cur = os.path.dirname(cur)
    return os.path.realpath(cur)


grandparentDir = getParentDirectory(2)
sys.path.append(grandparentDir)

from database import Database
from faceClustering import *


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


def outputDecorator(label):
    # include the probability in the label
    label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)

    # display the label and bounding box rectangle on the output
    # frame
    cv2.putText(
        frame,
        label,
        (startX, startY - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        color,
        2,
    )
    cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)


def saveFrameThread(fcOb, dbOb, picname, label, permission, frame):
    if permission or fcOb.addFrame(frame):
        # print("inside")
        cv2.imwrite(picname, frame)
        if label == "No Mask":
            dbOb.saveImageDb(frame, 0)
            uploadOnAws(picname)
        else:
            print("db 1")
            dbOb.saveImageDb(frame, 1)


import socket


if __name__ == "__main__":
    dir_ = getParentDirectory(0)
    # HOST = "127.0.0.1"  # The server's hostname or IP address
    # PORT = 65432  # The port used by the server

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
    fcOb = faceClustering()
    dbOb = Database()
    # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.connect((HOST, PORT))

    i = 0
    # loop over the frames from the video stream
    while True:
        # grab the frame from the threaded video stream and resize it
        # to have a maximum width of 400 pixels
        # frame = vs.read()
        ret, frame = cap.read()
        # print(i)

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
                color = (0, 255, 0) if label == "Mask" else (0, 0, 255)
                expansion = 10
                only_face_color = frame[
                    startY - expansion : endY + expansion,
                    startX - expansion : endX + expansion,
                ]
                if label == "No Mask":
                    picname = output_path + r"nmsk\\" + str(i) + ".png"
                    # thread here
                    # GIL - Global Interpreter Lock - One thread at a time
                    # Can't use threads
                    permission = False
                else:
                    picname = output_path + "mmsk\\" + str(i) + ".png"
                    permission = True

                # s.sendall(json.dumps(only_face_color.tolist()).encode() + b"|")
                args = [fcOb, dbOb, picname, label, permission, only_face_color]
                saveFrameThread(*args)

            # Experiment :
            # print(type(only_face_color))
            # args = [
            #     picname,
            #     permission,
            #     only_face_color.tolist(),
            # ]
            # args = json.dumps(args)
            # res = subprocess.Popen(
            #     ["python ", grandparentDir + r"\faceClusteringProgram.py"],
            #     close_fds=True,
            #     stdin=subprocess.PIPE,
            #     stdout=subprocess.PIPE,
            # )
            # res.stdin.write(b"hello")
            # output = res.communicate()[0]
            # res.stdin.close()

        i += 1

        # outputDecorator(label)
        # show the output frame
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

    # do a bit of cleanup
    cv2.destroyAllWindows()
    # cap.stop()
