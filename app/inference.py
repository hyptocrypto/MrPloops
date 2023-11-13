import numpy as np
from datetime import datetime, timedelta
import time
import os
import cv2
import time
from log import get_logger
from fastai.vision.all import load_learner
from PIL import Image

LOGGER = get_logger("inference.log")


class PoopinDetector:
    def __init__(self, model) -> None:
        self.model = model
        self.pooping_frame_count = 0
        self.pooping_frame_threshold = 3
        self.motion_frame_count = 0
        self.motion_frame_threshold = 50
        self.first_frame = self.get_frame()

    def get_time(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    def should_terminate(self):
        """
        We terminate the detector after a positive alert or to many motion frames,
        or just after 5 min to avoid issues with stream breaking
        """

        if (
            self.motion_frames >= 50
            or self.pooping_frame_count >= self.pooping_frame_threshold
            or (datetime.now() - self.start_time) > timedelta(minutes=5)
        ):
            print("term")
            return True

    def get_frame(self) -> np.array:
        return np.array(Image.open("img.jpg"))

    def format_frame(self, frame: Image.Image):
        return frame.resize((244, 244))

    def save_frame(self, frame, poopin=False):
        "Save frame of motion detected"
        cv2.imwrite(
            f"{os.getcwd()}/img/{'poopin' if poopin else 'not_poopin'}/{self.get_time()}.png",
            frame,
        )

    def crop_frame(self, frame, bbox, pad=80):
        "Crop the frame based on the bounding box cords. Add some padding for good measure"
        x, y, w, h = bbox
        x_pad = max(0, x - pad)
        y_pad = max(0, y - pad)
        w_pad = min(frame.shape[1] - x_pad, w + 2 * pad)
        h_pad = min(frame.shape[0] - y_pad, h + 2 * pad)
        return frame[y_pad : y_pad + h_pad, x_pad : x_pad + w_pad]

    def predict_frame(self, frame):
        pred = self.model.predict(self.format_frame(frame))
        if pred[0] == "pooping":
            print("Poopin")
            self.pooping_frame_count += 1
            if self.pooping_frame_count >= self.pooping_frame_threshold:
                os.system("afplay poopin_alert.m4a")
                self.save_frame(frame, poopin=True)
                return
        else:
            self.pooping_frame_count -= 1
        # print("Not pooping")
        # self.save_frame(frame)

    def detect_motion(self):
        "Use some grey scale diff to calculate motion/diff from first frame."
        current_frame = self.get_frame()
        frame_diff = cv2.absdiff(
            cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY),
            cv2.cvtColor(self.first_frame, cv2.COLOR_BGR2GRAY),
        )
        _, thresh = cv2.threshold(frame_diff, 70, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, None, iterations=3)
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest_contour) > 900:
                x, y, w, h = cv2.boundingRect(largest_contour)
                motion_frame = self.crop_frame(current_frame, (x, y, w, h))
                self.motion_frames += 1
                return motion_frame

    def read_frames(self):
        # Get first frame in greyscale
        # WE do this so we can compare to subsequent frames to determine movement
        time.sleep(5)  # Wait from some frames to show up in queue
        print("Starting read_frames thread")
        if self.q.empty() != True:
            frame = self.q.get()
            first_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            while True:
                if self.should_terminate():
                    break
                frame = self.q.get()
                if (motion_frame := self.detect_motion(first_frame, frame)) is not None:
                    self.predict_frame(motion_frame)
        else:
            print("No frames in queue")

    def run(self):
        while True:
            if (motion_frame := self.detect_motion()) is not None:
                self.predict_frame(motion_frame)


if __name__ == "__main__":
    # Write process_id to to file so we can terminate the process on shutdown.
    with open("motion.pid", "+w") as f:
        f.write(str(os.getpid()))

    model = load_learner("dog_be_pooping.pkl")
    d = PoopinDetector(model=model)
    d.run()
