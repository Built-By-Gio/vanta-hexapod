import json, math, os, sys, uuid, zipfile, io
import numpy as np
import trimesh

SRC = "./_dev/hx2/print/stl/"
OUT = sys.argv[1] if len(sys.argv) > 1 else "./_dev/hx2/print/hexapod_v4_A1.3mf"
APP = "BambuStudio-01.10.00.00"
BED = 256.0
STRIDE = BED * 1.2  # PartPlate.cpp: plate spacing = bed * (1 + LOGICAL_PART_PLATE_GAP)
PRINTER, PROCESS = "Bambu Lab A1 0.4 nozzle", "0.20mm Standard @BBL A1"
FILAMENTS = ["Generic PLA @BBL A1"]
FIL_IDS = ["GFL99"]
FIL_COLOURS = ["#1A1A1A"]

LINK = {"wall_loops": "4", "sparse_infill_density": "15%", "sparse_infill_pattern": "gyroid", "top_shell_layers": "4", "bottom_shell_layers": "3"}
LINK3 = {**LINK, "wall_loops": "3"}           # femur, tibia, bracket A: slicer-checked, 3 walls is plenty at these stresses
SUP = {"enable_support": "1", "support_type": "tree(auto)"}
BODY = {"wall_loops": "3", "sparse_infill_density": "15%", "sparse_infill_pattern": "gyroid"}
LIGHT = {"wall_loops": "2", "sparse_infill_density": "10%", "sparse_infill_pattern": "gyroid"}   # carries boards only
ARMOUR = {"wall_loops": "2", "sparse_infill_density": "5%", "sparse_infill_pattern": "gyroid", "top_shell_layers": "3", "bottom_shell_layers": "3"}   # cosmetic only
CAP = {"wall_loops": "4", "sparse_infill_density": "15%", "sparse_infill_pattern": "gyroid", "top_shell_layers": "4", "bottom_shell_layers": "4"}
PARTS = {
    "01_base_x1": ("Base", BODY),
    "02_top_stiffeners_x1": ("Top stiffeners", {**BODY, **SUP}),
    "03_bottom_stiffeners_x1": ("Bottom stiffeners", {**BODY, **SUP}),
    "04_battery_mount_x1": ("Battery mount", LIGHT),
    "05_electronics_plate_x1": ("Electronics plate", LIGHT),
    "06_pi_deck_x1": ("Pi deck + camera wall", LIGHT),
    "07_femur_x6": ("Femur", LINK3),
    "08_tibia_x6": ("Tibia", {**LINK3, **SUP}),
    "09_bracket_A_coxa_x6": ("Bracket A COXA (clearance holes)", {**LINK3, **SUP}),
    "09_bracket_A_link_x12": ("Bracket A FEMUR-TIBIA (self-tap)", {**LINK3, **SUP}),
    "10_bracket_B_alu_x18": ("Bracket B ALU disc horn", LINK),
    "11_servo_cap_plus0_x18": ("Servo cap +0", CAP),
    "11_servo_cap_plus1_x18": ("Servo cap +1", CAP),
    "11_servo_cap_plus2_x18": ("Servo cap +2", CAP),
    "11_servo_cap_plus3_x18": ("Servo cap +3", CAP),
    "13_armor_femur_x12": ("Armour femur plate", ARMOUR),
    "14_armor_shin_x6": ("Armour shin plate", ARMOUR),
}


def grid(part, n, cols, cx, cy, dx, dy, rot=0):
    out = []
    rows = math.ceil(n / cols)
    for i in range(n):
        r, c = divmod(i, cols)
        out.append((part, cx + (c - (cols - 1) / 2) * dx, cy + ((rows - 1) / 2 - r) * dy, rot))
    return out


AC, AL, BA, T, F = "09_bracket_A_coxa_x6", "09_bracket_A_link_x12", "10_bracket_B_alu_x18", "08_tibia_x6", "07_femur_x6"
caps = lambda v: grid(f"11_servo_cap_plus{v}_x18", 17, 4, 128, 128, 52, 30)
CAPNOTE = " - print ONLY the plate whose size your test joint fit"
PLATES = [
    ("1 TEST FIRST - caps +0..+3, bracket A femur-tibia, bracket B alu: build one joint",
     [(f"11_servo_cap_plus{v}_x18", 55 + 56 * (v % 2), 175 - 36 * (v // 2), 0) for v in range(4)] + [(AL, 190, 160, 0), (BA, 128, 70, 0)]),
    ("2 Base - honeycomb pockets, logo pocket, plate columns", [("01_base_x1", 128, 128, 0)]),
    ("3 Top + bottom stiffeners", [("02_top_stiffeners_x1", 68, 128, 0), ("03_bottom_stiffeners_x1", 188, 128, 0)]),
    ("4 Battery mount + electronics plate", [("04_battery_mount_x1", 80, 128, 0), ("05_electronics_plate_x1", 180, 128, 0)]),
    ("5 Pi deck + 6 femurs", [("06_pi_deck_x1", 56, 128, 0)] + grid(F, 6, 1, 177, 128, 0, 36)),
    ("6 Tibias x3 + bracket A COXA x3", grid(T, 3, 3, 80, 128, 50, 0) + grid(AC, 3, 1, 205, 128, 0, 64, 90)),
    ("7 Tibias x3 + bracket A COXA x3", grid(T, 3, 3, 80, 128, 50, 0) + grid(AC, 3, 1, 205, 128, 0, 64, 90)),
    ("8 Bracket A FEMUR-TIBIA x11 (12th is on plate 1)", grid(AL, 11, 4, 128, 128, 62, 48)),
    ("9 Bracket B ALU x17 (18th is on plate 1)", grid(BA, 17, 3, 128, 128, 58, 36)),
    ("10 Servo caps +0 x17" + CAPNOTE, caps(0)),
    ("11 Servo caps +1 x17" + CAPNOTE, caps(1)),
    ("12 Servo caps +2 x17" + CAPNOTE, caps(2)),
    ("13 Servo caps +3 x17" + CAPNOTE, caps(3)),
    ("14 Armour: femur plates x12 (cosmetic, 5% infill)", grid("13_armor_femur_x12", 12, 3, 128, 128, 77, 51)),
    ("15 Armour: shin plates x6 (cosmetic, 5% infill)", grid("14_armor_shin_x6", 6, 2, 128, 128, 102, 24)),
]

meshes = {}
for key in PARTS:
    m = trimesh.load(SRC + key + ".stl")
    b = m.bounds
    m.apply_translation([-(b[0][0] + b[1][0]) / 2, -(b[0][1] + b[1][1]) / 2, -b[0][2]])
    meshes[key] = m


def footprint(key, rot):
    m = meshes[key]
    R = trimesh.transformations.rotation_matrix(math.radians(rot), [0, 0, 1])
    v = trimesh.transform_points(m.vertices, R)
    return v[:, :2].min(0), v[:, :2].max(0)


objects, items, plates_xml = [], [], []
oid = 0
problems = []
_v = math.sqrt(len(PLATES)); cols = int(round(_v)) + (1 if _v > round(_v) else 0)  # PartPlateList::compute_colum_count
for pi, (pname, placements) in enumerate(PLATES):
    row, col = divmod(pi, cols)
    ox, oy = col * STRIDE, -row * STRIDE
    boxes = []
    inst = []
    counts = {}
    for key, x, y, rot in placements:
        lo, hi = footprint(key, rot)
        lo, hi = lo + [x, y], hi + [x, y]
        pad = 6 if PARTS[key][1].get("support_on_build_plate_only") or key.startswith("01") else 0
        if (lo < 2 + pad).any() or (hi > BED - 2 - pad).any():
            problems.append(f"plate {pi+1}: {key} off bed {lo.round(1)} {hi.round(1)}")
        for blo, bhi, bk in boxes:
            if (lo < bhi + 4).all() and (hi > blo - 4).all():
                problems.append(f"plate {pi+1}: {key} too close to {bk}")
        boxes.append((lo, hi, key))
        oid += 1
        counts[key] = counts.get(key, 0) + 1
        label, cfg = PARTS[key]
        name = f"{label} {counts[key]}" if sum(1 for p in placements if p[0] == key) > 1 else label
        objects.append((oid, key, name, cfg))
        c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        items.append((oid, f"{c:.6f} {s:.6f} 0 {-s:.6f} {c:.6f} 0 0 0 1 {ox + x:.4f} {oy + y:.4f} 0"))
        inst.append(oid)
    plates_xml.append((pi + 1, pname, inst))

if problems:
    print("\n".join(problems))
    sys.exit(1)

if len(sys.argv) > 2:   # optional overview PNG of every plate
    import textwrap, matplotlib
    from scipy.spatial import ConvexHull
    matplotlib.use("Agg"); import matplotlib.pyplot as plt
    rows = math.ceil(len(PLATES) / cols)
    fig, axs = plt.subplots(rows, cols, figsize=(3.6 * cols, 4.0 * rows))
    for ax in axs.flat: ax.axis("off")
    for pi, (pname, placements) in enumerate(PLATES):
        ax = axs.flat[pi]; ax.set_aspect("equal"); ax.set_xlim(-4, BED + 4); ax.set_ylim(-4, BED + 4)
        ax.add_patch(plt.Rectangle((0, 0), BED, BED, fc="#f3f1ec", ec="#aaa"))
        for key, x, y, rot in placements:
            p = trimesh.transform_points(meshes[key].vertices, trimesh.transformations.rotation_matrix(math.radians(rot), [0, 0, 1]))[:, :2] + [x, y]
            h = ConvexHull(p).vertices
            ax.fill(p[h, 0], p[h, 1], color="#b8621a" if "TPU" not in key else "#8e1a12", alpha=0.85)
        ax.set_title(textwrap.fill(pname, 42), fontsize=7, loc="left")
    plt.tight_layout(); plt.savefig(sys.argv[2], dpi=80)


def mesh_xml(m):
    v = "\n".join(f'     <vertex x="{a:.5f}" y="{b:.5f}" z="{c:.5f}"/>' for a, b, c in m.vertices)
    t = "\n".join(f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in m.faces)
    return f"    <mesh>\n     <vertices>\n{v}\n     </vertices>\n     <triangles>\n{t}\n     </triangles>\n    </mesh>\n"


model = io.StringIO()
model.write('<?xml version="1.0" encoding="UTF-8"?>\n')
model.write('<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
            'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021">\n')
model.write(f' <metadata name="Application">{APP}</metadata>\n')
model.write(' <metadata name="BambuStudio:3mfVersion">1</metadata>\n')
model.write(' <metadata name="Title">VANTA v6 - main print set, made by Gio (A1)</metadata>\n')
model.write(' <metadata name="Designer">Gio</metadata>\n')
model.write(' <resources>\n')
for o, key, name, cfg in objects:
    model.write(f'  <object id="{o}" type="model" name="{name}">\n')
    model.write(mesh_xml(meshes[key]))
    model.write('  </object>\n')
model.write(' </resources>\n <build>\n')
for o, tr in items:
    model.write(f'  <item objectid="{o}" transform="{tr}" printable="1"/>\n')
model.write(' </build>\n</model>\n')

cfgx = io.StringIO()
cfgx.write('<?xml version="1.0" encoding="UTF-8"?>\n<config>\n')
for o, key, name, cfg in objects:
    m = meshes[key]
    cfgx.write(f'  <object id="{o}">\n    <metadata key="name" value="{name}"/>\n')
    if "extruder" not in cfg:
        cfgx.write('    <metadata key="extruder" value="1"/>\n')
    for k, v in cfg.items():
        cfgx.write(f'    <metadata key="{k}" value="{v}"/>\n')
    cfgx.write(f'    <metadata face_count="{len(m.faces)}"/>\n')
    cfgx.write(f'    <part id="{o}" subtype="normal_part">\n      <metadata key="name" value="{name}"/>\n')
    cfgx.write('      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>\n')
    cfgx.write(f'      <metadata key="source_file" value="{key}.stl"/>\n')
    cfgx.write(f'      <mesh_stat face_count="{len(m.faces)}" edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>\n')
    cfgx.write('    </part>\n  </object>\n')
for pid, pname, inst in plates_xml:
    cfgx.write(f'  <plate>\n    <metadata key="plater_id" value="{pid}"/>\n    <metadata key="plater_name" value="{pname}"/>\n')
    cfgx.write('    <metadata key="locked" value="false"/>\n')
    for o in inst:
        cfgx.write(f'    <model_instance>\n      <metadata key="object_id" value="{o}"/>\n      <metadata key="instance_id" value="0"/>\n'
                   f'      <metadata key="identify_id" value="{1000 + o}"/>\n    </model_instance>\n')
    cfgx.write('  </plate>\n')
cfgx.write('</config>\n')

# project settings: only long-standing keys. Bambu fills every other value from the installed
# A1 system presets (load_external_preset), and unknown keys make older versions reject the whole file.
proj = {
    "from": "project",
    "name": "project_settings",
    "version": "01.10.00.00",
    "printer_technology": "FFF",
    "printer_model": "Bambu Lab A1",
    "printer_settings_id": PRINTER,
    "print_settings_id": PROCESS,
    "filament_settings_id": FILAMENTS,
    "filament_colour": FIL_COLOURS,
    "filament_type": ["PLA"],
    "nozzle_diameter": ["0.4"],
    "printable_area": ["0x0", "256x0", "256x256", "0x256"],
    "printable_height": "256",
    "curr_bed_type": "Textured PEI Plate",
    "inherits_group": ["", "", "", ""],
    "different_settings_to_system": ["", "", "", ""],
}

ct = ('<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
      ' <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
      ' <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>\n'
      ' <Default Extension="png" ContentType="image/png"/>\n</Types>\n')
rels = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        ' <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n'
        '</Relationships>\n')

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", ct)
    z.writestr("_rels/.rels", rels)
    z.writestr("3D/3dmodel.model", model.getvalue())
    z.writestr("Metadata/model_settings.config", cfgx.getvalue())
    z.writestr("Metadata/project_settings.config", json.dumps(proj, indent=4))
print("wrote", OUT, os.path.getsize(OUT) // 1024, "KB,", len(objects), "objects on", len(PLATES), "plates")
