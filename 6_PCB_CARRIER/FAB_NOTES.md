# VANTA carrier board, rev A

Open `vanta_carrier.kicad_pro` in KiCad 7, 8 or 9.

## What it is

The board replaces the two PCA9685 breakouts, the XL4015 buck and the Wago splits.

- **Mounting:** it screws onto the electronics plate's 8 PCA bosses with the same M2.5×6 screws.
- **Fit:** the outline, holes and header rows come from `body2.py`. The two servo header rows sit under the Pi deck's plug windows. J6 sits under the deck's jumper slot.
- **Clearance:** the tallest part is 11.4 mm, which leaves 1.75 mm under the deck. This was checked against the plate, posts, bosses, deck and SBEC with the STEP model. The plate and the Pi deck don't change.
- **Software:** the existing software runs unchanged: same buses, same 0x40 addresses, same channel map.

## Order

| Setting | Value |
|---|---|
| Layers | 4 |
| Thickness | 1.6 mm |
| Outer copper | 1 oz |
| Inner copper | 1 oz if the fab offers it, 0.5 oz works |
| Min track / space | 0.2 / 0.2 mm |
| Min via | 0.6 / 0.3 mm |

Upload these files:
- Gerbers: `fab/vanta_carrier_gerbers.zip`.
- Assembly: `fab/BOM_JLC.csv` + `fab/CPL_JLC.csv`. Choose both SMT and through-hole assembly, so nothing needs soldering.

Copper layers:

| Layer | Carries |
|---|---|
| F.Cu | signals and GND fill, plus a V_SERVO strip under each servo row |
| In1 | GND plane |
| In2 | V_SERVO (servo rows + right side) and VBAT (middle + buck) |
| B.Cu | VBAT fill |

## Check before paying

1. **Rotations:** the fab's placement preview often rotates TSSOP, SOT-23 and electrolytic caps wrong. Fix any part whose pin 1 or + doesn't line up with the silkscreen.
2. **Terminal direction:** J1, J2 and J3 are push-in terminals. Their wire openings should face away from the board: J2 and J3 toward the SBEC, J1 toward the rear. Check it in the 3D viewer.
3. **Polarity:** there is no reverse-polarity protection. The + and − marks are on the silkscreen.

## DRC

- 0 errors, 0 unrouted.
- The 15 courtyard warnings come from the servo headers sitting 2.54 mm apart on purpose, and from J6 sitting close to two mounting holes (it still clears the screw heads).
