"""v6 mech hull: replaces shell.py. Faceted armour built tight round the real contents (v5 electronics layout, camera 5mm lower).
Low centre deck just over the Pi, one pod over the GPIO jumper plugs, camera head at the front; panel seams, bolt bosses, louvres, visor, VANTA/MADE BY GIO inlays.
Sits inside the v5 shell envelope, so leg clearance can only improve. Prints upright (skirt down) with tree supports.
Writes out/hull_inplace.stl + out/hull_text_inlay.stl (body frame)."""
import json, math, itertools, os, tempfile, numpy as np, trimesh
from shapely.geometry import Polygon, Point, box as sbox
from shapely.ops import unary_union
import body2 as B

U = dict(engine="manifold")
TM = trimesh.transformations
OUTER = Polygon(json.load(open("free_region.json"))).buffer(-1.0, join_style=1).buffer(1.0, join_style=1).simplify(0.05)
Z0, ZS = B.PLATE_TOP, B.DECK_TOP + 2.6          # skirt from the plate up to the shoulder; screw bosses sit on the deck
WALL, GAP = 1.6, 2.0
LENS_Z = B.DECK_TOP + 20 - B.CAM_DROP
# what the hull must clear (x, y, z ranges): Pi board+parts, USB/ethernet, GPIO jumper plugs (+ mirrored bump for symmetry), camera wall/ribs/board
PI_UP = 4.0           # Pi sits 4mm higher (9mm bosses) so the servo leads can fold over the PCA plugs under it
PI = [((-28, 28), (-54.5, 30.5), (52 + PI_UP, 62 + PI_UP)), ((-26, 26), (-56.5, -34.5), (52 + PI_UP, 69 + PI_UP))]
# GPIO jumpers use pins 1-29 (PCA #1 on 1/3/5/14, PCA #2 on bus 3: 17/7/29/20, buck on 2/4/6/9); pin 1 is the end away from the USB ports.
# Housings top out ~z71, +4 for the wire bend. Only this strip needs the height, so it gets one pod; the rest of the roof stays low.
JUMP = ((-28, -20), (-16, 25), (52 + PI_UP, 75 + PI_UP))
# two 30x30x7 fans under the roof, blowing down on the Pi; held by 4 screws each through the roof
FANS = [(0.0, -19.0), (0.0, 13.0)]
FAN_S, FAN_T, FAN_HOLE = 30.0, 7.0, 24.0
FAN_TOP = 74.0                                   # inner roof face; fans hang from it
FAN_BOX = ((-15.25, 15.25), (-34.25, 28.25), (52 + PI_UP, FAN_TOP - GAP))
CAM = [((-17.5, 17.5), (57, 60), (47, 79 - B.CAM_DROP)), ((-17.5, -16), (45, 57), (47, 61)), ((16, 17.5), (45, 57), (47, 61)),
       ((-12.5, 12.5), (60, 61.6), (52.5 - B.CAM_DROP, 76.5 - B.CAM_DROP))]
DIRS = np.array([d for d in itertools.product([-1, 0, 1], repeat=3) if any(d)], float)
DIRS /= np.linalg.norm(DIRS, axis=1)[:, None]


def grow(boxes, m):      # box corners pushed out m in 26 directions: the hull gets crisp 45-degree chamfers
    return np.array([np.array(c) + d * m for (x, y, z) in boxes for c in itertools.product(x, y, z) for d in DIRS])


def ring(poly, z, keep=lambda p: True):
    pts = [p for p in list(poly.exterior.coords)[:-1] if keep(p)]
    return np.c_[np.array(pts), np.full(len(pts), z)]


def prism(poly, z0, z1):
    out = [trimesh.creation.extrude_polygon(g, z1 - z0).apply_translation([0, 0, z0]) for g in getattr(poly, "geoms", [poly]) if g.area > 0.01]
    return trimesh.util.concatenate(out) if len(out) > 1 else out[0]


def armour(m, inset):
    base = OUTER.buffer(-inset, join_style=2)
    hulls = [np.r_[ring(base, ZS), grow(PI + [FAN_BOX], m)]]
    hulls.append(grow([JUMP, (JUMP[0], JUMP[1], (ZS, ZS + 1))], m))   # one armoured pod over the jumper plugs
    hulls.append(np.r_[grow(CAM, m), ring(sbox(-17.5 - m, 36, 17.5 + m, 60), ZS)])
    return trimesh.boolean.union([trimesh.convex.convex_hull(h) for h in hulls], **U)


def hexboss(c, n, r=2.6, h=1.2):
    b = prism(Polygon([(r * math.cos(math.radians(a)), r * math.sin(math.radians(a))) for a in range(0, 360, 60)]), -1.0, h)
    z = np.array([0, 0, 1.0]); n = np.asarray(n, float) / np.linalg.norm(n)
    if abs(n @ z) < 0.999: b.apply_transform(TM.rotation_matrix(math.acos(n @ z), np.cross(z, n)))
    return b.apply_translation(c)


def text_on(outer, txt, size, sel, depth=0.6):
    """text inlay (depth mm into the surface) centred on the largest facet passing sel(normal, centre); reads upright"""
    from build123d import Text, extrude, export_stl, FontStyle, Align
    f = max(outer.facets, key=lambda f: outer.area_faces[f].sum() if sel(outer.face_normals[f[0]], outer.triangles_center[f].mean(0)) else 0)
    n = outer.face_normals[f[0]]; c = outer.triangles_center[f].mean(0)
    up = np.array([0, 0, 1.0]) - n * n[2]; up /= np.linalg.norm(up); x = np.cross(up, n)
    t = os.path.join(tempfile.gettempdir(), "_txt.stl")
    export_stl(extrude(Text(txt, size, font_path="./_dev/fonts/Archivo-ExtraBold.ttf",
                            align=(Align.CENTER, Align.CENTER)), amount=2 * depth), t)
    m = trimesh.load(t)
    T = np.eye(4); T[:3, 0], T[:3, 1], T[:3, 2], T[:3, 3] = x, up, n, c - n * depth
    return trimesh.boolean.intersection([m.apply_transform(T), outer], **U)


def fan_mounts(h):
    """locating frame round each fan, hex grille over its blades, 4 screw holes through the roof"""
    from hexcut import hex_cells
    frames, cuts = [], []
    for fx, fy in FANS:
        a, b = FAN_S / 2 + 0.25, FAN_S / 2 + 1.45
        frames.append(prism(sbox(fx - b, fy - b, fx + b, fy + b).difference(sbox(fx - a, fy - a, fx + a, fy + a)), FAN_TOP - 3.5, FAN_TOP + 0.5))
        holes = [(fx + sx * FAN_HOLE / 2, fy + sy * FAN_HOLE / 2) for sx in (-1, 1) for sy in (-1, 1)]
        grille = Point(fx, fy).buffer(13.8).difference(unary_union([Point(p).buffer(3.4) for p in holes]))
        cuts += [prism(c, FAN_TOP - 0.5, FAN_TOP + 6) for c in hex_cells(grille, 6.0, 1.4, origin=(fx, fy))]
        cuts += [trimesh.creation.cylinder(1.7, 12, transform=TM.translation_matrix([x, y, FAN_TOP + 2])) for x, y in holes]
    h = trimesh.boolean.union([h, *frames], **U)
    return trimesh.boolean.difference([h, *cuts], **U)


def hull():
    outer = trimesh.boolean.union([prism(OUTER, Z0, ZS), armour(GAP + WALL, 4.5)], **U)
    inner = trimesh.boolean.union([prism(OUTER.buffer(-WALL), Z0 - 1, ZS - WALL), prism(OUTER.buffer(-6.1), ZS - WALL - 0.1, ZS + 0.5), armour(GAP, 6.1)], **U)
    skin = trimesh.boolean.difference([outer, trimesh.boolean.union([prism(OUTER.buffer(-0.8), Z0 - 1, ZS), armour(GAP + WALL - 0.8, 5.3)], **U)], **U)
    h = trimesh.boolean.difference([outer, inner], **U)
    # screw bosses on the deck at the 4 posts, reached through ports in the armour
    bosses = [trimesh.creation.cylinder(5.5, ZS - B.DECK_TOP, transform=TM.translation_matrix([x, y, (ZS + B.DECK_TOP) / 2])) for x, y in B.POSTS]
    h = trimesh.boolean.union([h, *bosses], **U)
    for x, y in B.POSTS:
        h = trimesh.boolean.difference([h, trimesh.creation.cylinder(1.7, 20, transform=TM.translation_matrix([x, y, ZS])),
                                        trimesh.creation.cylinder(4.0, 60, transform=TM.translation_matrix([x, y, ZS + 30.0]))], **U)
    cuts = [trimesh.boolean.intersection([skin, prism(unary_union([sbox(-10.5, -80, -9.5, 80), sbox(9.5, -80, 10.5, 80),
                                                                    sbox(-60, -14.5, 60, -13.5), sbox(-60, 25.5, 60, 26.5)]), ZS + 1, 100)], **U),   # panel seams
            trimesh.boolean.intersection([skin, prism(sbox(-15, 40, 15, 80), LENS_Z - 4.5, LENS_Z + 4.5)], **U),                                      # visor recess
            trimesh.creation.cylinder(5.6, 30, transform=TM.rotation_matrix(np.pi / 2, [1, 0, 0]) @ TM.translation_matrix([0, LENS_Z, -60])),        # lens
            prism(unary_union([sbox(-16, y - 1.6, 16, y + 1.6) for y in (-50.0, -43.0)]), ZS + 2, 100)]                               # louvres over the Pi
    for sx in (-1, 1):
        for y in (-50.0, 0.0, 50.0):
            cuts.append(prism(sbox(min(sx * 25, sx * 47), y - 9, max(sx * 25, sx * 47), y + 9), Z0 - 1, Z0 + 10))                                  # servo leads
    h = trimesh.boolean.difference([h, *cuts], **U)
    bolts = []
    for x, y in [(-24, -10.0), (-24, 19.0)] + [(sx * 12, 52.0) for sx in (-1, 1)]:
        loc, _, tri = outer.ray.intersects_location([[x, y, 150]], [[0, 0, -1]])
        if len(loc): i = np.argmax(loc[:, 2]); bolts.append(hexboss(loc[i], outer.face_normals[tri[i]]))
    h = trimesh.boolean.union([h, *bolts], **U)
    h = fan_mounts(h)
    text = trimesh.util.concatenate([text_on(outer, "VANTA", 7.0, lambda n, c: n[0] < -0.45 and n[2] > 0.2 and c[2] > ZS + 3 and -50 < c[1] < -20),
                                     text_on(outer, "VANTA", 7.0, lambda n, c: n[0] > 0.45 and n[2] > 0.2 and c[2] > ZS + 3 and -50 < c[1] < -20),
                                     text_on(outer, "MADE BY GIO", 3.6, lambda n, c: n[1] < -0.45 and n[2] < 0.8 and c[2] > ZS + 4)])
    h = trimesh.boolean.difference([h, text], **U)
    return h, text, outer


if __name__ == "__main__":
    h, text, outer = hull()
    env = prism(OUTER, Z0, 82.5)
    old = trimesh.load("out/shell_inplace.stl")
    print("hull top %.1f (v5 shell %.1f), height %.1f mm; outer volume %d cm3 (v5 %d); outside v5 envelope %.2f mm3; watertight %s; %.1f cm3 plastic"
          % (h.bounds[1][2], old.bounds[1][2], h.bounds[1][2] - Z0, outer.volume / 1000, env.volume / 1000,
             trimesh.boolean.difference([outer, env], **U).volume, h.is_watertight, h.volume / 1000))
    h.export("out/hull_inplace.stl"); text.export("out/hull_text_inlay.stl")
