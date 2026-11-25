from build123d import *

CASE_L, CASE_W = 41.0, 20.1
SHAFT_X = 10.2
WALL, SKIRT = 1.8, 4.0
BRG_OD, BRG_W, FL_OD, FL_T = 13.05, 5.0, 15.2, 1.15
WEB = 0.6
FLOOR = WEB + BRG_W
NOTCH_W = 9.0


def servo_cap():
    outer = Box(CASE_L + 2 * WALL, CASE_W + 2 * WALL, FLOOR + SKIRT, align=(Align.CENTER, Align.CENTER, Align.MIN))
    outer = Pos(0, 0, -FLOOR) * outer
    outer = fillet(outer.edges().filter_by(Axis.Z), 1.5)
    c = outer - Box(CASE_L, CASE_W, SKIRT + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    c -= Pos(SHAFT_X, 0, -FLOOR - 0.1) * Cylinder(BRG_OD / 2, BRG_W + 0.1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    c -= Pos(SHAFT_X, 0, -FLOOR - 0.1) * Cylinder(FL_OD / 2, FL_T + 0.1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    c -= Pos(SHAFT_X, 0, -1) * Cylinder(5.0, 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    c -= Pos(CASE_L / 2 + WALL / 2, 0, 0) * Box(WALL + 2, NOTCH_W, SKIRT * 2 + 0.2)
    return c


if __name__ == "__main__":
    c = servo_cap()
    print("volume cm3", round(c.volume / 1000, 2), "bbox", c.bounding_box().size)
    export_stl(c, "out/servo_cap.stl")
    export_step(c, "out/servo_cap.step")
