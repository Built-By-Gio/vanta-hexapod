"""v5 print STLs: hex lightening + insert/self-tap mix within Gio's stock.
Reads print/stl_v4 (v4 print STLs, inserts + 623 bearing mod) and out/ (caps, B brackets); writes print/stl.
All coordinates are in each part's print frame (see prep_print.py)."""
import sys, numpy as np, trimesh
from trimesh.transformations import rotation_matrix as R
D = "./_dev/"
sys.path[:0] = [D + "lite", D + "st"]
from hexcut import hex_poly, hex_cells, slab_region, cut
from selftap import cyl

SRC, DST, OUT = D + "hx2/print/stl_v4/", D + "hx2/print/stl/", D + "hx2/out/"
TAP_R, CLR_R, CB_R, INS_R = 1.4, 1.7, 3.25, 2.2   # Ø2.8 self-tap, Ø3.4 clearance, Ø6.5 head counterbore, Ø4.4 insert
U = dict(engine="manifold")
sub = lambda m, *t: trimesh.boolean.difference([m, *t], **U) if t else m
add = lambda m, *t: trimesh.boolean.union([m, *t], **U)


def retap(m, ax, c, a, b, r=TAP_R, fill_r=2.5):
    """fill an existing hole between a..b on axis ax and re-drill it at radius r"""
    c = np.asarray(c, float)
    return sub(add(m, cyl(ax, c, fill_r, a, b)), cyl(ax, c, r, a - 0.5, b + 0.5))


def hex_through(c, a, us, zc, r, half=16.0):
    """pointy-top hexes in the vertical plane spanned by horizontal dir a and z, cut through +-half along the other horizontal dir"""
    a = np.r_[a, 0.0] / np.linalg.norm(a); n = np.cross([0, 0, 1], a); ez = np.array([0, 0, 1.0])
    tools = []
    for u in us:
        p = trimesh.creation.extrude_polygon(hex_poly(u, zc, r), 2 * half)
        l = p.vertices
        v = np.r_[c, 0.0] + np.outer(l[:, 0], a) + np.outer(l[:, 1], ez) + np.outer(l[:, 2] - half, n)
        f = p.faces if np.linalg.det(np.c_[a, ez, n]) > 0 else p.faces[:, ::-1]
        tools.append(trimesh.Trimesh(v, f))
    return tools


def femur(m):
    # honeycomb row through both rails between the servo tab holes; 3mm flanges, 2.5mm ribs
    xs = [s * x for s in (-1, 1) for x in (14.4, 23.8, 33.2, 42.6)]
    m = cut(m, 1, [hex_poly(x, 7.0, 4.0) for x in xs], -16, 16)
    # knee end (-x, tibia servo outer tabs) keeps its 2 inserts; the other six tab holes self-tap
    for x in (-4.2, 4.2, 52.8):
        for y in (-5.25, 5.25):
            m = retap(m, 2, [x, y, 0], 1.8, 14.0)
    return m


def tibia(m):
    # 4 holes onto tibia bracket A: Ø3.4 clearance, Ø6.5 x 4 head counterbore on the outer face (flange is y 60.875..68.875)
    for x in (6.0, 16.0):
        for z in (5.0, 15.0):
            c = [x, 64.85, z]
            m = sub(add(m, cyl(1, np.array(c), 2.3, 60.875, 68.875)), cyl(1, np.array(c), CLR_R, 59, 70), cyl(1, np.array(c), CB_R, 64.875, 70))
    return m


def bracket_A(m, coxa):
    for x in (0.25, 10.25):
        for z in (5.0, 15.0):
            c = np.array([x, 16.98, z])
            if coxa:   # screws pass through into the femur bracket: clearance + counterbore from the inner face (y 12.9)
                m = sub(add(m, cyl(1, c, 2.3, 13.0, 21.0)), cyl(1, c, CLR_R, 12, 22), cyl(1, c, CB_R, 12, 16.9))
            else:
                m = retap(m, 1, c, 13.0, 21.0, fill_r=2.3)
    if not coxa:   # end face: B screws self-tap (alu joints + the two stock tibia joints)
        for z in (5.0, 15.0):
            m = retap(m, 0, [24.6, 17.0, z], 19.0, 28.15, fill_r=2.4)
    return m


BASE_POCKETS = [((61.4, 0.0), (1, 0), 6.0, 3.0, (-15.4, -7.7, 0, 7.7, 15.4)),          # middle legs: walls 12 tall
                ((50.3, 75.7), (1, 1), 7.0, 4.0, (-14.15, -4.72, 4.72, 14.15)),         # corner legs: walls 14 tall
                ((50.3, -75.7), (-1, 1), 7.0, 4.0, (-14.15, -4.72, 4.72, 14.15))]


def base(m):
    tools = []
    for (cx, cy), a, zc, r, us in BASE_POCKETS:
        for s in (1, -1):
            tools += hex_through((s * cx, cy), (s * a[0], a[1]), us, zc, r, 15.0)
    m = sub(m, *tools)
    # coxa servo inner tabs (under the bottom stiffener): self-tap 10 deep
    for x, y in ((37.14, 5.25), (36.87, 54.81), (29.45, 62.24)):
        for sx in (-1, 1):
            for sy in (-1, 1):
                m = retap(m, 2, [sx * x, sy * y, 0], 0.0, 10.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            m = retap(m, 2, [sx * 30.64, sy * 52.0, 0], 0.0, 6.0)          # stiffener corners / battery ears
            c = np.array([sx * 32.64, sy * 58.0, 0])                         # electronics plate: column up to the plate
            m = add(m, cyl(2, c, 2.4, 5.7, 14.1), cyl(2, c, 3.75, 13.5, 21.2))
            m = sub(m, cyl(2, c, INS_R, 15.2, 21.5))
    return m


def top_stiffeners(m):
    for sx in (-1, 1):
        for sy in (-1, 1):
            m = sub(m, cyl(2, np.array([sx * 32.63, sy * 58.0, 0]), 4.15, -1, 13))   # clears the base column
    return m


def bottom_stiffeners(m):
    for x, y in ((37.14, 5.25), (36.87, 54.81), (29.45, 62.24)):            # inner servo tabs: 2.4mm left under the head
        for sx in (-1, 1):
            for sy in (-1, 1):
                m = sub(m, cyl(2, np.array([sx * x, sy * y, 0]), CB_R, -1, 7.3))
    for sx in (-1, 1):
        for sy in (-1, 1):
            c = np.array([sx * 30.63, sy * 52.0, 0])
            m = sub(add(m, cyl(2, c, 2.5, 0.0, 10.0)), cyl(2, c, CLR_R, -1, 11), cyl(2, c, CB_R, -1, 7.6))
    return m


def honeycomb_slab(m, t, pitch, origin, rib=3.0):
    """big hex windows through the flat 0..t slab only, 3mm clear of every boss, post, slot and edge"""
    return cut(m, 2, hex_cells(slab_region(m, 2, 0.0, t, margin=3.0), pitch, rib, origin=origin), -1, t + 0.01)


def oriented(path, M):
    m = trimesh.load(path).apply_transform(M)
    m.apply_translation([-m.bounds.mean(0)[0], -m.bounds.mean(0)[1], -m.bounds[0][2]])
    return m


JOBS = {
    "07_femur_x6": lambda: femur(trimesh.load(SRC + "07_femur_x6.stl")),
    "08_tibia_x6": lambda: tibia(trimesh.load(SRC + "08_tibia_x6.stl")),
    "09_bracket_A_coxa_x6": lambda: bracket_A(trimesh.load(SRC + "09_bracket_A_x18.stl"), True),
    "09_bracket_A_link_x12": lambda: bracket_A(trimesh.load(SRC + "09_bracket_A_x18.stl"), False),
    "01_base_x1": lambda: base(trimesh.load(SRC + "01_base_x1.stl")),
    "02_top_stiffeners_x1": lambda: top_stiffeners(trimesh.load(SRC + "02_top_stiffeners_x1.stl")),
    "04_battery_mount_x1": lambda: honeycomb_slab(trimesh.load(SRC + "04_battery_mount_x1.stl"), 2.0, 18, (0, 0)),
    "05_electronics_plate_x1": lambda: honeycomb_slab(trimesh.load(SRC + "05_electronics_plate_x1.stl"), 3.0, 16, (8, 0)),
    "06_pi_deck_x1": lambda: honeycomb_slab(oriented(OUT + "pi_deck_inplace.stl", np.eye(4)), 3.0, 24, (0, 0)),   # v6 deck: lower camera, plug windows
    "03_bottom_stiffeners_x1": lambda: bottom_stiffeners(trimesh.load(SRC + "03_bottom_stiffeners_x1.stl")),
    "10_bracket_B_alu_x18": lambda: oriented(D + "gg/bracket_B_alu.stl", R(np.pi / 2, [0, 1, 0])),
    **{f"11_servo_cap_plus{e}_x18": (lambda e=e: oriented(OUT + f"servo_cap623_plus{e}.stl", R(np.pi, [1, 0, 0]))) for e in range(4)},
}

# print part -> (native source it was oriented from, prep rotation, native v5 file for the assembly / sweeps / rig)
NATIVE = {
    "01_base_x1": (D + "legacy/01_base_x1_logo_pocket.stl", np.eye(4), "base.stl"),
    "02_top_stiffeners_x1": (D + "gg/top_stiffeners.stl", R(np.pi, [1, 0, 0]), "top_stiffeners.stl"),
    "03_bottom_stiffeners_x1": (D + "gg/bottom_stiffeners.stl", R(np.pi, [1, 0, 0]), "bottom_stiffeners.stl"),
    "07_femur_x6": (D + "gg/femur.stl", np.eye(4), "femur.stl"),
    "08_tibia_x6": (D + "gg/tibia.stl", R(np.pi / 2, [0, 1, 0]), "tibia.stl"),
    "09_bracket_A_coxa_x6": (OUT + "bracket_A_capped.stl", R(np.pi / 2, [1, 0, 0]), "bracket_A_coxa.stl"),
    "09_bracket_A_link_x12": (OUT + "bracket_A_capped.stl", R(np.pi / 2, [1, 0, 0]), "bracket_A_link.stl"),
    "04_battery_mount_x1": (D + "gg/battery_mount.stl", np.eye(4), "battery_mount.stl"),
    "05_electronics_plate_x1": (OUT + "electronics_plate_inplace.stl", np.eye(4), "electronics_plate_inplace.stl"),
    "06_pi_deck_x1": (OUT + "pi_deck_inplace.stl", np.eye(4), "pi_deck_inplace.stl"),
}


def to_native(key, m):
    src, M, _ = NATIVE[key]
    s = trimesh.load(src).apply_transform(M)
    T = np.eye(4); T[:3, 3] = [-s.bounds.mean(0)[0], -s.bounds.mean(0)[1], -s.bounds[0][2]]
    return m.copy().apply_transform(np.linalg.inv(T @ M))


def colour_parts():
    """colour file: mech hull upright (skirt on the bed) with its text inlays, and the optional AMS base with the v5 base mods"""
    B = D + "brand/stl/"
    sh = trimesh.load(OUT + "hull_inplace.stl"); dz = -sh.bounds[0][2]
    sh.apply_translation([0, 0, dz]); sh.export(B + "S_top_shell.stl")
    trimesh.load(OUT + "hull_text_inlay.stl").apply_translation([0, 0, dz]).export(B + "S_top_shell_text_ACCENT.stl")
    base(trimesh.load(D + "brand/stl_v4/D_base_logo_ams.stl")).export(B + "D_base_logo_ams.stl")


if __name__ == "__main__":
    import shutil
    for k in (sys.argv[1:] or [*JOBS, "colour"]):
        if k == "colour":
            colour_parts(); print("colour parts written"); continue
        out = JOBS[k]()
        assert out.is_watertight and out.is_volume, k
        out.export(DST + k + ".stl")
        if k in NATIVE:
            to_native(k, out).export(D + "gg/v5/" + NATIVE[k][2])
        print(f"{k:28s} {out.extents.round(1)} {out.volume / 1000:6.2f} cm3")
    for f in ("bracket_B_alu.stl",):
        shutil.copy(D + "gg/" + f, D + "gg/v5/" + f)
    shutil.copy(OUT + "servo_cap623_plus0.stl", D + "gg/v5/cap.stl")
