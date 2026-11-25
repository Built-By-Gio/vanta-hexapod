from build123d import *
import cap as C

BRG_OD, BRG_W = 10.05, 4.0
PLATE = 1.6                     # floor everywhere except the bearing boss
BOSS_AF = BRG_OD + 2 * 2.4      # hex boss across flats
RIB_W, RIB_H = 2.5, 2.4


def servo_cap_623(extra=0):
    """Prints skirt-down (z flipped by prep). Bearing outer face stays at z = -floor like v4;
    only the hex boss reaches it, the rest of the floor is a 1.6mm plate stiffened by 6 hex-direction ribs."""
    web = 1.6 + extra
    floor = web + BRG_W
    shell = Box(C.CASE_L + 2 * C.WALL, C.CASE_W + 2 * C.WALL, PLATE + C.SKIRT, align=(Align.CENTER, Align.CENTER, Align.MIN))
    shell = fillet((Pos(0, 0, -PLATE) * shell).edges().filter_by(Axis.Z), 1.5)
    c = shell - Box(C.CASE_L, C.CASE_W, C.SKIRT + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    c += Pos(C.SHAFT_X, 0, -floor) * extrude(RegularPolygon(BOSS_AF / 2, 6, major_radius=False), amount=floor - 0.01)
    for a in range(0, 360, 60):
        rib = Pos(C.SHAFT_X, 0, -PLATE - RIB_H) * Rot(0, 0, a) * Box(40, RIB_W, RIB_H + 0.01, align=(Align.MIN, Align.CENTER, Align.MIN))
        c += rib & Pos(0, 0, -PLATE - RIB_H) * Box(C.CASE_L + 2 * C.WALL - 1, C.CASE_W + 2 * C.WALL - 1, RIB_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    c -= Pos(C.SHAFT_X, 0, -floor - 0.1) * Cylinder(BRG_OD / 2, BRG_W + 0.1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    c -= Pos(C.SHAFT_X, 0, -floor) * Cylinder(2.0, floor, align=(Align.CENTER, Align.CENTER, Align.MIN))
    c -= Pos(C.SHAFT_X, 0, -1) * Cylinder(5.0, 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    c -= Pos(C.CASE_L / 2 + C.WALL / 2, 0, 0) * Box(C.WALL + 2, C.NOTCH_W, C.SKIRT * 2 + 0.2)
    return c


if __name__ == "__main__":
    for e in range(4):
        c = servo_cap_623(e)
        export_stl(c, f"out/servo_cap623_plus{e}.stl")
        print(e, round(c.volume / 1000, 2), c.bounding_box().size)
    export_step(servo_cap_623(0), "out/servo_cap623.step")
