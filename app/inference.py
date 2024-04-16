import os
import queue
import sys
import threading
import time
from datetime import datetime, timedelta

import cv2
from config import RTSP_URL
from fastai.vision.all import load_learner
from log import get_logger
from PIL import Image

LOGGER = get_logger("inference.log")


class PoopinDetector:
    def __init__(self, model, debug) -> None:
        self.q = queue.Queue()
        self.debug = debug
        self.motion_frames = 0
        self.model = model
        self.pooping_frame_count = 0
        self.pooping_frame_threshold = 8
        self.empty_queue_count = 0
        self.start_time = datetime.now()
        self.term = False  # Flag for receive_frames thread to check for termination.

    def get_time(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    def _log(self, msg: str, err: bool = False):
        if self.debug:
            print(msg)
        else:
            LOGGER.error(msg) if err else LOGGER.info(msg)

    def should_terminate(self):
        """
        We terminate the detector after a positive alert, to many motion frames,
        or just after 5 min to avoid issues with stream breaking
        """
        if self.term:
            self._log("Early termination")
            return True

        if self.empty_queue_count > 1000:
            self._log("Terminated due to empty queue")
            self.term = True
            return True

        if self.motion_frames >= 1000:
            self._log("Terminated due to motion frames")
            self.term = True
            return True

        if (datetime.now() - self.start_time) > timedelta(minutes=5):
            self._log("Terminated due to time limit")
            self.term = True
            return True

    def format_frame(self, frame):
        return Image.fromarray(frame).resize((244, 244))

    def save_frame(self, frame, poopin=False):
        "Save frame of motion detected"
        cv2.imwrite(
            f"{os.getcwd()}/img/{'poopin' if poopin else 'not_poopin'}/{self.get_time()}.png",
            frame,
        )

    def crop_frame(self, frame, bbox, pad=120):
        "Crop the frame based on the bounding box cords. Add some padding for good measure"
        x, y, w, h = bbox
        x_pad = max(0, x - pad)
        y_pad = max(0, y - pad)
        w_pad = min(frame.shape[1] - x_pad, w + 2 * pad)
        h_pad = min(frame.shape[0] - y_pad, h + 2 * pad)
        return frame[y_pad : y_pad + h_pad, x_pad : x_pad + w_pad]

    def receive_frames(self):
        "Dump frames into queue"
        self._log("Starting receive frames thread")
        cap = cv2.VideoCapture(RTSP_URL)
        ret, frame = cap.read()
        self.q.put(frame)
        while ret:
            if self.term:
                break
            ret, frame = cap.read()
            if not ret:
                cap = cv2.VideoCapture()
            self.q.put(frame)
        self._log("Breaking receive frames thread")
        self.term = True

    def predict_frame(self, frame):
        """
        One positive frame should not trigger the alert, there can be false positives.
        So we try a hacky 'average' technique. Positive frame increments by 2, negative frame decrements by 1.
        """
        pred = self.model.predict(self.format_frame(frame))
        self._log(pred)
        if pred[0] == "pooping":
            self.pooping_frame_count += 2
            self.save_frame(frame, poopin=True)
            if self.pooping_frame_count >= self.pooping_frame_threshold:
                os.system("afplay poopin_alert.m4a")
                self.term = True
                return
        else:
            self.pooping_frame_count -= 1

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
                x, y, w, h = cv2.boundingRect(largest_contour)
                motion_frame = self.crop_frame(current_frame, (x, y, w, h))
                self.motion_frames += 1
                return motion_frame

    def read_frames(self):
        try:
            sleep_count = 0
            while self.q.empty():
                self._log("No frames in queue")
                time.sleep(1)  # Wait from some frames to show up in queue
                sleep_count += 1
                if sleep_count >= 20:
                    self.term = True
                    return

            self._log("Starting read frames thread")
            empty_queue_count = 0
            frame = self.q.get()
            first_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            while True:
                if self.should_terminate():
                    break
                if self.q.empty():
                    empty_queue_count += 1
                    continue
                frame = self.q.get()
                if (motion_frame := self.detect_motion(first_frame, frame)) is not None:
                    self.predict_frame(motion_frame)
            self._log("Breaking read frames thread")
        except Exception as e:
            self._log(str(e), err=True)
            self.term = True

    def run(self):
        """
        One thread will read frames into queue,
        another will process them.
        Refs: https://stackoverflow.com/questions/49233433/opencv-read-errorh264-0x8f915e0-error-while-decoding-mb-53-20-bytestream
        """
        receive_frames_thread = threading.Thread(target=self.receive_frames)
        receive_frames_thread.start()
        self.read_frames()
        receive_frames_thread.join()


if __name__ == "__main__":
    # Write process_id to to file so we can terminate the process on shutdown.
    with open("inference.pid", "+w") as f:
        f.write(str(os.getpid()))

    debug = len(sys.argv) > 1

    model = load_learner("dog_be_pooping.pkl")

    # The way we detect motion is by comparing the first frame too all subsequent frames.
    # However, this causes the potential situation where something is changed in the cam frame,
    # (Like furniture being moved), to give false positive for movement in all subsequent frames.
    # To combat this, we run in a loop. After a few positive movement frames, we re-init the detector
    # so the first frame is reset. Kinda hacky, but seams to work.
    while True:
        print("Creating new detector instance") if debug else LOGGER.info(
            "Creating new detector instance"
        )
        PoopinDetector(model=model, debug=debug).run()
