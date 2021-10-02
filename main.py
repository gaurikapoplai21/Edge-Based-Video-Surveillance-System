from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
import base64
import cv2
import subprocess
import socket
import time
from threading import Thread

from database import *


# def create_table(sql):
#     try:
#         c = conn.cursor()
#         c.execute(sql)
#         conn.commit()
#     except Exception as e:
#         print(e)


def open_file(dir):
    f = open(dir, "r")
    return f.read()


def insert_algo(algo):
    try:
        c = conn.cursor()
        c.execute(
            """INSERT INTO algorithm(algoName) 
                    VALUES(?)""",
            algo,
        )
        conn.commit()
    except Exception as e:
        print(e)


def getAlgo(id):
    try:
        c = conn.cursor()
        c.execute("""SELECT * FROM algorithm WHERE algoName = (?)""", (id,))
        return c.fetchone()
    except:
        pass


def downloadAlgo():
    print("Downloading Algorithm ... ")
    os.system("python ./algorithmDownload.py " + AlgoName)


algoProcess = None
playing = False


def start():
    global playing
    if playing:
        return
    # Normal Execution
    # cmd = "run.cmd"
    # os.system(cmd)

    playing = True
    cmd = {"args": ["cmdRun.bat"], "close_fds": True}
    process = subprocess.Popen(**cmd)


def sendStopSignal():

    HOST = "127.0.0.1"
    PORT = 6969
    Message = b"Stop"

    clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientSock.sendto(Message, (HOST, PORT))


def stop():
    global playing
    if not playing:
        return
    sendStopSignal()
    playing = False


def timedStopSignal(duration):
    if not playing:
        return
    while not expliciteStop and duration:
        duration -= 1
        time.sleep(1)
    if not playing:
        return
    print("Time up!!!")
    if not expliciteStop:
        stop()


def getAllAlgo():
    c = conn.cursor()
    c.execute("SELECT * FROM algorithm")
    algoDetails = []
    for i in c.fetchall():
        algoDetails.append(i)
    return algoDetails


def getImages(ob):
    cur = conn.cursor()
    cur.execute("SELECT * FROM face_info")
    imgs = []
    for x in cur.fetchall():
        image = ob.decode(x[1], x[2])
        _, buffer_img = cv2.imencode(".jpg", image)
        imgs.append((base64.b64encode(buffer_img).decode("utf-8"), x[3]))
    return imgs


def oneTime(ob):
    ob.make_table(
        """CREATE TABLE IF NOT EXISTS algorithm (
            id integer PRIMARY KEY AUTOINCREMENT, 
            algoName text NOT NULL
            );"""
    )
    ob.make_table(
        """CREATE TABLE IF NOT EXISTS face_info (
						id integer PRIMARY KEY AUTOINCREMENT,
						face text NOT NULL,
						shape text NOT NULL,
						mask boolean NOT NULL
					);"""
    )
    insert_algo(("OpenCv",))
    insert_algo(("MobileNet",))


app = Flask(__name__)
expliciteStop = 0


@app.route("/", methods=["POST", "GET"])
def index():
    global AlgoName
    ob = Database()
    # oneTime(ob)
    algoDetails = getAllAlgo()
    imgs = getImages(ob)
    if request.method == "GET":
        return render_template(
            "./index.html", algoDetails=algoDetails, images=imgs, algoSeleted=AlgoName
        )
    else:
        if request.form.get("start"):
            start()
            duration = request.form.get("time")
            print("Duration :", duration)
            if duration:
                hms = duration.split(":")
                extraTime = 50
                s = int(hms[0]) * 3600 + int(hms[1]) * 60 + int(hms[2]) * 1 + extraTime
                task = Thread(target=timedStopSignal, args=(s,))
                task.start()
            return redirect(url_for("index"))
        elif request.form.get("stop"):
            global expliciteStop
            expliciteStop = 1
            stop()
            return redirect(url_for("index"))
        else:
            for algo in algoDetails:
                if request.form.get(str(algo[0])):
                    AlgoName = algo[1]
                    downloadAlgo()
            print("RUNNING [INFO] :", AlgoName)
            return render_template(
                "./index.html",
                algoDetails=algoDetails,
                images=imgs,
                algoSeleted=AlgoName,
            )


if __name__ == "__main__":
    conn = sqlite3.connect(r"capstone.db", check_same_thread=False)
    AlgoName = "MobileNet"
    app.run(debug=True)
