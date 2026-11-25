"""Copy every v6 deliverable from _dev into the VANTA folder layout (generators run separately: run_v6.py, make_3mf_v4.py, make_color.py, guide6.py)."""
import os, shutil, glob
D = "./"
V = D + "_dev/"


def fresh(d):
    os.makedirs(d, exist_ok=True)
    for f in glob.glob(d + "*"):
        os.remove(f)


fresh(D + "1_PRINT/stl_main/")
for f in glob.glob(V + "hx2/print/stl/*.stl"):
    shutil.copy(f, D + "1_PRINT/stl_main/")
fresh(D + "1_PRINT/stl_color_AMS/")
for src, dst in (("S_top_shell", "1_mech_hull_BLACK"), ("S_top_shell_text_ACCENT", "1_mech_hull_lettering_SILVER"), ("C_logo_letters_ACCENT", "2_front_logo_letters_SILVER"),
                 ("D_base_logo_ams", "3_optional_base_BLACK"), ("D_base_logo_ACCENT", "3_optional_base_logo_SILVER")):
    shutil.copy(V + f"brand/stl/{src}.stl", D + f"1_PRINT/stl_color_AMS/{dst}.stl")
shutil.copy(V + "blend4/VANTA_rigged_walk.blend", D + "2_BLENDER/VANTA_rigged_walk.blend")
shutil.copy(V + "gg/asm5_stand.glb", D + "3_CAD/VANTA_standing.glb")
shutil.copy(V + "hx2/out/servo_cap623.step", D + "3_CAD/servo_cap.step")
fresh(D + "3_CAD/stl_in_place/")
for f in glob.glob(V + "gg/v5/*.stl"):
    shutil.copy(f, D + "3_CAD/stl_in_place/" + ("servo_cap_plus0.stl" if f.endswith("cap.stl") else os.path.basename(f)))
for f in ("hull_inplace.stl", "hull_text_inlay.stl"):
    shutil.copy(V + "hx2/out/" + f, D + "3_CAD/stl_in_place/")
fresh(D + "3_CAD/source/")
for f in ("hx2/build_v5.py", "hx2/bracket_b_alu.py", "hx2/hull.py", "hx2/armor.py", "hx2/refs.py", "hx2/cap.py", "hx2/cap623.py", "hx2/body2.py",
          "hx2/legparts.py", "hx2/prep_print.py", "hx2/make_3mf_v4.py", "hx2/coxa_cap_fp.json", "hx2/coxa_servo_fp.json", "hx2/deck_outline.json",
          "hx2/emount_outline.json", "hx2/free_region.json", "st/bearing623.py", "st/selftap.py", "st/holes.py", "lite/hexcut.py", "lite/slice.py",
          "lite/table.py", "lite/compare.py", "gg/v5asm.py", "gg/sweep.py", "gg/sweep_v5.py", "gg/sweep_v6.py", "gg/walkcheck.py", "gg/screwpath.py", "gg/asm2.py",
          "gg/export_rig.py", "gg/hexapod.urdf", "blend4/build_blend.py", "blend4/verify.py", "brand/make_color.py", "brand/logo.py",
          "man5/render5.py", "man6/renders5.py", "man6/guide5.py", "man6/guide6.py", "run_v6.py", "deliver.py"):
    shutil.copy(V + f, D + "3_CAD/source/")
fresh(D + "renders/")
for k, dst in (("hero_color", "vanta_v6.png"), ("rear_color", "vanta_v6_rear.png"), ("s12top", "vanta_v6_top_open.png"), ("s10", "femur_joint_alu.png"), ("s12", "leg_armour.png"),
               ("s18", "mech_hull.png"), ("t_10_bracket_B_alu_x18", "bracket_B_alu.png"), ("t_11_servo_cap_plus0_x18", "servo_cap.png")):
    shutil.copy(V + f"man6/r5/{k}.png", D + "renders/" + dst)
print("delivered")
