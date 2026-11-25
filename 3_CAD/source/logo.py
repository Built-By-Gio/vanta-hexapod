import json, sys
sys.path.insert(0, "./_dev/hx2")
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from build123d import *
import trimesh, numpy as np
from shapely.geometry import Polygon as SPoly

FACE_Y, DEPTH, CLEAR = 66.0, 1.0, 0.12

raw = json.load(open("./_dev/up1/logo2d.json"))
polys = [SPoly(p["ext"], p["holes"]) for p in raw]
logo = unary_union(polys).buffer(0.25, join_style=1).buffer(-0.25, join_style=1)
logo = unary_union([g for g in (logo.geoms if logo.geom_type == "MultiPolygon" else [logo]) if g.area > 1.0])
logo = logo.simplify(0.02)
from shapely import affinity
logo = affinity.translate(logo, 0, (14.0 - logo.bounds[3] - logo.bounds[1]) / 2)
pieces = list(logo.geoms) if logo.geom_type == "MultiPolygon" else [logo]
print("logo pieces", len(pieces), [round(p.area, 1) for p in pieces], [round(v, 1) for v in logo.bounds])

def to_face(sp):
    sp = orient(sp, 1.0)
    f = Face(Wire.make_polygon([Vector(x, y, 0) for x, y in list(sp.exterior.coords)[:-1]], close=True))
    for h in sp.interiors:
        f -= Face(Wire.make_polygon([Vector(x, y, 0) for x, y in list(h.coords)[:-1]], close=True))
    return f

def solid_xz(sp, y0, y1):
    out = None
    for p in (sp.geoms if sp.geom_type == "MultiPolygon" else [sp]):
        s = extrude(to_face(p), amount=y1 - y0, dir=(0, 0, 1))
        out = s if out is None else out + s
    return out

def place(s, y_front, depth):
    return Pos(0, y_front, 0) * Rot(90, 0, 0) * s

pocket2d = logo.buffer(CLEAR, join_style=2)
P = place(solid_xz(pocket2d, 0, DEPTH + 0.3), FACE_Y + 0.3, DEPTH)
L = place(solid_xz(logo.buffer(-0.03, join_style=2), 0, DEPTH), FACE_Y, DEPTH)
print("pocket bbox", P.bounding_box().min, P.bounding_box().max)
print("letters bbox", L.bounding_box().min, L.bounding_box().max)
export_stl(P, "pocket_tool.stl"); export_stl(L, "logo_inplace.stl")
