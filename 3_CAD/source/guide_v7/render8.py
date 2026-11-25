"""python render8.py -- in.glb out.png view w h frame margin   (frame: all | hl)"""
import bpy, sys, math, os
from mathutils import Vector, Matrix

FAM = {'base': (0.36, 0.37, 0.40), 'bottom_stiffeners': (0.36, 0.37, 0.40), 'top_stiffeners': (0.36, 0.37, 0.40), 'battery_mount': (0.36, 0.37, 0.40),
       'electronics_plate': (0.44, 0.45, 0.48), 'pi_deck': (0.44, 0.45, 0.48),
       'bracket_A': (0.26, 0.40, 0.60), 'bracket_B_alu': (0.18, 0.52, 0.50), 'servo_cap': (0.82, 0.62, 0.16),
       'femur': (0.46, 0.52, 0.28), 'tibia': (0.52, 0.34, 0.24), 'armor_femur': (0.74, 0.74, 0.76), 'armor_shin': (0.74, 0.74, 0.76),
       'REF_MG995': (0.05, 0.05, 0.06), 'horn_alu': (0.80, 0.81, 0.84), 'bearing_623': (0.78, 0.79, 0.81),
       'REF_pca9685_x2': (0.30, 0.18, 0.55), 'REF_raspberry_pi4': (0.10, 0.42, 0.22), 'REF_camera': (0.10, 0.42, 0.22),
       'REF_buck_sbec': (0.16, 0.30, 0.55), 'battery': (0.16, 0.17, 0.20), 'REF_fan_x2': (0.08, 0.08, 0.09),
       'top_hull': (0.14, 0.14, 0.15), 'top_hull_text_ACCENT': (0.8, 0.81, 0.83), 'wire': (0.24, 0.10, 0.06)}
NEW = (0.93, 0.45, 0.08); GHOST = (0.55, 0.55, 0.57)
V = {"iso": (1, -1, 0.8), "backiso": (0.6, 1, 0.55), "top": (0, 0, 1), "under": (0.5, -0.6, -0.8), "front": (0, 1, 0.3), "hero": (1, -1.25, 0.55)}


def render(glb, out, view, w, h, frame='all', margin=1.0):
    res = (int(w), int(h)); margin = float(margin)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = int(os.environ.get("SAMPLES", "20")); sc.cycles.use_denoising = True
    sc.render.film_transparent = True
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.view_settings.view_transform = "Standard"
    sc.world = bpy.data.worlds.new("W"); sc.world.use_nodes = True; sc.world.node_tree.nodes["Background"].inputs[1].default_value = 0.9
    bpy.ops.import_scene.gltf(filepath=glb)
    fix = Matrix.Rotation(math.radians(-90), 4, "X")
    for o in bpy.data.objects:
        if o.parent is None: o.matrix_world = fix @ o.matrix_world
    bpy.context.view_layer.update()
    mats, objs, hl, wn = {}, [], [], []
    for o in bpy.data.objects:
        if o.type != "MESH": continue
        role, fam = o.name.split("|")[0], o.name.split("|")[1]
        if role in ("new", "wirenew") and fam != "REF_MG995":
            col, alpha = NEW, 1.0
            if role == "new": hl.append(o)
            else: wn.append(o)
        elif role == "new":
            col, alpha = FAM[fam], 1.0; hl.append(o)
        elif role == "ghost": col, alpha = GHOST, 0.13
        else: col, alpha = FAM.get(fam, (0.5, 0.5, 0.5)), 1.0
        key = (col, alpha)
        if key not in mats:
            m = bpy.data.materials.new(str(key)); m.use_nodes = True
            b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (*col, 1); b.inputs["Roughness"].default_value = 0.5
            b.inputs["Alpha"].default_value = alpha
            if fam in ("horn_alu", "bearing_623", "top_hull_text_ACCENT") and role != "new": b.inputs["Metallic"].default_value = 0.85
            mats[key] = m
        o.data.materials.clear(); o.data.materials.append(mats[key]); objs.append(o)
        if role == "ghost": o.visible_shadow = False
    use = (hl or wn) if frame == "hl" else objs
    allpts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    pts = [o.matrix_world @ Vector(c) for o in use for c in o.bound_box]
    lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)])
    ctr = (lo + hi) / 2
    alo = Vector([min(p[i] for p in allpts) for i in range(3)]); ahi = Vector([max(p[i] for p in allpts) for i in range(3)])
    r = (ahi - alo).length / 2
    d = Vector(V[view]).normalized()
    cam = bpy.data.objects.new("c", bpy.data.cameras.new("c")); sc.collection.objects.link(cam); sc.camera = cam
    cam.data.type = "ORTHO"; cam.data.clip_end = 1e6
    cam.location = ctr + d * r * 6
    cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    bpy.context.view_layer.update()
    xs, ys = [], []
    for p in pts:
        q = cam.matrix_world.inverted() @ p; xs.append(q.x); ys.append(q.y)
    cam.data.ortho_scale = max(max(xs) - min(xs), (max(ys) - min(ys)) * res[0] / res[1]) * 1.08 * margin
    cam.data.shift_x = ((max(xs) + min(xs)) / 2) / cam.data.ortho_scale
    cam.data.shift_y = ((max(ys) + min(ys)) / 2) / cam.data.ortho_scale
    for ang, e in (((50, 0, 30), 3.0), ((60, 0, -140), 1.2), ((-40, 0, 200), 0.6), ((180, 0, 0), 0.8)):
        L = bpy.data.objects.new("s", bpy.data.lights.new("s", "SUN")); L.data.energy = e; L.rotation_euler = [math.radians(v) for v in ang]; sc.collection.objects.link(L)
    sc.render.filepath = out; bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    render(*a)
