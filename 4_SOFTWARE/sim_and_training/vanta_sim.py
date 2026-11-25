"""VANTA learning to walk. A field of simulated VANTAs each try a slightly different brain;
every generation the brains that walked furthest pull the next generation their way.

    pip install mujoco numpy
    python vanta_sim.py            watch them train (close the window to stop; progress is saved)
    python vanta_sim.py fast       train with no window, much quicker
    python vanta_sim.py watch      replay the best brain so far (vanta_brain.npy)
    python vanta_sim.py RL         same, but with that leg missing (FL ML RL FR MR RR), so it learns
                                   a 5-legged walk. Works with fast and watch too: python vanta_sim.py RL watch

The orange robot is the current best brain. The black ones are its mutations.
Needs the meshes folder next to this file.
"""
import os
import sys
import time
import numpy as np
import mujoco

ROBOTS = 121                    # 1 current-best + mutations (keep it odd). Lower it if the window lags.
COLS = 11
EPISODE_S, STEP_S = 6.0, 0.004
PERIOD_S = 0.8                  # one walking cycle
HIDDEN = 16
SIGMA, LEARN_RATE = 0.08, 0.04
RENDER_EVERY = 5                # raise to train faster while watching
ORBIT = 0.02                    # camera degrees per frame, 0 to hold still
SAVE = "vanta_brain.npy"
LEGS = ["FL", "ML", "RL", "FR", "MR", "RR"]
MISSING = None                  # index into LEGS, set from the command line

COXA, FEMUR, TIBIA = 0.068, 0.0767, 0.101
MOUNT = [(0.082, 0.057, 45), (0, 0.071, 90), (-0.082, 0.057, 135),
         (0.082, -0.057, -45), (0, -0.071, -90), (-0.082, -0.057, -135)]
LIMITS = np.radians([[-35, 35], [-80, 85], [-52, 73]])
STAND = np.radians([0, -1, -1])            # the pose the real robot stands in
SWING = np.radians([25, 30, 30])           # how far a brain may move each joint from the stand
STAND_Z = 0.108
MESHES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "meshes")
PARTS = ["body_pla", "body_dark", "body_metal", "body_accent", "coxa_pla",
         "femur_pla", "femur_dark", "femur_metal", "tibia_pla", "tibia_foot"]


def build(n):
    robots, motors = "", ""
    for i in range(n):
        x, y = -(i // COLS) * 3.0, ((i + COLS // 2) % COLS - (COLS - 1) / 2) * 0.7
        pla = "best" if i == 0 else "pla"

        def vis(mesh, mat):
            return f'<geom class="vis" mesh="{mesh}" material="{mat}"/>'

        legs = ""
        for m, (mx, my, ang) in enumerate(MOUNT):
            if m == MISSING:
                continue
            j = f"r{i}_l{m}"
            legs += f"""
      <body pos="{mx} {my} 0" euler="0 0 {np.radians(ang)}">
        <joint name="{j}_c" axis="0 0 1" range="{LIMITS[0][0]} {LIMITS[0][1]}"/>
        <geom class="col" type="capsule" fromto="0 0 0 {COXA} 0 0" size="0.012" mass="0.03"/>
        {vis("coxa_pla", pla)}
        <body pos="{COXA} 0 0">
          <joint name="{j}_f" axis="0 -1 0" range="{LIMITS[1][0]} {LIMITS[1][1]}"/>
          <geom class="col" type="capsule" fromto="0 0 0 {FEMUR} 0 0" size="0.014" mass="0.14"/>
          {vis("femur_pla", pla)}{vis("femur_dark", "dark")}{vis("femur_metal", "metal")}
          <body pos="{FEMUR} 0 0">
            <joint name="{j}_t" axis="0 1 0" range="{LIMITS[2][0]} {LIMITS[2][1]}"/>
            <geom class="col" type="capsule" fromto="0 0 0 0 0 {-TIBIA + 0.005}" size="0.008" mass="0.03"/>
            {vis("tibia_pla", pla)}{vis("tibia_foot", "foot")}
          </body>
        </body>
      </body>"""
            for k, part in enumerate("cft"):
                motors += f'<position joint="{j}_{part}" kp="20" forcerange="-0.9 0.9" ctrlrange="{LIMITS[k][0]} {LIMITS[k][1]}"/>\n'
        robots += f"""
    <body name="r{i}" pos="{x} {y} {STAND_Z}">
      <freejoint/>
      <geom class="col" type="box" size="0.09 0.055 0.02" pos="0 0 0.01" mass="1.0"/>
      <geom class="col" type="box" size="0.07 0.024 0.013" pos="0 0 -0.024" mass="0.35"/>
      {vis("body_pla", pla)}{vis("body_dark", "dark")}{vis("body_metal", "metal")}{vis("body_accent", "accent")}{legs}
    </body>"""
    meshes = "".join(f'<mesh name="{p}" file="{p}.stl"/>' for p in PARTS)
    # MG995: about 0.9 N·m stall and 6 rad/s, which is what forcerange and joint damping give.
    # Only the hidden "col" shapes touch the floor; the meshes are just for looks.
    return f"""
<mujoco>
  <compiler angle="radian" meshdir="{MESHES}"/>
  <option timestep="{STEP_S}" integrator="implicitfast"/>
  <default>
    <joint damping="0.15" armature="0.005"/>
    <default class="col"><geom contype="0" conaffinity="1" friction="1.0 0.005 0.0001" group="3"/></default>
    <default class="vis"><geom type="mesh" contype="0" conaffinity="0" density="0" group="1"/></default>
  </default>
  <asset>
    {meshes}
    <texture type="skybox" builtin="gradient" rgb1="0.62 0.70 0.80" rgb2="0.93 0.94 0.95" width="256" height="1536"/>
    <texture name="floor" type="2d" builtin="checker" rgb1="0.60 0.62 0.65" rgb2="0.55 0.57 0.60" mark="edge" markrgb="0.42 0.44 0.47" width="512" height="512"/>
    <material name="floor" texture="floor" texrepeat="100 100" reflectance="0.12" shininess="0.2"/>
    <material name="pla" rgba="0.07 0.07 0.08 1" specular="0.5" shininess="0.5"/>
    <material name="best" rgba="0.95 0.42 0.04 1" specular="0.5" shininess="0.5"/>
    <material name="dark" rgba="0.02 0.02 0.025 1" specular="0.8" shininess="0.8"/>
    <material name="metal" rgba="0.75 0.76 0.78 1" specular="1" shininess="0.9" reflectance="0.3"/>
    <material name="accent" rgba="0.86 0.87 0.9 1" specular="0.6" shininess="0.6"/>
    <material name="foot" rgba="0.55 0.06 0.04 1"/>
  </asset>
  <visual>
    <headlight ambient="0.45 0.45 0.45" diffuse="0.35 0.35 0.35" specular="0.1 0.1 0.1"/>
    <quality shadowsize="8192" offsamples="8"/>
    <map shadowclip="6" zfar="80" fogstart="25" fogend="70"/>
    <rgba haze="0.93 0.94 0.95 1" fog="0.93 0.94 0.95 1"/>
    <global offwidth="1920" offheight="1080"/>
  </visual>
  <worldbody>
    <light directional="true" dir="-0.4 0.5 -1" diffuse="0.7 0.7 0.68" specular="0.3 0.3 0.3" castshadow="true"/>
    <geom type="plane" size="100 100 0.1" material="floor" contype="1" conaffinity="0"/>
    {robots}
  </worldbody>
  <actuator>
    {motors}
  </actuator>
</mujoco>"""


N_PARAMS = HIDDEN * 4 + HIDDEN + 18 * HIDDEN + 18


def act(brains, t):
    """brains: (n, N_PARAMS). Each is a small network: where we are in the step cycle -> 18 joint angles."""
    a = 2 * np.pi * t / PERIOD_S
    x = np.array([np.sin(a), np.cos(a), np.sin(2 * a), np.cos(2 * a)])
    i = HIDDEN * 4
    w1 = brains[:, :i].reshape(-1, HIDDEN, 4)
    b1 = brains[:, i:i + HIDDEN]
    i += HIDDEN
    w2 = brains[:, i:i + 18 * HIDDEN].reshape(-1, 18, HIDDEN)
    b2 = brains[:, i + 18 * HIDDEN:]
    h = np.tanh(w1 @ x + b1)
    out = np.tanh(np.einsum("nij,nj->ni", w2, h) + b2).reshape(-1, 6, 3)
    keep = [m for m in range(6) if m != MISSING]
    return (STAND + out * SWING)[:, keep].reshape(len(brains), -1)


def run(model, data, brains, viewer=None):
    """One episode for every robot at once. Returns how well each one walked."""
    n = len(brains)
    mujoco.mj_resetData(model, data)
    qpos = data.qpos.reshape(n, -1)
    qpos[:, 7:] = np.tile(STAND, (qpos.shape[1] - 7) // 3)
    start = qpos[:, :2].copy()
    mujoco.mj_forward(model, data)
    tilt = np.zeros(n)
    steps = int(EPISODE_S / STEP_S)
    for s in range(steps):
        if s % 5 == 0:   # the real robot updates its servos every 20 ms too
            data.ctrl[:] = act(brains, s * STEP_S).ravel()
        mujoco.mj_step(model, data)
        up = 1 - 2 * (qpos[:, 4] ** 2 + qpos[:, 5] ** 2)   # 1 = level, 0 = on its side
        tilt += 1 - up
        if viewer and s % RENDER_EVERY == 0:
            if not viewer.is_running():
                return None
            viewer.cam.azimuth += ORBIT
            viewer.sync()
    forward = qpos[:, 0] - start[:, 0]
    drift = np.abs(qpos[:, 1] - start[:, 1])
    fell = (up < 0.5) | (qpos[:, 2] < 0.05)
    return forward - 0.5 * drift - 0.5 * tilt / steps - 1.0 * fell


def train(show):
    rng = np.random.default_rng()
    model = mujoco.MjModel.from_xml_string(build(ROBOTS))
    data = mujoco.MjData(model)
    try:
        best = np.load(SAVE)
        print("continuing from", SAVE)
    except FileNotFoundError:
        best = rng.normal(0, 0.1, N_PARAMS)
    viewer = None
    if show:
        from mujoco import viewer as mjv
        viewer = mjv.launch_passive(model, data, show_left_ui=False, show_right_ui=False)
        viewer.cam.lookat[:] = [-2, 0, 0.1]
        viewer.cam.distance, viewer.cam.elevation, viewer.cam.azimuth = 6, -14, 200
    record, gen, half = -9, 0, (ROBOTS - 1) // 2
    while True:
        gen += 1
        noise = rng.normal(0, 1, (half, N_PARAMS))
        brains = np.vstack([best, best + SIGMA * noise, best - SIGMA * noise])
        score = run(model, data, brains, viewer)
        if score is None:
            break
        rank = np.argsort(np.argsort(score[1:])) / (2 * half - 1) - 0.5
        best = best + LEARN_RATE / SIGMA * (rank[:half] - rank[half:]) @ noise / half
        print(f"generation {gen:4d}   orange walked {score[0]:5.2f} m   best mutation {score[1:].max():5.2f} m")
        if score[0] > record:
            record = score[0]
            np.save(SAVE, brains[0])
    print("saved", SAVE)


def watch():
    model = mujoco.MjModel.from_xml_string(build(1))
    data = mujoco.MjData(model)
    brain = np.load(SAVE)[None]
    from mujoco import viewer as mjv
    with mjv.launch_passive(model, data, show_left_ui=False, show_right_ui=False) as viewer:
        viewer.cam.distance, viewer.cam.elevation = 1.0, -20
        t = 0.0
        while viewer.is_running():
            if round(t / STEP_S) % 5 == 0:
                data.ctrl[:] = act(brain, t).ravel()
            mujoco.mj_step(model, data)
            t += STEP_S
            viewer.cam.lookat[:] = data.qpos[:3]
            viewer.cam.azimuth += ORBIT
            viewer.sync()
            time.sleep(STEP_S)


if __name__ == "__main__":
    args = [a.lower() for a in sys.argv[1:]]
    for i, leg in enumerate(LEGS):
        if leg.lower() in args:
            MISSING, SAVE = i, f"vanta_brain_no_{leg}.npy"
            print("training without the", leg, "leg ->", SAVE)
    mode = "watch" if "watch" in args else "fast" if "fast" in args else "show"
    if mode == "watch":
        watch()
    else:
        train(show=mode != "fast")
