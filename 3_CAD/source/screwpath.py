"""For every M3-ish hole in the assembled robot (zero pose, leg 1 + body), list the material stack along its axis.
usage: python screwpath.py [leg_prefix]   -> prints one line per unique screw path"""
import numpy as np, trimesh, warnings, sys
warnings.filterwarnings("ignore")
exec(open("sweep.py").read().split("def objs")[0].replace("DELTA = float(sys.argv[1]); MODE = sys.argv[2]", "DELTA = 4.5; MODE = 'new'"))
sys.path.insert(0, "../st")
from holes import find_holes
meshes["MG996R.stl"] = trimesh.load("hw_MG996R.stl")
LEG = sys.argv[1] if len(sys.argv) > 1 else "leg_1_"
parts = {}
for n, f, M in pose({}):
    if f in ("electronics.stl", "battery.stl") or (n.startswith("leg_") and not n.startswith(LEG)): continue
    m = (cap if f == "cap" else mesh(f)).copy().apply_transform(M); m.apply_scale(1000)
    parts[n] = m
seen, HC = [], {}
for n, f, M in pose({}):
    if n not in parts or "motor" in n or f == "cap": continue
    if f not in HC: HC[f] = find_holes(mesh(f), 1.0, 2.5, 0.4)
    for h in HC[f]:
        ax = np.eye(3)[h["ax"]]
        Mm = M.copy(); Mm[:3, :] *= 1000
        c = trimesh.transform_points([h["c"]], Mm)[0]
        d = Mm[:3, :3] @ ax; d /= np.linalg.norm(d)
        if any(np.linalg.norm(np.cross(c - s, d)) < 1.0 and abs(d @ sd) > 0.99 for s, sd in seen): continue
        seen.append((c, d))
        # a part occupies station t if most of a ring of points just outside the hole wall is inside it;
        # 'hole' = the axis itself is open there, 'SOLID' = the screw would hit material
        e1 = np.cross(d, [0.577, 0.577, 0.577]); e1 /= np.linalg.norm(e1); e2 = np.cross(d, e1)
        ts = np.arange(-30, 30, 0.2)
        ring = [np.cos(a) * e1 + np.sin(a) * e2 for a in np.linspace(0, 2 * np.pi, 8, endpoint=False)]
        print(f"{n.replace(LEG, ''):22s} r{h['r']:.2f} c={np.round(c, 1).tolist()} dir={np.round(d, 2).tolist()}")
        for pn, pm in parts.items():
            if np.linalg.norm(np.clip(c, *pm.bounds) - c) > 32: continue
            pts = np.array([c + d * t + u * (h["r"] + 0.6) for t in ts for u in ring])
            occ = pm.contains(pts).reshape(len(ts), len(ring)).mean(1) >= 0.5
            if not occ.any(): continue
            axis_in = pm.contains(c + d * ts[:, None])
            edges = np.flatnonzero(np.diff(np.r_[0, occ.astype(int), 0]))
            for a, b in zip(edges[0::2], edges[1::2]):
                solid = axis_in[a:b].mean() > 0.5
                print(f"      {ts[a]:7.1f} .. {ts[b - 1] + 0.2:7.1f}  ({(b - a) * 0.2:5.1f})  {pn.replace(LEG, '')}{'  SOLID' if solid else ''}")
