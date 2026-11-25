"""v6 checks: (1) every contact involving the armour plates or bracket_B_alu, all legs posed together inside the real joint limits;
any bracket_B_alu contact is re-tested with the stock bracket_B at the same pose (v4) to see if it is new.
(2) closest approach of each leg to the hull and body parts."""
import itertools, sys, numpy as np, trimesh
from sweep_v5 import legs, kind
from v5asm import pose5, G
H = G + "../hx2/out/"
NEW = ("armor", "bracket_B_alu")


def contacts(version, poses):
    out = {}
    for c, f_, t in poses:
        ang = {}
        for L in range(1, 7): ang.update({f"leg_{L}_coxa": c * (1 if L % 2 else -1), f"leg_{L}_femur": f_, f"leg_{L}_tibia": t})
        cm = trimesh.collision.CollisionManager()
        for k, m in legs(version, ang).items(): cm.add_object(k, m)
        _, names = cm.in_collision_internal(return_names=True)
        for a, b in names:
            if version == 4 or any(w in a or w in b for w in NEW):
                key = tuple(sorted((kind(a), kind(b)))) + (("same leg",) if a.split("_")[1] == b.split("_")[1] else ("other leg",))
                out.setdefault(key, set()).add((c, f_, t))
    return out


if __name__ == "__main__":
    grid = list(itertools.product([-35, 0, 35], [-80, -40, 0, 40, 85], [-125, -90, -60, -30, 0]))
    s6 = contacts(5, grid)
    print("== contacts involving armour / alu bracket B (joint limits):", flush=True)
    for k, v in sorted(s6.items()):
        note = ""
        if "bracket_B" in k[0] + k[1] and "armor" not in k[0] + k[1]:
            s4 = contacts(4, sorted(v)[:6])
            note = "  (stock bracket B also touches here: not new)" if k in s4 else "  NEW vs stock"
        print("  ", k, len(v), sorted(v)[:4], note, flush=True)
    print("  total", len(s6), flush=True)
    hull = trimesh.collision.CollisionManager(); hull.add_object("hull", trimesh.load(H + "hull_inplace.stl"))
    worst = (99, None)
    for c, f_, t in itertools.product([-35, -20, 0, 20, 35], [-40, 0, 40, 80], [-110, -60, -20]):
        for L in range(1, 7):
            cmL = trimesh.collision.CollisionManager()
            for k, m in legs(5, {f"leg_{L}_coxa": c, f"leg_{L}_femur": f_, f"leg_{L}_tibia": t}, f"leg_{L}_").items():
                if "coxa_motor|" not in k: cmL.add_object(k, m)
            d, (_, n) = hull.min_distance_other(cmL, return_names=True)
            if d < worst[0]: worst = (round(d, 2), (kind(n), L, c, f_, t))
    print("== closest any leg part comes to the hull:", worst, flush=True)
    print("SWEEP6 DONE", flush=True)
