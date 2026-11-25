"""Slice every print STL with its 3MF settings; print/save grams per part and total.
usage: python table.py <stl_dir> <out.json> [settings_module]"""
import json, sys, os, importlib.util
from concurrent.futures import ThreadPoolExecutor
from slice import grams

d, out = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("m3", sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(__file__), "../hx2/make_3mf_v4.py"))
src = open(spec.origin).read().split("def grid")[0]  # PARTS dict only, skip mesh loading
ns = {}; exec(src, ns)
PARTS = ns["PARTS"]

def run(key):
    cfg = PARTS[key][1]
    qty = int(key.rsplit("_x", 1)[1])
    g = grams(os.path.join(d, key + ".stl"), int(cfg.get("wall_loops", 3)), int(cfg["sparse_infill_density"].rstrip("%")),
              support=cfg.get("enable_support") == "1", top=int(cfg.get("top_shell_layers", 4)), bottom=int(cfg.get("bottom_shell_layers", 3)))
    return key, qty, g

with ThreadPoolExecutor(6) as ex:
    rows = list(ex.map(run, [k for k in PARTS if os.path.exists(os.path.join(d, k + ".stl"))]))
res = {}
for key, qty, g in rows:
    if not isinstance(g, tuple): print(key, "FAILED", g); continue
    res[key] = {"each": g[0], "qty": qty, "time": g[1]}
    print(f"{key:32s} {g[0]:7.2f} g x{qty:<3d} = {g[0] * qty:7.1f} g   {g[1]}")
json.dump(res, open(out, "w"), indent=1)
