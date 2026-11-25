import numpy as np, trimesh, json, warnings, sys
warnings.filterwarnings("ignore")
sys.path.insert(0, "./_dev/gg")
from v5asm import *
from v5asm import CAP5, V, ARMOR, load
O = "./_dev/blend4/parts/"
H = "./_dev/hx2/out/"
SHAFT = np.array([30.25, 9.75])
def bearing():
    from trimesh.creation import annulus
    return trimesh.util.concatenate([annulus(3.0, 6.5, 3.9, transform=translation_matrix([0, 0, 3.05])), annulus(3.0, 7.5, 1.1, transform=translation_matrix([0, 0, 0.55]))])
def horn():
    from trimesh.creation import cylinder, box
    return trimesh.util.concatenate([cylinder(4.5, 4.5, transform=translation_matrix([0, 0, 2.25])), box([18, 6.0, 2.0], translation_matrix([8, 0, 3.5])), cylinder(3.0, 2.0, transform=translation_matrix([17, 0, 3.5]))])
def horn_alu():   # 25T disc, top where the stock arm top sits; z relative to the spline tip like horn()
    from trimesh.creation import cylinder
    return trimesh.util.concatenate([cylinder(12.5, 3.0, transform=translation_matrix([0, 0, 1.75])), cylinder(4.5, 2.6, transform=translation_matrix([0, 0, -1.05]))])
BRG, HORN, HORN_ALU = bearing(), horn(), horn_alu()
NAMES = {1: "FR", 2: "MR", 3: "RR", 4: "RL", 5: "ML", 6: "FL"}
def mm(M): M = M.copy(); M[:3, 3] *= 1000; return M
WL = {}
def wlink(n):
    if n in WL: return WL[n]
    if n not in child: WL[n] = np.eye(4); return WL[n]
    j = child[n]; WL[n] = wlink(j.find("parent").get("link")) @ T(j.find("origin")); return WL[n]
def first_joint(n):
    while n in child:
        j = child[n]
        if j.get("type") == "revolute": return j
        n = j.find("parent").get("link")
    return None
joints = {}
for j in R.findall("joint"):
    if j.get("type") != "revolute": continue
    leg, kind = int(j.get("name").split("_")[1]), j.get("name").split("_")[2]
    Jw = mm(wlink(j.find("child").get("link")))
    joints[f"{NAMES[leg]}_{kind}"] = {"matrix": Jw.tolist(), "axis": [float(v) for v in j.find("axis").get("xyz").split()],
                                      "parent": None if kind == "coxa" else f"{NAMES[leg]}_{'coxa' if kind == 'femur' else 'femur'}"}
groups = {}
def add(key, mat, m):
    groups.setdefault((key, mat), []).append(m)
for n, l in links.items():
    v = l.find("visual")
    if v is None: continue
    f = v.find("geometry/mesh").get("filename").split("/")[-1]
    if f in ("electronics.stl",): continue
    j = first_joint(n)
    Wv = mm(wlink(n) @ T(v.find("origin")))
    if j is None:
        key = "body"; M = Wv
    else:
        leg, kind = int(j.get("name").split("_")[1]), j.get("name").split("_")[2]
        key = f"{NAMES[leg]}_{kind}"; M = np.linalg.inv(np.array(joints[key]["matrix"])) @ Wv
    mat = {"MG996R.stl": "servo", "battery.stl": "battery"}.get(f, "pla")
    add(key, mat, v5_mesh(n, f)[0].copy().apply_transform(M))
    if f == "MG996R.stl":
        add(key, "pla", CAP5.copy().apply_transform(M))
        add(key, "metal", BRG.copy().apply_transform(M @ translation_matrix([*SHAFT, -35.6])))
        alu = n.startswith("leg_") and is_alu(n)
        add(key, "metal" if alu else "horn", (HORN_ALU if alu else HORN).copy().apply_transform(M @ translation_matrix([*SHAFT, 14.05])))
    if f in ARMOR:
        add(key, "pla", load(V + ARMOR[f] + ".stl").copy().apply_transform(M))
L = trimesh.load("./_dev/legacy/C_logo_letters_ACCENT.stl").apply_transform(rotation_matrix(np.pi / 2, [1, 0, 0]))
L.apply_translation(np.array([0.84, 66.0, 7.0]) - np.array([L.bounds.mean(0)[0], L.bounds[1][1], L.bounds.mean(0)[2]]))
add("body", "accent", L)
for nm, mat in (("electronics_plate_inplace", "pla"), ("pi_deck_inplace", "pla")):
    add("body", mat, trimesh.load(V + nm + ".stl"))
for nm, mat in (("ref_pca", "pca"), ("ref_mods", "module"), ("ref_pi", "pcb"), ("ref_cam", "pcb")):
    add("body", mat, trimesh.load(H + nm + ".stl"))
add("shell", "pla", trimesh.load(H + "hull_inplace.stl")); add("shell", "accent", trimesh.load(H + "hull_text_inlay.stl"))
index = []
for (key, mat), ms in groups.items():
    fn = f"{key}__{mat}.stl"; trimesh.util.concatenate(ms).export(O + fn); index.append({"group": key, "mat": mat, "file": fn})
json.dump({"joints": joints, "parts": index}, open("./_dev/blend4/rig.json", "w"), indent=1)
print(len(index), "part files;", len(joints), "joints")
print(L.bounds.round(2).tolist())
