import bpy, json, math
from mathutils import Matrix, Vector
D = "./_dev/blend4/"
rig = json.load(open(D + "rig.json")); walk = json.load(open(D + "walk.json"))
FEMUR_Z = 8.7
TIB_OFF = -73.0
RANGES = {"coxa": (-35, 35), "femur": (-80, 85), "tibia": (-52, 73)}

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system = "METRIC"; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = "MILLIMETERS"
sc.render.fps = 30; sc.frame_start = 1; sc.frame_end = len(walk)

MATS = {"pla": (0.02, 0.021, 0.024, 0.6), "accent": (0.78, 0.79, 0.81, 0.3), "tpu": (0.55, 0.06, 0.04, 0.7), "servo": (0.02, 0.02, 0.025, 0.35),
        "metal": (0.75, 0.76, 0.78, 0.25), "horn": (0.85, 0.85, 0.82, 0.5), "battery": (0.15, 0.17, 0.2, 0.4), "pcb": (0.05, 0.25, 0.1, 0.4),
        "pca": (0.12, 0.08, 0.3, 0.4), "module": (0.08, 0.16, 0.32, 0.4)}
mats = {}
for k, (r, g, b, rough) in MATS.items():
    m = bpy.data.materials.new(k); m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]; bsdf.inputs["Base Color"].default_value = (r, g, b, 1); bsdf.inputs["Roughness"].default_value = rough
    if k in ("metal", "accent"): bsdf.inputs["Metallic"].default_value = 1.0
    m.diffuse_color = (r * 1.6 + 0.04, g * 1.6 + 0.04, b * 1.6 + 0.04, 1)
    mats[k] = m

def col(name, parent=None):
    c = bpy.data.collections.new(name); (parent or sc.collection).children.link(c); return c
C_ROBOT = col("VANTA"); C_SHELL = col("Shell (hide to see inside)", C_ROBOT); C_BODY = col("Body", C_ROBOT); C_LEGS = col("Legs", C_ROBOT)

arm_data = bpy.data.armatures.new("VANTA_rig"); arm = bpy.data.objects.new("VANTA_rig", arm_data)
C_ROBOT.objects.link(arm); arm.show_in_front = True; arm_data.display_type = "STICK"
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="EDIT")
eb = arm_data.edit_bones
root = eb.new("body"); root.head = (0, 0, 0); root.tail = (0, -40, 0)
bone_rest = {}
for name, j in rig["joints"].items():
    J = Matrix(j["matrix"]); ax = Vector(j["axis"]).normalized()
    R = Vector((0, 1, 0)).rotation_difference(ax).to_matrix().to_4x4()
    Mb = J @ R
    b = eb.new(name)
    b.head = Mb.to_translation(); b.tail = b.head + (Mb.to_3x3() @ Vector((0, 22, 0)))
    b.align_roll(Mb.to_3x3() @ Vector((0, 0, 1)))
    bone_rest[name] = Mb
for name, j in rig["joints"].items():
    eb[name].parent = eb[j["parent"]] if j["parent"] else root
    eb[name].use_connect = False
bpy.ops.object.mode_set(mode="POSE")
for name in rig["joints"]:
    pb = arm.pose.bones[name]; pb.rotation_mode = "XYZ"
    pb.lock_rotation = (True, False, True); pb.lock_location = (True, True, True); pb.lock_scale = (True, True, True)
    kind = name.split("_")[1]
    lo, hi = RANGES[kind]
    if kind == "coxa": lo, hi = -hi, -lo
    if kind == "tibia": lo, hi = lo + TIB_OFF, hi + TIB_OFF
    c = pb.constraints.new("LIMIT_ROTATION"); c.use_limit_y = True; c.min_y = math.radians(lo); c.max_y = math.radians(hi); c.owner_space = "LOCAL"
bpy.ops.object.mode_set(mode="OBJECT")
bpy.context.view_layer.update()

for p in rig["parts"]:
    bpy.ops.wm.stl_import(filepath=D + "parts/" + p["file"])
    o = bpy.context.selected_objects[0]
    o.name = f"{p['group']}_{p['mat']}"
    for c in o.users_collection: c.objects.unlink(o)
    g = p["group"]
    (C_SHELL if g == "shell" else C_BODY if g == "body" else C_LEGS).objects.link(o)
    o.data.materials.append(mats[p["mat"]])
    if g in ("body", "shell"):
        o.parent = arm
    else:
        Jw = Matrix(rig["joints"][g]["matrix"])
        o.parent = arm; o.parent_type = "BONE"; o.parent_bone = g
        bpy.context.view_layer.update()
        o.matrix_world = Jw
    bpy.ops.object.shade_auto_smooth() if False else None

def leg_angles(fr):
    out = {}
    for leg, (c, f, t) in fr["joints"].items():
        out[f"{leg}_coxa"] = -c; out[f"{leg}_femur"] = f; out[f"{leg}_tibia"] = t + TIB_OFF
    return out

act = bpy.data.actions.new("Walk")
arm.animation_data_create(); arm.animation_data.action = act
for i, fr in enumerate(walk):
    frame = i + 1
    p = fr["pose"]
    arm.location = (-p["y"], p["x"] - walk[0]["pose"]["x"], p["z"] - FEMUR_Z)
    arm.rotation_euler = (-p["pitch"], p["roll"], p["yaw"])
    arm.keyframe_insert("location", frame=frame); arm.keyframe_insert("rotation_euler", frame=frame)
    for name, a in leg_angles(fr).items():
        pb = arm.pose.bones[name]; pb.rotation_euler = (0, math.radians(a), 0); pb.keyframe_insert("rotation_euler", frame=frame)

sc.frame_set(1)
cam_d = bpy.data.cameras.new("Camera"); cam_d.lens = 50; cam_d.clip_start = 10; cam_d.clip_end = 100000
cam = bpy.data.objects.new("Camera", cam_d); sc.collection.objects.link(cam); sc.camera = cam
cam.location = (-620, -620, 430)
tr = cam.constraints.new("TRACK_TO"); tr.target = arm; tr.track_axis = "TRACK_NEGATIVE_Z"; tr.up_axis = "UP_Y"
sun_d = bpy.data.lights.new("Sun", "SUN"); sun_d.energy = 3.5; sun = bpy.data.objects.new("Sun", sun_d); sun.rotation_euler = (math.radians(50), 0, math.radians(30)); sc.collection.objects.link(sun)
bpy.ops.mesh.primitive_plane_add(size=6000, location=(0, 300, -0.2)); fl = bpy.context.active_object; fl.name = "Floor"
fm = bpy.data.materials.new("floor"); fm.use_nodes = True; fm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.5, 0.5, 0.52, 1); fl.data.materials.append(fm)
sc.world = bpy.data.worlds.new("World"); sc.world.color = (0.6, 0.62, 0.65)
for area in []: pass
bpy.ops.wm.save_as_mainfile(filepath=D + "VANTA_rigged_walk.blend")
print("saved")
