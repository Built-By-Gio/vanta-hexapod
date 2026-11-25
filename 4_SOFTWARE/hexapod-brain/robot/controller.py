import math
import random

from .kinematics import LEGS, TRIPOD_A, TRIPOD_B, leg_ik, out_of_range

REACH = 145.0
LOW_Z, HIGH_Z = 50.0, 115.0
WALK_MIN_Z = 75.0
REST_Z = 38.0
FOLD = (0.0, 80.0, 60.0)
LIFT = 30.0
WAVE = 20.0
MOVE_S = 4.0
BLEND_S = 1.5

GAITS = {
    "FOLLOW": dict(cycle=1.0, speed=60.0, turn=0.5),
    "FAST FOLLOW": dict(cycle=0.7, speed=140.0, turn=0.8),
    "FREE ROAM": dict(cycle=0.9, speed=80.0, turn=0.6),
}


def _smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def _approach(cur, target, rate, dt):
    step = rate * dt
    return target if abs(target - cur) <= step else cur + math.copysign(step, target - cur)


def _neutral(leg):
    mx, my, g = LEGS[leg]
    g = math.radians(g)
    return mx + REACH * math.cos(g), my + REACH * math.sin(g)


def _bounce(b):
    return [0.0, 0.0, 12 * math.sin(b), math.radians(4) * math.sin(b), 0.0, 0.0], {}


def _sway(b):
    s = math.sin(b / 2)
    return [0.0, 20 * s, 4 * abs(s), math.radians(6) * s, 0.0, math.radians(12) * s], {}


def _stomp(b):
    s = math.sin(b / 2)
    lift = {leg: 25 * max(0.0, s) for leg in TRIPOD_A} | {leg: 25 * max(0.0, -s) for leg in TRIPOD_B}
    return [0.0, 0.0, 6 * abs(s), 0.0, 0.0, math.radians(8) * s], lift


def _wave(b):
    s = math.sin(b)
    return [-15.0, 8 * math.sin(b / 2), 0.0, 0.0, 0.0, 0.0], {"FL": WAVE + 10 * s, "FR": WAVE - 10 * s}


DANCE_MOVES = (_bounce, _sway, _stomp, _wave)


class Robot:
    def __init__(self):
        self.mode = "STAND"
        self.height = 50
        self.z = self._height_z()
        self.x = self.y = self.yaw = 0.0
        self.v = [0.0, 0.0, 0.0]
        self.feet = {leg: list(_neutral(leg)) for leg in LEGS}
        self.lift = {leg: 0.0 for leg in LEGS}
        self.swing_from = {}
        self.phase = 0.0
        self.walking = False
        self.offset = [0.0] * 6
        self.joints = {leg: leg_ik(leg, *self.feet[leg], -self.z) for leg in LEGS}
        self.blend = None
        self.target = None
        self.t = 0.0
        self.mode_t = 0.0
        self.roam_next = 0.0
        self.roam_cmd = (0.0, 0.0)
        self.warnings = []

    def _height_z(self):
        return LOW_Z + (HIGH_Z - LOW_Z) * self.height / 100

    def command(self, cmd):
        if cmd == "RAISE":
            self.height = min(100, self.height + 10)
            return
        if cmd == "LOWER":
            self.height = max(0, self.height - 10)
            return
        if cmd == self.mode:
            return
        if (cmd == "TRANSPORT") != (self.mode == "TRANSPORT"):
            self.blend = dict(joints=dict(self.joints), z=self.z, t=0.0)
        self.mode, self.mode_t = cmd, 0.0

    def step(self, dt):
        self.t += dt
        self.mode_t += dt
        self.warnings = []
        if self.mode == "STOP":
            return

        cmd = self._velocity_command() if self.z >= WALK_MIN_Z - 1 else (0.0, 0.0, 0.0)
        gait = GAITS.get(self.mode, GAITS["FOLLOW"])
        for i, rate in enumerate((250.0, 250.0, 1.5)):
            self.v[i] = _approach(self.v[i], cmd[i], rate, dt)

        target_z = REST_Z if self.mode == "TRANSPORT" else LOW_Z if self.mode == "CROUCH" else self._height_z()
        if self.mode in GAITS or self.mode == "DANCE":
            # Legs run out of tibia travel lifting a foot this close to the ground, so walking keeps some height.
            target_z = max(target_z, WALK_MIN_Z)
        if self.mode != "TRANSPORT":
            self.z = _approach(self.z, target_z, 40.0, dt)
        if self.mode == "DANCE":
            self._dance(dt)
        else:
            self._settle_offset(dt)
        if self.mode != "TRANSPORT":
            self._gait(gait["cycle"], dt)

        ik = {}
        for leg in LEGS:
            fx, fy = self.feet[leg]
            ik[leg] = leg_ik(leg, *self._to_body(fx, fy, -self.z + self.lift[leg]))
        target = {leg: FOLD for leg in LEGS} if self.mode == "TRANSPORT" else ik

        if self.blend:
            self.blend["t"] += dt
            k = _smooth(self.blend["t"] / BLEND_S)
            self.joints = {leg: tuple(a + (b - a) * k for a, b in zip(self.blend["joints"][leg], target[leg])) for leg in LEGS}
            if self.mode == "TRANSPORT":
                self.z = self.blend["z"] + (REST_Z - self.blend["z"]) * k
            if k >= 1:
                self.blend = None
        else:
            self.joints = target

        for leg, angles in self.joints.items():
            for name in out_of_range(angles):
                self.warnings.append(f"{leg} {name} {angles[('coxa', 'femur', 'tibia').index(name)]:.0f}°")

    def _velocity_command(self):
        g = GAITS.get(self.mode)
        if not g:
            return (0.0, 0.0, 0.0)
        if self.mode == "FREE ROAM":
            if self.t >= self.roam_next:
                self.roam_next = self.t + random.uniform(2.0, 5.0)
                self.roam_cmd = (g["speed"] * random.choice((0.4, 1.0, 1.0)), random.uniform(-1, 1) * g["turn"])
            v, w = self.roam_cmd
            if math.hypot(self.x, self.y) > 1500:
                home = math.atan2(-self.y, -self.x) - self.yaw
                w = g["turn"] * max(-1.0, min(1.0, math.atan2(math.sin(home), math.cos(home))))
            return (v, 0.0, w)
        if not self.target:
            # Lost the hand: keep walking straight until told to STOP, don't just stall.
            return (g["speed"], 0.0, 0.0)
        x, size = self.target
        w = max(-1.0, min(1.0, -(x - 0.5) * 3)) * g["turn"]
        v = 0.0 if size > 0.18 else g["speed"]
        return (v, 0.0, w)

    def _gait(self, cycle, dt):
        vx, vy, w = self.v
        moving = abs(vx) > 1 or abs(vy) > 1 or abs(w) > 0.02
        off_home = any(math.dist(self.feet[leg], _neutral(leg)) > 1.0 for leg in LEGS)
        if not (moving or off_home or self.walking):
            return
        if not self.walking:
            self.walking, self.phase = True, 0.0
            self.swing_from = {leg: tuple(self.feet[leg]) for leg in TRIPOD_A}

        prev = self.phase
        self.phase = (self.phase + dt / cycle) % 1.0
        if prev < 0.5 <= self.phase or self.phase < prev:
            swinging = TRIPOD_A if self.phase < 0.5 else [l for l in LEGS if l not in TRIPOD_A]
            self.swing_from = {leg: tuple(self.feet[leg]) for leg in swinging}
            if not moving and not off_home and self.phase < prev:
                self.walking = False
                self.phase = 0.0
                return

        half = self.phase * 2 if self.phase < 0.5 else self.phase * 2 - 1
        for leg in LEGS:
            fx, fy = self.feet[leg]
            if leg in self.swing_from and ((leg in TRIPOD_A) == (self.phase < 0.5)):
                nx, ny = _neutral(leg)
                tx = nx + (vx - w * ny) * cycle / 4
                ty = ny + (vy + w * nx) * cycle / 4
                sx, sy = self.swing_from[leg]
                k = _smooth(half)
                self.feet[leg] = [sx + (tx - sx) * k, sy + (ty - sy) * k]
                self.lift[leg] = LIFT * math.sin(math.pi * half)
            else:
                self.feet[leg] = [fx - (vx - w * fy) * dt, fy - (vy + w * fx) * dt]
                self.lift[leg] = 0.0

        c, s = math.cos(self.yaw), math.sin(self.yaw)
        self.x += (vx * c - vy * s) * dt
        self.y += (vx * s + vy * c) * dt
        self.yaw += w * dt

    def _dance(self, dt):
        # 16s routine on a 120bpm beat, loops until another mode takes over.
        t = self.mode_t
        seg = (t % (MOVE_S * len(DANCE_MOVES))) / MOVE_S
        i = int(seg)
        k = _smooth((seg - i - 0.85) / 0.15)
        b = 2 * math.pi * 2.0 * t
        off_a, lift_a = DANCE_MOVES[i](b)
        off_b, lift_b = DANCE_MOVES[(i + 1) % len(DANCE_MOVES)](b)
        self.offset = [a + (c - a) * k for a, c in zip(off_a, off_b)]
        for leg in LEGS:
            a, c = lift_a.get(leg, 0.0), lift_b.get(leg, 0.0)
            self.lift[leg] = _approach(self.lift[leg], a + (c - a) * k, 250, dt)

    def _settle_offset(self, dt):
        self.offset = [_approach(o, 0.0, 60.0 if i < 3 else 0.6, dt) for i, o in enumerate(self.offset)]
        if self.mode != "DANCE" and not self.walking:
            for leg in LEGS:
                self.lift[leg] = _approach(self.lift[leg], 0.0, 150, dt)

    def _to_body(self, x, y, z):
        dx, dy, dz, roll, pitch, yaw = self.offset
        px, py, pz = x - dx, y - dy, z - dz
        cy, sy = math.cos(-yaw), math.sin(-yaw)
        px, py = px * cy - py * sy, px * sy + py * cy
        cp, sp = math.cos(-pitch), math.sin(-pitch)
        px, pz = px * cp + pz * sp, -px * sp + pz * cp
        cr, sr = math.cos(-roll), math.sin(-roll)
        py, pz = py * cr - pz * sr, py * sr + pz * cr
        return px, py, pz

    def pose(self):
        dx, dy, dz, roll, pitch, yaw = self.offset
        c, s = math.cos(self.yaw), math.sin(self.yaw)
        return dict(x=self.x + dx * c - dy * s, y=self.y + dx * s + dy * c, z=self.z + dz,
                    yaw=self.yaw + yaw, pitch=pitch, roll=roll)
