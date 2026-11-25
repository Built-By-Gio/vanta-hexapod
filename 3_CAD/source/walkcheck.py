"""Collisions over the real gait: every frame of blend4/walk.json (controller tripod walk), all six legs, v6 parts incl. armour.
Prints any contact that involves armour / bracket_B_alu, plus the joint-angle range the gait actually uses."""
import json, numpy as np, trimesh
from sweep_v5 import legs, kind
NAMES = {"FR": 1, "MR": 2, "RR": 3, "RL": 4, "ML": 5, "FL": 6}
walk = json.load(open("./_dev/blend4/walk.json"))
rng = np.array([[a for leg in fr["joints"].values() for a in leg] for fr in walk]).reshape(len(walk), 6, 3)
print("gait range (controller deg) coxa %.0f..%.0f femur %.0f..%.0f tibia %.0f..%.0f" % (rng[..., 0].min(), rng[..., 0].max(), rng[..., 1].min(), rng[..., 1].max(), rng[..., 2].min(), rng[..., 2].max()), flush=True)
hits = {}
for i, fr in enumerate(walk[::3]):
    ang = {}
    for leg, (c, f, t) in fr["joints"].items():
        L = NAMES[leg]; ang.update({f"leg_{L}_coxa": -c, f"leg_{L}_femur": f, f"leg_{L}_tibia": t - 73.0})
    cm = trimesh.collision.CollisionManager()
    for k, m in legs(5, ang).items(): cm.add_object(k, m)
    _, names = cm.in_collision_internal(return_names=True)
    for a, b in names:
        if any(w in a or w in b for w in ("armor", "bracket_B_alu")) and not ("bracket_A" in a + b and "bracket_B" in a + b and a.split("_")[1] == b.split("_")[1]):
            hits.setdefault(tuple(sorted((kind(a), kind(b)))) + (("same leg",) if a.split("_")[1] == b.split("_")[1] else ("other leg",)), []).append(i * 3)
print("contacts during the walk:", {k: (len(v), v[:5]) for k, v in hits.items()} or "none", flush=True)
print("WALK DONE", flush=True)
