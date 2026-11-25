"""headless sanity check of the rigged walk file: bones, locks, limits, frames, foot contact, shell collection"""
import bpy, math
bpy.ops.wm.open_mainfile(filepath="./_dev/blend4/VANTA_rigged_walk.blend")
sc = bpy.context.scene
arm = bpy.data.objects["VANTA_rig"]
bones = [b for b in arm.pose.bones if b.name != "body"]
print("bones", len(bones), "frames", sc.frame_start, sc.frame_end, "fps", sc.render.fps)
bad = [b.name for b in bones if tuple(b.lock_rotation) != (True, False, True) or not any(c.type == "LIMIT_ROTATION" for c in b.constraints)]
print("bones without single-axis lock + limit:", bad)
for b in bones[:3]:
    c = [c for c in b.constraints if c.type == "LIMIT_ROTATION"][0]
    print(" ", b.name, round(math.degrees(c.min_y)), "..", round(math.degrees(c.max_y)))
print("shell collection:", [c.name for c in bpy.data.collections if "Shell" in c.name])
for f in (1, 30, 60, 90, 120, 150, 180):
    sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get()
    zs = []
    for o in bpy.data.objects:
        if o.name.endswith("_tibia_tpu"):
            oe = o.evaluated_get(dg); zs.append(round(min((oe.matrix_world @ v.co).z for v in oe.data.vertices), 1))
    print("frame", f, "foot min z", sorted(zs))
