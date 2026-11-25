"""Hold every servo at 1500us so the horns can be fitted at the zero pose.

Run on the Pi:  python tools/center_servos.py
Ctrl+C releases the servos (outputs off).
"""
import argparse
import sys
import time
from pathlib import Path

from smbus2 import SMBus

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from robot.servos import ADDR, CHANNELS, LED0, counts, release, setup

BUSES = {1: "PCA #1 (FL, ML, RL)", 3: "PCA #2 (FR, MR, RR)"}


def pulse(bus, ch, us):
    off = counts(us)
    bus.write_i2c_block_data(ADDR, LED0 + 4 * ch, [0, 0, off & 0xFF, off >> 8])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--us", type=int, default=1500)
    args = ap.parse_args()

    buses = {}
    for n, name in BUSES.items():
        try:
            b = SMBus(n)
            setup(b)
            buses[n] = b
            print(f"bus {n}: {name} ok")
        except OSError as e:
            print(f"bus {n}: {name} not found ({e}). Check wiring and config.txt.")

    # One servo at a time so 18 of them don't all jump (and spike the current) together.
    n = 0
    for leg, (bus, chans) in CHANNELS.items():
        if bus not in buses:
            continue
        for ch in chans:
            pulse(buses[bus], ch, args.us)
            n += 1
            time.sleep(0.15)
    print(f"Holding {args.us}us on {n} servos. Ctrl+C to release.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        for b in buses.values():
            for ch in range(16):
                release(b, ch)
            b.close()
        print("released")


if __name__ == "__main__":
    main()
