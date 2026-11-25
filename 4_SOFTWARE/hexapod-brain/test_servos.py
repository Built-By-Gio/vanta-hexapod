"""Servo output without hardware: a fake I2C bus records what would be sent to the two PCA9685s."""

from robot.controller import Robot
from robot.servos import CHANNELS, JOINTS, Servos, counts


class FakeBus:
    def __init__(self, n):
        self.n, self.regs = n, {}

    def write_byte_data(self, addr, reg, val):
        self.regs[reg] = val

    def write_i2c_block_data(self, addr, reg, data):
        assert len(data) <= 32
        for i, v in enumerate(data):
            self.regs[reg + i] = v


def channel_us(bus, ch):
    r = bus.regs
    off = r[0x06 + 4 * ch + 2] | r[0x06 + 4 * ch + 3] << 8
    return off * 20000 / 4096


cal = {"us_per_deg": 2000 / 180, "trim_us": {"FR_femur": 20.0}, "flip": ["ML_tibia"]}
s = Servos(cal, smbus=FakeBus)
assert set(s.buses) == {1, 3}

s.write({leg: (0.0, 0.0, 0.0) for leg in CHANNELS})
for leg, (b, chans) in CHANNELS.items():
    for i, j in enumerate(JOINTS):
        want = counts(1500 + cal["trim_us"].get(f"{leg}_{j}", 0)) * 20000 / 4096
        assert channel_us(s.buses[b], chans[i]) == want, (leg, j)
print("zero pose: 1500us everywhere, trim applied on FR femur")

s.write({"FR": (10.0, 10.0, 10.0), "ML": (0.0, 0.0, 10.0)})
us = [channel_us(s.buses[3], c) for c in (15, 12, 9)]
assert us[0] < 1490 and us[1] > 1610 and us[2] > 1590, us
assert channel_us(s.buses[1], 7) < 1400, "ML tibia is flipped"
print("directions: coxa -, femur +, tibia +, flip honoured:", [round(u) for u in us])

s.write({"FR": (90.0, -200.0, 0.0)})
assert abs(channel_us(s.buses[3], 15) - (1500 - 35 * cal["us_per_deg"])) < 3
assert abs(channel_us(s.buses[3], 12) - (1500 - 80 * cal["us_per_deg"] + 20)) < 3
print("out-of-range angles clamp to the joint limits")

r = Robot()
r.target = (0.5, 0.1)
r.command("FOLLOW")
lo = hi = 1500
for _ in range(300):
    r.step(1 / 50)
    s.write(r.joints)
    for b, chans in CHANNELS.values():
        for ch in chans:
            u = channel_us(s.buses[b], ch)
            lo, hi = min(lo, u), max(hi, u)
assert 900 < lo and hi < 2100, (lo, hi)
print(f"6s of walking: pulses stay within {lo:.0f}..{hi:.0f}us")
