# Running VANTA on the Pi

These steps are for a Raspberry Pi 4 with Raspberry Pi OS (64-bit, Bookworm). Do them once, before guide step 17.

## 1. Flash the SD card

Use Raspberry Pi Imager and pick **Raspberry Pi OS (64-bit)**. In the settings (gear icon):
- Hostname: `vanta`.
- Username: `gio`. If you pick a different one, change it in `vanta.service` too.
- Your WiFi network.
- Turn on SSH.

Boot the Pi, then from your laptop: `ssh gio@vanta.local`

## 2. I2C, the second I2C bus, and the camera

```
sudo raspi-config nonint do_i2c 0
sudo nano /boot/firmware/config.txt
```

Add these lines at the bottom:

```
dtparam=i2c_arm=on
dtparam=i2c_arm_baudrate=400000
dtoverlay=i2c-gpio,bus=3,i2c_gpio_sda=4,i2c_gpio_scl=5,i2c_gpio_delay_us=2
```

- **Bus 1** (pins 3 and 5) is PCA #1: FL, ML, RL (the legs on your right when you face the robot). Coxas 0-1-2, femurs 3-4-5, tibias 6-7-8, front leg first.
- **Bus 3** (pins 7 and 29) is PCA #2: FR, MR, RR (the legs on your left when you face it). Coxas 15-14-13, femurs 12-11-10, tibias 9-8-7, front leg first.

Both boards are at address 0x40, which is why they need separate buses.

Check that `camera_auto_detect=1` is still in the file; it is by default, and it finds the OV5647. Then `sudo reboot`.

## 3. Install

```
sudo apt update
sudo apt install -y python3-picamera2 python3-opencv i2c-tools
python3 -m venv --system-site-packages ~/vanta-venv
source ~/vanta-venv/bin/activate
```

Copy the `hexapod-brain` folder to `/home/gio/hexapod-brain`, for example `scp -r hexapod-brain gio@vanta.local:~` from your laptop. Then:

```
cd ~/hexapod-brain
pip install -r requirements-pi.txt
```

Use `requirements-pi.txt` here, not `requirements.txt`. OpenCV and the camera library come from apt, and the pip OpenCV would clash with them.

## 4. Check the boards

Do this with the battery in and the switch on.

```
i2cdetect -y 1
i2cdetect -y 3
```

Both should show `40`.
- **One is missing:** check that board's SDA and SCL jumpers (guide step 4 picture) and that its VCC is on 3.3V.
- **Bus 3 doesn't exist at all:** the `dtoverlay` line isn't in `config.txt`, or you haven't rebooted since adding it.

`python tools/center_servos.py` holds every servo at its centre position. That's guide steps 4 and 17.

## 5. Calibrate

Do this once, after the robot is built. Hold the robot up off the table first.

```
python tools/calibrate.py
```

It goes through all 18 joints. For each one:
1. It moves the joint 15° and tells you which way it should have gone. Type `n` if it went the other way, and it flips that joint.
2. You trim the joint until it's straight: type `+1`, `-0.5` and so on (degrees), then press Enter.

It saves `calibration.json` after every joint. To redo legs: `--leg FR --leg ML`.

Optional, but it makes the walking more accurate: `python tools/calibrate.py --scale`. You lay a phone level app on the front-right femur and type in what it reads at 45°.

## 6. Run it

Hold the robot up the first time.

```
python sim.py --robot
```

This does everything at once:
- It drives the servos 50 times a second.
- It reads gestures from the robot's camera.
- It prints a **phone control** link. That page has a big STOP button, every mode, height and the live camera.

Without the camera: `python sim.py --robot --no-camera`. The phone page still works.

When it starts, it steps into STAND one leg at a time. Ctrl+C (or stopping the service) turns the servos off, and the robot sits down hard. Have a hand under it.

The MediaPipe hand tracking runs at about 8–12 fps on a Pi 4. That's fine for gestures, but the follow steering reacts a bit slower than on your laptop. The servo loop doesn't wait for the camera, so walking stays smooth either way.

## 7. Start on boot (optional)

```
sudo cp vanta.service /etc/systemd/system/
sudo systemctl enable --now vanta
journalctl -u vanta -f      # see what it's doing
sudo systemctl stop vanta   # servos off
```

## If something's off

| What you see | Fix |
|---|---|
| A leg moves the wrong way in every mode | Rerun calibrate for that leg and flip the joint. |
| Every femur and tibia overshoots or undershoots | Run `calibrate.py --scale`. |
| `vcgencmd get_throttled` isn't `0x0` | Set the buck to 5.1–5.2V. Check both 5V and both GND jumpers. |
| Follow mode turns away from your hand | Tell me. It's one sign in `sim.py`. |
