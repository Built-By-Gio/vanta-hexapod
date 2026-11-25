# Hexapod brain

## Run the gesture viewer on your PC

Use Python 3.11 or 3.12. MediaPipe doesn't always have wheels for the newest Python.

```
cd hexapod-brain
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python gesture_view.py
```

The first run downloads the hand model (~8MB) into `models/`. Press `q` to quit. Options: `--camera 1` picks another webcam, and `--no-mirror` turns off the selfie flip.

## Run the sim

```
python sim.py
```

It opens a browser tab with the real robot model, and your hand gestures drive it. The top-right shows what the camera sees. Use `python sim.py --no-camera` to drive it with the keyboard only.

- FOLLOW, FAST FOLLOW, FREE ROAM and DANCE keep going until you give STOP (open palm) or switch modes. In the follow modes the robot steers toward your hand; if the hand leaves the frame it keeps walking straight. Bringing your hand right up to the camera makes it pause, and it carries on when you pull back.
- DANCE loops a 16s routine (bounce, sway + twist, tripod stomp, front-leg wave) over and over until STOP.
- CROUCH, STAND, TRANSPORT, RAISE and LOWER are one-shot: they do the move and hold it.
- FREE ROAM wanders on its own and turns back if it gets more than 1.5m from the start.
- In the browser: `H` hides or shows the shell, `C` toggles camera follow, and number keys 1–8 plus the arrow keys trigger modes.
- If a move would push a joint past the range the CAD says is safe, a red "joint limit" warning appears.

The sim runs the same controller code (`robot/`) that will drive the real servos, so what you see is what the robot will do.

## Phone control

```
python sim.py --lan
```

It prints a `Phone control: http://...:8765/control` link. Open that on your phone (same WiFi) for a big STOP button, all the modes, height, the live camera and the log. Gestures keep working alongside it; whichever command comes last wins. The page is served by the robot itself, so the same page will drive the real hexapod once it's running on the Pi. If Windows asks about the firewall the first time, allow it on private networks.

## On the robot

`PI_SETUP.md` covers the whole Pi side:
- I2C setup,
- install,
- calibration (`tools/calibrate.py`),
- running with real servos (`python sim.py --robot`),
- starting on boot.

`python test_servos.py` checks the servo output without hardware.

`python test_robot.py` checks the leg math: IK accuracy, feet not slipping while walking, and every mode staying inside the joint limits.

## Gestures

Hold a gesture steady for about half a second to trigger it. STOP triggers almost instantly. RAISE and LOWER repeat while you hold them.

| Hand | Mode |
|---|---|
| open palm | STOP |
| fist | CROUCH |
| index finger up | FOLLOW |
| peace | FAST FOLLOW |
| 3 fingers (index, middle, ring) | FREE ROAM |
| rock (index + pinky) | DANCE |
| shaka (thumb + pinky) | TRANSPORT |
| OK | STAND |
| thumb up | RAISE body |
| thumb down | LOWER body |

The `T I M R P` boxes at the bottom show which fingers the classifier thinks are extended. If a gesture won't register, those boxes tell you which finger it's misreading.

`python test_gestures.py` runs the classifier against synthetic hands. It doesn't need a camera.

## On the Pi later

The same code runs there. `camera.py` switches to the Pi camera automatically when `picamera2` is installed (`sudo apt install python3-picamera2`).
