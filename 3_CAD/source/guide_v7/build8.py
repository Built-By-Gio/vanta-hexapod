"""Per-step scenes for guide rev 8: cumulative builds, wires, and a progress inset per step.
Node names: role|family  with role in new / built / ghost / wire / wirenew."""
import os, trimesh, numpy as np
G = './v6/g7/'; O = G + 'glb8/'; os.makedirs(O, exist_ok=True); os.makedirs(G + 'r8', exist_ok=True)
S = trimesh.load(G + 'stand7.glb')
PART = {}
for n in S.graph.nodes_geometry:
    T, g = S.graph[n]; PART[n] = S.geometry[g].copy().apply_transform(T)
NODES = list(PART)


def fam(n):
    lab = n.split('|')[-1]
    return {'REF_battery': 'battery'}.get(lab, lab)


def leg(L, *kinds):
    out = []
    for n in NODES:
        if not n.startswith(f'leg_{L}_'): continue
        k = n.split('|')[0][len(f'leg_{L}_'):]
        for want in kinds:
            if k == want or k.startswith(want + '_') or k.startswith(want + '|'): out.append(n)
    return out


BODY0 = ['base|base']
STIFF = ['bottom_stiffeners|bottom_stiffeners', 'battery_mount|battery_mount', 'battery|REF_battery']
PLATE = ['top_stiffeners|top_stiffeners', 'electronics_plate', 'REF_pca9685_x2', 'REF_buck_sbec']
DECK = ['pi_deck', 'REF_raspberry_pi4', 'REF_camera']
HULL = ['top_hull', 'top_hull_text_ACCENT', 'REF_fan_x2']
COXA_SERVO = lambda L: [n for n in leg(L, 'coxa_motor', 'coxa_motor_cap') if 'horn' not in n]
COXA_JOINT = lambda L: leg(L, 'coxa_bracket_A', 'coxa_bracket_B') + [n for n in leg(L, 'coxa_motor') if 'horn' in n]
FEMUR_FRAME = lambda L: leg(L, 'femur_motor', 'femur_motor_cap', 'tibia_motor', 'tibia_motor_cap') + [n for n in leg(L, 'femur') if n.endswith('|femur')]
FEMUR_FRAME_NOHORN = lambda L: [n for n in FEMUR_FRAME(L) if 'horn' not in n]
FEMUR_JOINT = lambda L: leg(L, 'femur_bracket_A', 'femur_bracket_B') + [n for n in leg(L, 'femur_motor') if 'horn' in n]
TIBIA_JOINT = lambda L: leg(L, 'tibia_bracket_A', 'tibia_bracket_B') + [n for n in leg(L, 'tibia_motor') if 'horn' in n] + [n for n in leg(L, 'tibia') if n.endswith('|tibia')]
ARMOR = lambda L: leg(L, 'femur_armor', 'tibia_armor')
ALL = lambda f: [n for L in range(1, 7) for n in f(L)]

# ---------- wires ----------
C = {L: PART[f'leg_{L}_coxa_motor_cap|servo_cap'].centroid for L in range(1, 7)}
FC = {L: PART[f'leg_{L}_femur_motor_cap|servo_cap'].centroid for L in range(1, 7)}
TC = {L: PART[f'leg_{L}_tibia_motor_cap|servo_cap'].centroid for L in range(1, 7)}
# channel map: right legs (x>0) front board y=+24, left legs rear board y=-24. FR=1, MR=2, RR=3, FL=6, ML=5, RL=4
CH = {1: 0, 2: 3, 3: 6, 6: 0, 5: 3, 4: 6}


def header(L, j):
    ch = CH[L] + j
    return np.array([-26 + ch * 3.8, 24 if L <= 3 else -24, 42.0])


def smooth(pts, n=10):
    p = np.asarray(pts, float)
    if len(p) < 3: return p
    P = np.vstack([p[0], p, p[-1]]); out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-2]); return np.array(out)


def tube(pts, r=1.2):
    pts = smooth(pts); parts = []
    for a, b in zip(pts[:-1], pts[1:]):
        v = b - a; h = np.linalg.norm(v)
        if h < 1e-6: continue
        cyl = trimesh.creation.cylinder(r, h, sections=12)
        z = np.array([0, 0, 1.0]); d = v / h
        ax = np.cross(z, d)
        if np.linalg.norm(ax) > 1e-6: cyl.apply_transform(trimesh.transformations.rotation_matrix(np.arccos(np.clip(z @ d, -1, 1)), ax))
        elif d[2] < 0: cyl.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]))
        cyl.apply_translation((a + b) / 2); parts.append(cyl)
    for p in pts[1:-1:3]: parts.append(trimesh.creation.icosphere(1, r).apply_translation(p))
    return trimesh.util.concatenate(parts)


def coxa_wire(L, end='header'):
    c = C[L]; u = c[:2] / np.linalg.norm(c[:2])
    p0 = np.array([*(c[:2] - u * 21), 37.5])
    p1 = np.array([*(u * 34), 39.0])
    p2 = np.array([*(u * 20), 46.0])
    if end == 'loose': return [p0, p1, np.array([*(u * 16), 44.0])]
    return [p0, p1, p2, header(L, 0)]


def leg_wire(L, which, end='header'):
    start = FC[L] if which == 'femur' else TC[L]
    c = C[L]; u = c[:2] / np.linalg.norm(c[:2]); side = np.array([-u[1], u[0]]) * (6 if which == 'femur' else 11)
    p0 = start + np.array([0, 0, 5.0])
    rail = np.array([*(u * 165 + side * 1.4), 26.0])
    frame_in = np.array([*(u * 143 + side * 1.2), 26.0])
    joint = np.array([*(u * 104 + side * 0.9), 46.0])
    over = np.array([*(u * 72 + side * 0.6), 44.0])
    body = np.array([*(u * 44 + side * 0.4), 44.0])
    if end == 'frame': return [p0, rail, frame_in]
    if end == 'loose': return [p0, rail, frame_in, joint, over, np.array([*(u * 26 + side * 0.3), 46.0])]
    return [p0, rail, frame_in, joint, over, body, header(L, 1 if which == 'femur' else 2)]


def wires(kind, legs, end='header'):
    out = []
    for L in legs:
        if kind in ('coxa', 'all'): out.append(('coxa', L, coxa_wire(L, end)))
        if kind in ('leg', 'all'):
            out.append(('femur', L, leg_wire(L, 'femur', end))); out.append(('tibia', L, leg_wire(L, 'tibia', end)))
    return out


def scene(name, built=(), new=(), ghost=(), wire=(), wirenew=()):
    sc = trimesh.Scene(); i = 0
    for role, group in (('built', built), ('new', new), ('ghost', ghost)):
        for n in group:
            k = f'{role}|{fam(n)}|{i}'; i += 1
            sc.add_geometry(PART[n], node_name=k, geom_name=k)
    for role, group in (('wire', wire), ('wirenew', wirenew)):
        for kind, L, pts in group:
            k = f'{role}|wire|{i}'; i += 1
            sc.add_geometry(tube(pts), node_name=k, geom_name=k)
    f = O + name + '.glb'; sc.export(f); return f


ALLPARTS = NODES
jobs = []


def step(name, built, new, view, frame='hl', margin=2.2, wire=(), wirenew=(), inset=True, res=(1000, 900), hide_ghost_in_main=True):
    built = list(dict.fromkeys(built)); new = list(dict.fromkeys(new))
    f = scene(name, built, new, [], wire, wirenew)
    jobs.append((f, G + f'r8/{name}.png', view, res, frame, margin))
    if inset:
        done = set(built) | set(new)
        ghost = [n for n in ALLPARTS if n not in done]
        fi = scene(name + '_p', built, new, ghost)
        jobs.append((fi, G + f'r8/{name}_p.png', 'iso', (640, 520), 'all', 1.0))


T6 = BODY0 + ALL(COXA_SERVO)
T7 = T6 + STIFF
T8 = T7 + ALL(COXA_JOINT)
T10 = T8 + ALL(FEMUR_FRAME_NOHORN) + ALL(FEMUR_JOINT)
T11 = T10 + ALL(TIBIA_JOINT)
T12 = T11 + ALL(ARMOR)
T13 = T12 + PLATE
T16 = T13 + DECK
W_COXA_LOOSE = wires('coxa', range(1, 7), 'loose')
W_LEG_FRAME = lambda Ls: wires('leg', Ls, 'frame')
W_LEG_LOOSE = lambda Ls: wires('leg', Ls, 'loose')
W_ALL_LOOSE = W_COXA_LOOSE + W_LEG_LOOSE(range(1, 7))
W_ALL = wires('all', range(1, 7))

step('s05', [], ALL(COXA_SERVO) + [n for n in ALL(FEMUR_FRAME_NOHORN) if 'motor' in n], 'iso', 'all', 1.0, inset=True, res=(10, 10))  # placeholder main (not used)
jobs.pop(-2)   # keep only the progress inset for step 5
step('s06', BODY0, ALL(COXA_SERVO), 'under', 'all', 1.0)
step('s06b', BODY0, ALL(COXA_SERVO), 'iso', 'all', 1.0, wirenew=W_COXA_LOOSE, inset=False)
step('s07', T6, STIFF, 'under', 'all', 1.0, wire=W_COXA_LOOSE)
step('s08', T7, COXA_JOINT(1), 'iso', 'hl', 2.6, wire=W_COXA_LOOSE)
step('s09', [], FEMUR_FRAME_NOHORN(1), 'iso', 'all', 1.0, wirenew=W_LEG_FRAME([1]), inset=False)
step('s09_p', T8, ALL(FEMUR_FRAME_NOHORN), 'iso', 'all', 1.0, inset=True, res=(10, 10)); jobs.pop(-2)
step('s10', T8 + FEMUR_FRAME_NOHORN(1), FEMUR_JOINT(1), 'backiso', 'hl', 2.4, wire=W_COXA_LOOSE + W_LEG_FRAME([1]), wirenew=[w for w in W_LEG_LOOSE([1])])
step('s11', T10, TIBIA_JOINT(1), 'backiso', 'hl', 2.2, wire=W_ALL_LOOSE)
step('s12', T11, ARMOR(1), 'backiso', 'hl', 2.0, wire=W_ALL_LOOSE)
step('s13', T12, PLATE, 'iso', 'hl', 1.5, wire=W_ALL_LOOSE)
step('s15', T13, [], 'top', 'hl', 1.0, wirenew=W_ALL, res=(1000, 1000))
step('s16', T13, DECK, 'iso', 'hl', 1.5, wire=W_ALL)
step('s17', T16, [], 'iso', 'all', 1.0, wire=W_ALL)
step('s18', T16, HULL, 'iso', 'all', 1.0, wire=W_ALL)
with open(G + 'jobs8.txt', 'w') as f:
    for glb, png, view, res, frame, margin in jobs:
        f.write(f'{glb} {png} {view} {res[0]} {res[1]} {frame} {margin}\n')
print(len(jobs), 'jobs')
