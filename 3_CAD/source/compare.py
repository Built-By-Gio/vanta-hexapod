"""Markdown before/after table from table.py runs + the shell. python compare.py baseline_v4.json after_v6.json"""
import json, sys, re
from slice import grams

b, a = json.load(open(sys.argv[1])), json.load(open(sys.argv[2]))
V = "./_dev/brand/"
b["S_top_shell_x1"] = {"each": grams(V + "stl_v4/S_top_shell.stl", 3, 15)[0], "qty": 1, "time": grams(V + "stl_v4/S_top_shell.stl", 3, 15)[1]}
g = grams(V + "stl/S_top_shell.stl", 2, 10, support=True)   # v6 hull prints upright with tree supports
a["S_top_shell_x1"] = {"each": g[0], "qty": 1, "time": g[1]}
ROWS = [("Base", ["01_base_x1"], ["01_base_x1"]), ("Top stiffeners", ["02_top_stiffeners_x1"], ["02_top_stiffeners_x1"]),
        ("Bottom stiffeners", ["03_bottom_stiffeners_x1"], ["03_bottom_stiffeners_x1"]), ("Battery mount", ["04_battery_mount_x1"], ["04_battery_mount_x1"]),
        ("Electronics plate", ["05_electronics_plate_x1"], ["05_electronics_plate_x1"]), ("Pi deck", ["06_pi_deck_x1"], ["06_pi_deck_x1"]),
        ("Femur ×6", ["07_femur_x6"], ["07_femur_x6"]), ("Tibia ×6", ["08_tibia_x6"], ["08_tibia_x6"]),
        ("Bracket A ×18", ["09_bracket_A_x18"], ["09_bracket_A_coxa_x6", "09_bracket_A_link_x12"]),
        ("Bracket B ×18", ["10_bracket_B_x18"], ["10_bracket_B_alu_x18"]),
        ("Servo cap ×18 (+0)", ["11_servo_cap_plus0_x18"], ["11_servo_cap_plus0_x18"]),
        ("Leg armour (new)", [], ["13_armor_femur_x12", "14_armor_shin_x6"]), ("Top shell / mech hull", ["S_top_shell_x1"], ["S_top_shell_x1"])]
mins = lambda t: sum(int(v) * {"h": 60, "m": 1, "s": 1 / 60}[u] for v, u in re.findall(r"(\d+)([hms])", t))
tot = lambda d, ks: sum(d[k]["each"] * d[k]["qty"] for k in ks)
ttm = lambda d, ks: sum(mins(d[k]["time"]) * d[k]["qty"] for k in ks)
print("| Part | v4 each | v4 total | v6 each | v6 total | Saved |\n|---|---|---|---|---|---|")
T = [0, 0, 0, 0]
for name, kb, ka in ROWS:
    gb, ga = tot(b, kb), tot(a, ka)
    eb = " / ".join(f"{b[k]['each']:.1f}" for k in kb) or "–"; ea = " / ".join(f"{a[k]['each']:.1f}" for k in ka)
    d = gb - ga
    print(f"| {name} | {eb} g | {gb:.0f} g | {ea} g | {ga:.0f} g | {'−' if d >= 0 else '+'}{abs(d):.0f} g |")
    T[0] += gb; T[1] += ga; T[2] += ttm(b, kb); T[3] += ttm(a, ka)
print(f"| **Total PLA** | | **{T[0]:.0f} g** | | **{T[1]:.0f} g** | **−{T[0] - T[1]:.0f} g ({100 * (T[0] - T[1]) / T[0]:.0f}%)** |")
print(f"\nPrint time (one of each, summed): v4 {T[2] / 60:.1f} h, v6 {T[3] / 60:.1f} h")
