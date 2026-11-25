import argparse
import json
import math
import signal
import socket
import threading
import time
import webbrowser
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import cv2

from gestures import GESTURE_TO_MODE, GestureLatch, classify
from robot.controller import Robot

SIM_DIR = Path(__file__).parent / "sim"
WEB_DIR = Path(__file__).parent / "web"
MODES = set(GESTURE_TO_MODE.values())

lock = threading.Lock()
robot_lock = threading.Lock()
shared = {"state": {}, "jpeg": None, "keys": deque(), "no_camera": False}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _send(self, body, ctype):
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/":
            self._send((SIM_DIR / "index.html").read_bytes(), "text/html; charset=utf-8")
        elif url.path == "/control":
            self._send((WEB_DIR / "control.html").read_bytes(), "text/html; charset=utf-8")
        elif url.path == "/rig.json":
            self._send((SIM_DIR / "rig.json").read_bytes(), "application/json")
        elif url.path == "/hexapod.glb":
            self._send((SIM_DIR / "hexapod.glb").read_bytes(), "model/gltf-binary")
        elif url.path == "/cmd":
            q = parse_qs(url.query)
            g, m = q.get("g", [""])[0], q.get("m", [""])[0]
            with lock:
                if g in GESTURE_TO_MODE:
                    shared["keys"].append(("key", GESTURE_TO_MODE[g]))
                elif m in MODES:
                    shared["keys"].append(("web", m))
            self._send(b"ok", "text/plain")
        elif url.path == "/state":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            try:
                while True:
                    with lock:
                        msg = json.dumps(shared["state"])
                    self.wfile.write(f"data: {msg}\n\n".encode())
                    self.wfile.flush()
                    time.sleep(1 / 30)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                pass
        elif url.path == "/cam.mjpg":
            if shared["no_camera"]:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
            self.end_headers()
            try:
                while True:
                    with lock:
                        jpg = shared["jpeg"]
                    if jpg:
                        self.wfile.write(b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpg + b"\r\n")
                    time.sleep(1 / 20)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                pass
        else:
            self.send_error(404)


def open_hands(camera_index):
    import mediapipe as mp
    from mediapipe.tasks.python import BaseOptions, vision
    from camera import Camera
    from gesture_view import MODEL, ensure_model

    ensure_model()
    landmarker = vision.HandLandmarker.create_from_options(vision.HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(MODEL)),
        running_mode=vision.RunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=0.6,
        min_hand_presence_confidence=0.6,
        min_tracking_confidence=0.5,
    ))
    return Camera(camera_index), landmarker, mp


def lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # No packet is sent; this just asks the OS which interface faces the network.
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def sigterm(*_):
    raise KeyboardInterrupt


def drive(robot, servos, stop, hz=50):
    """Real robot: step the controller and update the servos at a steady 50Hz, whatever the camera is doing."""
    period = 1 / hz
    last = time.monotonic()
    first = True
    while not stop.is_set():
        now = time.monotonic()
        dt, last = min(now - last, 0.1), now
        with robot_lock:
            robot.step(dt)
            joints = dict(robot.joints)
        servos.write(joints, stagger=0.3 if first else 0.0)
        first = False
        time.sleep(max(0.0, period - (time.monotonic() - now)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--camera", type=int, default=0)
    ap.add_argument("--no-camera", action="store_true", help="keyboard only")
    ap.add_argument("--no-mirror", action="store_true")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--lan", action="store_true", help="let other devices on your WiFi connect")
    ap.add_argument("--robot", action="store_true", help="on the Pi: drive the real servos (implies --lan, no browser)")
    args = ap.parse_args()
    if args.robot:
        args.lan = True
        # systemd stops the service with SIGTERM: treat it like Ctrl+C so the servos get released
        signal.signal(signal.SIGTERM, sigterm)

    shared["no_camera"] = args.no_camera
    server = ThreadingHTTPServer(("0.0.0.0" if args.lan else "127.0.0.1", args.port), Handler)
    server.daemon_threads = True
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{args.port}"
    print(f"{'Robot' if args.robot else 'Sim'} running at {url}  (Ctrl+C to quit)")
    if args.lan:
        print(f"Phone control: http://{lan_ip()}:{args.port}/control")
    if not args.robot:
        webbrowser.open(url)

    cam = landmarker = None
    if not args.no_camera:
        cam, landmarker, mp = open_hands(args.camera)
        from gesture_view import draw

    robot = Robot()
    stop = threading.Event()
    if args.robot:
        from robot.servos import Servos
        servos = Servos()
        threading.Thread(target=drive, args=(robot, servos, stop), daemon=True).start()
    latch = GestureLatch()
    log = deque(maxlen=3)
    t0 = last = time.monotonic()
    fps = 0.0

    try:
        while True:
            gesture, progress, bits = None, 0.0, None
            if cam:
                frame = cam.read()
                if frame is None:
                    break
                # the robot's camera looks at you, so its image is already the right way round
                if not args.no_mirror and not args.robot:
                    frame = cv2.flip(frame, 1)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                res = landmarker.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), int((time.monotonic() - t0) * 1000))
                lm = target = None
                if res.hand_landmarks:
                    lm = res.hand_landmarks[0]
                    gesture, bits = classify([(p.x, p.y, p.z) for p in res.hand_world_landmarks[0]])
                    cx = sum(p.x for p in lm) / len(lm)
                    size = math.dist((lm[0].x, lm[0].y), (lm[9].x, lm[9].y))
                    target = (cx, size)
                with robot_lock:
                    robot.target = target
            else:
                time.sleep(1 / 60)

            fired, progress = latch.update(gesture)
            with lock:
                keys = list(shared["keys"])
                shared["keys"].clear()
            for src, mode in ([(fired.replace("_", " "), GESTURE_TO_MODE[fired])] if fired else []) + keys:
                with robot_lock:
                    robot.command(mode)
                log.append(f"{time.strftime('%H:%M:%S')}  {src} -> {mode}")

            now = time.monotonic()
            dt = min(now - last, 0.1)
            last = now
            fps = 0.9 * fps + 0.1 / max(dt, 1e-3)
            with robot_lock:
                if not args.robot:
                    robot.step(dt)
                state = dict(mode=robot.mode, height=robot.height, gesture=gesture, progress=progress,
                             pose=robot.pose(), joints=dict(robot.joints), warnings=robot.warnings,
                             speed=round(math.hypot(robot.v[0], robot.v[1])), turn=round(math.degrees(robot.v[2])),
                             hand=robot.target is not None, log=list(log), fps=round(fps, 1))
            jpg = None
            if cam:
                draw(frame, lm, gesture, progress, dict(mode=robot.mode, height=robot.height, bits=bits), fps, log)
                small = cv2.resize(frame, (480, int(480 * frame.shape[0] / frame.shape[1])))
                jpg = cv2.imencode(".jpg", small, [cv2.IMWRITE_JPEG_QUALITY, 70])[1].tobytes()
            with lock:
                shared["state"] = state
                if jpg:
                    shared["jpeg"] = jpg
    except KeyboardInterrupt:
        pass
    finally:
        stop.set()
        if args.robot:
            time.sleep(0.1)
            servos.release()
            print("servos released")
        if cam:
            cam.close()
        server.shutdown()


if __name__ == "__main__":
    main()
