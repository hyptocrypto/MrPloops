import cv2

# RTSP URL
rtsp_url = "rtsp://192.168.1.56:8554/cam"

# Create a VideoCapture object
cap = cv2.VideoCapture(rtsp_url)

# Check if the VideoCapture object is successfully opened
if not cap.isOpened():
    print("Error: Could not open video stream.")
    exit()

try:
    while True:
        # Read a frame
        ret, frame = cap.read()

        if not ret:
            continue

        # Process the frame (you can replace this with your own logic)
        cv2.imshow("Video", frame)

        if cv2.waitKey(25) & 0xFF == ord("q"):
            break

except KeyboardInterrupt:
    pass

finally:
    # Release the VideoCapture object
    cap.release()
    cv2.destroyAllWindows()
