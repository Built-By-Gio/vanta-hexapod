import trimesh, numpy as np
from selftap import cyl
Y, Z = -13.0, 10.0
OUT, WALLF, SHO, PIN_END = -28.15, -22.15, -21.65, -17.65
CB_DEPTH = 1.75

def bracket_623(m):
    c = np.array([0, Y, Z], float)
    m = trimesh.boolean.difference([m, cyl(0, c, 4.2, WALLF + 0.02, PIN_END + 0.3)], engine='manifold')
    m = trimesh.boolean.union([m, cyl(0, c, 2.2, WALLF - 0.1, SHO)], engine='manifold')
    m = trimesh.boolean.difference([m, cyl(0, c, 1.4, OUT - 1, SHO + 1),
                                    cyl(0, c, 3.2, OUT - 1, OUT + CB_DEPTH)], engine='manifold')
    return m
