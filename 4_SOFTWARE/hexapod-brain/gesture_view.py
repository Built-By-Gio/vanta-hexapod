import argparse
import time
import urllib.request
from collections import deque
from pathlib import Path

import cv2
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions, vision

from camera import Camera
from gestures import GESTURE_TO_MODE, GestureLatch, classify

MODEL = Path(__file__).parent / "models" / "hand_landmarker.task"
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"

BONES = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7), (7, 8), (5, 9), (9, 10), (10, 11), (11, 12),
         (9, 13), (13, 14), (14, 15), (15, 16), (13, 17), (0, 17), (17, 18), (18, 19), (19, 20)]
AMBER = (0, 170, 255)
INK = (228, 230, 232)
DIM = (120, 124, 128)
RED = (60, 60, 230)
FONT = cv2.FONT_HERSHEY_DUPLEX
LEGEND = [("open_palm", "open palm"), ("fist", "fist"), ("point", "index up"), ("peace", "peace"),
          ("three", "3 fingers"), ("rock", "rock"), ("shaka", "shaka"), ("ok", "OK"),
          ("thumbs_up", "thumb up"), ("thumbs_down", "thumb down")]


def ensure_model():
    if not MODEL.exists():
        MODEL.parent.mkdir(exist_ok=True)
        print("Downloading hand model (~8MB)...")
        urllib.request.urlretrieve(MODEL_URL, MODEL)


def shade(img, x0, y0, x1, y1, alpha=0.55):
    roi = img[y0:y1, x0:x1]
    roi[:] = (roi * (1 - alpha)).astype(roi.dtype)


def text(img, s, org, scale=0.5, color=INK, thick=1):
    cv2.putText(img, s, org, FONT, scale, color, thick, cv2.LINE_AA)


def draw(frame, lm, gesture, progress, state, fps, log):
    h, w = frame.shape[:2]
    if lm:
        pts = [(int(p.x * w), int(p.y * h)) for p in lm]
        for a, b in BONES:
            cv2.line(frame, pts[a], pts[b], INK, 2, cv2.LINE_AA)
        for p in pts:
            cv2.circle(frame, p, 4, AMBER, -1, cv2.LINE_AA)

    shade(frame, 0, 0, w, 58)
    text(frame, "MODE", (14, 20), 0.42, DIM)
    text(frame, state["mode"], (14, 48), 0.95, RED if state["mode"] == "STOP" else AMBER, 2)
    text(frame, f"{fps:4.1f} fps", (w - 92, 22), 0.45, DIM)
    text(frame, f"height {state['height']}%", (w - 128, 46), 0.45, INK)

    lx = w - 232
    shade(frame, lx, 66, w - 8, 66 + 24 * len(LEGEND) + 10)
    for i, (g, name) in enumerate(LEGEND):
        y = 88 + i * 24
        live = g == gesture
        text(frame, name, (lx + 10, y), 0.45, INK if live else DIM)
        text(frame, GESTURE_TO_MODE[g], (lx + 108, y), 0.45, AMBER if live else DIM)
        if live and progress < 1.0:
            cv2.rectangle(frame, (lx + 10, y + 5), (lx + 10 + int(206 * progress), y + 8), AMBER, -1)

    shade(frame, 0, h - 64, w, h)
    bits = state.get("bits") or {}
    for i, k in enumerate(("thumb", "index", "middle", "ring", "pinky")):
        on = bits.get(k, False)
        x = 14 + i * 34
        cv2.rectangle(frame, (x, h - 50), (x + 26, h - 26), AMBER if on else DIM, -1 if on else 1)
        text(frame, k[0].upper(), (x + 7, h - 32), 0.5, (20, 20, 20) if on else DIM)
    seen = gesture.replace("_", " ") if gesture else ("no gesture" if lm else "no hand")
    text(frame, seen, (14, h - 8), 0.45, INK if gesture else DIM)
    for i, line in enumerate(reversed(log)):
        text(frame, line, (200, h - 44 + i * 16), 0.42, INK if i == 0 else DIM)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--camera", type=int, default=0)
    ap.add_argument("--no-mirror", action="store_true")
    args = ap.parse_args()

    ensure_model()
    landmarker = vision.HandLandmarker.create_from_options(vision.HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(MODEL)),
        running_mode=vision.RunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=0.6,
        min_hand_presence_confidence=0.6,
        min_tracking_confidence=0.5,
    ))
    cam = Camera(args.camera)
    latch = GestureLatch()
    state = {"mode": "STAND", "height": 50, "bits": None}
    log = deque(maxlen=3)
    t0, last, fps = time.monotonic(), time.monotonic(), 0.0

    while True:
        frame = cam.read()
        if frame is None:
            break
        if not args.no_mirror:
            frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = landmarker.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), int((time.monotonic() - t0) * 1000))

        lm, gesture = None, None
        if res.hand_landmarks:
            lm = res.hand_landmarks[0]
            world = [(p.x, p.y, p.z) for p in res.hand_world_landmarks[0]]
            gesture, state["bits"] = classify(world)
        else:
            state["bits"] = None

        fired, progress = latch.update(gesture)
        if fired:
            cmd = GESTURE_TO_MODE[fired]
            if cmd == "RAISE":
                state["height"] = min(100, state["height"] + 10)
            elif cmd == "LOWER":
                state["height"] = max(0, state["height"] - 10)
            else:
                state["mode"] = cmd
            log.append(f"{time.strftime('%H:%M:%S')}  {fired.replace('_', ' ')} -> {cmd}")

        now = time.monotonic()
        fps = 0.9 * fps + 0.1 / max(now - last, 1e-3)
        last = now
        draw(frame, lm, gesture, progress, state, fps, log)
        cv2.imshow("hexapod gestures  (q to quit)", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cam.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
