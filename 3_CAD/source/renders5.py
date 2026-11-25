"""Guide renders: part thumbnails, insert maps, step views. python renders5.py [name ...]  (default: all missing)"""
import os, sys, numpy as np, trimesh
from trimesh.transformations import rotation_matrix as Rm
D = "./_dev/"
P, O = D + "hx2/print/stl/", D + "man6/r5/"
STAND = D + "gg/asm5_stand.glb"
os.makedirs(O, exist_ok=True)
sys.path.insert(0, D + "man5")
from render5 import render


def marker(c, n):   # red insert disc, Ø5 x 1.2, sitting on the face with normal n
    m = trimesh.creation.cylinder(3.2, 1.6, sections=32)
    n = np.asarray(n, float); z = np.array([0, 0, 1.0])
    if abs(n @ z) < 0.999:
        ax = np.cross(z, n); m.apply_transform(Rm(np.arccos(n @ z), ax))
    elif n[2] < 0: m.apply_transform(Rm(np.pi, [1, 0, 0]))
    m.apply_translation(np.asarray(c) + n * 0.4)
    return m


def glb(name, parts):
    sc = trimesh.Scene()
    for i, (k, m) in enumerate(parts): k = f"{i}{k}" if k.startswith("m|") else k; sc.add_geometry(m, node_name=k, geom_name=k)
    f = O + name + ".glb"; sc.export(f); return f


THUMBS = ["01_base_x1", "02_top_stiffeners_x1", "03_bottom_stiffeners_x1", "04_battery_mount_x1", "05_electronics_plate_x1", "06_pi_deck_x1",
          "07_femur_x6", "08_tibia_x6", "09_bracket_A_coxa_x6", "09_bracket_A_link_x12", "10_bracket_B_alu_x18",
          "11_servo_cap_plus0_x18", "13_armor_femur_x12", "14_armor_shin_x6"]
JOBS = {}
for k in THUMBS:
    JOBS["t_" + k] = (lambda k=k: glb("t_" + k, [(f"part|{k}", trimesh.load(P + k + ".stl"))]), "iso", 1.0, 520, 400, "-", "-", "-")


def ins_base():
    b = trimesh.load(P + "01_base_x1.stl"); parts = [("base|base", b)]
    for x, y in ((85.13, 5.25), (70.81, 88.75), (63.39, 96.18)):
        for sx in (-1, 1):
            for sy in (-1, 1): parts.append(("m|insert", marker([sx * x, sy * y, 0], [0, 0, -1])))
    F = Rm(np.pi, [1, 0, 0])   # turned over, the way you hold it to fit these
    return [(k, m.copy().apply_transform(F)) for k, m in parts]


def ins_top():
    b = trimesh.load(P + "01_base_x1.stl"); parts = [("base|base", b)]
    for sx in (-1, 1):
        for sy in (-1, 1): parts.append(("m|insert", marker([sx * 32.64, sy * 58.0, 21.2], [0, 0, 1])))
    return parts


def ins_femur():
    return [("femur|femur", trimesh.load(P + "07_femur_x6.stl"))] + [("m|insert", marker([-52.8, y, 14.0], [0, 0, 1])) for y in (-5.25, 5.25)]


def ins_acoxa():
    return [("a|bracket_A", trimesh.load(P + "09_bracket_A_coxa_x6.stl"))] + [("m|insert", marker([28.15, 17.0, z], [1, 0, 0])) for z in (5.0, 15.0)]


def ins_plate():
    return [("p|electronics_plate", trimesh.load(P + "05_electronics_plate_x1.stl"))] + \
        [("m|insert", marker([sx * 33.0, sy * 46.0, 22.8], [0, 0, 1])) for sx in (-1, 1) for sy in (-1, 1)]


JOBS.update({
    "i_base_under": (lambda: glb("i_base_under", ins_base()), "iso", 1.0, 700, 560, "-", "-", "-"),
    "i_base_top": (lambda: glb("i_base_top", ins_top()), "iso", 1.0, 700, 560, "-", "-", "-"),
    "i_femur": (lambda: glb("i_femur", ins_femur()), "iso", 1.0, 700, 560, "-", "-", "-"),
    "i_acoxa": (lambda: glb("i_acoxa", ins_acoxa()), "iso", 1.0, 700, 560, "-", "-", "-"),
    "i_plate": (lambda: glb("i_plate", ins_plate()), "iso", 1.0, 700, 560, "-", "-", "-"),
})
COXA = ",".join(f"leg_{L}_coxa_motor" for L in range(1, 7))
JOBS.update({   # in-situ step views from the standing GLB: (view, zoom, w, h, highlight, hide, only-prefixes)
    "s01": (None, "backiso", 1.0, 900, 900, "bracket_B_alu,horn_alu", "-", "leg_2_femur_motor,leg_2_femur_bracket"),
    "s05": (None, "iso", 1.0, 900, 900, "servo_cap,bearing_623", "-", "leg_2_femur_motor"),
    "s06": (None, "under", 1.0, 900, 900, "servo_cap", "-", "base|," + COXA),
    "s07": (None, "under", 1.0, 900, 900, "bottom_stiffeners,battery_mount", "-", "base|,battery," + COXA + ",bottom_stiffeners"),
    "s08": (None, "iso", 1.0, 900, 900, "leg_1_coxa_bracket_A|bracket_A,leg_1_coxa_bracket_B|bracket_B_alu,leg_1_coxa_motor|horn_alu", "-", "base|,leg_1_coxa"),
    "s09": (None, "iso", 1.0, 900, 900, "femur", "-", "leg_2_femur|,leg_2_femur_motor,leg_2_tibia_motor"),
    "s10": (None, "backiso", 1.0, 900, 900, "leg_2_femur_bracket_A|bracket_A,leg_2_femur_bracket_B|bracket_B_alu,leg_2_femur_motor|horn_alu", "-",
            "leg_2_coxa_bracket,leg_2_femur,leg_2_tibia_motor"),
    "s11": (None, "backiso", 1.0, 900, 900, "leg_2_tibia_bracket_A|bracket_A,leg_2_tibia_bracket_B|bracket_B_alu,leg_2_tibia_motor|horn_alu,leg_2_tibia|tibia", "-",
            "leg_2_femur|,leg_2_tibia"),
    "s12": (None, "backiso", 1.0, 900, 900, "armor_femur,armor_shin", "top_hull,top_hull_text_ACCENT", "leg_2_"),
    "s12top": (None, "top", 1.0, 900, 900, "-", "top_hull,top_hull_text_ACCENT", "-"),
    "s13": (None, "iso", 1.0, 900, 900, "top_stiffeners,electronics_plate", "-", "base|,top_stiffeners,electronics_plate," + COXA),
    "s16": (None, "iso", 1.0, 900, 900, "pi_deck", "-", "base|,top_stiffeners,electronics_plate,pi_deck,REF_," + COXA),
    "s18": (None, "iso", 1.0, 900, 900, "top_hull", "-", "-"),
    "hero": (None, "iso", 1.0, 1400, 1000, "-", "-", "-"),
})

if __name__ == "__main__":
    names = sys.argv[1:] or [k for k in JOBS if not os.path.exists(O + k + ".png")]
    for k in names:
        make, view, zoom, w, h, hl, hide, only = JOBS[k]
        f = make() if make else STAND
        render(f, O + k + ".png", view, zoom, w, h, hl, hide, only)   # in-process: child processes get killed on this box
        print(k, "ok" if os.path.exists(O + k + ".png") else "FAILED", flush=True)
