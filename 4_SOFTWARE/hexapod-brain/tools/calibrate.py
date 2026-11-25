"""Walk through all 18 joints: check each one turns the right way, then trim it straight.
Saves calibration.json after every joint, so you can stop and pick up later with --leg.

Run on the Pi, robot fully built, held up off the table:  python tools/calibrate.py
"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from robot.servos import CHANNELS, JOINTS, Servos, load_calibration, save_calibration

PLUS = {"coxa": "swing counterclockwise, seen from above",
        "femur": "lift the knee up",
        "tibia": "swing the foot in toward the body"}
STRAIGHT = {"coxa": "leg points straight out from the body",
            "femur": "femur level with the table",
            "tibia": "tibia straight down"}


def ask(prompt):
    try:
        return input(prompt).strip().lower()
    except EOFError:
        return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--leg", choices=list(CHANNELS), action="append", help="only these legs (repeat for more)")
    ap.add_argument("--scale", action="store_true", help="only check degrees-per-pulse with a phone level app")
    args = ap.parse_args()

    cal = load_calibration()
    servos = Servos(cal)
    pose = {leg: [0.0, 0.0, 0.0] for leg in CHANNELS}
    servos.write(pose, stagger=0.3)
    print("All joints at zero (the step 12 pose). Ctrl+C at any time releases the servos.\n")

    try:
        if args.scale:
            check_scale(servos, pose, cal)
            return
        for leg in args.leg or list(CHANNELS):
            for i, joint in enumerate(JOINTS):
                name = f"{leg}_{joint}"
                while True:
                    print(f"{name}: moving +15 deg. It should {PLUS[joint]}.")
                    pose[leg][i] = 15.0
                    servos.write(pose)
                    time.sleep(1.0)
                    pose[leg][i] = 0.0
                    servos.write(pose)
                    time.sleep(0.5)
                    if ask("  Right way? [Y/n] ") != "n":
                        break
                    flips = set(cal["flip"]) ^ {name}
                    cal["flip"] = sorted(flips)
                    servos.write(pose)
                    print("  Flipped. Testing again.")
                print(f"  Now trim until: {STRAIGHT[joint]}. Type +1, -0.5, +3 ... (degrees), Enter when it's right.")
                while True:
                    a = ask(f"  {name} trim {cal['trim_us'].get(name, 0) / cal['us_per_deg']:+.1f} deg > ")
                    if not a:
                        break
                    try:
                        cal["trim_us"][name] = round(cal["trim_us"].get(name, 0) + float(a) * cal["us_per_deg"], 1)
                    except ValueError:
                        print("  A number like +1 or -0.5, or Enter to move on.")
                        continue
                    servos.write(pose)
                save_calibration(cal)
                print("  saved\n")
        print("Done. calibration.json is used by sim.py --robot.")
    except KeyboardInterrupt:
        print()
    finally:
        servos.release()
        print("released")


def check_scale(servos, pose, cal):
    print("Put a phone with a level app flat on the FR femur. Zero it there, then press Enter.")
    ask("")
    pose["FR"][1] = 45.0
    servos.write(pose)
    r = ask("FR femur sent to +45 deg. What does the phone read? ")
    pose["FR"][1] = 0.0
    servos.write(pose)
    try:
        reading = abs(float(r))
    except ValueError:
        print("No reading, nothing changed.")
        return
    if not 20 < reading < 80:
        print("That's far off 45. Check the phone is on the femur and try again. Nothing changed.")
        return
    cal["us_per_deg"] = round(cal["us_per_deg"] * 45.0 / reading, 3)
    save_calibration(cal)
    print(f"us_per_deg -> {cal['us_per_deg']} (saved). Re-check the trims if this changed a lot.")


if __name__ == "__main__":
    main()
