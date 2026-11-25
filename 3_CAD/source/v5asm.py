"""v5 assembly: sweep.py's URDF posing with the v5 part meshes swapped in.
pose5(angles) yields (link_name, label, mesh_mm_native, M) with M mapping native mm -> world metres (x1000 after)."""
import os, sys, numpy as np, trimesh, warnings
warnings.filterwarnings("ignore")
G = "./_dev/gg/"
_cwd = os.getcwd(); os.chdir(G)
exec(open(G + "sweep.py").read().split("def objs")[0].replace("DELTA = float(sys.argv[1]); MODE = sys.argv[2]", "DELTA = 4.5; MODE = 'new'"))
os.chdir(_cwd)
meshes["MG996R.stl"] = trimesh.load(G + "hw_MG996R.stl")


def mesh(f):   # sweep.py's loader, but independent of the working folder
    if f not in meshes: meshes[f] = trimesh.load(G + {"battery.stl": "hw_battery.stl", "electronics.stl": "elec_simple.stl"}.get(f, f))
    return meshes[f]
V = G + "v5/"
# v6: every joint has an aluminium disc horn and bracket_B_alu
_cache = {}


def load(p):
    if p not in _cache: _cache[p] = trimesh.load(p)
    return _cache[p]


def leg_of(n):
    return int(n.split("_")[1]) if n.startswith("leg_") else 0


def is_alu(n):
    return n.startswith("leg_")


def v5_mesh(n, f):
    if f == "bracket_A.stl": return load(V + ("bracket_A_coxa.stl" if "_coxa_" in n else "bracket_A_link.stl")), "bracket_A"
    if f == "bracket_B.stl": return (load(V + "bracket_B_alu.stl"), "bracket_B_alu") if is_alu(n) else (load(V + "bracket_B_v5.stl"), "bracket_B")
    if f in ("base.stl", "femur.stl", "tibia.stl", "top_stiffeners.stl", "bottom_stiffeners.stl", "battery_mount.stl"): return load(V + f), f[:-4]
    return mesh(f), {"MG996R.stl": "REF_MG995", "battery.stl": "REF_battery"}.get(f, f[:-4])


CAP5 = load(V + "cap.stl").copy().apply_translation([20.05, 9.75, -30.0])   # same placement sweep.py gives cap0


ARMOR = {"femur.stl": "armor_femur", "tibia.stl": "armor_shin"}   # cosmetic plates glued on, in the part's own frame


def pose5(angles, armour=True):
    for n, f, M in pose(angles):
        if f == "cap": yield n, "servo_cap", CAP5, M; continue
        m, label = v5_mesh(n, f)
        yield n, label, m, M
        if armour and f in ARMOR: yield n + "_armor", ARMOR[f], load(V + ARMOR[f] + ".stl"), M


def alu_heads():
    """the 4 horn screw heads (M3 socket, Ø5.5 x 3) proud of bracket_B_alu's outer face, at the outermost slot end"""
    hs = []
    for a in np.radians([0, 90, 180, 270]):
        c = trimesh.creation.cylinder(2.75, 3.0, sections=24)
        c.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]))
        c.apply_translation([28.9 + 1.5, 10.0 * np.cos(a), 34.0 + 10.0 * np.sin(a)])
        hs.append(c)
    return trimesh.util.concatenate(hs)
