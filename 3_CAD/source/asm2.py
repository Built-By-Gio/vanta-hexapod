"""Standing v5 assembly -> GLB.  usage: python asm2.py '<controller angles json or {}>' out.glb
angles: {"FR": [coxa, femur, tibia], ...} in controller degrees (stand.json style) or {} for the zero pose."""
import numpy as np, trimesh, json, sys, os, tempfile, warnings
warnings.filterwarnings("ignore")
D = "./_dev/"
sys.path[:0] = [D + "gg", D + "hx2"]
from v5asm import pose5, is_alu, V
from trimesh.transformations import translation_matrix as Tm
from build123d import export_stl
os.chdir(D + "hx2")
import body2 as B

NAMES = {"FR": 1, "MR": 2, "RR": 3, "RL": 4, "ML": 5, "FL": 6}
SHAFT = np.array([30.25, 9.75])          # spline axis in the MG995 mesh frame (export_rig.py)
H = D + "hx2/out/"


def tm(shapes):
    out = []
    for s in (shapes if isinstance(shapes, list) else [shapes]):
        t = os.path.join(tempfile.gettempdir(), "_t.stl"); export_stl(s, t); out.append(trimesh.load(t))
    return trimesh.util.concatenate(out)


def horn(alu):
    c = trimesh.creation
    if alu:   # 25T disc: Ø25 x 3 plate seated where the stock arm top sits, Ø9 hub under it
        return trimesh.util.concatenate([c.cylinder(12.5, 3.0, transform=Tm([0, 0, 15.8])), c.cylinder(4.5, 2.6, transform=Tm([0, 0, 13.0]))])
    return trimesh.util.concatenate([c.cylinder(4.5, 4.5, transform=Tm([0, 0, 2.25 + 14.05])), c.box([18, 6.0, 2.0], Tm([8, 0, 3.5 + 14.05])),
                                     c.cylinder(3.0, 2.0, transform=Tm([17, 0, 3.5 + 14.05]))])


def bearing():
    from trimesh.creation import annulus
    return trimesh.util.concatenate([annulus(1.5, 5.0, 4.0, transform=Tm([0, 0, -35.6 + 2.0]))])


def angles(ctrl):
    a = {}
    for leg, (c, f, t) in ctrl.items():
        L = NAMES[leg]; a.update({f"leg_{L}_coxa": -c, f"leg_{L}_femur": f, f"leg_{L}_tibia": t - 73.0})
    return a


if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else "{}"
    ctrl = json.load(open(a)) if a.endswith(".json") else json.loads(a)
    ctrl = ctrl.get("joints", ctrl)
    sc = trimesh.Scene()

    def put(m, M, name):
        m = m.copy().apply_transform(M); m.apply_scale(1000); sc.add_geometry(m, node_name=name, geom_name=name)

    for n, label, m, M in pose5(angles(ctrl)):
        if label == "electronics": continue
        put(m, M, f"{n}|{label}")
        if label == "REF_MG995" and n.startswith("leg_"):
            alu = is_alu(n)
            put(horn(alu), M @ Tm([*SHAFT, 0]), f"{n}|horn_{'alu' if alu else 'stock'}")
            put(bearing(), M @ Tm([*SHAFT, 0]), f"{n}|bearing_623")
    for k, f in (("electronics_plate", V + "electronics_plate_inplace.stl"), ("pi_deck", V + "pi_deck_inplace.stl"),
                 ("top_hull", H + "hull_inplace.stl"), ("top_hull_text_ACCENT", H + "hull_text_inlay.stl")):
        m = trimesh.load(f); sc.add_geometry(m, node_name=k, geom_name=k)
    for k, s in (("REF_pca9685_x2", B.pca_dummy()), ("REF_raspberry_pi4", B.pi_dummy()), ("REF_buck_sbec", B.module_dummies()), ("REF_camera", B.cam_dummy())):
        m = tm(s); sc.add_geometry(m, node_name=k, geom_name=k)
    out =sys.argv[2] if len(sys.argv) > 2 else D + "gg/asm5.glb"
    sc.export(out)
    print("ok", len(sc.geometry), "geometries", sc.bounds.round(1).tolist())
