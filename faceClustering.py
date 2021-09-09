import face_recognition, cv2


class faceClustering:
    def __init__(self):
        self._encodedFrames = []

    def check(self, res):
        # True: Unique Frame
        # False: Frame Match Found
        if res == []:
            return True
        for x in res:
            if x:
                return False
        return True

    def addFrame(self, frame):
        # True: Frame Added
        # False: Frame Discarded
        cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        encodedList = face_recognition.face_encodings(frame)
        if not encodedList:
            return False
        encoded = encodedList[0]
        res = face_recognition.compare_faces(self._encodedFrames, encoded)
        # print(res)
        if self.check(res):
            self._encodedFrames.append(encoded)
            return True
        return False


if __name__ == "__main__":
    print("Face Clustering")
