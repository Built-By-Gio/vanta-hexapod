import trimesh, numpy as np
from build123d import export_stl
import cap as C

DELTA = 4.5
CUT_X = -34.0


def bracket_A_capped():
    m = trimesh.load("./_dev/gg/bracket_A.stl")
    v = m.vertices.copy()
    assert not ((v[:, 0] > CUT_X - 4) & (v[:, 0] < CUT_X + 4)).any()
    v[v[:, 0] < CUT_X, 0] -= DELTA
    out = trimesh.Trimesh(v, m.faces, process=False)
    assert out.is_watertight
    return out


if __name__ == "__main__":
    b = bracket_A_capped()
    print("bracket_A_capped", b.extents.round(2), round(b.volume / 1000, 2))
    b.export("out/bracket_A_capped.stl")
    for extra in (0, 1, 2, 3):
        C.WEB = 0.6 + extra
        C.FLOOR = C.WEB + C.BRG_W
        c = C.servo_cap()
        export_stl(c, f"out/servo_cap_plus{extra}.stl")
        print("cap +%d" % extra, round(c.volume / 1000, 2), "cm3")
