"""The 18 MG995s on two PCA9685 boards (both at 0x40: PCA #1 on I2C bus 1, PCA #2 on bus 3).

Controller angles (degrees) -> pulse: 1500us + sign * angle * US_PER_DEG + trim.
Angle 0 on every joint is the step 12 pose (coxa straight out, femur level, tibia straight down),
which is where the horns went on at 1500us. Trims and any flipped directions live in calibration.json
(written by tools/calibrate.py).
"""
import json
import time
from pathlib import Path

from robot.kinematics import LIMITS

ADDR = 0x40
MODE1, PRESCALE, LED0 = 0x00, 0xFE, 0x06
# Facing the robot from the front: the legs on your right (the robot's left) are on PCA #1 (bus 1), channels 0 up;
# the legs on your left (the robot's right) are on PCA #2 (bus 3), channels 15 down. Grouped by joint, front leg first:
# coxas 0-2 / 15-13, femurs 3-5 / 12-10, tibias 6-8 / 9-7. Values are (coxa, femur, tibia).
CHANNELS = {"FL": (1, (0, 3, 6)), "ML": (1, (1, 4, 7)), "RL": (1, (2, 5, 8)),
            "FR": (3, (15, 12, 9)), "MR": (3, (14, 11, 8)), "RR": (3, (13, 10, 7))}
JOINTS = ("coxa", "femur", "tibia")
# From the URDF: every leg is the same parts rotated, so the signs match on both sides.
# Assumes a bigger pulse turns the horn counterclockwise seen from the horn side (MG995 spec); calibrate.py checks it.
SIGN = {"coxa": -1, "femur": 1, "tibia": 1}
US_PER_DEG = 2000 / 180
CALIBRATION = Path(__file__).resolve().parent.parent / "calibration.json"


def load_calibration():
    if CALIBRATION.exists():
        return json.loads(CALIBRATION.read_text())
    return {"us_per_deg": US_PER_DEG, "trim_us": {}, "flip": []}


def save_calibration(cal):
    CALIBRATION.write_text(json.dumps(cal, indent=2))


def setup(bus):
    bus.write_byte_data(ADDR, MODE1, 0x10)
    # 25MHz / (4096 * 50Hz) - 1. Clone boards run a few % fast; the per-servo trims soak that up.
    bus.write_byte_data(ADDR, PRESCALE, 121)
    bus.write_byte_data(ADDR, MODE1, 0x00)
    time.sleep(0.005)
    bus.write_byte_data(ADDR, MODE1, 0xA0)


def counts(us):
    return round(us * 4096 / 20000)


def release(bus, ch):
    bus.write_i2c_block_data(ADDR, LED0 + 4 * ch, [0, 0, 0, 0x10])


class Servos:
    def __init__(self, cal=None, smbus=None):
        if smbus is None:
            from smbus2 import SMBus as smbus
        self.cal = cal or load_calibration()
        self.buses = {}
        for n in sorted({b for b, _ in CHANNELS.values()}):
            self.buses[n] = smbus(n)
            setup(self.buses[n])
        self.live = set()

    def pulse_us(self, leg, joint, angle):
        lo, hi = LIMITS[joint]
        name = f"{leg}_{joint}"
        sign = -SIGN[joint] if name in self.cal["flip"] else SIGN[joint]
        return 1500 + sign * max(lo, min(hi, angle)) * self.cal["us_per_deg"] + self.cal["trim_us"].get(name, 0)

    def write(self, joints, stagger=0.0):
        """joints: {leg: (coxa, femur, tibia)} in controller degrees."""
        for leg, angles in joints.items():
            bus, chans = CHANNELS[leg]
            for joint, ch, a in zip(JOINTS, chans, angles):
                off = counts(self.pulse_us(leg, joint, a))
                self.buses[bus].write_i2c_block_data(ADDR, LED0 + 4 * ch, [0, 0, off & 0xFF, off >> 8])
            if stagger and leg not in self.live:
                # first write per leg: one leg at a time so 18 servos don't all lurch (and spike the current) together
                self.live.add(leg)
                time.sleep(stagger)

    def release(self):
        for bus in self.buses.values():
            for ch in range(16):
                release(bus, ch)
