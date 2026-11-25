"""Test the 6 coxa servos in the base before the legs go on.

Run on the Pi, battery in:  python tools/test_coxa.py
Each coxa goes to centre, one at a time, then swings +15 / -15 and back. Ctrl+C releases them.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from robot.servos import CHANNELS, Servos

ORDER = ["FL", "ML", "RL", "FR", "MR", "RR"]


def main():
    servos = Servos()
    pose = {}
    try:
        for leg in ORDER:
            pose[leg] = [0.0, 0.0, 0.0]
            servos.write({leg: pose[leg]})
            bus, chans = CHANNELS[leg]
            print(f"{leg} coxa (bus {bus}, ch {chans[0]}) -> centre")
            time.sleep(0.6)
        input("All six at centre. Enter to swing each one (Ctrl+C to stop).")
        for leg in ORDER:
            print(f"{leg}: +15 should swing counterclockwise seen from above")
            for a in (15, 0, -15, 0):
                pose[leg][0] = a
                servos.write({leg: pose[leg]})
                time.sleep(0.8)
        print("done, holding centre. Ctrl+C to release.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print()
    finally:
        servos.release()
        print("released")


if __name__ == "__main__":
    main()
