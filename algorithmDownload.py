import sys
import os

if len(sys.argv) != 2:
    print("\nUsage: python3 algorithmDownload.py algoname\n")
    print("You can choose OpenCv or MobileNet for algoname")
    exit()

arg = sys.argv[1]
algorithms = "./algorithms"
opencv = "./algorithms/OpenCv"
mobilenet = "./algorithms/MobileNet"
face_detector = mobilenet + "/face_detector"

s3 = "https://capstonealgorithms.s3.amazonaws.com/"

if arg == "OpenCv" and not os.path.isdir(opencv):
    if not os.path.isdir(algorithms):
        os.makedirs(algorithms)
    if not os.path.isdir(opencv):
        os.makedirs(opencv)
    os.system("curl " + s3 + "OpenCv/main.py > " + opencv + "/main.py")
elif arg == "MobileNet" and not os.path.isdir(mobilenet):
    if not os.path.isdir(algorithms):
        os.makedirs(algorithms)
    if not os.path.isdir(face_detector):
        os.makedirs(face_detector)
    if not os.path.isdir(mobilenet):
        os.system("mkdir " + mobilenet)

    os.system("curl " + s3 + "MobileNet/main.py > " + mobilenet + "/main.py")
    os.system(
        "curl "
        + s3
        + "MobileNet/mask_detector.model > "
        + mobilenet
        + "/mask_detector.model"
    )
    os.system(
        "curl "
        + s3
        + "MobileNet/face_detector/deploy.prototxt > "
        + face_detector
        + "/deploy.prototxt"
    )
    os.system(
        "curl "
        + s3
        + "MobileNet/face_detector/res10_300x300_ssd_iter_140000.caffemodel > "
        + face_detector
        + "/res10_300x300_ssd_iter_140000.caffemodel"
    )
