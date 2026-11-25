"""Blender (headless): import the GLB, keyframe the assembly, write timeline.json (+ 2D anchors), render frames.
blender -b --python bl_build.py -- test | render [first last]"""
import bpy, sys, os, json, math, time
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
S = r"."
sys.path.insert(0, S)
import vanta_steps as VS
FPS, W, H = VS.FPS, 1920, 1080
MODE = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["test"]
GREY, RED = (0.80, 0.80, 0.80, 1.0), (0.92, 0.10, 0.05, 1.0)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=S + r"\vanta_zip\VANTA\3_CAD\VANTA_standing.glb")
sc = bpy.context.scene
objs = {o.name: o for o in bpy.data.objects if o.type == "MESH"}
print("import rot", tuple(round(math.degrees(a)) for a in next(iter(objs.values())).rotation_euler))
for o in objs.values():
    o.rotation_mode = 'XYZ'; o.rotation_euler = (-math.pi / 2, 0, 0)   # the GLB holds Z-up data; the importer assumed Y-up (and left objects in quaternion mode)
    o.color = GREY
bpy.context.view_layer.update()
LOCAL_C = {n: sum((Vector(c) for c in o.bound_box), Vector()) / 8 for n, o in objs.items()}
CENT = {n: objs[n].matrix_world @ LOCAL_C[n] for n in objs}
print("hull centre", tuple(round(v, 1) for v in CENT["top_hull"]), "tibia tip z", round(min((objs["leg_1_tibia|tibia"].matrix_world @ Vector(c)).z for c in objs["leg_1_tibia|tibia"].bound_box), 1))
NAMES = sorted(objs); print("NAMES sample", [n for n in NAMES if "femur" in n][:6])

# ---------- selectors ----------
BODY = {"base": "base|base", "bottom_stiff": "bottom_stiffeners|bottom_stiffeners", "battery_mount": "battery_mount|battery_mount", "battery": "battery|REF_battery",
        "top_stiff": "top_stiffeners|top_stiffeners", "plate": "electronics_plate", "pca": "REF_pca9685_x2", "buck": "REF_buck_sbec", "deck": "pi_deck",
        "pi": "REF_raspberry_pi4", "cam": "REF_camera", "fans": "REF_fan_x2", "hull": "top_hull", "hull_text": "top_hull_text_ACCENT"}
KIND = {"servo": "|REF_MG995", "cap": "|servo_cap", "bearing": "|bearing_623", "horn": "|horn_alu", "A": "|bracket_A", "B": "|bracket_B_alu", "frame": "|femur", "bar": "|tibia"}


def leg_of(n): return int(n.split("_")[1]) if n.startswith("leg_") else None
def joint_of(n): return n.split("|")[0].split("_")[2] if n.startswith("leg_") else None


def select(sel):
    """'base' | 'servo' | 'coxa:horn' | 'armor:shin' | 'femur:B@2' | 'all' -> list of object names"""
    if sel == "all": return list(NAMES)
    if sel in BODY: return [BODY[sel]]
    leg = None
    if "@" in sel: sel, leg = sel.split("@"); leg = int(leg)
    joint, kind = sel.split(":") if ":" in sel else (None, sel)
    out = []
    for n in NAMES:
        if not n.startswith("leg_"): continue
        if leg and leg_of(n) != leg: continue
        if joint == "armor":
            if "armor" not in n or not n.endswith("|armor_" + kind): continue
        else:
            if "armor" in n: continue
            if joint and joint_of(n) != joint: continue
            if not n.endswith(KIND[kind]): continue
        out.append(n)
    assert out, sel
    return out


# ---------- offsets ----------
AXIS = {}
for n in NAMES:
    if n.endswith("|horn_alu"):
        motor = n.replace("|horn_alu", "|REF_MG995"); AXIS[(leg_of(n), joint_of(n))] = (CENT[n] - CENT[motor]).normalized()
BODY_EXPLODE = {"base": (0, 0, 0), "bottom_stiff": (0, 0, -55), "battery_mount": (0, 0, -85), "battery": (0, 0, -115), "top_stiff": (0, 0, 45), "plate": (0, 0, 80),
                "pca": (0, 0, 110), "buck": (0, 0, 110), "deck": (0, 0, 150), "pi": (0, 0, 180), "cam": (0, 0, 180), "fans": (0, 0, 230), "hull": (0, 0, 260), "hull_text": (0, 0, 260)}
BODY_INV = {v: k for k, v in BODY.items()}


def explode(n):
    if n in BODY_INV: return Vector(BODY_EXPLODE[BODY_INV[n]])
    c = CENT[n]; u = Vector((c.x, c.y, 0)).normalized(); leg, joint = leg_of(n), joint_of(n)
    if "armor" in n: return Vector((0, 0, 50)) if n.endswith("|armor_femur") else u * 250
    R = {"coxa": 60, "femur": 130, "tibia": 200}[joint]; a = AXIS[(leg, joint)]
    sub = {"|REF_MG995": a * 0, "|servo_cap": -a * 25, "|bearing_623": -a * 40, "|horn_alu": a * 25, "|bracket_B_alu": a * 40, "|bracket_A": a * 55, "|femur": a * 0, "|tibia": Vector((0, 0, -30))}
    return u * R + sub[next(k for k in sub if n.endswith(k))]


BENCH = {}
for n in NAMES:
    if n.endswith("|REF_MG995"):
        leg, joint = leg_of(n), joint_of(n)
        g = Vector(((leg - 3.5) * 85, {"coxa": 70, "femur": -15, "tibia": -100}[joint], 0)); off = g - CENT[n]
        for k in ("|REF_MG995", "|servo_cap", "|bearing_623", "|horn_alu"): BENCH[n.replace("|REF_MG995", k)] = off
for key, x in (("battery", -200), ("buck", -70), ("pca", 60), ("pi", 190)):
    n = BODY[key]; BENCH[n] = Vector((x, 210, 0)) - CENT[n] + Vector((0, 0, 8))


def rest(n, layout):
    if layout == "exploded": return explode(n)
    if layout == "bench": return BENCH.get(n, Vector((0, 0, 0)))
    return Vector((0, 0, 0))


# ---------- keyframes ----------
def F(t): return int(round(t * FPS))
state_vis = {n: True for n in NAMES}; state_red = {n: False for n in NAMES}


def key_vis(n, f, vis):
    o = objs[n]; o.hide_render = not vis; o.keyframe_insert("hide_render", frame=f); state_vis[n] = vis


def key_loc(n, f, v):
    o = objs[n]; o.location = v; o.keyframe_insert("location", frame=f)


def key_col(n, f, red):
    o = objs[n]; o.color = RED if red else GREY; o.keyframe_insert("color", frame=f); state_red[n] = red


for n in NAMES: key_vis(n, 1, True); key_loc(n, 1, Vector()); key_col(n, 1, False)
visible = set(NAMES)
FLY = {}   # seg id -> {name: (fstart, fend)}
for seg in VS.SEGMENTS:
    f0, f1 = seg["f0"], seg["f1"]
    if seg["reset"]: visible = set()
    for s in seg["show"]: visible |= set(select(s))
    for s in seg["hide"]: visible -= set(select(s))
    # fly-in schedule
    fly = {}
    t = seg["t0"] + 0.6
    if seg["new"]:
        if seg["per_leg"]:
            groups = [[m for m in select(s) if leg_of(m) == VS.LEAD] for s in seg["new"]]
            for g in groups:
                for m in g: fly[m] = (F(t), F(t + 1.2))
                t += seg["stagger"]
            t += 0.5
            for leg in (1, 3, 6, 4, 5):
                for s in seg["new"]:
                    for m in select(s):
                        if leg_of(m) == leg: fly[m] = (F(t), F(t + 1.2))
                t += 0.35
        else:
            for s in seg["new"]:
                ms = select(s)
                for i, m in enumerate(ms):
                    ts = t + (seg["spread"] * i / max(1, len(ms) - 1) if seg["spread"] else 0)
                    fly[m] = (F(ts), F(ts + 1.2))
                t += seg["stagger"]
    FLY[seg["id"]] = fly
    for n in NAMES:
        on = n in visible or n in fly
        if state_vis[n] != (n in visible): key_vis(n, f0, n in visible)
        if n in fly:
            fs, fe = fly[n]
            if not state_vis[n] or n not in visible: key_vis(n, fs, True)
            start = rest(n, seg["layout"]) + (Vector(seg["explode_override"]) if seg["explode_override"] else explode(n))
            key_loc(n, f0, start); key_loc(n, fs, start); key_loc(n, fe, rest(n, seg["layout"])); key_loc(n, f1, rest(n, seg["layout_end"]))
            if not state_red[n]: key_col(n, fs - 4, False)
            key_col(n, fs, True); key_col(n, f1, True); key_col(n, f1 + 8, False)
            visible.add(n)
        elif on:
            key_loc(n, f0, rest(n, seg["layout"])); key_loc(n, f1, rest(n, seg["layout_end"]))
    for s in seg["highlight"]:
        for n in select(s):
            if n not in visible: continue
            key_col(n, f0 + 2, False); key_col(n, f0 + 12, True); key_col(n, f1, True); key_col(n, f1 + 8, False)
def all_fcurves(act):
    if hasattr(act, "fcurves") and not act.is_action_layered if hasattr(act, "is_action_layered") else False: return list(act.fcurves)
    out = []
    for layer in act.layers:
        for strip in layer.strips:
            for cb in strip.channelbags: out += list(cb.fcurves)
    return out
for act in bpy.data.actions:
    for fcu in all_fcurves(act):
        if fcu.data_path == "hide_render":
            for kp in fcu.keyframe_points: kp.interpolation = "CONSTANT"

# ---------- camera ----------
cam_d = bpy.data.cameras.new("Cam"); cam_d.lens = 50; cam_d.clip_start = 5; cam_d.clip_end = 20000
cam = bpy.data.objects.new("Cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
tgt = bpy.data.objects.new("Tgt", None); sc.collection.objects.link(tgt)
tr = cam.constraints.new("TRACK_TO"); tr.target = tgt; tr.track_axis = "TRACK_NEGATIVE_Z"; tr.up_axis = "UP_Y"


def target_point(seg):
    t = seg["view"]["target"]
    if isinstance(t, str):
        n = select(t)[0]; return CENT[n] + rest(n, seg["layout"])
    return Vector(t)


def pose(seg, lt):
    v = seg["view"]; d = Vector(v["dir"]).normalized(); k = max(0.0, min(1.0, lt / seg["dur"]))
    az = math.atan2(d.y, d.x) + math.radians(v.get("orbit", 0)) * k; el = math.asin(d.z)
    dist = v["dist"] + (v.get("dist2", v["dist"]) - v["dist"]) * k
    T = target_point(seg)
    return T + dist * Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el))), T


def smooth(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)


prev = None
for i, seg in enumerate(VS.SEGMENTS):
    for f in range(seg["f0"], seg["f1"] + 1):
        lt = (f - seg["f0"]) / FPS
        L, T = pose(seg, lt)
        if prev and lt < 1.2:
            k = smooth(lt / 1.2); Lp, Tp = pose(prev, prev["dur"] + lt); L = Lp.lerp(L, k); T = Tp.lerp(T, k)
        cam.location = L; cam.keyframe_insert("location", frame=f)
        tgt.location = T; tgt.keyframe_insert("location", frame=f)
        cam_d.shift_x = seg["shift"]; cam_d.keyframe_insert("shift_x", frame=f)
    prev = seg

# ---------- render settings ----------
sc.render.engine = "BLENDER_WORKBENCH"; sh = sc.display.shading
sh.light = "STUDIO"; sh.color_type = "OBJECT"; sh.show_cavity = True; sh.cavity_type = "BOTH"; sh.show_object_outline = True; sh.show_shadows = False
sh.cavity_ridge_factor = 1.6; sh.cavity_valley_factor = 1.6; sh.curvature_ridge_factor = 1.2; sh.curvature_valley_factor = 1.2
sc.display.render_aa = "8"; sc.render.film_transparent = True
sc.render.resolution_x = W; sc.render.resolution_y = H; sc.render.resolution_percentage = 100; sc.render.fps = FPS
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGBA"; sc.render.image_settings.compression = 30
sc.view_settings.view_transform = "Standard"
sc.frame_start = 1; sc.frame_end = VS.TOTAL_FRAMES

# ---------- timeline + anchors ----------
if MODE[0] in ("test", "anchors"):
    out = []
    for seg in VS.SEGMENTS:
        d = {k: v for k, v in seg.items() if k != "view"}
        names = [select(t)[0] if t else None for t in seg["targets"]]
        anchors = []
        for f in range(seg["f0"], seg["f1"] + 1):
            sc.frame_set(f); row = []
            for n in names:
                if n is None: row.append(None); continue
                p = objs[n].matrix_world @ LOCAL_C[n]; v = world_to_camera_view(sc, cam, p)
                row.append([round(v.x * W, 1), round((1 - v.y) * H, 1)])
            anchors.append(row)
        d["anchor_names"] = names; d["anchors"] = anchors; d["fly"] = {n: list(v) for n, v in FLY[seg["id"]].items()}
        out.append(d)
    json.dump({"fps": FPS, "W": W, "H": H, "total": VS.TOTAL_FRAMES, "segments": out}, open(S + r"\timeline.json", "w"), indent=0)
    print("timeline.json written", VS.TOTAL_FRAMES, "frames")
    bpy.ops.wm.save_as_mainfile(filepath=S + r"\vanta_film.blend")

os.makedirs(S + r"\frames", exist_ok=True)
if MODE[0] == "test":
    os.makedirs(S + r"\test", exist_ok=True); t = time.time()
    picks = []
    for seg in VS.SEGMENTS:
        picks += [(seg["id"] + "_a", seg["f0"] + int(2.0 * FPS)), (seg["id"] + "_b", seg["f0"] + int(min(seg["dur"] - 1, 9) * FPS))]
    for name, f in picks:
        sc.frame_set(f); sc.render.filepath = S + rf"\frames\f_{f:05d}.png"; bpy.ops.render.render(write_still=True)
    print("test renders", len(picks), "in", round(time.time() - t, 1), "s")
elif MODE[0] == "render":
    if len(MODE) > 2: sc.frame_start, sc.frame_end = int(MODE[1]), int(MODE[2])
    sc.render.filepath = S + r"\frames\f_"; sc.render.use_overwrite = False; sc.render.use_placeholder = True
    t = time.time(); bpy.ops.render.render(animation=True); print("rendered", sc.frame_start, sc.frame_end, "in", round(time.time() - t), "s")






