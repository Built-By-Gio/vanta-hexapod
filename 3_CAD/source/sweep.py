import xml.etree.ElementTree as ET, numpy as np, trimesh, itertools, sys
from trimesh.transformations import euler_matrix, translation_matrix, rotation_matrix
DELTA = float(sys.argv[1]); MODE = sys.argv[2]
R = ET.parse("hexapod.urdf").getroot()
def T(o):
    if o is None: return np.eye(4)
    return translation_matrix([float(v) for v in o.get("xyz", "0 0 0").split()]) @ euler_matrix(*[float(v) for v in o.get("rpy", "0 0 0").split()], "sxyz")
links = {l.get("name"): l for l in R.findall("link")}
child = {j.find("child").get("link"): j for j in R.findall("joint")}
S = np.diag([1e-3] * 3 + [1])
bA = trimesh.load("bracket_A.stl")
if MODE == "new":
    v = bA.vertices.copy(); v[v[:, 0] < -34, 0] -= DELTA; bA = trimesh.Trimesh(v, bA.faces)
cap = trimesh.load("cap0.stl").apply_translation([20.05, 9.75, -30.0])
meshes = {"bracket_A.stl": bA}
def mesh(f):
    if f not in meshes: meshes[f] = trimesh.load({"MG996R.stl": "servo_simple.stl", "battery.stl": "hw_battery.stl", "electronics.stl": "elec_simple.stl"}.get(f, f))
    return meshes[f]
def pose(angles):
    W = {}
    def world(n):
        if n in W: return W[n]
        if n not in child: W[n] = np.eye(4); return W[n]
        j = child[n]; M = world(j.find("parent").get("link")) @ T(j.find("origin"))
        a = angles.get(j.get("name"), 0.0)
        if a: M = M @ rotation_matrix(np.radians(a), [float(x) for x in j.find("axis").get("xyz").split()])
        W[n] = M; return M
    out = []
    for n, l in links.items():
        v = l.find("visual")
        if v is None: continue
        f = v.find("geometry/mesh").get("filename").split("/")[-1]
        M = world(n) @ T(v.find("origin")) @ S
        out.append((n, f, M))
        if MODE == "new" and f == "MG996R.stl": out.append((n + "_cap", "cap", M))
    return out
def objs(angles):
    cm = {}
    for n, f, M in pose(angles):
        m = cap if f == "cap" else mesh(f)
        cm[n + "|" + f] = m.copy().apply_transform(M @ np.diag([1000, 1000, 1000, 1]) if False else M)
    return cm
watch = ("bracket_A", "cap")
hits = {}
grid = list(itertools.product([-45, 0, 45], [-80, -40, 0, 40, 80], [-120, -70, -20, 0]))
for ci, (c, f_, t) in enumerate(grid):
    ang = {}
    for L in range(1, 7): ang.update({f"leg_{L}_coxa": c * (1 if L % 2 else -1), f"leg_{L}_femur": f_, f"leg_{L}_tibia": t})
    cm = trimesh.collision.CollisionManager()
    o = objs(ang)
    for k, m in o.items(): cm.add_object(k, m)
    _, names = cm.in_collision_internal(return_names=True)
    for a, b in names:
        if not any(w in a or w in b for w in watch): continue
        key = tuple(sorted([a.split("|")[0].replace("leg_1_", "L_").split("_cap")[0] + ("|cap" if "_cap" in a else "|" + a.split("|")[1]), b.split("|")[0] + ("|cap" if "_cap" in b else "|" + b.split("|")[1])]))
        hits.setdefault(key, []).append((c, f_, t))
for k, v in sorted(hits.items()): print(k, len(v), v[:4])
print("total pairs", len(hits))
