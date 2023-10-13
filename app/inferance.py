from config import RSTP_URL
import os
from PIL import Image
from fastai.vision.all import load_learner
import cv2


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
        cap = cv2.VideoCapture(RSTP_URL)
        while True:
            success, frame = cap.read()
            if not success:
                print("Error reading frame")
                break
            if ret := self.process_frame(frame):
                return

    def process_frame(self, frame):
        pred = self.model.predict(self.format_frame(frame))
        if pred[0] == "pooping":
            self.positive_frame()
        else:
            self.negative_frame()

        if self.count >= self.thresh:
            os.system("afplay poopin_alert.m4a")
            os.system("afplay poopin_alert.m4a")
            return


if __name__ == "__main__":
    while True:
        alert = PoopinAlert()
        alert.process_frame()
        del alert
