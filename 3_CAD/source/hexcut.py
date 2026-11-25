import trimesh, numpy as np
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
from shapely import affinity

def sec(m, ax, z):
    n = np.eye(3)[ax]
    s = m.section(plane_origin=n * z, plane_normal=n)
    if s is None: return Polygon()
    o = [i for i in range(3) if i != ax]
    polys = []
    for e in s.discrete:
        pass
    p2, T = s.to_2D()
    # map 2D back to the two remaining world axes
    out = []
    for p in p2.polygons_full:
        def mp(cs):
            c = np.array(cs); c3 = trimesh.transform_points(np.c_[c, np.zeros(len(c))], T)
            return c3[:, o]
        out.append(Polygon(mp(p.exterior.coords), [mp(i.coords) for i in p.interiors]))
    return unary_union(out).buffer(0)

def slab_region(m, ax, z0, z1, step=0.25, margin=2.5, clear=0.6):
    lo, hi = m.bounds[:, ax]
    inside = [sec(m, ax, z) for z in np.arange(z0 + 0.05, z1, step)]
    reg = inside[0]
    for s in inside[1:]: reg = reg.intersection(s)
    outside = [sec(m, ax, z) for z in np.r_[np.arange(lo + 0.05, z0 - 0.05, step), np.arange(z1 + 0.05, hi, step)]]
    if outside: reg = reg.difference(unary_union(outside).buffer(clear))
    return reg.buffer(-margin)

def hex_poly(cx, cy, r, rot=0):
    a = np.radians(np.arange(6) * 60 + 30 + rot)
    return Polygon(np.c_[cx + r * np.cos(a), cy + r * np.sin(a)])

def hex_cells(region, pitch, rib, rot=0, minfrac=1.0, origin=None):
    if region.is_empty: return []
    r = (pitch - rib) / np.sqrt(3)  # circumradius from flat-to-flat (pitch-rib)
    minx, miny, maxx, maxy = region.bounds
    ox, oy = origin if origin is not None else ((minx + maxx) / 2, (miny + maxy) / 2)
    dx, dy = pitch, pitch * np.sqrt(3) / 2
    cells = []
    for j in range(int(-(oy - miny) / dy) - 2, int((maxy - oy) / dy) + 3):
        for i in range(int(-(ox - minx) / dx) - 2, int((maxx - ox) / dx) + 3):
            x = ox + i * dx + (dx / 2 if j % 2 else 0); y = oy + j * dy
            h = hex_poly(x, y, r)
            if region.contains(h): cells.append(h)
    return cells

def cut(m, ax, cells, z0, z1):
    if not cells: return m
    o = [i for i in range(3) if i != ax]
    prisms = []
    for h in cells:
        p = trimesh.creation.extrude_polygon(h, z1 - z0)
        # extrude along local z -> map local (x,y,z) to world (o0,o1,ax)
        v = np.zeros_like(p.vertices)
        v[:, o[0]] = p.vertices[:, 0]; v[:, o[1]] = p.vertices[:, 1]; v[:, ax] = p.vertices[:, 2] + z0
        q = trimesh.Trimesh(v, p.faces if np.linalg.det(np.eye(3)[[o[0], o[1], ax]]) > 0 else p.faces[:, ::-1])
        prisms.append(q)
    tool = trimesh.boolean.union(prisms, engine='manifold') if len(prisms) > 1 else prisms[0]
    return trimesh.boolean.difference([m, tool], engine='manifold')

def grams(m, walls=3, infill=0.15, dens=1.24):
    V = m.volume / 1000; A = m.area / 100
    sh = min(V, A * walls * 0.042)
    return (sh + infill * (V - sh)) * dens
