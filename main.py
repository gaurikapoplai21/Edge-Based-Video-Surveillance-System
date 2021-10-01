from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
import base64
import cv2
import subprocess
import socket

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

    # Normal Execution
    # cmd = "run.cmd"
    # os.system(cmd)

    playing = True
    cmd = {"args": ["run.cmd"], "close_fds": True}
    process = subprocess.Popen(**cmd)


def sendStopSignal():

    HOST = "127.0.0.1"
    PORT = 50000
    Message = b"Stop"

    clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientSock.sendto(Message, (HOST, PORT))


def stop():
    # if process is None:
    #     return
    # process.terminate()
    if not playing:
        return
    sendStopSignal()
    pass


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
            return redirect(url_for("index"))
        elif request.form.get("stop"):
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
