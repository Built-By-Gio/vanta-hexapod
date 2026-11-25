import trimesh, numpy as np
from trimesh.transformations import rotation_matrix as R
G = "./_dev/gg/"
X = lambda d: R(np.radians(d), [1, 0, 0]); Y = lambda d: R(np.radians(d), [0, 1, 0])
PARTS = {
    "01_base_x1": ("./_dev/legacy/01_base_x1_logo_pocket.stl", np.eye(4)),
    "02_top_stiffeners_x1": (G + "top_stiffeners.stl", X(180)),
    "03_bottom_stiffeners_x1": (G + "bottom_stiffeners.stl", X(180)),
    "04_battery_mount_x1": (G + "battery_mount.stl", np.eye(4)),
    "05_electronics_plate_x1": ("out/electronics_plate_inplace.stl", np.eye(4)),
    "06_pi_deck_x1": ("out/pi_deck_inplace.stl", np.eye(4)),
    "07_femur_x6": (G + "femur.stl", np.eye(4)),
    "08_tibia_x6": (G + "tibia.stl", Y(90)),
    "09_bracket_A_capped_x18": ("out/bracket_A_capped.stl", X(90)),
    "10_bracket_B_x18": (G + "bracket_B.stl", Y(90)),
    "11_servo_cap_plus0_x18": ("out/servo_cap_plus0.stl", np.eye(4)),
    "11_servo_cap_plus1_x18": ("out/servo_cap_plus1.stl", np.eye(4)),
    "11_servo_cap_plus2_x18": ("out/servo_cap_plus2.stl", np.eye(4)),
    "11_servo_cap_plus3_x18": ("out/servo_cap_plus3.stl", np.eye(4)),
    "12_foot_TPU_x6": ("out/foot_sleek_TPU.stl", np.eye(4)),
}
for k, (src, M) in PARTS.items():
    m = trimesh.load(src).apply_transform(M)
    m.apply_translation([-m.bounds.mean(0)[0], -m.bounds.mean(0)[1], -m.bounds[0][2]])
    assert m.is_watertight, k
    m.export(f"print/stl/{k}.stl")
    print(f"{k:28s} {m.extents.round(1)}  {m.volume/1000:6.1f} cm3")
