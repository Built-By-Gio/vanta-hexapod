POST_TOP = 44.0
RISER_T = 2.8
DECK_Z = 56.7
DECK_T = 3.0
POSTS = [(33.0, 46.0), (33.0, -46.0), (-33.0, 46.0), (-33.0, -46.0)]
COLS = [(25.0, 36.0), (-25.0, 36.0), (21.5, -44.5), (-21.5, -44.5)]
COL_D = 9.0
INSERT_D = 4.2
INSERT_DEPTH = 6.0
M3 = 3.4
M2 = 2.4
OLD_DECK = [(34.41, 12.85), (36.42, 14.94), (38.21, 15.63), (38.21, 48.74), (23.34, 63.6), (-23.86, 63.58), (-38.19, 49.26), (-38.21, 42.21), (-35.7, 40.93), (-34.87, 39.92), (-34.27, 38.19), (-34.24, 22.32), (-34.57, 20.68), (-34.93, 20.0), (-26.0, 20.0), (-26.0, 30.3), (26.0, 30.3), (26.0, 12.3), (-26.0, 12.3), (-26.0, -12.3), (26.0, -12.3), (26.0, -30.3), (-26.0, -30.3), (-26.0, -40.0), (-36.0, -40.0), (-36.0, -14.55), (-37.1, -15.56), (-38.22, -16.06), (-38.19, -49.75), (-24.34, -63.6), (23.88, -63.56), (38.23, -49.2), (38.22, -16.13), (36.9, -15.74), (36.26, -15.29), (34.54, -13.54), (33.88, -11.94), (33.85, 10.99)]
DECK = [(14, 53.5), (14, 44), (26.5, 44), (29.8, 39.9), (29.8, 20.4), (30.0, 15.1), (29.1, 12.3), (29.1, -13.1), (30.0, -15.8), (33.4, -19.3), (33.4, -39.4), (29.5, -40.5), (26.8, -43.4), (26.2, -46.0), (26.6, -48.1), (27.8, -50.3), (29.2, -51.5), (22.1, -58.5), (-22.1, -58.5), (-29.2, -51.5), (-27.8, -50.3), (-26.6, -48.1), (-26.2, -46.0), (-26.8, -43.4), (-29.5, -40.5), (-33.4, -39.4), (-33.4, -19.3), (-30.0, -15.8), (-29.1, -13.1), (-29.1, 12.3), (-30.0, 15.1), (-29.8, 20.4), (-29.8, 39.9), (-26.5, 44), (-14, 44), (-14, 53.5)]
CAM_HOLE_SQ = 32.6
CAM_CY = 24.0
CAM_SPACER = 3.0
TONGUE_HOLES = [(9.0, 50.0), (-9.0, 50.0)]
SIDE_SLOTS = [(20.5, 27.5, -30.0, 8.0), (-27.5, -20.5, -30.0, 8.0)]
NOTCH_RECTS = [(30.4, 34.4, -31.25, -28.75), (30.4, 34.4, -25.25, -22.75), (26.8, 30.8, 22.75, 25.25), (26.8, 30.8, 28.75, 31.25), (-34.4, -30.4, -31.25, -28.75), (-34.4, -30.4, -25.25, -22.75), (-30.8, -26.8, 22.75, 25.25), (-30.8, -26.8, 28.75, 31.25)]
UNDER_ESP = (-12.5, 12.35, -47.0, 10.0)
ARM_SLOTS = [[(12.34, -20.0), (12.34, 3.0), (18.35, 3.0), (18.35, -20.0), (13.95, -20.0), (13.95, 2.0), (12.35, 2.0), (12.35, -20.0)], [(12.34, -24.0), (12.34, -47.0), (18.35, -47.0), (18.35, -24.0), (13.95, -24.0), (13.95, -46.0), (12.35, -46.0), (12.35, -24.0)]]
ESP_RAIL_X = -14.25
ESP_END_Y = 13.0
ESP_GAP = 2.5
ESP_T = 1.6
ESP_LEDGE = 0.8
ESP_W_MIN = 25.0
HOOK_FACE = 10.35
ARM_X1 = 13.95
HOOKS = [(-2.0, 2.0), (-46.0, -42.0)]
RAIL_RISE = 5.299999999999997
IMU_WALLS = [(11.5, 13.1, 16.049999999999997, 41.95), (-13.1, -11.5, 16.049999999999997, 41.95)]
IMU_STOPS = [(-7.5, 7.5, 14.449999999999998, 16.049999999999997), (-7.5, 7.5, 41.95, 43.550000000000004)]
IMU_TABS = [(11.0, 11.5, 25.0, 33.0), (-11.5, -11.0, 25.0, 33.0)]
IMU_SLITS = [(11.4, 13.2, 23.5, 24.5), (11.4, 13.2, 33.5, 34.5), (-13.2, -11.4, 23.5, 24.5), (-13.2, -11.4, 33.5, 34.5)]
IMU_H = 4.6
LENS_Z = 61.7
LENS_Y_FRONT = 63.0
LENS_BACK = 62.2
POCKET = 8.8
LENS_HOLE = 7.5
CAM_MOD = 8.5
HOLDER_X = 8.0
HOLDER_Y0 = 53.8
HOLDER_Z0 = 55.5
HOLDER_Z1 = 68.0
FLANGE = (-13.0, 13.0, 46.0, 54.0)
FLANGE_T = 2.5

import os
import adsk.core, adsk.fusion

VI = adsk.core.ValueInput
BASE = os.path.join(os.path.expanduser("~"), "Documents", "Vanta Prototyping")
REF_DIR = os.path.join(BASE, "deck_refs")
OUT_DIR = os.path.join(BASE, "deck_out")
PARAMS = [
    ("post_top", f"{POST_TOP} mm", "top of electronics-plate posts"),
    ("riser_t", f"{RISER_T} mm", "riser plate thickness (same as old deck plate)"),
    ("deck_z", f"{DECK_Z} mm", "top deck underside (old deck + 12.7)"),
    ("deck_t", f"{DECK_T} mm", "top deck thickness"),
    ("col_d", f"{COL_D} mm", "riser column diameter"),
    ("insert_depth", f"{INSERT_DEPTH} mm", "M3 heat-set insert hole depth"),
    ("esp_gap", f"{ESP_GAP} mm", "ESP32 board underside above deck"),
    ("cam_spacer", f"{CAM_SPACER} mm", "camera baseboard spacer height"),
    ("lens_z", f"{LENS_Z} mm", "camera lens centre height (hull hole centre)"),
    ("cam_mod", f"{CAM_MOD} mm", "OV5640 lens block width (measure yours)"),
]
PRINT_COMPS = ("VANTA Riser", "VANTA Top Deck", "VANTA Camera Holder", "VANTA Cam Spacers")
NAMES = PRINT_COMPS + ("Reference (do not print)",)


def cm(v):
    return v / 10.0


def P(x, y):
    return adsk.core.Point3D.create(cm(x), cm(y), 0)


def run(_context):
    app = adsk.core.Application.get()
    des = adsk.fusion.Design.cast(app.activeProduct)
    des.designType = adsk.fusion.DesignTypes.ParametricDesignType
    root = des.rootComponent

    tl = des.timeline
    if tl.count:
        tl.markerPosition = 0
        tl.deleteAllAfterMarker()

    up = des.userParameters
    for n, v, c in PARAMS:
        p = up.itemByName(n)
        if p:
            p.expression = v
        else:
            up.add(n, VI.createByString(v), "mm", c)

    NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation
    CUT = adsk.fusion.FeatureOperations.CutFeatureOperation

    def new_comp(name):
        return root

    def plane(comp, expr, name):
        inp = comp.constructionPlanes.createInput()
        inp.setByOffset(comp.xYConstructionPlane, VI.createByString(expr))
        pl = comp.constructionPlanes.add(inp)
        pl.name = name
        pl.isLightBulbOn = False
        return pl

    def sketch(comp, pl, name):
        sk = comp.sketches.add(pl)
        sk.name = name
        sk.isComputeDeferred = True
        return sk

    def poly(sk, pts):
        ls = sk.sketchCurves.sketchLines
        first = prev = None
        for x, y in pts[1:]:
            a = prev.endSketchPoint if prev else P(*pts[0])
            prev = ls.addByTwoPoints(a, P(x, y))
            first = first or prev
        ls.addByTwoPoints(prev.endSketchPoint, first.startSketchPoint)

    def rect(sk, x0, x1, y0, y1):
        sk.sketchCurves.sketchLines.addTwoPointRectangle(P(x0, y0), P(x1, y1))

    def circ(sk, x, y, d):
        sk.sketchCurves.sketchCircles.addByCenterRadius(P(x, y), cm(d / 2))

    def extrude(comp, sk, expr, op, body=None):
        sk.isComputeDeferred = False
        profs = adsk.core.ObjectCollection.create()
        for i in range(sk.profiles.count):
            profs.add(sk.profiles.item(i))
        if profs.count == 0:
            raise RuntimeError(f"sketch '{sk.name}' has no closed profiles")
        inp = comp.features.extrudeFeatures.createInput(profs, op)
        inp.setDistanceExtent(False, VI.createByString(expr))
        if body is not None:
            inp.participantBodies = body if isinstance(body, list) else [body]
        f = comp.features.extrudeFeatures.add(inp)
        f.name = sk.name
        return f

    def rects(comp, pl, name, items, expr, op, body=None):
        sk = sketch(comp, pl, name)
        for r in items:
            rect(sk, *r)
        return extrude(comp, sk, expr, op, body)

    # ---------------- riser: old deck plate outline + 4 columns ----------------
    rc = new_comp("VANTA Riser")
    sk = sketch(rc, plane(rc, "post_top", "post top"), "riser outline (old deck plate)")
    poly(sk, OLD_DECK)
    riser = extrude(rc, sk, "riser_t", NEW).bodies.item(0)
    riser.name = "Riser"
    sk = sketch(rc, plane(rc, "post_top - 1 mm", "below riser"), "post screw holes (hull screws)")
    for x, y in POSTS:
        circ(sk, x, y, M3)
    extrude(rc, sk, "riser_t + 2 mm", CUT, riser)
    sk = sketch(rc, plane(rc, "post_top + riser_t", "riser top"), "columns")
    for x, y in COLS:
        circ(sk, x, y, COL_D)
    extrude(rc, sk, "deck_z - post_top - riser_t", JOIN, riser)
    sk = sketch(rc, plane(rc, "deck_z - insert_depth", "insert hole bottom"), "M3 insert holes")
    for x, y in COLS:
        circ(sk, x, y, INSERT_D)
    extrude(rc, sk, "insert_depth + 0.5 mm", CUT, riser)

    # ---------------- top deck ----------------
    dc = new_comp("VANTA Top Deck")
    p_deck = plane(dc, "deck_z", "deck underside")
    p_top = plane(dc, "deck_z + deck_t", "deck top")
    p_cut = plane(dc, "deck_z - 1 mm", "below deck")
    sk = sketch(dc, p_deck, "deck outline")
    poly(sk, DECK)
    deck = extrude(dc, sk, "deck_t", NEW).bodies.item(0)
    deck.name = "Top Deck"

    sk = sketch(dc, p_cut, "screw holes")
    for x, y in COLS:
        circ(sk, x, y, M3)
    for sx in (1, -1):
        for sy in (1, -1):
            circ(sk, sx * CAM_HOLE_SQ / 2, CAM_CY + sy * CAM_HOLE_SQ / 2, M2)
    for x, y in TONGUE_HOLES:
        circ(sk, x, y, M2)
    extrude(dc, sk, "deck_t + 2 mm", CUT, deck)
    rects(dc, p_cut, "wire slots", SIDE_SLOTS, "deck_t + 2 mm", CUT, deck)
    rects(dc, p_cut, "zip-tie notches", NOTCH_RECTS, "deck_t + 2 mm", CUT, deck)
    rects(dc, p_cut, "opening under ESP32", [UNDER_ESP], "deck_t + 2 mm", CUT, deck)
    sk = sketch(dc, p_cut, "ESP32 clip arm slots")
    for s in ARM_SLOTS:
        poly(sk, s)
    extrude(dc, sk, "deck_t + 2 mm", CUT, deck)

    rx = ESP_RAIL_X
    rects(dc, p_top, "ESP32 fixed rail", [(rx - 2.4, rx, -58.0, ESP_END_Y + 2.4)], f"esp_gap + {ESP_T + 1.2} mm", JOIN, deck)
    rects(dc, p_top, "ESP32 rail ledge", [(rx - 0.1, rx + ESP_LEDGE, -57.0, ESP_END_Y)], "esp_gap", JOIN, deck)
    ex0, ex1 = rx, rx + ESP_W_MIN - 3
    rects(dc, p_top, "ESP32 end stop", [(ex0, ex1, ESP_END_Y, ESP_END_Y + 2.4)], f"esp_gap + {ESP_T + 1.1} mm", JOIN, deck)
    rects(dc, p_top, "ESP32 end ledge", [(ex0 + 2, ex1 - 2, ESP_END_Y - ESP_LEDGE, ESP_END_Y)], "esp_gap", JOIN, deck)
    p_lip = plane(dc, f"deck_z + deck_t + esp_gap + {ESP_T + 0.3} mm", "ESP32 lip underside")
    rects(dc, p_lip, "ESP32 end lip", [(ex0 + 2, ex1 - 2, ESP_END_Y - 1.0, ESP_END_Y)], "0.8 mm", JOIN, deck)
    rects(dc, p_top, "clip hook shelves", [(HOOK_FACE - ESP_LEDGE, ARM_X1, y0, y1) for y0, y1 in HOOKS], "esp_gap", JOIN, deck)
    rects(dc, p_top, "clip hook walls", [(HOOK_FACE, ARM_X1, y0, y1) for y0, y1 in HOOKS], f"esp_gap + {ESP_T + 1.2} mm", JOIN, deck)

    rects(dc, p_top, "IMU pocket walls", IMU_WALLS, f"{IMU_H + 0.8} mm", JOIN, deck)
    rects(dc, p_top, "IMU end stops", IMU_STOPS, "1.5 mm", JOIN, deck)
    rects(dc, plane(dc, f"deck_z + deck_t + {IMU_H + 0.1} mm", "IMU tab underside"), "IMU snap tabs", IMU_TABS, "0.7 mm", JOIN, deck)
    rects(dc, plane(dc, "deck_z + deck_t + 1.5 mm", "IMU slit bottom"), "IMU tab relief slits", IMU_SLITS, "5 mm", CUT, deck)

    # ---------------- camera holder (bolts to deck tongue) ----------------
    hc = new_comp("VANTA Camera Holder")
    hz0 = HOLDER_Z0
    rects(hc, plane(hc, f"{hz0} mm", "holder bottom"), "holder block", [(-HOLDER_X, HOLDER_X, HOLDER_Y0, LENS_Y_FRONT)], f"{HOLDER_Z1 - hz0} mm", NEW)
    holder = hc.features.extrudeFeatures.item(hc.features.extrudeFeatures.count - 1).bodies.item(0)
    holder.name = "Camera Holder"
    rects(hc, plane(hc, "deck_z + deck_t", "tongue top"), "holder flange", [(FLANGE[0], FLANGE[1], FLANGE[2], FLANGE[3])], f"{FLANGE_T} mm", JOIN, holder)
    p_pk = plane(hc, "lens_z - cam_mod / 2 - 0.15 mm", "lens block pocket bottom")
    sk = sketch(hc, p_pk, "lens block pocket")
    rect(sk, -POCKET / 2, POCKET / 2, HOLDER_Y0 - 1, LENS_BACK)
    extrude(hc, sk, "cam_mod + 0.3 mm", CUT, holder)
    sk = sketch(hc, plane(hc, f"lens_z - {LENS_HOLE / 2} mm", "lens window bottom"), "lens window")
    rect(sk, -LENS_HOLE / 2, LENS_HOLE / 2, LENS_BACK - 0.5, LENS_Y_FRONT + 1)
    extrude(hc, sk, f"{LENS_HOLE} mm", CUT, holder)
    sk = sketch(hc, plane(hc, f"{hz0 - 1} mm", "below holder"), "flex slot")
    rect(sk, -4.5, 4.5, HOLDER_Y0 - 1, HOLDER_Y0 + 4)
    extrude(hc, sk, "lens_z - cam_mod / 2 - 0.15 mm - " + f"{hz0 - 1} mm", CUT, holder)
    sk = sketch(hc, plane(hc, "deck_z + deck_t - 1 mm", "below flange"), "flange bolt holes")
    for x, y in TONGUE_HOLES:
        circ(sk, x, y, M2)
    extrude(hc, sk, f"{FLANGE_T + 2} mm", CUT, holder)

    # ---------------- camera baseboard spacers ----------------
    sc = new_comp("VANTA Cam Spacers")
    sk = sketch(sc, plane(sc, "deck_z - cam_spacer", "spacer bottom"), "spacers")
    for sx in (1, -1):
        for sy in (1, -1):
            circ(sk, sx * CAM_HOLE_SQ / 2, CAM_CY + sy * CAM_HOLE_SQ / 2, 5.0)
    f = extrude(sc, sk, "cam_spacer", NEW)
    spacers = [f.bodies.item(i) for i in range(f.bodies.count)]
    for i, b in enumerate(spacers):
        b.name = f"Cam Spacer {i + 1}"
    sk = sketch(sc, plane(sc, "deck_z - cam_spacer - 1 mm", "below spacers"), "spacer holes")
    for sx in (1, -1):
        for sy in (1, -1):
            circ(sk, sx * CAM_HOLE_SQ / 2, CAM_CY + sy * CAM_HOLE_SQ / 2, M2)
    extrude(sc, sk, "cam_spacer + 2 mm", CUT, spacers)

    # ---------------- export ----------------
    os.makedirs(OUT_DIR, exist_ok=True)
    em = des.exportManager
    groups = {"VANTA_Riser": ["Riser"], "VANTA_Top_Deck": ["Top Deck"], "VANTA_Camera_Holder": ["Camera Holder"]}
    for i in range(root.bRepBodies.count):
        b = root.bRepBodies.item(i)
        if b.name.startswith("Cam Spacer"):
            groups.setdefault("VANTA_Cam_Spacers", []).append(b.name)
    for fn, names in groups.items():
        for n in names:
            b = root.bRepBodies.itemByName(n)
            o = em.createSTLExportOptions(b, os.path.join(OUT_DIR, (fn if len(names) == 1 else n.replace(" ", "_")) + ".stl"))
            o.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
            em.execute(o)
    em.execute(em.createSTEPExportOptions(os.path.join(OUT_DIR, "VANTA_deck_parts.step"), root))
    for i in range(root.bRepBodies.count):
        b = root.bRepBodies.item(i)
        print(b.name, "volume cm3", round(b.volume, 2), "solid", b.isSolid)
    print("features", root.features.count, "exported to", OUT_DIR)
