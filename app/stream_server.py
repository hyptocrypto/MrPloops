import os
from config import RTSP_URL
from flask import Flask, render_template, Response
import cv2


app = Flask(__name__)


def generate_frames():
    cap = cv2.VideoCapture(RTSP_URL)
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
