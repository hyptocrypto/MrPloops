import os
from config import RTSP_URL
from flask import Flask, render_template, Response
import cv2


app = Flask(__name__)


def detect_motion(first_frame, current_frame):
    frame_diff = cv2.absdiff(
        cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY), first_frame
    )
    _, thresh = cv2.threshold(frame_diff, 50, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        if cv2.contourArea(contour) < 500:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(current_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)


def generate_frames():
    cap = cv2.VideoCapture(RTSP_URL)
    # Get first frame in greyscale
    # WE do this so we can compare to subsequent frames to determine movement
    _, first_frame = cap.read()
    first_frame = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)
    while True:
        success, frame = cap.read()

        if not success:
            break
        else:
            ret, buffer = cv2.imencode(".jpg", frame)
            if not ret:
                continue
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
        )


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
    app.run(debug=True)
