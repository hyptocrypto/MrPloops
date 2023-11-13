import cv2
import numpy as np
import sys

# Read video properties
width, height = 1920, 1080  # Set to your desired frame size
channels = 3  # RGB

# Define buffer to store video frames
frame_buffer_size = width * height * channels
frame_buffer = np.zeros((height, width, channels), dtype=np.uint8)

try:
    while True:
        # Read a frame from the standard input
        raw_frame = sys.stdin.buffer.read(frame_buffer_size)

        if not raw_frame:
            break

        # Convert raw frame to NumPy array
        frame_buffer = np.frombuffer(raw_frame, dtype=np.uint8).reshape(
            (height, width, channels)
        )

        # Process the frame (you can replace this with your own logic)
        processed_frame = cv2.cvtColor(frame_buffer, cv2.COLOR_RGB2BGR)
        cv2.imshow("Video", processed_frame)
        if cv2.waitKey(25) & 0xFF == ord("q"):
            break

except KeyboardInterrupt:
    pass

finally:
    # Cleanup
    cv2.destroyAllWindows()
