import face_recognition, cv2


def detect(path):
    l = {}
    for i in range(0, 60):
        img = cv2.imread(path + str(i) + ".png")
        print(i)
        cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if len(face_recognition.face_encodings(img)) != 0:
            l[i] = True
        else:
            l[i] = False

    return l


def main():
    path = "E:/Capstone/Implementation/output/nmsk/"
    path1 = "E:/Capstone/Implementation/output/nmsk/1.png"
    path2 = "E:/Capstone/Implementation/output/nmsk/27.png"
    path3 = "E:/Capstone/Implementation/test.png"
    i1 = cv2.imread(path1)
    i2 = cv2.imread(path2)
    i3 = cv2.imread(path3)
    # print(i3)
    # cv2.resize(i1, (0, 0), None, 0.25, 0.25)
    # cv2.resize(i2, (0, 0), None, 0.25, 0.25)
    # cv2.resize(i3, (0, 0), None, 0.25, 0.25)
    cv2.cvtColor(i1, cv2.COLOR_BGR2GRAY)
    cv2.cvtColor(i2, cv2.COLOR_BGR2GRAY)
    cv2.cvtColor(i3, cv2.COLOR_BGR2GRAY)
    # print(face_recognition.face_encodings(i1))
    # print(face_recognition.face_encodings(i2))
    encode1 = face_recognition.face_encodings(i1)[0]
    encode2 = face_recognition.face_encodings(i2)[0]
    encode3 = face_recognition.face_encodings(i3)[0]

    # l = detect(path)
    l = {
        0: False,
        1: True,
        2: True,
        3: True,
        4: True,
        5: True,
        6: False,
        7: True,
        8: True,
        9: True,
        10: False,
        11: True,
        12: True,
        13: True,
        14: True,
        15: True,
        16: False,
        17: False,
        18: True,
        19: True,
        20: True,
        21: True,
        22: True,
        23: True,
        24: True,
        25: True,
        26: True,
        27: True,
        28: True,
        29: True,
        30: True,
        31: True,
        32: True,
        33: True,
        34: True,
        35: True,
        36: True,
        37: True,
        38: True,
        39: True,
        40: True,
        41: True,
        42: True,
        43: True,
        44: True,
        45: True,
        46: True,
        47: True,
        48: True,
        49: True,
        50: True,
        51: True,
        52: True,
        53: True,
        54: True,
        55: True,
        56: True,
        57: True,
        58: True,
        59: True,
    }
    s = {}
    for k in l.keys():
        if not l[k]:
            continue
        print(k)
        x = cv2.imread(path + str(k) + ".png")
        cv2.cvtColor(x, cv2.COLOR_BGR2GRAY)
        encode2 = face_recognition.face_encodings(x)[0]
        res = face_recognition.compare_faces([encode1], encode2)
        s[k] = res
    print(s)

    return


# {0: False, 1: True, 2: True, 3: True, 4: True, 5: True, 6: False, 7: True, 8: True, 9: True, 10: False, 11: True, 12: True, 13: True, 14: True, 15: True, 16: False, 17: False, 18: True, 19: True, 20: True, 21: True, 22: True, 23: True, 24: True, 25: True, 26: True, 27: True, 28: True, 29: True, 30: True, 31: True, 32: True, 33: True, 34: True, 35: True, 36: True, 37: True, 38: True, 39: True, 40: True, 41: True, 42: True, 43: True, 44: True, 45: True, 46: True, 47: True, 48: True, 49: True, 50: True, 51: True, 52: True, 53: True, 54: True, 55: True, 56: True, 57: True, 58: True, 59: True}

if __name__ == "__main__":
    main()
