# Credits

Leg, body, stiffener and battery-mount geometry: **ggldnl, Hexapod-Hardware**
https://github.com/ggldnl/Hexapod-Hardware. Licensed CERN-OHL-W-2.0 (https://ohwr.org/cern_ohl_w_v2.txt).

## Unchanged from ggldnl's repo

- `3_CAD/source/hexapod.urdf`

## Modified from ggldnl's parts

The changes are made in `3_CAD/source/build_v5.py`, `bracket_b_alu.py` and `body2.py`.

| Part | What changed | Files in this repo |
|---|---|---|
| base | honeycomb windows in the servo-pocket walls, 4 columns for the electronics plate, self-tap holes for the inner tabs and stiffener corners, logo pocket in the front | `1_PRINT/stl_main/01_base_x1.stl`, `1_PRINT/stl_color_AMS/3_optional_base_BLACK.stl`, `3_CAD/stl_in_place/base.stl` |
| top stiffeners | corner holes opened to clear the base columns | `1_PRINT/stl_main/02_top_stiffeners_x1.stl`, `3_CAD/stl_in_place/top_stiffeners.stl` |
| bottom stiffeners | head counterbores, so M3x10 reaches | `1_PRINT/stl_main/03_bottom_stiffeners_x1.stl`, `3_CAD/stl_in_place/bottom_stiffeners.stl` |
| battery mount | honeycomb floor | `1_PRINT/stl_main/04_battery_mount_x1.stl`, `3_CAD/stl_in_place/battery_mount.stl` |
| femur | honeycomb windows in the side rails, self-tap tab holes | `1_PRINT/stl_main/07_femur_x6.stl`, `3_CAD/stl_in_place/femur.stl` |
| tibia | counterbored clearance holes for the bracket A screws | `1_PRINT/stl_main/08_tibia_x6.stl`, `3_CAD/stl_in_place/tibia.stl` |
| bracket A → bracket A capped | pin side lengthened 4.5 mm, 623 bearing boss and axle, coxa (clearance) and femur/tibia (self-tap) variants | `1_PRINT/stl_main/09_bracket_A_coxa_x6.stl`, `09_bracket_A_link_x12.stl`, `3_CAD/stl_in_place/bracket_A_coxa.stl`, `bracket_A_link.stl` |
| bracket B → bracket B alu | reshaped for a 25T aluminium disc horn, used on every joint | `1_PRINT/stl_main/10_bracket_B_alu_x18.stl`, `3_CAD/stl_in_place/bracket_B_alu.stl` |

## Files that contain ggldnl-derived geometry together with VANTA parts

- `1_PRINT/*.3mf` (print plates)
- `3_CAD/VANTA_standing.glb`
- `4_SOFTWARE/hexapod-brain/sim/hexapod.glb`
- `4_SOFTWARE/sim_and_training/meshes/*.stl` (simplified robot meshes for the simulator)

## VANTA's own (not from ggldnl)

Servo caps, electronics plate, Pi deck, mech hull and tall hull variants, top deck, riser and camera holder (`3_CAD/deck_hull_fusion/`), leg armour, branding, the carrier PCB, all firmware and software, and the assembly guide.

## Software dependencies (not included in this repo)

- Bluepad32 (ricardoquesada) and its esp32-bluepad32 Arduino board package
- Adafruit PWM Servo Driver library and Adafruit BusIO
- MuJoCo and NumPy (simulator and training)
- OpenCV, Picamera2 and MediaPipe (legacy Pi software only)

If you share this build, keep this notice, `LICENSE-HARDWARE` and the source files with it, as the licence asks.
