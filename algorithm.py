from concurrent.futures.thread import ThreadPoolExecutor
from multiprocessing.pool import ThreadPool
import threading
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
import base64
import cv2
import asyncio

from tensorflow.python.keras.applications.mobilenet_v2 import MobileNetV2
from database import *
import subprocess, time


def create_table(sql):
    try:
        c = conn.cursor()
        c.execute(sql)
        conn.commit()
    except Exception as e:
        print(e)


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


def runAlgo():
    cmd = "python ./algorithms/" + AlgoName + "/main.py"
    # Normal Execution
    # os.system("python ./algorithms/" + AlgoName + "/main.py")

    # SubProcess
    algoProcess = subprocess.Popen(
        ["python ", "./algorithms/" + AlgoName + "/main.py"],
        close_fds=True,
    )

    # Threading
    # t = threading.Thread(target=os.system(cmd))
    # t.start()
    # t.join()

    # exe = ThreadPoolExecutor(2)
    # exe.submit(os.system(cmd))


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
    create_table(
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
        if request.form.get("run"):
            # asyncio.run(runAlgo())
            runAlgo()
            return redirect(url_for("index"))
        else:
            for algo in algoDetails:
                if request.form.get(str(algo[0])):
                    print("here")
                    AlgoName = algo[1]
                    downloadAlgo()
            print(AlgoName)
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
