import time
import os
from config import RTSP_URL
from flask import Flask, render_template, Response
import cv2
import time
import queue
import threading

q = queue.Queue()

app = Flask(__name__)


def save_frame(frame, bbox):
    t = time.time()
    d = os.getcwd()
    frame_name = f"{d}/motion/img/frame_{t}.png"
    bbox_name = f"{d}/motion/bbox/bbox_{t}.txt"
    with open(bbox_name, "w+") as f:
        f.write(",".join(map(str, bbox)))
    cv2.imwrite(frame_name, frame)


def ReceiveFrames():
    cap = cv2.VideoCapture(RTSP_URL)
    ret, frame = cap.read()
    q.put(frame)
    while ret:
        ret, frame = cap.read()
        q.put(frame)


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


def generate_frames():
    # Get first frame in greyscale
    # WE do this so we can compare to subsequent frames to determine movement
    if q.empty() != True:
        frame = q.get()
        first_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        while True:
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
    return Response(
        generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


if __name__ == "__main__":
    with open("stream.pid", "+w") as f:
        f.write(str(os.getpid()))
    read_frames_thread = threading.Thread(target=ReceiveFrames)
    read_frames_thread.start()
    app.run(debug=True)
