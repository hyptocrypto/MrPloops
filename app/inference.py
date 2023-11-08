from log import get_logger
from config import RTSP_URL
import os
from PIL import Image
from fastai.vision.all import load_learner
import cv2

LOGGER = get_logger()


class PoopinAlert:
    def __init__(self):
        self.model = load_learner("dog_be_pooping.pkl")
        self.thresh = 3
        self.count = 0

    def positive_frame(self):
        self.count += 1

    def negative_frame(self):
        self.count = 0

    def format_frame(self, frame):
        return Image.fromarray(frame).resize((224, 224))

    def read_frames(self):
        cap = cv2.VideoCapture(RTSP_URL)
        while True:
            success, frame = cap.read()
            if not success:
                print("Error reading frame")
                break
            if ret := self.process_frame(frame):
                break

    def process_frame(self, frame):
        pred = self.model.predict(self.format_frame(frame))
        LOGGER.info(pred)
        if pred[0] == "pooping":
            self.positive_frame()
        else:
            self.negative_frame()

        if self.count >= self.thresh:
            os.system("afplay poopin_alert.m4a")
            return True
        return False


if __name__ == "__main__":
    with open("inference.pid", "+w") as f:
        f.write(str(os.getpid()))
    while True:
        alert = PoopinAlert()
        alert.read_frames()
        del alert
