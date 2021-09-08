import numpy as np
import cv2
import random
import sys

sys.path.append("E:\Capstone\Implementation")
from database import Database


class face_detect:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self.nose_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_mcs_nose.xml"
        )
        self.imgno = 0

    def draw(self, ob, frame):
        for (x, y, w, h) in ob:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

    def preprocessing(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return gray

    def detect_mask(self, only_face, only_face_color):
        per = 0.6
        x_ = len(only_face)
        y_ = len(only_face[0])
        mask = only_face[
            int(x_ * per) : x_ - int(x_ * 0.1), int(y_ * 0.3) : y_ - int(y_ * 0.3)
        ]
        # mask_blur = cv2.medianBlur(mask, 3)
        _, gray_thresh = cv2.threshold(mask, 100, 255, cv2.THRESH_BINARY)
        total = 0
        white = 0
        black = 0
        for i, row in enumerate(gray_thresh):
            for j, col in enumerate(row):
                total += 1
                if col == 255:
                    white += 1
                else:
                    black += 1
        print("white: ", white / total)
        print("black: ", black / total)
        if (white / total) * 100 > 99 or (black / total) * 100 > 99:
            print("Nice mask")
            cv2.imwrite(
                output_path + "mmsk/" + str(self.imgno) + ".png",
                only_face_color,
            )
            ob.saveImageDb(only_face_color, 1)
        else:
            print("No mask")
            cv2.imwrite(
                output_path + "nmsk/" + str(self.imgno) + ".png",
                only_face_color,
            )
            ob.saveImageDb(only_face_color, 0)
        self.imgno += 1
        return only_face

    def main(self, frame):
        if frame is None:
            return []

        gray = self.preprocessing(frame)

        face = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.3,
            minNeighbors=5,
            minSize=(20, 20),
            flags=cv2.CASCADE_SCALE_IMAGE,
        )

        for (x, y, w, h) in face:
            only_face = gray[y : y + h, x : x + w]
            only_face_color = frame[y : y + h, x : x + w]
            return self.detect_mask(only_face, only_face_color)
        return frame


if __name__ == "__main__":
    f = face_detect()
    ob = Database()
    cap = cv2.VideoCapture("mmsk.mp4")
    output_path = "E:/Capstone/Implementation/output/"
    while 1:
        ret, frame = cap.read()
        frame = f.main(frame)
        if len(frame):
            cv2.imshow("Mask Detection", frame)
        else:
            break
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break

cap.release()
cv2.destroyAllWindows()
