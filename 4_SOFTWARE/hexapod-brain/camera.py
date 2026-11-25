import sys
import cv2


class Camera:
    """Webcam on the PC, the Pi camera (via Picamera2) on the robot. Both hand back BGR frames."""

    def __init__(self, index=0, width=640, height=480):
        self.picam = None
        try:
            from picamera2 import Picamera2
            self.picam = Picamera2()
            self.picam.configure(self.picam.create_video_configuration(main={"size": (width, height), "format": "RGB888"}))
            self.picam.start()
            return
        except ImportError:
            pass
        backend = cv2.CAP_DSHOW if sys.platform == "win32" else cv2.CAP_ANY
        self.cap = cv2.VideoCapture(index, backend)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        if not self.cap.isOpened():
            raise RuntimeError(f"Couldn't open camera {index}. Try --camera 1 if you have more than one.")

    def read(self):
        if self.picam:
            # Picamera2's "RGB888" is actually BGR byte order, which is what OpenCV wants.
            return self.picam.capture_array()
        ok, frame = self.cap.read()
        return frame if ok else None

    def close(self):
        if self.picam:
            self.picam.stop()
        else:
            self.cap.release()
