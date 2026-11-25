"""v4 vs v5 collision + clearance sweep.
1) all six legs posed together over sweep.py's grid: any part pair touching in v5 that never touched in v4 is reported.
2) each leg alone over sweep2/shellsweep's grid against the body (base, stiffeners, plate, deck, shell): min clearance v4 vs v5."""
import itertools, numpy as np, trimesh, sys
from v5asm import pose, pose5, mesh, cap, meshes, is_alu, alu_heads, G
H = G + "../hx2/out/"
HEADS = alu_heads()


def legs(version, ang, only=None):
    out = {}
    src = pose5(ang) if version == 5 else ((n, f[:-4] if f != "cap" else "servo_cap", cap if f == "cap" else mesh(f), M) for n, f, M in pose(ang))
    for n, label, m, M in src:
        if not n.startswith("leg_") or (only and not n.startswith(only)): continue
        if version == 5 and label == "bracket_B_alu": m = trimesh.util.concatenate([m, HEADS])
        mm = m.copy().apply_transform(M); mm.apply_scale(1000)
        out[f"{n}|{label}"] = mm
    return out


def kind(name):   # leg-agnostic pair key with v4/v5 labels unified ('femur_bracket_B|bracket_B', 'femur_motor|servo' ...)
    n, label = name.split("|")
    label = {"MG996R": "servo", "REF_MG995": "servo", "bracket_B_alu": "bracket_B"}.get(label, label)
    return n.split("_", 2)[2] + "|" + label


def internal(version):
    seen = {}
    for c, f_, t in itertools.product([-45, 0, 45], [-80, -40, 0, 40, 80], [-120, -70, -20, 0]):
        ang = {}
        for L in range(1, 7): ang.update({f"leg_{L}_coxa": c * (1 if L % 2 else -1), f"leg_{L}_femur": f_, f"leg_{L}_tibia": t})
        cm = trimesh.collision.CollisionManager()
        for k, m in legs(version, ang).items(): cm.add_object(k, m)
        _, names = cm.in_collision_internal(return_names=True)
        for a, b in names:
            key = tuple(sorted((kind(a), kind(b)))) + (("same leg",) if a.split("_")[1] == b.split("_")[1] else ("other leg",))
            seen.setdefault(key, set()).add((c, f_, t))
    return seen


def body(version):
    b = {"electronics_plate": trimesh.load(H + "electronics_plate_inplace.stl"), "pi_deck": trimesh.load(H + "pi_deck_inplace.stl"),
         "shell": trimesh.load(H + ("shell_inplace.stl" if version == 5 else "shell_inplace_v4.stl"))}
    src = pose5({}) if version == 5 else ((n, f[:-4], mesh(f), M) for n, f, M in pose({}) if f != "cap")
    for n, label, m, M in src:
        if n in ("base", "top_stiffeners", "bottom_stiffeners", "battery_mount"):
            mm = m.copy().apply_transform(M); mm.apply_scale(1000); b[n] = mm
    return b


def clearance(version):
    cms = {}
    for k, m in body(version).items():
        cms[k] = trimesh.collision.CollisionManager(); cms[k].add_object(k, m)
    worst = {}
    for c, f_, t in itertools.product([-40, -20, 0, 20, 40], [-40, 0, 40, 80], [-110, -60, -20]):
        for L in range(1, 7):
            cmL = trimesh.collision.CollisionManager()
            for k, m in legs(version, {f"leg_{L}_coxa": c, f"leg_{L}_femur": f_, f"leg_{L}_tibia": t}, f"leg_{L}_").items():
                if "coxa_motor|" in k: continue          # the coxa servo itself sits in the base pocket
                cmL.add_object(k, m)
            for bn, cmB in cms.items():
                d, (_, ln) = cmB.min_distance_other(cmL, return_names=True)
                key = (bn, kind(ln))
                if d < worst.get(key, (99,))[0]: worst[key] = (round(d, 2), (L, c, f_, t))
    return worst


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "both"
    if what in ("internal", "both"):
        s4, s5 = internal(4), internal(5)
        print("== leg part pairs touching in v5 but never in v4:")
        new = {k: v for k, v in s5.items() if k not in s4}
        for k, v in sorted(new.items()): print("  NEW", k, len(v), sorted(v)[:4])
        for k in s5:
            if k in s4 and len(s5[k]) > len(s4[k]): print("  MORE", k, len(s4[k]), "->", len(s5[k]))
        print("  (v4 pairs:", len(s4), " v5 pairs:", len(s5), ")")
    if what in ("clearance", "both"):
        w4, w5 = clearance(4), clearance(5)
        print("== closest leg approach to each body part (mm), v4 -> v5:")
        for bn in sorted({k[0] for k in w4} | {k[0] for k in w5}):
            a = min((v for k, v in w4.items() if k[0] == bn), default=None); b = min((v for k, v in w5.items() if k[0] == bn), default=None)
            bk = min(((v, k[1]) for k, v in w5.items() if k[0] == bn), default=None)
            print(f"  {bn:20s} v4 {a}   v5 {b}   ({bk[1] if bk else ''})")
