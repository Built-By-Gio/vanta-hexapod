"""Make the thumbnail / insert-map GLBs and print the render job list (one line per render)."""
import os, numpy as np, trimesh
from trimesh.transformations import rotation_matrix as Rm
G = './v6/g7/'
P = './v6/out6/VANTA/1_PRINT/stl_main/'
O = G + 'r/'; os.makedirs(O, exist_ok=True); os.makedirs(G + 'glb', exist_ok=True)
STAND = G + 'stand7.glb'


def marker(c, n):
    m = trimesh.creation.cylinder(3.2, 1.6, sections=32)
    n = np.asarray(n, float); z = np.array([0, 0, 1.0])
    if abs(n @ z) < 0.999:
        ax = np.cross(z, n); m.apply_transform(Rm(np.arccos(n @ z), ax))
    elif n[2] < 0: m.apply_transform(Rm(np.pi, [1, 0, 0]))
    m.apply_translation(np.asarray(c) + n * 0.4)
    return m


def glb(name, parts):
    sc = trimesh.Scene()
    for i, (k, m) in enumerate(parts):
        k = f"{i}{k}" if k.startswith("m|") else k
        sc.add_geometry(m, node_name=k, geom_name=k)
    f = G + 'glb/' + name + '.glb'; sc.export(f); return f


jobs = []
THUMBS = ["01_base_x1", "02_top_stiffeners_x1", "03_bottom_stiffeners_x1", "04_battery_mount_x1", "05_electronics_plate_x1", "06_pi_deck_x1",
          "07_femur_x6", "08_tibia_x6", "09_bracket_A_coxa_x6", "09_bracket_A_link_x12", "10_bracket_B_alu_x18",
          "11_servo_cap_plus2_x18", "13_armor_femur_x12", "14_armor_shin_x6"]
for k in THUMBS:
    jobs.append((glb('t_' + k, [(f"part|{k}", trimesh.load(P + k + ".stl"))]), 't_' + k, 'iso', 1.0, 520, 400, '-', '-', '-'))

b = trimesh.load(P + "01_base_x1.stl")
parts = [("base|base", b)]
for x, y in ((85.13, 5.25), (70.81, 88.75), (63.39, 96.18)):
    for sx in (-1, 1):
        for sy in (-1, 1): parts.append(("m|insert", marker([sx * x, sy * y, 0], [0, 0, -1])))
F = Rm(np.pi, [1, 0, 0])
jobs.append((glb('i_base_under', [(k, m.copy().apply_transform(F)) for k, m in parts]), 'i_base_under', 'iso', 1.0, 700, 560, '-', '-', '-'))
jobs.append((glb('i_base_top', [("base|base", b)] + [("m|insert", marker([sx * 32.64, sy * 58.0, 21.2], [0, 0, 1])) for sx in (-1, 1) for sy in (-1, 1)]),
             'i_base_top', 'iso', 1.0, 700, 560, '-', '-', '-'))
jobs.append((glb('i_femur', [("femur|femur", trimesh.load(P + "07_femur_x6.stl"))] + [("m|insert", marker([-52.8, y, 14.0], [0, 0, 1])) for y in (-5.25, 5.25)]),
             'i_femur', 'iso', 1.0, 700, 560, '-', '-', '-'))
jobs.append((glb('i_acoxa', [("a|bracket_A", trimesh.load(P + "09_bracket_A_coxa_x6.stl"))] + [("m|insert", marker([28.15, 17.0, z], [1, 0, 0])) for z in (5.0, 15.0)]),
             'i_acoxa', 'iso', 1.0, 700, 560, '-', '-', '-'))
jobs.append((glb('i_plate', [("p|electronics_plate", trimesh.load(P + "05_electronics_plate_x1.stl"))] +
                 [("m|insert", marker([sx * 33.0, sy * 46.0, 22.8], [0, 0, 1])) for sx in (-1, 1) for sy in (-1, 1)]),
             'i_plate', 'iso', 1.0, 700, 560, '-', '-', '-'))

COXA = ",".join(f"leg_{L}_coxa_motor" for L in range(1, 7))
HULL = "top_hull,top_hull_text_ACCENT,REF_fan_x2"
S = {
    "s05": ("iso", "servo_cap,bearing_623", "-", "leg_2_femur_motor"),
    "s06": ("under", "servo_cap", "-", "base|," + COXA),
    "s07": ("under", "bottom_stiffeners,battery_mount", "-", "base|,battery," + COXA + ",bottom_stiffeners"),
    "s08": ("iso", "leg_1_coxa_bracket_A|bracket_A,leg_1_coxa_bracket_B|bracket_B_alu,leg_1_coxa_motor|horn_alu", "-", "base|,leg_1_coxa"),
    "s09": ("iso", "femur", "-", "leg_2_femur|,leg_2_femur_motor,leg_2_tibia_motor"),
    "s10": ("backiso", "leg_2_femur_bracket_A|bracket_A,leg_2_femur_bracket_B|bracket_B_alu,leg_2_femur_motor|horn_alu", "-",
            "leg_2_coxa_bracket,leg_2_femur,leg_2_tibia_motor"),
    "s11": ("backiso", "leg_2_tibia_bracket_A|bracket_A,leg_2_tibia_bracket_B|bracket_B_alu,leg_2_tibia_motor|horn_alu,leg_2_tibia|tibia", "-",
            "leg_2_femur|,leg_2_tibia"),
    "s12": ("backiso", "armor_femur,armor_shin", HULL, "leg_2_"),
    "oneleg": ("backiso", "-", HULL, "leg_2_"),
    "s12top": ("top", "-", HULL, "-"),
    "s13": ("iso", "top_stiffeners,electronics_plate,REF_pca9685_x2,REF_buck_sbec", "-", "base|,top_stiffeners,electronics_plate,REF_pca,REF_buck," + COXA),
    "s14": ("iso", "battery|REF_battery,REF_buck_sbec", "-", "base|,battery,battery_mount,bottom_stiffeners,top_stiffeners,electronics_plate,REF_pca,REF_buck," + COXA),
    "s16": ("iso", "pi_deck,REF_raspberry_pi4,REF_camera", "-", "base|,top_stiffeners,electronics_plate,pi_deck,REF_," + COXA),
    "s17": ("iso", "-", HULL, "-"),
    "s18": ("iso", "top_hull,REF_fan_x2", "-", "-"),
}
for k, (v, hl, hide, only) in S.items():
    jobs.append((STAND, k, v, 1.0, 900, 900, hl, hide, only))
jobs.append((STAND, 'hero', 'hero', 1.0, 1800, 1300, '-', '-', '-'))
jobs.append((STAND, 'hero_open', 'hero', 1.0, 1600, 1100, '-', HULL, '-'))

with open(G + 'jobs.txt', 'w') as f:
    for j in jobs: f.write(' '.join(str(x) for x in (j[0], O + j[1] + '.png') + j[2:]) + '\n')
print(len(jobs), 'jobs')
