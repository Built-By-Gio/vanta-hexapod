"""Train VANTA's leg network: foot position (mm, in the leg's own frame) -> coxa, femur, tibia angles.

The network is never shown the inverse-kinematics maths. It only sees examples made by the forward
direction (pick random joint angles, work out where the foot ends up) and learns to run that backwards.

    pip install numpy
    python train_ik.py            -> writes ik_net.h (copy it into the vanta_hexapod_pad sketch folder)
"""
import numpy as np

COXA, FEMUR, TIBIA = 68.0, 76.7, 101.0
LIMITS = np.array([[-35, 35], [-80, 85], [-52, 73]], float)
HIDDEN, STEPS, BATCH, LR = 48, 30000, 2048, 2e-3
IN_SCALE, OUT_SCALE = 200.0, 90.0
rng = np.random.default_rng(0)


def foot(angles):
    c, f, t = np.radians(angles).T
    psi = f - t - np.pi / 2
    r = COXA + FEMUR * np.cos(f) + TIBIA * np.cos(psi)
    return np.stack([r * np.cos(c), r * np.sin(c), FEMUR * np.sin(f) + TIBIA * np.sin(psi)], 1)


def examples(n):
    angles = rng.uniform(LIMITS[:, 0], LIMITS[:, 1], (n, 3))
    return foot(angles) / IN_SCALE, angles / OUT_SCALE


def forward(p, x):
    h1 = np.tanh(x @ p["W1"].T + p["B1"])
    h2 = np.tanh(h1 @ p["W2"].T + p["B2"])
    return h1, h2, h2 @ p["W3"].T + p["B3"]


p = {"W1": rng.normal(0, 0.6, (HIDDEN, 3)), "B1": np.zeros(HIDDEN),
     "W2": rng.normal(0, 0.15, (HIDDEN, HIDDEN)), "B2": np.zeros(HIDDEN),
     "W3": rng.normal(0, 0.15, (3, HIDDEN)), "B3": np.zeros(3)}
m = {k: np.zeros_like(v) for k, v in p.items()}
v = {k: np.zeros_like(v) for k, v in p.items()}

for step in range(1, STEPS + 1):
    x, y = examples(BATCH)
    h1, h2, out = forward(p, x)
    err = out - y
    d3 = 2 * err / err.size
    d2 = (d3 @ p["W3"]) * (1 - h2 ** 2)
    d1 = (d2 @ p["W2"]) * (1 - h1 ** 2)
    grad = {"W3": d3.T @ h2, "B3": d3.sum(0), "W2": d2.T @ h1, "B2": d2.sum(0), "W1": d1.T @ x, "B1": d1.sum(0)}
    lr = LR * 0.5 * (1 + np.cos(np.pi * step / STEPS))
    for k in p:   # Adam
        m[k] = 0.9 * m[k] + 0.1 * grad[k]
        v[k] = 0.999 * v[k] + 0.001 * grad[k] ** 2
        p[k] -= lr * (m[k] / (1 - 0.9 ** step)) / (np.sqrt(v[k] / (1 - 0.999 ** step)) + 1e-8)
    if step % 3000 == 0 or step == 1:
        print(f"step {step:6d}   average angle error {np.abs(err).mean() * OUT_SCALE:6.2f} deg")

x, y = examples(50000)
pred = forward(p, x)[2] * OUT_SCALE
miss = np.linalg.norm(foot(pred) - x * IN_SCALE, axis=1)
print(f"\ntested on 50,000 new foot positions it has never seen:")
print(f"  joint angles off by {np.abs(pred - y * OUT_SCALE).mean():.2f} deg on average")
print(f"  foot lands {miss.mean():.1f} mm from the target on average, {np.percentile(miss, 99):.1f} mm at worst (99%)")

with open("ik_net.h", "w") as f:
    f.write(f"// made by train_ik.py: 3 -> {HIDDEN} -> {HIDDEN} -> 3, tanh. Foot (mm) / IK_IN_SCALE in, angles (deg) / IK_OUT_SCALE out.\n")
    f.write(f"#define IK_H {HIDDEN}\nconst float IK_IN_SCALE = {IN_SCALE}, IK_OUT_SCALE = {OUT_SCALE};\n")
    for k, a in p.items():
        dims = "".join(f"[{d}]" for d in a.shape)
        body = ", ".join(f"{w:.6f}f" for w in a.ravel())
        f.write(f"const float IK_{k}{dims} = {{{body}}};\n".replace("{{", "{").replace("}}", "}"))
print("\nwrote ik_net.h")
