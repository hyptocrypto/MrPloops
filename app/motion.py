import time
import os
from config import RTSP_URL
import cv2
import time
import queue
import threading
from log import get_logger
from fastai.vision.all import load_learner

LOGGER = get_logger("motion.log")

model = load_learner("dog_be_poopin.pkl")


class MotionDetector:
    def __init__(self) -> None:
        self.q = queue.Queue()
        self.motion_frames = 0

    def should_terminate(self):
        return self.motion_frames >= 5

    def crop_frame(self, frame, bbox, pad=50):
        "Crop the frame based on the bounding box cords. Add some padding for good measure"
        x, y, w, h = bbox
        x_pad = max(0, x - pad)
        y_pad = max(0, y - pad)
        w_pad = min(frame.shape[1] - x_pad, w + 2 * pad)
        h_pad = min(frame.shape[0] - y_pad, h + 2 * pad)
        return frame[y_pad : y_pad + h_pad, x_pad : x_pad + w_pad]

    def receive_frames(self):
        "Put every 15th frame in the queue"
        frame_count = 0
        frame_count_thresh = 15
        cap = cv2.VideoCapture(RTSP_URL)
        ret, frame = cap.read()
        self.q.put(frame)
        while ret:
            if self.should_terminate():
                return
            ret, frame = cap.read()
            if frame_count >= frame_count_thresh:
                self.q.put(frame)
                frame_count = 0
            else:
                frame_count += 1

    def detect_motion(self, first_frame, current_frame):
        "Use some grey scale diff to calculate motion/diff from first frame."
        frame_diff = cv2.absdiff(
            cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY), first_frame
        )
        _, thresh = cv2.threshold(frame_diff, 65, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, None, iterations=3)
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest_contour) > 500:
                x, y, w, h = cv2.boundingRect(largest_contour)
                # DO SOME PREDICITONS instead of saving frames
                self.save_frame(current_frame, (x, y, w, h))
                self.motion_frames += 1

    def read_frames(self):
        # Get first frame in greyscale
        # WE do this so we can compare to subsequent frames to determine movement
        time.sleep(5)  # Wait from some frames to show up in queue
        if self.q.empty() != True:
            frame = self.q.get()
            first_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            while True:
                frame = self.q.get()
                self.detect_motion(first_frame, frame)
                if self.should_terminate():
                    return
        else:
            LOGGER.error("No frames in queue")

    def run(self):
        read_frames_thread = threading.Thread(target=self.receive_frames)
        process_frames_thread = threading.Thread(target=self.read_frames)
        read_frames_thread.start()
        process_frames_thread.start()
        read_frames_thread.join()
        process_frames_thread.join()


if __name__ == "__main__":
    with open("motion.pid", "+w") as f:
        f.write(str(os.getpid()))
    while True:
        print("Creating new detector instance")
        d = MotionDetector()
        d.run()
        del d
