import json
from build123d import *

PLATE_Z, PLATE_T = 21.2, 3.0
PLATE_TOP = PLATE_Z + PLATE_T
DECK_Z, DECK_T = 44.0, 3.0
DECK_TOP = DECK_Z + DECK_T
MOUNT_HOLES = [(sx * 32.63, sy * 58.0) for sx in (-1, 1) for sy in (-1, 1)]
POSTS = [(sx * 33.0, sy * 46.0) for sx in (-1, 1) for sy in (-1, 1)]
PCA_SIZE, PCA_HOLE = (62.2, 25.4), (55.9, 19.05)
PCA_CENTERS = [(0.0, -13.6), (0.0, 13.6)]
BUCK = (0.0, -42.0, 54.0, 24.0)    # moved out so the boards and their zip ties clear the PCAs
SBEC = (0.0, 43.5, 50.0, 28.0)
PI_SIZE, PI_HOLE = (56.0, 85.0), (49.0, 58.0)
PI_C = (0.0, -12.0)
PI_HOLES = [(PI_C[0] + sx * PI_HOLE[0] / 2, PI_C[1] - 85 / 2 + 3.5 + i * PI_HOLE[1]) for sx in (-1, 1) for i in (0, 1)]
CAM_Y = 60.0
CAM_SIZE, CAM_HOLES = (25.0, 24.0), (21.0, 12.5)
CAM_TILT = 12.0
CAM_DROP = 5.0          # v6: camera 5mm lower so the hull's head is lower
PCA_PLUG_ROWS = [(cy + (1 if cy > 0 else -1) * (PCA_SIZE[1] / 2 - 5)) for _, cy in PCA_CENTERS]   # servo-plug rows under the deck
INSERT_R = 2.1


def box(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def cyl(r, z0, z1, x=0, y=0):
    return Pos(x, y, (z0 + z1) / 2) * Cylinder(r, z1 - z0)


def outline_face():
    pts = json.load(open("emount_outline.json"))[:-1]
    return Polygon(*[tuple(p) for p in pts], align=None)


def zip_slots(part, cx, cy, length, width, z0, z1):
    for dx in (-length / 2 + 7, length / 2 - 7):
        for side in (-1, 1):
            y = cy + side * (width / 2 + 1.5)
            part -= box(cx + dx - 2, cx + dx + 2, y - 1.0, y + 1.0, z0 - 1, z1 + 1)
    return part


def elec_plate():
    p = Pos(0, 0, PLATE_Z) * extrude(outline_face(), amount=PLATE_T)
    for x, y in MOUNT_HOLES:
        p -= cyl(1.7, PLATE_Z - 1, PLATE_TOP + 1, x, y)
    for cx, cy in PCA_CENTERS:
        for sx in (-1, 1):
            for sy in (-1, 1):
                x, y = cx + sx * PCA_HOLE[0] / 2, cy + sy * PCA_HOLE[1] / 2
                p += cyl(3.0, PLATE_TOP - 0.1, PLATE_TOP + 5, x, y)
                p -= cyl(1.1, PLATE_TOP - 1, PLATE_TOP + 6, x, y)
    for cx, cy, l, w in (BUCK, SBEC):
        p = zip_slots(p, cx, cy, l, w, PLATE_Z, PLATE_TOP)
    for x, y in POSTS:
        p += cyl(4.5, PLATE_TOP - 0.1, DECK_Z, x, y)
        p -= cyl(INSERT_R, DECK_Z - 5, DECK_Z + 1, x, y)
    for fp in json.load(open("coxa_cap_fp.json")) + json.load(open("coxa_servo_fp.json")):
        p -= Pos(0, 0, PLATE_Z - 1) * extrude(Polygon(*[tuple(c) for c in fp[:-1]], align=None), amount=PLATE_T + 2, dir=(0, 0, 1))
    for y in (-27.5, 27.5):
        p -= box(-20, 20, y - 1.5, y + 1.5, PLATE_Z - 1, PLATE_TOP + 1)
    return p


def deck_face():
    pts = json.load(open("deck_outline.json"))[:-1]
    f = Polygon(*[tuple(p) for p in pts], align=None)
    return f




def pi_deck():
    d = Pos(0, 0, DECK_Z) * extrude(deck_face(), amount=DECK_T, dir=(0, 0, 1))
    for x, y in POSTS:
        d -= cyl(1.7, DECK_Z - 1, DECK_TOP + 1, x, y)
    for x, y in PI_HOLES:
        d += cyl(3.0, DECK_TOP - 0.1, DECK_TOP + 5, x, y)
        d -= cyl(1.1, DECK_TOP - 1, DECK_TOP + 6, x, y)
    d -= box(-36, -26, -40, 20, DECK_Z - 1, DECK_TOP + 1)
    for y in PCA_PLUG_ROWS:   # servo plugs stand ~16.5mm off the PCA: let them pass up through the deck
        d -= box(-26, 26, y - 6, y + 6, DECK_Z - 1, DECK_TOP + 1)
    w = CAM_SIZE[0] / 2 + 5
    wall = box(-w, w, CAM_Y - 3, CAM_Y, DECK_TOP - 0.1, DECK_TOP + 32 - CAM_DROP)
    lens_z = DECK_TOP + 20 - CAM_DROP
    wall -= Pos(0, CAM_Y - 1.5, lens_z) * Rot(90, 0, 0) * Cylinder(8.0, 6)
    for hx in (-CAM_HOLES[0] / 2, CAM_HOLES[0] / 2):
        for hz in (lens_z + CAM_HOLES[1] / 2 - 2.5, lens_z - CAM_HOLES[1] / 2 - 2.5):
            wall -= Pos(hx, CAM_Y - 1.5, hz) * Rot(90, 0, 0) * Cylinder(1.15, 6)
    wall -= box(-9, 9, CAM_Y - 4, CAM_Y + 1, DECK_TOP + 29 - CAM_DROP, DECK_TOP + 33 - CAM_DROP)
    for s in (-1, 1):
        rib = Plane.YZ * Polygon((CAM_Y - 3, DECK_TOP), (CAM_Y - 15, DECK_TOP), (CAM_Y - 3, DECK_TOP + 14), align=None)
        wall += Pos(s * (w - 1.5), 0, 0) * extrude(rib, amount=1.5, both=True)
    d += wall
    return d


def deck_text(height=0.6):
    out = None
    for txt, size, y in (("VANTA", 7.5, 19.0), ("MADE BY GIO", 4.5, -22.0)):
        t = Text(txt, size, font_style=FontStyle.BOLD, align=(Align.CENTER, Align.CENTER))
        s = Pos(34.5, y, DECK_TOP - 0.6) * extrude(Rot(0, 0, 90) * t, amount=height)
        out = s if out is None else out + s
    return out


def pca_dummy():
    b = Compound([])
    out = []
    for cx, cy in PCA_CENTERS:
        z0 = PLATE_TOP + 5
        brd = box(cx - PCA_SIZE[0] / 2, cx + PCA_SIZE[0] / 2, cy - PCA_SIZE[1] / 2, cy + PCA_SIZE[1] / 2, z0, z0 + 1.6)
        side = -1 if cy < 0 else 1
        hy = cy + side * (PCA_SIZE[1] / 2 - 5)
        hdr = box(cx - 25, cx + 25, hy - 4, hy + 4, z0 + 1.6, z0 + 13)
        out += [brd, hdr]
    return out


def pi_dummy():
    x0, y0 = PI_C[0] - 28, PI_C[1] - 42.5
    z0 = DECK_TOP + 5
    p = box(x0, x0 + 56, y0, y0 + 85, z0, z0 + 1.6)
    p += box(x0 + 2, x0 + 54, y0 - 2, y0 + 20, z0 + 1.6, z0 + 17)
    p += box(x0 + 1, x0 + 6, y0 + 27, y0 + 78, z0 + 1.6, z0 + 10)
    return p


def module_dummies():
    out = []
    for cx, cy, l, w in (BUCK, SBEC):
        out.append(box(cx - l / 2, cx + l / 2, cy - w / 2, cy + w / 2, PLATE_TOP, PLATE_TOP + 15))
    return out


def cam_dummy():
    lens_z = DECK_TOP + 20 - CAM_DROP
    b = box(-12.5, 12.5, CAM_Y, CAM_Y + 1.6, lens_z - 14.5, lens_z + 9.5)
    b += Pos(0, CAM_Y + 1.6, lens_z) * Rot(-90, 0, 0) * Cylinder(4, 5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return b


if __name__ == "__main__":
    for name, f in (("electronics_plate", elec_plate), ("pi_deck", pi_deck)):
        s = f()
        print(name, round(s.volume / 1000, 2), "cm3", s.bounding_box().min, s.bounding_box().max)
        export_stl(s, f"out/{name}_inplace.stl")
