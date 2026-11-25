"""Cycles render of a GLB, coloured by part label (text after '|'). Import render() or run:
python render5.py in.glb out.png view zoom w h [highlight,labels] [hide,labels] [only,name,prefixes]"""
import bpy, sys, math
from mathutils import Vector, Matrix

C = {"REF_MG995": (0.07, 0.07, 0.08), "horn_alu": (0.72, 0.74, 0.78), "bearing_623": (0.75, 0.76, 0.78),
     "top_hull_text_ACCENT": (0.8, 0.81, 0.83), "REF_raspberry_pi4": (0.1, 0.4, 0.2), "REF_camera": (0.1, 0.4, 0.2),
     "REF_pca9685_x2": (0.25, 0.17, 0.5), "insert": (0.8, 0.08, 0.06), "REF_buck_sbec": (0.15, 0.3, 0.55), "REF_battery": (0.2, 0.22, 0.26)}
PLA, NEW, DIM = (0.42, 0.43, 0.45), (0.93, 0.45, 0.08), (0.16, 0.16, 0.17)
V = {"iso": (1, -1, 0.8), "iso2": (-1, -1, 0.8), "back": (0, 1, 0.2), "backiso": (0.6, 1, 0.55), "low": (1, -1, 0.35), "top": (0, 0, 1),
     "under": (0.5, -0.6, -0.8), "front": (0, -1, 0.25), "side": (1, 0, 0.3)}


def render(glb, out, view, zoom, w, h, hl="-", hide="-", only="-"):
    res = (int(w), int(h)); zoom = float(zoom)
    hl = set(hl.split(",")) if hl != "-" else set()
    hide = set(hide.split(",")) if hide != "-" else set()
    only = only.split(",") if only != "-" else None
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 32; sc.cycles.use_denoising = True
    sc.render.film_transparent = True
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.view_settings.view_transform = "Standard"
    sc.world = bpy.data.worlds.new("W"); sc.world.use_nodes = True; sc.world.node_tree.nodes["Background"].inputs[1].default_value = 0.9
    bpy.ops.import_scene.gltf(filepath=glb)
    fix = Matrix.Rotation(math.radians(-90), 4, "X")
    for o in bpy.data.objects:
        if o.parent is None: o.matrix_world = fix @ o.matrix_world
    bpy.context.view_layer.update()
    mats, objs = {}, []
    for o in bpy.data.objects:
        if o.type != "MESH": continue
        name = o.name.split(".")[0]
        label = name.split("|")[-1]
        if label in hide or (only and not any(name.startswith(p) or label == p for p in only)):
            o.hide_render = True; continue
        col = NEW if (label in hl or name in hl) else C.get(label, DIM if label == "top_hull" else PLA)
        key = str(col)
        if key not in mats:
            m = bpy.data.materials.new(key); m.use_nodes = True
            b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (*col, 1); b.inputs["Roughness"].default_value = 0.45
            if label in ("horn_alu", "bearing_623", "top_hull_text_ACCENT"): b.inputs["Metallic"].default_value = 0.9
            mats[key] = m
        o.data.materials.clear(); o.data.materials.append(mats[key]); objs.append(o)
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)])
    ctr = (lo + hi) / 2; r = (hi - lo).length / 2
    d = Vector(V[view]).normalized()
    cam = bpy.data.objects.new("c", bpy.data.cameras.new("c")); sc.collection.objects.link(cam); sc.camera = cam
    cam.data.type = "ORTHO"; cam.data.clip_end = 1e6
    cam.location = ctr + d * r * 6
    cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    bpy.context.view_layer.update()
    xs, ys = [], []
    for p in pts:
        q = cam.matrix_world.inverted() @ p; xs.append(q.x); ys.append(q.y)
    cam.data.ortho_scale = max(max(xs) - min(xs), (max(ys) - min(ys)) * res[0] / res[1]) * 1.08 / zoom
    cam.data.shift_x = ((max(xs) + min(xs)) / 2) / cam.data.ortho_scale
    cam.data.shift_y = ((max(ys) + min(ys)) / 2) / cam.data.ortho_scale
    for ang, e in (((50, 0, 30), 3.0), ((60, 0, -140), 1.2), ((-40, 0, 200), 0.6), ((180, 0, 0), 0.8)):
        L = bpy.data.objects.new("s", bpy.data.lights.new("s", "SUN")); L.data.energy = e; L.rotation_euler = [math.radians(v) for v in ang]; sc.collection.objects.link(L)
    sc.render.filepath = out; bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    render(*a)
