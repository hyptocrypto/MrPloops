import os
from PIL import Image
from fastai.vision.all import load_learner
from config import RTSP_URL
import cv2


learn = load_learner("dog_be_pooping.pkl")


def process_frame(frame):
    img = Image.fromarray(frame)
    return img.resize((224, 224))


def read_frames():
    cap = cv2.VideoCapture(RTSP_URL)
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            pred = learn.predict(process_frame(frame))
            print(pred)
        if pred[0] == "pooping":
            os.system("afplay poopin_alert.m4a")


read_frames()
