import sys
from datetime import datetime, timedelta
import time
import os
from config import RTSP_URL
from flask import Flask, render_template, Response
import cv2
import time
import queue
import threading


app = Flask(__name__)


def receive_frames(q: queue.Queue, term: bool = False):
    """
    Dump frames into queue.
    This will run in background thread and self terminate after 1 min.
    Otherwise to many threads will stack up filling queues that are not being read from.
    This will result in memory depletion.
    """
    end = datetime.now() + timedelta(minutes=1)
    print("Starting receive frames thread")
    cap = cv2.VideoCapture(RTSP_URL)
    ret, frame = cap.read()
    q.put(frame)
    while ret:
        if datetime.now() > end:
            break
        if term:
            break
        ret, frame = cap.read()
        if not ret:
            cap = cv2.VideoCapture(RTSP_URL)
        q.put(frame)
    print("Breaking receive frames")


def detect_motion(first_frame, current_frame):
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
            return cv2.rectangle(current_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return current_frame


def generate_frames(q: queue.Queue):
    # Get first frame in greyscale
    # WE do this so we can compare to subsequent frames to determine movement
    if not q.empty():
        frame = q.get()
        first_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        while True:
            if not q.empty():
                frame = q.get()
                frame = detect_motion(first_frame, frame)
                ret, buffer = cv2.imencode(".jpg", frame)
                if not ret:
                    continue
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
                )

    else:
        print("Error. No frames in queue")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    q = queue.Queue()
    receive_frames_thread = threading.Thread(target=receive_frames, args=(q,))
    receive_frames_thread.start()
    while q.empty():
        time.sleep(1)
        print("Waiting for frames in queue")
    return Response(
        generate_frames(q),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


if __name__ == "__main__":
    with open("stream.pid", "+w") as f:
        f.write(str(os.getpid()))
    if len(sys.argv) > 1:
        app.run(debug=True)
    else:
        app.run(debug=True, host="0.0.0.0", port=80)
