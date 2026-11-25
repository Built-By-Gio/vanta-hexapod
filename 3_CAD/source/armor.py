"""v6 leg armour (cosmetic): 2 plates per femur (over both servos), 1 shin plate per tibia (outer face).
Thin: 1.2mm plate + 0.8mm raised rib + printed hex bolt bosses. Fixed with CA glue or double-sided tape (no screws).
Writes print STLs (flat) to print/stl and assembly copies (part frames) to gg/v5."""
import sys, math, numpy as np, trimesh
from shapely.geometry import Polygon, box as sbox
D = "./_dev/"
sys.path[:0] = [D + "gg", D + "lite"]
import v5asm
from hexcut import sec

T, RIB, BOSS = 1.2, 0.8, 1.0
prism = lambda poly, z0, z1: trimesh.creation.extrude_polygon(poly, z1 - z0).apply_translation([0, 0, z0])
hexagon = lambda x, y, r: Polygon([(x + r * math.cos(math.radians(a)), y + r * math.sin(math.radians(a))) for a in range(0, 360, 60)])


def plate(poly, bolts):
    """flat plate in its own XY: base T, inset rib, hex bosses; z up = outer face"""
    parts = [prism(poly, 0, T), prism(poly.buffer(-4.5, join_style=2), T - 0.1, T + RIB)] + [prism(hexagon(x, y, 2.2), T - 0.1, T + RIB + BOSS) for x, y in bolts]
    return trimesh.boolean.union(parts, engine="manifold")


P5 = {n: (l, m, M) for n, l, m, M in v5asm.pose5({}, armour=False)}
nat = lambda part, frame: np.linalg.inv(P5[frame][2]) @ P5[part][2]
# femur: plate outline in femur native (x, z), between the clevises, trimmed 5mm at the knee end so a fully folded tibia clears it
srv = [P5[f"leg_2_{k}_motor"][1].copy().apply_transform(nat(f"leg_2_{k}_motor", "leg_2_femur")) for k in ("femur", "tibia")]
z0, z1 = min(s.bounds[0][2] for s in srv), max(s.bounds[1][2] for s in srv)
x0, x1 = -4.5, 66.5
fprof = Polygon([(x0 + 7, z0), (x1 - 7, z0), (x1, z0 + 7), (x1, z1 - 7), (x1 - 7, z1), (x0 + 7, z1), (x0, z1 - 7), (x0, z0 + 7)])
fem = plate(fprof, [(x0 + 6, z0 + 6), (x1 - 6, z0 + 6), (x0 + 6, z1 - 6), (x1 - 6, z1 - 6)])
# shin: tibia outline in tibia native (y, z), skipping the bracket-A flange (y > 30) and the tip (y < -66: grip tape goes there)
tsec = sec(P5["leg_2_tibia"][1], 0, 0.0)
tprof = Polygon(max(getattr(tsec, "geoms", [tsec]), key=lambda g: g.area).exterior).intersection(sbox(-66, -100, 30, 100)).buffer(-0.6, join_style=2)
cy, cz = tprof.centroid.coords[0]
shin = plate(tprof, [(y, z) for y, z in ((cy + 22, cz), (cy - 22, cz), (cy, cz)) if tprof.buffer(-3).contains(Polygon(hexagon(y, z, 2.2)))])
Mt = P5["leg_2_tibia"][2]
OUT = 1.0 if (Mt[:3, :3] @ [1.0, 0, 0])[0] > 0 else -1.0       # leg 2 points +x in the body frame: which native x face is outward

if __name__ == "__main__":
    P = D + "hx2/print/stl/"
    for k, m in (("13_armor_femur_x12", fem), ("14_armor_shin_x6", shin)):
        m = m.copy(); m.apply_translation([-m.bounds.mean(0)[0], -m.bounds.mean(0)[1], -m.bounds[0][2]]); m.export(P + k + ".stl")
        print(k, m.extents.round(1), round(m.volume / 1000, 2), "cm3")
    # assembly copies: femur plates on both rails (y = +-14.6 out), shin on the outward native-x face
    sides = []
    for s in (-1, 1):
        v = fem.vertices; sides.append(trimesh.Trimesh(np.c_[v[:, 0], s * (14.6 + v[:, 2]), v[:, 1]], fem.faces if s < 0 else fem.faces[:, ::-1]))
    trimesh.util.concatenate(sides).export(D + "gg/v5/armor_femur.stl")
    v = shin.vertices
    trimesh.Trimesh(np.c_[OUT * (10.1 + v[:, 2]), v[:, 0], v[:, 1]], shin.faces if OUT > 0 else shin.faces[:, ::-1]).export(D + "gg/v5/armor_shin.stl")
    print("assembly copies written; shin on native", "+x" if OUT > 0 else "-x")
