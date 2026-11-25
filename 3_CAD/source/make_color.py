import json, math, os, sys, uuid, zipfile, io
import numpy as np
import trimesh

SRC = "./_dev/brand/stl/"
OUT = sys.argv[1] if len(sys.argv) > 1 else "./_dev/brand/VANTA_print_COLOR_AMS_A1.3mf"
APP = "BambuStudio-01.10.00.00"
BED = 256.0
STRIDE = BED * 1.2  # PartPlate.cpp: plate spacing = bed * (1 + LOGICAL_PART_PLATE_GAP)
PRINTER, PROCESS = "Bambu Lab A1 0.4 nozzle", "0.20mm Standard @BBL A1"
FILAMENTS = ["Generic PLA @BBL A1", "Generic PLA @BBL A1"]
FIL_IDS = ["GFL99", "GFU99"]
FIL_COLOURS = ["#1A1A1A", "#C8CACD"]   # black + silver (any accent PLA works)

LINK = {"wall_loops": "4", "sparse_infill_density": "15%", "sparse_infill_pattern": "gyroid", "top_shell_layers": "4", "bottom_shell_layers": "3"}
SUP = {"enable_support": "1", "support_type": "tree(auto)"}
BODY = {"wall_loops": "3", "sparse_infill_density": "15%", "sparse_infill_pattern": "gyroid"}
CAP = {"wall_loops": "4", "sparse_infill_density": "15%", "sparse_infill_pattern": "gyroid", "top_shell_layers": "4", "bottom_shell_layers": "4"}
ACC = {"extruder": "2"}
PARTS = {
    "S_top_shell": ("Mech hull", {"wall_loops": "2", "sparse_infill_density": "10%", "sparse_infill_pattern": "gyroid", "enable_support": "1", "support_type": "tree(auto)"}),
    "S_top_shell_text_ACCENT": ("Hull lettering VANTA x2 + MADE BY GIO (silver)", {"extruder": "2"}),
    "C_logo_letters_ACCENT": ("Front logo letters (accent)", {**ACC, "wall_loops": "2", "sparse_infill_density": "100%"}),
    "D_base_logo_ams": ("Base, logo printed in", BODY),
    "D_base_logo_ACCENT": ("Base logo (accent)", {**BODY, **ACC}),
}
GROUPS = {"S_top_shell": ["S_top_shell", "S_top_shell_text_ACCENT"], "D_base_logo_ams": ["D_base_logo_ams", "D_base_logo_ACCENT"]}
KEEP = {"S_top_shell_text_ACCENT", "D_base_logo_ACCENT"}
PAIRS = set()
PLATES = [
    ("1 MECH HULL - AMS: black hull + silver lettering; upright, tree supports inside", [("S_top_shell", 128, 128, 0)]),
    ("2 FRONT LOGO LETTERS - silver (or any accent), no AMS needed", [("C_logo_letters_ACCENT", 128, 128, 0)]),
    ("3 OPTIONAL - base with logo printed in color on AMS (replaces main plate 2 + this file's plate 2)", [("D_base_logo_ams", 128, 128, 0)]),
]

meshes = {}
for key in PARTS:
    m = trimesh.load(SRC + key + ".stl")
    b = m.bounds
    if key not in KEEP:
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
            if frozenset((bk, key)) in PAIRS: continue
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
model.write(' <metadata name="Title">VANTA v6 - color parts (AMS), made by Gio (A1)</metadata>\n')
model.write(' <metadata name="Designer">Gio</metadata>\n')
model.write(' <resources>\n')
nid = 1000
parts_of = {}
for o, key, name, cfg in objects:
    keys = GROUPS.get(key, [key])
    if len(keys) == 1:
        model.write(f'  <object id="{o}" type="model" name="{name}">\n'); model.write(mesh_xml(meshes[key])); model.write('  </object>\n')
        parts_of[o] = [(o, key)]
        continue
    subs = []
    for k in keys:
        nid += 1; subs.append((nid, k))
        model.write(f'  <object id="{nid}" type="model" name="{PARTS[k][0]}">\n'); model.write(mesh_xml(meshes[k])); model.write('  </object>\n')
    model.write(f'  <object id="{o}" type="model" name="{name}">\n   <components>\n')
    for sid, k in subs:
        model.write(f'    <component objectid="{sid}" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>\n')
    model.write('   </components>\n  </object>\n')
    parts_of[o] = subs
model.write(' </resources>\n <build>\n')
for o, tr in items:
    model.write(f'  <item objectid="{o}" transform="{tr}" printable="1"/>\n')
model.write(' </build>\n</model>\n')

cfgx = io.StringIO()
cfgx.write('<?xml version="1.0" encoding="UTF-8"?>\n<config>\n')
for o, key, name, cfg in objects:
    cfgx.write(f'  <object id="{o}">\n    <metadata key="name" value="{name}"/>\n')
    if "extruder" not in cfg:
        cfgx.write('    <metadata key="extruder" value="1"/>\n')
    for k, v in cfg.items():
        cfgx.write(f'    <metadata key="{k}" value="{v}"/>\n')
    for sid, k in parts_of[o]:
        m = meshes[k]
        cfgx.write(f'    <part id="{sid}" subtype="normal_part">\n      <metadata key="name" value="{PARTS[k][0]}"/>\n')
        cfgx.write('      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>\n')
        cfgx.write(f'      <metadata key="extruder" value="{PARTS[k][1].get("extruder", "1")}"/>\n')
        cfgx.write(f'      <metadata key="source_file" value="{k}.stl"/>\n')
        cfgx.write(f'      <mesh_stat face_count="{len(m.faces)}" edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>\n')
        cfgx.write('    </part>\n')
    cfgx.write('  </object>\n')
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
    "filament_type": ["PLA", "PLA"],
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
