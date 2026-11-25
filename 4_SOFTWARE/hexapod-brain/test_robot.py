import math
from robot.kinematics import LEGS, leg_ik, leg_fk, out_of_range
from robot.controller import Robot, _neutral, LOW_Z, HIGH_Z

worst = 0.0
for leg in LEGS:
    nx, ny = _neutral(leg)
    for dz in (-LOW_Z, -80, -HIGH_Z):
        for dx in (-30, 0, 30):
            p = (nx + dx, ny + dx / 2, dz)
            q = leg_fk(leg, *leg_ik(leg, *p))
            worst = max(worst, math.dist(p, q))
print("ik roundtrip max error mm", round(worst, 4))
assert worst < 1e-6

for h in range(0, 101, 10):
    r = Robot(); r.height = h; r.z = r._height_z()
    bad = [out_of_range(leg_ik(l, *_neutral(l), -r.z)) for l in LEGS]
    assert not any(bad), (h, bad)
print("stance ok at every height")


def world_foot(r, leg):
    x, y, z = leg_fk(leg, *r.joints[leg])
    p = r.pose()
    c, s = math.cos(p["yaw"]), math.sin(p["yaw"])
    return (p["x"] + x * c - y * s, p["y"] + x * s + y * c, p["z"] + z)


def run(r, seconds, dt=1 / 30, check_plant=False):
    warn, drift = set(), 0.0
    last = {}
    for _ in range(int(seconds / dt)):
        r.step(dt)
        warn.update(w.split()[0] + " " + w.split()[1] for w in r.warnings)
        if check_plant:
            for leg in LEGS:
                wf = world_foot(r, leg)
                if r.lift[leg] == 0 and leg in last and last[leg][1] == 0:
                    in_swing = leg in r.swing_from and ((leg in ("FL", "MR", "RL")) == (r.phase < 0.5))
                    if not in_swing:
                        drift = max(drift, math.dist(wf[:2], last[leg][0][:2]))
                last[leg] = (wf, r.lift[leg])
    return warn, drift


scenarios = [
    ("FOLLOW straight", "FOLLOW", (0.5, 0.1), 50, 8),
    ("FOLLOW turning", "FOLLOW", (0.1, 0.1), 50, 8),
    ("FAST FOLLOW turning", "FAST FOLLOW", (0.9, 0.1), 50, 8),
    ("FAST FOLLOW tall", "FAST FOLLOW", (0.2, 0.1), 100, 8),
    ("FAST FOLLOW low", "FAST FOLLOW", (0.8, 0.1), 0, 8),
    ("FREE ROAM", "FREE ROAM", None, 50, 60),
    ("DANCE", "DANCE", None, 50, 40),
    ("DANCE low", "DANCE", None, 0, 40),
    ("DANCE tall", "DANCE", None, 100, 40),
    ("CROUCH", "CROUCH", None, 50, 4),
]
for label, mode, target, h, secs in scenarios:
    r = Robot(); r.height = h; r.z = r._height_z(); r.target = target
    r.command(mode)
    warn, drift = run(r, secs, check_plant=mode != "DANCE")
    print(f"{label:22s} warnings={sorted(warn) or 'none'}  foot slip={drift:.2f}mm  moved={math.hypot(r.x, r.y):.0f}mm")

r = Robot()
r.command("TRANSPORT"); w1, _ = run(r, 3)
folded = r.z
r.command("STAND"); w2, _ = run(r, 4)
print("TRANSPORT and back", sorted(w1 | w2) or "none", "rest z", round(folded, 1), "stand z", round(r.z, 1))

for mode in ("FOLLOW", "FAST FOLLOW", "FREE ROAM", "DANCE"):
    r = Robot(); r.command(mode); run(r, 3); x0, t0 = (r.x, r.y), r.phase
    run(r, 20)
    still_going = math.dist((r.x, r.y), x0) > 50 or mode == "DANCE" and r.mode_t > 20
    print(f"{mode:12s} keeps going with no hand for 20s: {still_going}")
    assert still_going

r = Robot(); r.target = (0.5, 0.1); r.command("FOLLOW"); run(r, 3)
r.command("STOP"); before = dict(r.joints); run(r, 1)
assert r.joints == before
print("STOP freezes joints")

r = Robot(); r.command("DANCE"); run(r, 32)
seen, lifted = set(), set()
for _ in range(16 * 60):
    r.step(1 / 60)
    seen.add(tuple(round(v, 1) for v in r.joints["ML"]))
    lifted |= {l for l in LEGS if r.lift[l] > 15}
print(f"DANCE 3rd loop: {len(seen)} distinct ML poses, legs lifted {sorted(lifted)}")
assert len(seen) > 200 and len(lifted) == 6
r.command("STOP"); r.command("STAND"); run(r, 2)
print("DANCE -> STAND lifts cleared:", all(v == 0 for v in r.lift.values()))
r.target = None; r.command("STAND"); run(r, 3)
print("feet back home after stopping:", all(math.dist(r.feet[l], _neutral(l)) < 1.5 for l in LEGS), "walking:", r.walking)
