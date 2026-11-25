import math
import time

WRIST = 0
THUMB = (1, 2, 3, 4)
FINGERS = {
    "index": (5, 6, 7, 8),
    "middle": (9, 10, 11, 12),
    "ring": (13, 14, 15, 16),
    "pinky": (17, 18, 19, 20),
}

GESTURE_TO_MODE = {
    "open_palm": "STOP",
    "fist": "CROUCH",
    "point": "FOLLOW",
    "peace": "FAST FOLLOW",
    "three": "FREE ROAM",
    "rock": "DANCE",
    "shaka": "TRANSPORT",
    "ok": "STAND",
    "thumbs_up": "RAISE",
    "thumbs_down": "LOWER",
}

# RAISE/LOWER nudge the body height and repeat while held; everything else switches mode once.
REPEATING = {"thumbs_up", "thumbs_down"}
HOLD_S = {"open_palm": 0.2}
DEFAULT_HOLD_S = 0.6
REPEAT_S = 0.5


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _dist(a, b):
    return math.dist(a, b)


def _angle(a, b, c):
    u, v = _sub(a, b), _sub(c, b)
    nu, nv = math.hypot(*u), math.hypot(*v)
    if nu == 0 or nv == 0:
        return 180.0
    cos = sum(x * y for x, y in zip(u, v)) / (nu * nv)
    return math.degrees(math.acos(max(-1.0, min(1.0, cos))))


def finger_states(pts):
    palm = _dist(pts[WRIST], pts[9])
    states = {}
    for name, (mcp, pip, dip, tip) in FINGERS.items():
        straight = _angle(pts[mcp], pts[pip], pts[tip]) > 150
        reaching = _dist(pts[WRIST], pts[tip]) > _dist(pts[WRIST], pts[pip]) * 1.1
        states[name] = straight and reaching
    cmc, mcp, ip, tip = THUMB
    thumb_straight = _angle(pts[mcp], pts[ip], pts[tip]) > 145
    thumb_out = _dist(pts[tip], pts[5]) > palm * 0.55
    states["thumb"] = thumb_straight and thumb_out
    return states, palm


def classify(pts):
    """pts: 21 (x, y, z) points in a y-down frame (MediaPipe world landmarks)."""
    s, palm = finger_states(pts)
    four = (s["index"], s["middle"], s["ring"], s["pinky"])

    if _dist(pts[4], pts[8]) < palm * 0.35 and s["middle"] and s["ring"] and s["pinky"]:
        return "ok", s

    if s["thumb"] and not any(four):
        v = _sub(pts[4], pts[2])
        n = math.hypot(*v)
        if v[1] < -0.6 * n:
            return "thumbs_up", s
        if v[1] > 0.6 * n:
            return "thumbs_down", s

    patterns = {
        (True, True, True, True): "open_palm" if s["thumb"] else None,
        (False, False, False, False): None if s["thumb"] else "fist",
        (True, False, False, False): "point",
        (True, True, False, False): "peace",
        (True, True, True, False): "three",
        (True, False, False, True): "rock",
        (False, False, False, True): "shaka" if s["thumb"] else None,
    }
    return patterns.get(four), s


class GestureLatch:
    """Turns a noisy per-frame gesture into deliberate commands: it has to be held steady first."""

    def __init__(self):
        self.current = None
        self.since = 0.0
        self.fired_at = None

    def update(self, gesture, now=None):
        now = time.monotonic() if now is None else now
        if gesture != self.current:
            self.current, self.since, self.fired_at = gesture, now, None
            return None, 0.0
        if gesture is None:
            return None, 0.0

        hold = HOLD_S.get(gesture, DEFAULT_HOLD_S)
        held = now - self.since
        if self.fired_at is None:
            if held >= hold:
                self.fired_at = now
                return gesture, 1.0
            return None, held / hold
        if gesture in REPEATING and now - self.fired_at >= REPEAT_S:
            self.fired_at = now
            return gesture, 1.0
        return None, 1.0
