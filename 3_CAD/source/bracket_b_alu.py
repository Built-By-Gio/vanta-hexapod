"""bracket_B for the DaFuRui 25T aluminium disc horn: Ø20 x 2 disc on a Ø9 x 4.5 hub (6.5 total), 4 threaded M3 holes on a 10mm square.
Native ggldnl frame: plate x 22.9 (servo side) .. 28.9, spline axis along x at (y 0, z 34).
The stock A-side (2 bolt holes at z 4) is untouched; the horn end becomes a hex pendant."""
import numpy as np, trimesh
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union

X0, X1 = 22.9, 28.9           # servo face, outer face
AX = (0.0, 34.0)              # spline axis (y, z)
DISC_R, DISC_D = 10.25, 2.4   # Ø20.5 pocket. 2.4 deep puts the disc top (hub on the spline shoulder + 6.5) where the tested horn's was, so the +0 caps still fit
HEX_R = 14.8                  # circumradius, vertex on z: leaves 2.5mm wall round the pocket at the flats
PCD, HOLE_R = 14.14, 1.65     # 10mm square = 14.14 across the diagonal
CENTER_R = 4.0                # window: reaches the horn's centre screw, clear of the 4 holes


def prism(poly, x0, x1):
    """extrude a (y, z) shapely polygon along +x from x0 to x1"""
    if poly.geom_type == "MultiPolygon":
        return trimesh.util.concatenate([prism(g, x0, x1) for g in poly.geoms])
    p = trimesh.creation.extrude_polygon(poly, x1 - x0)
    v = p.vertices[:, [2, 0, 1]].copy(); v[:, 0] += x0   # local (y,z,h) -> world (x=h, y, z)
    return trimesh.Trimesh(v, p.faces)  # (h,y,z) is an even permutation of (y,z,h): winding stays valid


def hexagon(r):
    a = np.radians(np.arange(6) * 60 + 90)
    return Polygon(np.c_[AX[0] + r * np.cos(a), AX[1] + r * np.sin(a)])


def slots():
    """4 round M3 clearance holes on the bolt circle (25 teeth x 4 holes: some tooth always lines them up within 1.8 deg)"""
    return unary_union([Point(AX[0] + PCD / 2 * np.cos(a), AX[1] + PCD / 2 * np.sin(a)).buffer(HOLE_R, 32) for a in np.radians([0, 90, 180, 270])])


def cbore_a_bolts(b):
    """2.9mm head counterbore on the two A-side bolts: a flat seat below the stock countersink; M3x8 reaches ~4.9mm into the insert"""
    return trimesh.boolean.difference([b] + [prism(Point(y, 4.0).buffer(3.25, 48), X1 - 2.9, X1 + 1) for y in (-5.0, 5.0)], engine="manifold")


def bracket_b_alu(stock):
    eng = dict(engine="manifold")
    fill = prism(Polygon([(-7, 12), (7, 12), (7, 40), (-7, 40)]), X0, X1)           # close the stock arm slot
    b = trimesh.boolean.union([stock, prism(hexagon(HEX_R), X0, X1), fill], **eng)
    cut = [prism(Point(*AX).buffer(DISC_R, 96), X0 - 1, X0 + DISC_D),
           prism(Point(*AX).buffer(CENTER_R, 48), X0, X1 + 1),
           prism(slots(), X0, X1 + 1)]
    return cbore_a_bolts(trimesh.boolean.difference([b] + cut, **eng))


if __name__ == "__main__":
    G = "./_dev/gg/"
    stock = trimesh.load(G + "bracket_B.stl")
    for name, b in (("bracket_B_alu", bracket_b_alu(stock)),):
        assert b.is_watertight
        print(name, b.bounds.round(2).tolist(), round(b.volume / 1000, 2), "cm3 (stock", round(stock.volume / 1000, 2), ")")
        b.export(G + name + ".stl")
