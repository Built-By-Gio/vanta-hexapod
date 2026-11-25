import trimesh, numpy as np
from holes import find_holes
DRILL_R = 1.4

def cyl(ax, c, r, a, b):
    T = np.eye(4)
    if ax == 0: T[:3, :3] = trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0])[:3, :3]
    if ax == 1: T[:3, :3] = trimesh.transformations.rotation_matrix(-np.pi/2, [1, 0, 0])[:3, :3]
    p = c.copy(); p[ax] = (a + b) / 2; T[:3, 3] = p
    return trimesh.creation.cylinder(radius=r, height=b - a, transform=T, sections=48)

def selftap(m, rmin=1.9, rmax=2.4, axes=(0, 1, 2)):
    holes = [h for h in find_holes(m, rmin, rmax) if h['ax'] in axes]
    fills, drills = [], []
    for h in holes:
        ax, c, r = h['ax'], h['c'], h['r']
        o = [i for i in range(3) if i != ax]
        d = np.linalg.norm(m.vertices[:, o] - c[o], axis=1)
        z = m.vertices[(np.abs(d - r) < 0.15) & (m.vertices[:, ax] > h['z0'] - 1) & (m.vertices[:, ax] < h['z1'] + 1), ax]
        a, b = z.min(), z.max()
        fills.append(cyl(ax, c, r + 0.15, a, b))
        drills.append(cyl(ax, c, DRILL_R, a - 0.3, b + 0.3))
    out = trimesh.boolean.union([m] + fills, engine='manifold')
    out = trimesh.boolean.difference([out] + drills, engine='manifold')
    return out, len(holes)
