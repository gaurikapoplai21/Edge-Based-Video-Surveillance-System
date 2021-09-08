import cv2
from cv2 import data
import numpy as np
import sqlite3
import base64

# Connection
conn = sqlite3.connect(r"capstone.db", check_same_thread=False)


class Database:
    # Create a table: Generic
    def make_table(self, sql):
        try:
            c = conn.cursor()
            c.execute(sql)
            conn.commit()
        except Exception as e:
            pass

    # Stores image to table
    def store_face(self, face, shape, mask):
        try:
            c = conn.cursor()
            c.execute(
                "INSERT INTO face_info(face, shape, mask) VALUES(?,?,?)",
                (
                    face,
                    shape,
                    mask,
                ),
            )
            conn.commit()
        except Exception as e:
            pass

    # Encodes the numpy image to string image; returns : string image and shape
    def encode(self, image):
        flattened = image.flatten()
        list_flattened = flattened.tolist()
        str_flattened = str(list_flattened)
        image_shape = str(image.shape)

        return (str_flattened, image_shape)

    # Decode the encoded string image to numpy array with right shape; returns : numpy array image
    def decode(self, str_flattened, image_shape):
        flattened = list(map(int, str_flattened.strip("][").split(", ")))
        np_flattened = np.array(flattened, dtype=np.uint8)
        return np_flattened.reshape(
            tuple(map(int, image_shape.strip(")(").split(", ")))
        )

    def saveImageDb(self, image, mask):
        str_flattened, image_shape = self.encode(image)
        self.store_face(str_flattened, image_shape, mask)

    def deleteAllFaces(self):
        print("Removing all faces ... ")
        cur = conn.cursor()
        cur.execute("DELETE FROM face_info WHERE 1")
        conn.commit()


def main():
    ob = Database()

    # Make table if it doen't exist
    # ob.make_table(
    #     """CREATE TABLE IF NOT EXISTS face_info (

    # 					id integer PRIMARY KEY AUTOINCREMENT,
    # 					face text NOT NULL,
    # 					shape text NOT NULL,
    # 					mask boolean NOT NULL
    # 				);"""
    # )

    # Image store in database
    # image = cv2.imread("E:/Capstone/Implementation/check/mmsk/116.png")
    # str_flattened, image_shape = ob.encode(image)
    # ob.store_face(str_flattened, image_shape, 0)

    # Image retrieve from database
    # cur = conn.cursor()
    # cur.execute("SELECT * FROM face_info")
    # for x in cur.fetchall():
    #     image = ob.decode(x[1], x[2])
    #     cv2.imshow("Face", image)
    #     cv2.waitKey(0)
    ob.deleteAllFaces()


if __name__ == "__main__":
    main()
