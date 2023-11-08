import time
import os
from config import RTSP_URL
import cv2
import time
import queue
import threading
from log import get_logger

LOGGER = get_logger("motion.log")


class MotionDetector:
    def __init__(self) -> None:
        self.q = queue.Queue()
        self.motion_frames = 0

    def should_terminate(self):
        return self.motion_frames >= 5

    def save_frame(self, frame, bbox):
        "Save frame and bbox of motion detected"
        t = time.time()
        d = os.getcwd()
        frame_name = f"{d}/motion/img/frame_{t}.png"
        bbox_name = f"{d}/motion/bbox/bbox_{t}.txt"
        LOGGER.info(f"Motion detected at {t}")
        with open(bbox_name, "w+") as f:
            f.write(",".join(map(str, bbox)))
        cv2.imwrite(frame_name, frame)

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
        _, thresh = cv2.threshold(frame_diff, 85, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, None, iterations=3)
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            if cv2.contourArea(contour) < 500:
                continue

            x, y, w, h = cv2.boundingRect(contour)
            self.save_frame(current_frame, (x, y, w, h))
            self.motion_frames += 1
            break
            # cv2.rectangle(current_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

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
