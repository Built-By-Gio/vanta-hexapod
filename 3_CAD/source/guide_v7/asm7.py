"""Standing GLB updated for the guide: new bracket B (DaFuRui Ø20 horn), new horn, +1 caps.
Every instance is located by fitting the old part (same vertex order) onto it."""
import trimesh, numpy as np
V = './v6/'
s = trimesh.load(V + 'hx/out/VANTA_standing.glb')


def fit(A, B):  # rigid T with T@A ~ B (Kabsch)
    ca, cb = A.mean(0), B.mean(0)
    U, _, Vt = np.linalg.svd((A - ca).T @ (B - cb))
    d = np.sign(np.linalg.det(Vt.T @ U.T))
    R = Vt.T @ np.diag([1, 1, d]) @ U.T
    T = np.eye(4); T[:3, :3] = R; T[:3, 3] = cb - R @ ca
    return T


def world(n):
    T, g = s.graph[n]; return s.geometry[g].copy().apply_transform(T)


oldB = trimesh.load(V + 'out2/VANTA/3_CAD/stl_in_place/bracket_B_alu.stl')
newB = trimesh.load(V + 'out6/VANTA/3_CAD/stl_in_place/bracket_B_alu.stl')
oldC = trimesh.load(V + 'out2/VANTA/3_CAD/stl_in_place/servo_cap_plus0.stl')
newC = trimesh.load(V + 'out6/VANTA/3_CAD/stl_in_place/servo_cap_plus1.stl')
# horn: joint/ frame is M applied to leg_1_tibia world (see joint/build.py). Bring joint/horn into old-B in-place frame.
jB = trimesh.load(V + 'joint/bracket_B_alu.stl')          # new B in joint frame
Tj = fit(newB.vertices, jB.vertices)                        # in-place -> joint frame
horn_ip = trimesh.load(V + 'joint/horn_alu.stl').apply_transform(np.linalg.inv(Tj))

out = trimesh.Scene()
err = []
for n in s.graph.nodes_geometry:
    lab = n.split('|')[-1]
    m = world(n)
    if lab == 'bracket_B_alu':
        T = fit(oldB.vertices, m.vertices); err.append(np.abs((oldB.copy().apply_transform(T)).vertices - m.vertices).max())
        out.add_geometry(newB.copy().apply_transform(T), node_name=n, geom_name=n)
        hn = n.replace('_bracket_B|bracket_B_alu', '_motor|horn_alu')
        out.add_geometry(horn_ip.copy().apply_transform(T), node_name=hn, geom_name=hn)
    elif lab == 'horn_alu':
        continue
    elif lab == 'servo_cap':
        T = fit(oldC.vertices, m.vertices); err.append(np.abs((oldC.copy().apply_transform(T)).vertices - m.vertices).max())
        out.add_geometry(newC.copy().apply_transform(T), node_name=n, geom_name=n)
    else:
        out.add_geometry(m, node_name=n, geom_name=n)
print('max fit error', max(err))
out.export(V + 'g7/stand7.glb')
# quick sanity: horn sits against bracket B and on the servo shaft
for L in (1, 4):
    for j in ('coxa', 'femur', 'tibia'):
        h = world  # noqa
print('nodes', len(out.graph.nodes_geometry))
