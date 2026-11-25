import math
from gestures import classify, GestureLatch

MCP = {"index": (-0.025, -0.085, 0), "middle": (0, -0.09, 0), "ring": (0.02, -0.085, 0), "pinky": (0.038, -0.075, 0)}
SEG = {"index": (0.04, 0.025, 0.02), "middle": (0.045, 0.028, 0.02), "ring": (0.042, 0.026, 0.02), "pinky": (0.032, 0.02, 0.018)}
ORDER = ["index", "middle", "ring", "pinky"]


def finger(base, segs, curled):
    bends = (70, 100, 60) if curled else (0, 0, 0)
    pts, p, ang = [base], base, 0.0
    for L, b in zip(segs, bends):
        ang += math.radians(b)
        p = (p[0], p[1] - L * math.cos(ang), p[2] - L * math.sin(ang))
        pts.append(p)
    return pts


def hand(ext, thumb="out", pinch=False):
    pts = [(0, 0, 0)]
    if thumb == "out":
        pts += [(-0.02, -0.02, 0), (-0.045, -0.04, 0), (-0.065, -0.06, 0), (-0.082, -0.077, 0)]
    elif thumb == "up":
        pts += [(-0.02, -0.02, 0), (-0.045, -0.03, 0), (-0.07, -0.035, 0), (-0.092, -0.038, 0)]
    elif thumb == "down":
        pts += [(-0.02, -0.02, 0), (-0.035, -0.03, -0.01), (-0.04, 0.0, -0.01), (-0.045, 0.025, -0.01)]
    else:
        pts += [(-0.02, -0.02, 0), (-0.03, -0.04, -0.01), (-0.02, -0.06, -0.02), (-0.008, -0.07, -0.02)]
    for name in ORDER:
        pts += finger(MCP[name], SEG[name], not ext[name])
    if pinch:
        pts[4] = (pts[8][0] - 0.005, pts[8][1], pts[8][2])
    return pts


def rot(pts, deg, axis):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    out = []
    for x, y, z in pts:
        if axis == "z":
            out.append((c * x - s * y, s * x + c * y, z))
        else:
            out.append((c * x + s * z, y, -s * x + c * z))
    return out


def E(*names):
    return {n: n in names for n in ORDER}


def _cases():
    return [
    ("open_palm", hand(E(*ORDER), "out")),
    ("fist", hand(E(), "tucked")),
    ("point", hand(E("index"), "tucked")),
    ("peace", hand(E("index", "middle"), "tucked")),
    ("three", hand(E("index", "middle", "ring"), "tucked")),
    ("rock", hand(E("index", "pinky"), "tucked")),
    ("shaka", hand(E("pinky"), "out")),
    ("thumbs_up", rot(hand(E(), "up"), 90, "z")),
    ("thumbs_down", rot(hand(E(), "up"), -90, "z")),
    ("ok", hand({"index": False, "middle": True, "ring": True, "pinky": True}, "out", pinch=True)),
]


CASES = _cases()
fails = 0
for expect, pts in CASES:
    variants = [("upright", pts), ("tilt z+25", rot(pts, 25, "z")), ("tilt z-25", rot(pts, -25, "z")), ("turn y+40", rot(pts, 40, "y"))]
    for label, v in variants:
        got, s = classify(v)
        ok = got == expect
        fails += not ok
        print(f"{'ok ' if ok else 'BAD'} {expect:12s} {label:10s} -> {got}  {''.join('1' if s[k] else '0' for k in ('thumb', *ORDER))}")

latch = GestureLatch()
fired = [latch.update("point", t / 10)[0] for t in range(10)]
assert fired.count("point") == 1 and fired.index("point") == 6, fired
latch = GestureLatch()
fired = [latch.update("thumbs_up", t / 10)[0] for t in range(20)]
assert fired.count("thumbs_up") >= 3, fired
latch = GestureLatch()
fired = [latch.update(g, t / 10)[0] for t, g in enumerate(["point"] * 4 + ["peace"] + ["point"] * 4)]
assert "point" not in fired, fired
print("latch ok")
print("FAILS", fails)
