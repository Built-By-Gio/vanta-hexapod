"""Run the v6 part pipeline in one process (this Windows box kills parents when a child python exits).
python run_v6.py [step ...]   steps: bracket deck hull armor parts"""
import os, sys, runpy, time
D = "./_dev/"
STEPS = {"bracket": ("hx2", "bracket_b_alu.py", []), "deck": ("hx2", "body2.py", []), "refs": ("hx2", "refs.py", []), "hull": ("hx2", "hull.py", []),
         "armor": ("hx2", "armor.py", []), "parts": ("hx2", "build_v5.py", []),
         "glb": ("gg", "asm2.py", [D + "blend4/stand.json", D + "gg/asm5_stand.glb"]), "rig": ("gg", "export_rig.py", []),
         "blend": ("blend4", "build_blend.py", []), "verify": ("blend4", "verify.py", [])}
for k in sys.argv[1:] or STEPS:
    d, f, args = STEPS[k]
    os.chdir(D + d); sys.argv = [f, *args]
    if D + d not in sys.path: sys.path.insert(0, D + d)
    t = time.time(); print(f"== {k}", flush=True)
    runpy.run_path(D + d + "/" + f, run_name="__main__")
    print(f"== {k} done in {time.time() - t:.0f}s", flush=True)
print("RUN DONE", flush=True)
