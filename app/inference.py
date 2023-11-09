from datetime import datetime, timedelta
import time
import os
from config import RTSP_URL
import cv2
import time
import queue
import threading
from log import get_logger
from fastai.vision.all import load_learner
from PIL import Image

LOGGER = get_logger("inference.log")


class PoopinDetector:
    def __init__(self, model) -> None:
        self.q = queue.Queue()
        self.motion_frames = 0
        self.model = model
        self.pooping_frame_count = 0
        self.pooping_frame_threshold = 3
        self.start_time = datetime.now()

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

    def format_frame(self, frame):
        return Image.fromarray(frame).resize((244, 244))

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

    def receive_frames(self):
        "Put every 15th frame in the queue"
        print("Starting receive frames thread")
        frame_count = 0
        frame_count_thresh = 15
        cap = cv2.VideoCapture(RTSP_URL)
        ret, frame = cap.read()
        self.q.put(frame)
        while ret:
            if self.should_terminate():
                break
            ret, frame = cap.read()
            if ret:
                if frame_count >= frame_count_thresh:
                    self.q.put(frame)
                    frame_count = 0
                else:
                    frame_count += 1

    def predict_frame(self, frame):
        pred = self.model.predict(self.format_frame(frame))
        print(pred)
        if pred[0] == "pooping":
            self.save_frame(frame, poopin=True)
            print("Poopin")
            self.pooping_frame_count += 1
            if self.pooping_frame_count >= self.pooping_frame_threshold:
                os.system("afplay poopin_alert.m4a")
                return
        print("Not pooping")
        self.save_frame(frame)

    def detect_motion(self, first_frame, current_frame):
        "Use some grey scale diff to calculate motion/diff from first frame."
        frame_diff = cv2.absdiff(
            cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY), first_frame
        )
        _, thresh = cv2.threshold(frame_diff, 70, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, None, iterations=3)
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest_contour) > 900:
                print("MOTION")
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
                print("frame")
                if (motion_frame := self.detect_motion(first_frame, frame)) is not None:
                    self.predict_frame(motion_frame)
        else:
            print("No frames in queue")

    def run(self):
        """
        One thread will read frames into queue,
        another will process them.
        Refs: https://stackoverflow.com/questions/49233433/opencv-read-errorh264-0x8f915e0-error-while-decoding-mb-53-20-bytestream
        """
        read_frames_thread = threading.Thread(target=self.receive_frames)
        process_frames_thread = threading.Thread(target=self.read_frames)
        read_frames_thread.start()
        process_frames_thread.start()
        read_frames_thread.join()
        process_frames_thread.join()


if __name__ == "__main__":
    # Write process_id to to file so we can terminate the process on shutdown.
    with open("motion.pid", "+w") as f:
        f.write(str(os.getpid()))

    model = load_learner("dog_be_pooping.pkl")

    # The way we detect motion is by comparing the first frame too all subsequent frames.
    # However, this causes the potential situation where something is changed in the cam frame,
    # (Like furniture being moved), to give false positive for movement in all subsequent frames.
    # To combat this, we run in a loop. After a few positive movement frames, we re-init the detector
    # so the first frame is reset. Kinda hacky, but seams to work.
    while True:
        print("Creating new detector instance")
        alert = PoopinDetector(model=model)
        alert.run()
