"""VANTA assembly guide v7. python guide7.py out.pdf"""
import sys, json
import pypdf
from lib7 import *
from diag7 import *
from diag7 import fitdraw
from reportlab.pdfbase import pdfmetrics

PAGES = []
CUR = 0


def page(f):
    PAGES.append(f); return f


ALU = ("Horn onto the spline, its centre screw in. Hold bracket B over it pointing the way this step says. If B's 4 holes don't sit over the horn's 4 holes, "
       "lift the horn, turn it **one tooth**, press it back. Repeat until they line up (it can take a dozen tries; one position is always within 2°). "
       "Then the **4 screws from the horn's bag** through B into the horn.")


# ============ 00 cover ============
@page
def cover():
    b, c = new_page(dark=True)
    from glyph import code_column
    import numpy as np
    from PIL import Image as PI
    col = code_column(560, 1500, fs=17, seed=7, col=(118, 118, 122), bg=(9, 9, 10))
    a = np.asarray(col, float); fade = np.clip(1.25 - np.linspace(0, 1, a.shape[0]) * 1.6, 0, 1)[:, None, None]
    a = 9 + (a - 9) * fade
    c.drawImage(ImageReader(PI.fromarray(a.astype('uint8'))), 36, 612 - 44 - 448, 168, 448)
    image(c, G + 'hero_glyph.png', 170, 40, 610, 470, pad=0)
    txt(c, 36, 462, 'VANTA', 'Arch', 76, W)
    txt(c, 40, 552, '18-DOF HEXAPOD  ·  ASSEMBLY GUIDE  ·  REV 9', 'MonoSB', 9.5, ORA)
    txt(c, 40, 568, 'Made by Gio.  Every step from a bag of parts to a walking robot.', 'Sans', 9.5, Color(.75, .75, .77))
    txt(c, 756, 568, 'legs, base, stiffeners: ggldnl/Hexapod-Hardware · CERN-OHL-W-2.0', 'Mono', 6.8, Color(.45, .45, .47), 'r')
    return done(b, c)


# ============ 01 start here ============
@page
def start():
    b, c = new_page('start here', CUR)
    y = title_block(c, 50, 'READ THIS FIRST', 'Start here', 'Six rules. Break one and something gets hurt: a servo, a print, the battery, your evening, or you.', w=440)
    rules = [("Centre before the horn.", "Every servo goes to its centre (1500 µs) before its horn goes on (step 4). After that, never twist a servo shaft by hand. It's the only reason the legs come out straight."),
             ("Servo power never comes from a board.", "Servos get the SBEC's 6.0 V through the PCA's green screw terminal. The ESP32, the Uno and the Pi only power the PCA chip (its VCC pin). A servo on a 5 V pin resets the board or worse."),
             ("Battery out while you work.", "Unplug it whenever you wire, screw or unscrew anything. Plug in only when a step says so."),
             ("One servo at a time.", "The first time servos power up, they start one by one (the sketches and the Pi software do this for you). Three MG995s jumping together pull a spike that glitches everything."),
             ("Snug, not tight.", "Screws into inserts or self-tap holes strip PLA. Stop when the part stops moving.")]
    rules.append(("Wire as you go.", "Every build step has a WIRES NOW box. It tells you which lead to route before the next part covers it. Skip one and you take the robot apart later to reach it."))
    for i, (h, s) in enumerate(rules):
        txt(c, 36, y + 2, f'{i + 1}', 'Arch', 20, ORA)
        txt(c, 62, y + 2, h, 'SansB', 10.5, INK)
        y = para(c, 62, y + 17, s, 9.3, 380, col=INK) + 9
    x = 470; y = 52
    txt(c, x, y, 'HOW TO READ THE PICTURES', 'MonoSB', 7.6, ORA); y += 16
    for col, s in ((ORA, 'Orange: the part (or wire) you add in this step'), (Color(.36, .37, .40), 'Grey: body prints · black: servos · silver: horns, bearings'),
                   (Color(.26, .40, .60), 'Blue: bracket A  ·  teal: bracket B  ·  ochre: servo caps'), (Color(.46, .52, .28), 'Olive: femur  ·  brown: tibia  ·  light grey: armour'),
                   (Color(.30, .18, .55), 'Purple: PCA boards · green: Pi, camera · dark red: wires')):
        c.setFillColor(col); c.rect(x, H - y - 9, 10, 10, stroke=0, fill=1); txt(c, x + 18, y, s, 'Sans', 8.6, INK); y += 14
    y = para(c, x, y + 2, 'Your prints are all black. The colours are only in this guide so you can tell parts apart. Build steps have a **progress** picture bottom-left: orange is this step, grey is done, faint is still to come.', 8.4, 286, col=MUTE)
    y += 6
    txt(c, x, y, 'ON EVERY STEP PAGE', 'MonoSB', 7.6, ORA); y += 15
    for s in ['**YOU NEED**: grab these first', '**DO THIS**: in order, one at a time', '**CHECK ✓**: don\'t move on until it\'s true',
              '**CAREFUL**: the one way this step goes wrong', '**×6** / **×18** badge: do one, check it, then the rest']:
        y = para(c, x, y, s, 9.2, 286) + 2
    y += 8
    txt(c, x, y, 'TOOLS', 'MonoSB', 7.6, ORA); y += 15
    for s in ['Soldering iron, insert tip, 200 °C (inserts only: nothing in VANTA is soldered)', '2.5 mm hex key (M3), 2 mm (M2.5), small Phillips (horn centre screw)',
              'Multimeter · flush cutters · zip ties · hobby knife', 'CA glue or double-sided tape · grip tape · marker pen',
              'Laptop with Arduino IDE + Chrome or Edge · USB-C cable', 'For the Pi: microSD card, SSH (built into Windows/macOS)']:
        y = para(c, x, y, '– ' + s, 9, 286) + 2
    y = max(y + 14, 470)
    box(c, 36, y, 720, 'WHERE THE FILES ARE  ·  in the VANTA folder', [
        '`1_PRINT/` the two 3MF files for the A1 (MAIN and COLOR) and loose STLs.   `3_CAD/` the robot in 3D, source scripts.',
        '`4_SOFTWARE/hexapod-brain.zip` the Pi code.   `5_ELECTRONICS_TEST/` the ESP32-S3 and Uno sketches, `servo_console.html`.'], MUTE, 8.8)
    return done(b, c)


# ============ 02 roadmap ============
@page
def roadmap():
    b, c = new_page('start here', CUR)
    title_block(c, 50, 'THE WHOLE BUILD', 'The map', 'Five parts. Bench tests come before the build, so a bad servo shows up before it\'s buried in a leg.', w=440)
    o = image(c, R + 'hero_open.png', 30, 150, 440, 330)
    txt(c, 250, 492, 'Hull off. Leg names: F/M/R = front, middle, rear. L/R = left, right (seen from behind).', 'Sans', 8, MUTE, 'c')
    txt(c, 250, 504, 'Each leg has 3 joints, body outward: coxa (swings) · femur (lifts) · tibia (reaches).', 'Sans', 8, MUTE, 'c')
    x = 492; y = 52
    parts = [('A', 'PREP', [('1', 'Build one joint, check the fit'), ('2', 'Heat-set inserts')]),
             ('B', 'BENCH', [('3', 'Power: battery, SBEC, buck'), ('4', 'Wire the ESP32, centre and test all 18 servos')]),
             ('C', 'BUILD', [('5–7', 'Caps, coxa servos, body'), ('8–11', 'Coxa, femur, tibia joints, grip tape'), ('12', 'Check legs, armour, one-leg walk test')]),
             ('D', 'ELECTRONICS', [('13–14', 'Electronics plate, power in the robot'), ('15–16', 'Servo leads, Pi deck, camera')]),
             ('E', 'BRAIN', [('17', 'Pi setup (do 17A before 16), first power-up, calibrate, walk'), ('18', 'Mech hull and fans')])]
    for L, name, rows in parts:
        c.setFillColor(INK); c.rect(x, H - y - 16, 16, 16, stroke=0, fill=1); txt(c, x + 8, y + 3.5, L, 'MonoSB', 9, W, 'c')
        txt(c, x + 24, y + 3.5, name, 'MonoSB', 9, INK); y += 24
        for n, s in rows:
            txt(c, x + 24, y, n, 'MonoSB', 9, ORA); y = para(c, x + 66, y, s, 9.4, 196) + 3
        y += 8
    y = box(c, x, y + 2, 264, 'ORDER OF WORK', ['Print plate 1 first and build step 1 while the big plates print.', 'Do part B (bench) before part C: a dead servo is a 2-minute swap on the table and a 20-minute one in a leg.',
                                                 'Do **17A** (Pi setup, on the desk) any time **before step 16**: the Pi goes into the robot with its SD card ready.'], MUTE, 8.8)
    return done(b, c)


# ============ 03 printed parts ============
@page
def parts():
    b, c = new_page('parts', CUR)
    title_block(c, 50, 'WHAT YOU PRINT', 'Printed parts')
    para(c, 260, 62, '`VANTA_print_MAIN_A1.3mf`, black PLA, 15% infill (armour 5%). Plate numbers in the corner.', 9.3, 496, col=MUTE)
    para(c, 260, 76, 'Caps: **+2** is the size that fits (plate 10, plus one on plate 1).  Hull + letters: the COLOR file (step 18).', 9.3, 496, col=MUTE)
    P = [("01_base_x1", "Base", "×1", "2"), ("02_top_stiffeners_x1", "Top stiffeners", "1 set", "3"), ("03_bottom_stiffeners_x1", "Bottom stiffeners", "1 set", "3"),
         ("04_battery_mount_x1", "Battery mount", "×1", "4"), ("05_electronics_plate_x1", "Electronics plate", "×1", "4"), ("06_pi_deck_x1", "Pi deck", "×1", "5"),
         ("07_femur_x6", "Femur", "×6", "5"), ("08_tibia_x6", "Tibia", "×6", "6–7"), ("09_bracket_A_coxa_x6", "Bracket A · coxa", "×6", "6–7"),
         ("09_bracket_A_link_x12", "Bracket A · femur/tibia", "×12", "1, 8"), ("10_bracket_B_alu_x18", "Bracket B · alu horn", "×18", "1, 9"),
         ("11_servo_cap_plus2_x18", "Servo cap +2", "×18", "1, 10"), ("13_armor_femur_x12", "Armour · femur", "×12", "11"), ("14_armor_shin_x6", "Armour · shin", "×6", "12")]
    cw, ch = 96.5, 226
    for i, (k, name, q, pl) in enumerate(P):
        r, col = divmod(i, 7); x, top = 36 + col * (cw + 7.4), 100 + r * (ch + 12)
        c.setFillColor(BOX); c.rect(x, H - top - ch, cw, ch, stroke=0, fill=1)
        image(c, R + 't_' + k + '.png', x + 4, top + 24, cw - 8, 118)
        txt(c, x + 8, top + 8, q, 'MonoSB', 9, ORA); txt(c, x + cw - 7, top + 8, 'pl ' + pl, 'Mono', 7, MUTE, 'r')
        yy = top + 154
        for l in wrap(name, 'SansB', 9.2, cw - 14): txt(c, x + 8, yy, l, 'SansB', 9.2, INK); yy += 11.5
        for l in wrap(k + '.stl', 'Mono', 6.2, cw - 12): txt(c, x + 8, yy + 2, l, 'Mono', 6.2, MUTE); yy += 8.5
    return done(b, c)


# ============ 04 hardware ============
@page
def hardware():
    b, c = new_page('parts', CUR)
    title_block(c, 50, 'WHAT YOU BOLT IN', 'Hardware')
    y = table(c, 36, 96, [('qty', 34), ('part', 136), ('where it goes', 200)], [
        ('18', '623ZZ bearing (3×10×4)', 'one in every servo cap'),
        ('18', 'DaFuRui 25T alu horn, Ø20 disc', 'every joint. Use the **centre screw and 4 screws from each horn\'s bag**'),
        ('44', 'M3 heat-set insert (M3×L4×OD5)', 'step 2 map. You have 50: 6 spare'),
        ('28', 'M3×6', 'coxa outer tabs 12 · femur knee tabs 12 · plate → columns 4'),
        ('48', 'M3×8', 'femur servo tabs, self-tap 36 · coxa B → A 12'),
        ('110', 'M3×10', 'axles 18 · B → A femur/tibia 24 · femur A → coxa A 24 · tibia → A 24 · stiffeners 16 · hull 4'),
        ('12', 'M3 washer', 'under the coxa outer-tab screws'),
        ('12', 'M2.5×6', 'Pi 4 · PCA boards 8'),
        ('4', 'M2×8 + nut', 'camera'),
        ('6', 'grip tape strip, ~25×60 mm', 'wrapped round each tibia tip: the feet'),
        ('–', 'CA glue or double-sided tape', 'armour plates')], size=8.6)
    y = box(c, 36, y + 10, 370, 'COUNT FIRST', ['Lay every screw out by size before step 5 and check it against this table.',
                                               '**Self-tap holes** (Ø2.8, no insert): run the screw in once to cut the thread, back it out, then assemble.'], MUTE, 8.6)
    title_block(c, 50, 'WHAT YOU WIRE', 'Electronics', x=430, w=326)
    table(c, 430, 96, [('qty', 34), ('part', 292)], [
        ('18', 'MG995 servo, plus 1–2 spares (one already died on the bench)'),
        ('6', '30 cm servo extension leads (the tibias)'),
        ('2', 'PCA9685 16-channel servo board'),
        ('1', 'Raspberry Pi 4 + microSD (16 GB+)'),
        ('1', 'OV5647 camera + ribbon'),
        ('1', '20A SBEC: servo power, **set to 6.0 V**'),
        ('1', 'XL4015 buck: Pi and fans, **set to 5.1 V**'),
        ('1', 'Zeee 2S 5200 mAh LiPo, **XT60** plug'),
        ('1 each', '20A inline fuse · XT60 rocker switch · LiPo alarm'),
        ('~8', 'Wago 221 lever connectors, 16 AWG wire, 3 XT60 pigtails'),
        ('12', 'female-female jumpers (Pi → PCAs 8, buck → Pi 4)'),
        ('2', '30 mm 5 V fans (hull roof), with their screws'),
        ('1', 'Velcro strap (holds the battery in its mount)'),
        ('bench', 'ESP32-S3 DevKit (or Arduino Uno) + USB cable + 4 jumpers')], size=8.6)
    return done(b, c)


# ============ 05 how a joint goes together ============
@page
def joint_a():
    b, c = new_page('A · prep', CUR)
    title_block(c, 50, 'BEFORE STEP 1', 'How a joint goes together', 'Every joint is the same: 18 of these. Two supports, like a door on two hinges.', w=460)
    ox, oy, s, _ = image(c, J + 'r_exploded.png', 30, 112, 380, 470)
    lab = json.load(open(J + 'r_exploded.png.json'))
    names = {'dim|bracket_B_alu0': ('Bracket B', 'r'), 'horn|horn_alu1': ('Ø20 alu horn', 'r'), 'servo|REF_MG9952': ('Servo (MG995)', 'r'),
             'capc|servo_cap3': ('Servo cap (+2)', 'r'), 'brg|bearing_6234': ('623ZZ bearing', 'r'), 'old|bracket_A5': ('Bracket A (the L)', 'l'), 'axle|axle6': ('Axle: M3×10', 'l')}
    for k, (t, side) in names.items():
        if k not in lab: continue
        px, py = lab[k]; X = ox + px * s; Yv = oy + py * s
        if k == 'old|bracket_A5': X, Yv = ox + 70 * s, oy + 640 * s
        tx = 420 if side == 'r' else 40
        c.setStrokeColor(ORA); c.setLineWidth(.6); c.line(X, H - Yv, tx - 4 if side == 'r' else tx + tw(t, 'Sans', 8.5) + 4, H - Yv)
        c.setFillColor(ORA); c.circle(X, H - Yv, 1.8, stroke=0, fill=1)
        c.setFillColor(W); c.rect(tx - 2, H - Yv - 4.5, tw(t, 'Sans', 8.5) + 4, 10, stroke=0, fill=1)
        txt(c, tx, Yv - 4.8, t, 'Sans', 8.5, INK)
    x, w = RX, RW
    t = box(c, x, 52, w, 'HORN SIDE  ·  this end drives', [
        'The horn pushes onto the servo spline. Its centre screw holds it.',
        'Its Ø20 disc drops into a pocket under bracket B. The 4 screws from the horn\'s bag go through B into the horn\'s threaded holes.',
        'Bracket A\'s long arm screws to B.'], ORA, 8.8)
    t = box(c, x, t + 8, w, 'CAP SIDE  ·  this end only pivots', [
        'Nothing screws into the cap. It slides over the servo bottom and is trapped between the servo and bracket A.',
        'The bearing presses into the cap, flush.',
        'The axle screw threads up into bracket A\'s foot. Its tip sits in the bearing. When the leg moves, the screw turns in the bearing.'], ORA, 8.8)
    joint_section(c, x - 6, t + 22)
    return done(b, c)


# ============ 06 step 1 ============
@page
def joint_b():
    b, c = new_page('A · prep', CUR)
    title_block(c, 50, 'STEP 1  ·  plate 1', 'Build one joint first', 'Plate 1 has one bracket A, one bracket B and one +2 cap. Build this joint first: it proves the fit before the rest. Orange = what you add in that picture.', w=560)
    steps = [('r_s1.png', 'Bearing into the cap', 'Press the 623ZZ into the round pocket on the outside of the **+2 cap**, flush. Push on a flat surface, never hammer.'),
             ('r_s2.png', 'Cap onto the servo', 'Over the bottom of the servo (the end away from the shaft). The wire goes through the notch.'),
             ('r_s3.png', 'Horn, then bracket B', 'Horn on, centre screw in. B over the disc, then the horn\'s 4 screws. For this test any tooth is fine.'),
             ('r_s4.png', 'Bracket A round the servo', 'Swing the L round so its foot lands under the cap. **2× M3×10** through B into A\'s end (they self-tap).'),
             ('r_s5.png', 'Axle screw', '**M3×10** up through A\'s foot. It cuts its own thread. Stop when the head sits in its recess.'),
             ('r_done.png', 'Check it', 'Turn bracket B by hand through the servo\'s range (servo unpowered, gently). Then read the box below.')]
    cw, ch = 232, 140
    for i, (img, ti, body) in enumerate(steps):
        col, row = i % 3, i // 3; x = 36 + col * (cw + 12); top = 108 + row * (ch + 66)
        image(c, J + img, x, top, cw, ch)
        c.setFillColor(INK); c.circle(x + 7, H - top - ch - 11, 7, stroke=0, fill=1); txt(c, x + 7, top + ch + 7.2, str(i + 1), 'SansB', 8.2, W, 'c')
        txt(c, x + 20, top + ch + 5.5, ti, 'SansB', 9.8, INK)
        para(c, x + 20, top + ch + 20, body, 8.6, cw - 20)
    top = 524
    c.setFillColor(BOX); c.rect(36, H - top - 50, 720, 50, stroke=0, fill=1); c.setFillColor(INK); c.rect(36, H - top - 50, 2.5, 50, stroke=0, fill=1)
    txt(c, 47, top + 8, 'CHECK ✓   +2 IS THE SIZE THAT FITS', 'MonoSB', 7.6, INK)
    para(c, 47, top + 22, '**Good:** A closes flat on B, no wobble at the cap, B turns smoothly.   **Clunks or wobbles** at the cap: the +3 cap (`stl_main/other_cap_sizes/`).   '
         '**Binds, or A won\'t close:** the +1 cap (same folder), and check the bearing is flush.   Only reprint caps if this joint says so.', 8.8, 700)
    return done(b, c)


# ============ 07 step 2 inserts ============
@page
def inserts():
    b, c = new_page('A · prep', CUR)
    title_block(c, 50, 'STEP 2', 'Heat-set inserts: 44 of your 50', 'Orange discs: an insert goes here, from that face. Every other M3 hole is a Ø2.8 self-tap hole: no insert, the screw cuts its own thread.', w=700)
    P = [('i_base_under', 'Base, underside  ·  12', 'Outer tab holes of the six coxa pockets. Turn the base over.'),
         ('i_base_top', 'Base, columns  ·  4', 'Top of the 4 plate columns.'),
         ('i_femur', 'Femur  ·  2 each = 12', 'The two knee-end tab holes, from the tab face.'),
         ('i_acoxa', 'Bracket A coxa  ·  2 each = 12', 'In the end face. Its 4-hole face is clearance + counterbore: nothing there.'),
         ('i_plate', 'Electronics plate  ·  4', 'Top of the 4 deck posts.')]
    cw = 136
    for i, (img, t, s) in enumerate(P):
        x = 36 + i * (cw + 10); top = 128
        c.setFillColor(BOX); c.rect(x, H - top - 190, cw, 190, stroke=0, fill=1)
        image(c, R + img + '.png', x + 4, top + 4, cw - 8, 182)
        txt(c, x, top + 200, t, 'SansB', 9, INK); para(c, x, top + 214, s, 8.4, cw)
    y = 400
    txt(c, 36, y, 'HOW TO SET ONE', 'MonoSB', 7.6, ORA)
    numbered(c, 36, y + 15, 340, ['Iron at **200 °C** for PLA. Insert on the hole, knurled end down, straight.',
                                  'Touch the iron tip into the insert. Let it sink **under its own weight**. Don\'t push.',
                                  'Stop when it\'s flush. Lift the iron straight up; press the top flat with something cool if it rose.',
                                  'Let it cool 10 s before the next one close by.'], 9.3)
    box(c, 400, y, 356, 'CAREFUL', ['A crooked insert makes a joint bind later. If one goes in at an angle, heat it and pull it out with the iron, let the plastic cool, try again.',
                                     'Wait for the iron to come back to 200 °C between inserts.'], ORA, 8.8, bg=Color(.99, .95, .91))
    box(c, 400, y + 92, 356, 'CHECK ✓', ['44 inserts in, all flush, none turn when a screw goes in.'], INK, 8.8)
    return done(b, c)


# ============ 08 step 3 power on the bench ============
@page
def bench_power():
    return step_page('B · bench', CUR, 3, 'Power on the bench', 'Build the power side on the table first. You\'ll use it to test every servo before it goes in a leg.',
                     ['Battery, fuse, switch, SBEC, buck, LiPo alarm', 'XT60 pigtails, 16 AWG wire, Wagos', 'Multimeter'],
                     ['Wire it like the picture. Strip 11 mm for a Wago, push the wire in, close the lever, tug it.',
                      'Leave the SBEC and buck **outputs disconnected** for now.',
                      'Battery unplugged, switch ON. Multimeter on beep, across + and − of the battery plug. A steady beep is a short: find it first.',
                      'Plug in the battery and the alarm. Switch on.',
                      'SBEC output → **6.0 V** (jumper or button on the SBEC). Buck output → **5.1 V** (turn the CV screw; it\'s multi-turn, so turn a lot).',
                      'Switch off. Connect the SBEC to PCA #1\'s green terminal: red to V+, black to GND. The buck waits for the Pi (step 16).'],
                     check=['SBEC reads 5.9–6.1 V, buck 5.1–5.2 V, with the meter on their outputs.'],
                     careful=['Never more than **5.25 V** on the Pi pins. Measure before the Pi is connected.', 'Red to V+, black to GND on the terminal. Backwards kills the PCA.'],
                     draw=lambda c: fitdraw(c, lambda c: power(c, 0, 0), 36, 56, 0.85))


# ============ 09 step 4A controller wiring ============
@page
def bench_ctrl():
    def d(c):
        tt = controller(c)
        plug(c, 60, tt + 26)
    return step_page('B · bench', CUR, '4', 'Wire the bench controller', 'An ESP32-S3 (or Uno) talks to one PCA board. It\'s how you test servos before the Pi exists.',
                     ['ESP32-S3 DevKit + USB-C cable (or an Uno)', 'PCA #1 with the SBEC on its terminal (step 3)', '4 female-female jumpers', 'All 18 servos'],
                     ['Battery unplugged. 4 jumpers exactly like the table: **3V3→VCC, GND→GND, GPIO 8→SDA, GPIO 9→SCL**.',
                      'Nothing on the PCA\'s **V+** header pin or **OE**. Servo power only ever comes through the green terminal.',
                      'Plug **one** servo into **channel 15** (the last header). Brown wire to the board edge (picture, bottom).',
                      'USB from the ESP32 to the laptop. Battery still out.'],
                     check=['Jumpers on the 3V3 pin, not 5V. The servo plug sits brown-to-edge.'],
                     careful=['Never connect the ESP32\'s 5V pin to the PCA\'s V+. The servos would pull power through your laptop\'s USB port.'],
                     draw=d, kicker='STEP 4 · A')


# ============ 10 step 4B arduino ide ============
@page
def ide():
    b, c = new_page('B · bench', CUR)
    y = title_block(c, 50, 'STEP 4 · B', 'Arduino IDE: first upload', 'Once per laptop. The files are in `5_ELECTRONICS_TEST/`.', w=440)
    y = numbered(c, 36, y + 8, 440, [
        'Install **Arduino IDE 2** from arduino.cc.',
        '**ESP32 board support:** File → Preferences → Additional boards URLs: `https://espressif.github.io/arduino-esp32/package_esp32_index.json`. Then Tools → Board → Boards Manager → search **esp32** → install (by Espressif).',
        '**Library:** Tools → Manage Libraries → search **Adafruit PWM Servo Driver** → install (say yes to its dependencies).',
        'Open `esp32s3/servo_console_s3/servo_console_s3.ino`. Uno users: `arduino_uno/servo_console/servo_console.ino`.',
        'Tools → Board → **ESP32S3 Dev Module**. Tools → **USB CDC On Boot: Enabled**. Tools → Port → the ESP32\'s port.',
        'Click **Upload** (the → arrow). Wait for "Done uploading".',
        'Tools → Serial Monitor, **115200 baud**. Press the board\'s **RST** button. You should see the console\'s ready line. Close the Serial Monitor before using the web page (step 4C).'], 9.4)
    x = RX - 20; w = RW + 20
    t = box(c, x, 52, w, 'THE FOLDER RULE', ['Every sketch lives in **its own folder with the same name**: `vanta_one_leg_s3/vanta_one_leg_s3.ino`.',
                                             'Two .ino files in one folder get glued together: you\'ll see **"redefinition of …"** errors. Move one out.'], ORA, 8.8, bg=Color(.99, .95, .91))
    t = box(c, x, t + 10, w, 'WHICH SKETCH WHEN', ['`servo_console_s3`: any servo, any channel, from a web page. Step 4C.',
                                                   '`vanta_one_leg_s3`: one built leg on ch 15/14/13. Find its home, then walk it. Step 12 · B.',
                                                   'Uno versions: same names in `arduino_uno/`.'], MUTE, 8.8)
    t = box(c, x, t + 10, w, 'IF THE SERIAL MONITOR IS BLANK', ['Shows only `ESP-ROM:` lines: press **RST** once.',
                                                                'Still nothing: USB CDC On Boot must be **Enabled**; re-upload.',
                                                                'Gibberish: baud isn\'t 115200.',
                                                                'S3 boards with two USB ports: use the one marked USB (not UART), or pick the other port in Tools → Port.'], MUTE, 8.8)
    return done(b, c)


# ============ 11 step 4C centre & test ============
@page
def centre():
    def d(c):
        x, t = 36, 60
        c.setFillColor(Color(.07, .07, .08)); c.rect(x, H - t - 300, 458, 300, stroke=0, fill=1)
        txt(c, x + 14, t + 12, 'VANTA // SERVOS', 'MonoSB', 9, W)
        for i, s in enumerate(['Connect COM port', 'ALL OFF', 'All live → 1500']):
            bx = x + 140 + i * 98; c.setFillColor(Color(.85, .25, .2) if i == 1 else Color(.14, .14, .16)); c.rect(bx, H - t - 22, 90, 16, stroke=0, fill=1)
            txt(c, bx + 45, t + 10.5, s, 'Mono', 7, W, 'c')
        for r in range(9):
            yy = t + 40 + r * 28; live = r == 0
            txt(c, x + 14, yy, f'CH {15 - r:02d}', 'Mono', 7.5, ORA if live else Color(.5, .5, .52))
            c.setStrokeColor(Color(.25, .25, .28)); c.setLineWidth(.5); c.line(x + 14, H - yy - 14, x + 444, H - yy - 14)
            c.setStrokeColor(ORA if live else Color(.32, .32, .35)); c.setLineWidth(3); c.line(x + 120, H - yy - 4, x + 300, H - yy - 4)
            c.setFillColor(ORA if live else Color(.5, .5, .52)); c.circle(x + 210, H - yy - 4, 5, stroke=0, fill=1)
            txt(c, x + 340, yy, '1500' if live else 'off', 'Mono', 7.5, W if live else Color(.5, .5, .52), 'r')
            txt(c, x + 352, yy, '−50 −10 1500 +10 +50 off', 'Mono', 6.5, Color(.55, .55, .58))
        para(c, x, t + 310, '`servo_console.html`, open in Chrome or Edge. Each row is one PCA channel, 15 at the top. Every channel starts OFF.', 8.5, 458, col=MUTE)
        y = t + 336
        txt(c, x, y, 'DEAD-SERVO CHECK  ·  do it for all 18 before any horn goes on', 'MonoSB', 7.6, ORA)
        table(c, x, y + 16, [('you send', 110), ('a good servo', 170), ('a dead servo', 178)], [
            ('**1500**', 'moves once to centre, holds, quiet', 'slams to an end stop and buzzes'),
            ('**+10 / −10**', 'tiny smooth step each click', 'jumps, twitches or snaps'),
            ('**1000 → 2000**', 'smooth sweep, about 45° each side', 'stalls, grinds, or runs past the end'),
            ('**off**', 'goes limp', '–')], size=8.6)
    return step_page('B · bench', CUR, '4', 'Centre and test all 18 servos', 'Each servo gets tested, then parked at the centre, where it stays until its horn goes on.',
                     ['The bench setup from 4A, console sketch uploaded', '`servo_console.html` in Chrome or Edge', 'All 18 servos'],
                     ['Battery in, switch on. Open `servo_console.html`, click **Connect COM port**, pick the ESP32.',
                      'One servo on **ch 15** (the top row). Press its **1500** button. Then do the dead-servo check (table, left).',
                      'Press **1500** once more. Wait a second. Press **off**.',
                      'Unplug it **without touching the shaft**. Next servo.',
                      'A shaft gets turned by accident later? Plug it back in and press 1500 again before its horn goes on.'],
                     check=['18 servos tested and left at centre. Any dead ones set aside.', 'From here on, nobody twists a shaft by hand.'],
                     tip=['Using the Pi instead? `python tools/center_servos.py` holds every servo on both boards at 1500. Same idea.'],
                     draw=d, kicker='STEP 4 · C')


# ============ 12–19 build steps ============
@page
def s5():
    return step_page('C · build', CUR, 5, 'Caps on all 18 servos', 'Same as step 1, on every servo. The bearing pocket is on the outside of the cap. The picture shows where the 18 end up.',
                     ['18 centred servos','18 **+2** caps (plate 10 + the one from plate 1)', '18 623ZZ bearings'],
                     ['Press a bearing into each cap\'s round pocket, flush with the face. Flat surface, steady thumb pressure.',
                      'Push the servo lead into the servo\'s rubber strain relief so it exits straight down. The cap notch is its only way out.',
                      'Slide the cap over the bottom of the servo, lead through the notch. Keep the shaft still.',
                      'Sort them: 6 go in the base (coxa), 12 go in the femur frames.'],
                     check=['Each bearing spins freely with a fingertip.', 'No cap turns on its servo. A loose one gets a wrap of tape on the servo.'],
                     img='s05', badge='×18', progress='s05_p', plabel='where they go')


@page
def s6():
    return step_page('C · build', CUR, 6, 'Coxa servos into the base', 'Fitted with the base upside down. Turned back over it looks like the picture: caps on top, shafts underneath.',
                     ['Base (16 inserts in)', '6 capped servos', '12× M3×6 + 12 washers'],
                     ['Base upside down, underside facing you. Drop each servo into its pocket **cap first**, until the tabs sit flat on the base.',
                      'Lead toward the middle of the base, not toward the leg.',
                      '**Outer tabs** (toward the leg): M3×6 + washer into the inserts. The inner tabs wait for step 7.',
                      'Turn the base right way up. Six caps on top, six shafts underneath.'],
                     check=['All six shafts face down, centred in their pockets. No servo rocks on its outer tab.'],
                     img='8:s06b', badge='×6', progress='s06_p',
                     wires=['The 6 coxa leads lie on top of the base, pointing at the centre. Coil the plugs loosely there.',
                            'They stay on top from now on: the electronics plate (step 13) goes over them and they come up through its windows.'])


@page
def s7():
    return step_page('C · build', CUR, 7, 'Bottom stiffeners, battery mount, switch', 'Underside. The stiffeners clamp the inner servo tabs and carry the battery. Structural: don\'t skip them.',
                     ['Bottom stiffeners, battery mount', '16× M3×10', 'Battery, Velcro strap', 'Fuse, switch, 2 zip ties'],
                     ['Base upside down again. Battery mount under the middle: its 4 corner ears go between the base and the stiffeners.',
                      'Stiffeners over the inner servo tabs and the ears.',
                      '**12× M3×10** through the counterbores, stiffener and tab into the base. They self-tap: snug only.',
                      '**4× M3×10** through the stiffener corners and the battery ears.',
                      'Battery in, Velcro strap through the slots. Leave it **unplugged**.'],
                     check=['Press on each coxa servo: nothing wobbles. The battery mount doesn\'t rattle.'], img='8:s07', progress='s07_p',
                     wires=['Zip-tie the **fuse and switch** to the side of the battery mount now, switch facing out where a finger reaches it. This is the last time the underside is this open.',
                            'Feed the switch\'s **output lead** (the one that will go to the Wagos) up through the gap beside the battery mount to the top of the base. Leave the battery\'s own XT60 underneath.',
                            'Balance lead: tuck it where the LiPo alarm can clip on from below.'])


@page
def s8():
    return step_page('C · build', CUR, 8, 'Coxa joints', 'The first joint of each leg. The servo is fixed in the base; the bracket swings. One leg shown; the progress picture has all six.',
                     ['Per leg: bracket A **coxa**, bracket B, 1 horn + its screws', '2× M3×8, 1× M3×10 (axle)'],
                     [ALU.replace('Hold bracket B over it', 'The shaft is underneath here: hold bracket B against it from below') + ' **Target: B points straight out from the body.**',
                      'Bracket A round the outside of the servo: its foot sits **over the cap on top**, its other end meets B underneath.',
                      'A to B: **2× M3×8** through B into A\'s inserts. Axle: **M3×10** down through A\'s foot into the bearing.',
                      'Swing the bracket gently to both ends of its travel (about 35° each way).'],
                     check=['All six coxa brackets point straight out. Smooth swing, no click, nothing pinched.'],
                     careful=['Don\'t turn the servo shaft to line the holes up. Turn the horn on the spline instead.'],
                     img='8:s08', badge='×6', progress='s08_p',
                     wires=['The coxa lead must not sit under bracket A\'s foot. Route it inward first, then check at both ends of the swing that A doesn\'t touch it.'])


@page
def s9():
    return step_page('C · build', CUR, 9, 'Femur frames', 'Built off the robot. Each femur carries two servos: femur servo (body end) and tibia servo (knee end).',
                     ['Per leg: 1 femur (2 inserts in), 2 capped servos', '6× M3×8, 2× M3×6', '1× 30 cm extension, 2 zip ties'],
                     ['Drop both servos in, cap first, from the insert face. The tabs rest on the frame.',
                      'Both output shafts on the **same side**.',
                      'The two knee-end holes have inserts: **M3×6**. The other six self-tap: **M3×8**.',
                      'Make all six frames identical. Lay them side by side: same side shafts, same side caps.'],
                     check=['Both shafts on one side, both caps poking out the other. All six frames match.'],
                     img='8:s09', badge='×6', progress='s09_p_p', plabel='all six, in place',
                     wires=['Plug the **30 cm extension** onto the tibia servo lead now and tape the joint.',
                            'Run both leads along the frame to the body end and zip-tie them to the rail (2 ties). The armour (step 12) covers the rails, so the leads go in first.'])


@page
def s10():
    return step_page('C · build', CUR, 10, 'Femur joints', 'The femur frame hangs off the coxa bracket. This time the servo body swings, not the bracket.',
                     ['Per leg: bracket A femur/tibia, bracket B, 1 horn + screws, a femur frame', '7× M3×10'],
                     ['Hold the femur frame **level**, sticking straight out. ' + ALU,
                      'Bracket A round the servo: foot under the cap, **2× M3×10** through B into A, **M3×10** axle.',
                      'Bolt this A back-to-back onto the coxa A: **4× M3×10** from inside the coxa bracket. The heads sink into its counterbores.',
                      'Lift the femur to the top of its range and back down. Nothing should pull.'],
                     check=['With the servos still centred, every femur sticks straight out and level.'], img='8:s10', badge='×6', progress='s10_p',
                     wires=['The leg\'s two leads now cross the coxa joint. Leave a **finger-sized loop** over the joint (coxa swings ±35°, femur −80 … +85°).',
                            'Then run them over the coxa bracket into the body, toward the centre of the base, next to the coxa lead.'])


@page
def s11():
    return step_page('C · build', CUR, 11, 'Tibia joints and grip feet', 'Last joint, then grip tape on the tip. The grip tape is the foot.',
                     ['Per leg: bracket A femur/tibia, bracket B, 1 horn + screws, 1 tibia', '7× M3×10, a strip of grip tape'],
                     ['Bracket A round the knee servo the same way as step 10, axle included. ' + ALU.split('. Then')[0] + '. **Target: tibia straight down while the femur is level.** Then the horn\'s 4 screws.',
                      'Tibia onto A\'s 4-hole face: **4× M3×10** through the tibia\'s counterbores (they self-tap into A).',
                      'Wrap grip tape round the bottom **25 mm** of the tip, overlap on the inner face, press hard, trim.'],
                     check=['Femur level, tibia straight down, tape tight with no loose edge.'], img='8:s11', badge='×6', progress='s11_p',
                     wires=['No lead crosses this joint (the tibia has no servo). Fold the tibia all the way in and check the tibia lead at the knee isn\'t pulled tight.'])


@page
def s12():
    return step_page('C · build', CUR, 12, 'Check the legs, fit the armour', 'Everything at centre first, then the armour. It\'s cosmetic: glue or tape, no screws.',
                     ['The robot from step 11', '12 femur plates, 6 shin plates', 'CA glue or double-sided tape'],
                     ['Look at it from the front and the side: **coxa straight out, femur level, tibia straight down**, on every leg.',
                      'One off by more than a few degrees: its 4 horn screws out, horn one tooth, screws back.',
                      'Femur plates: one each side rail, rib outward, cut corner toward the knee. Glue only where the plate touches.',
                      'Shin plates: outer face of each tibia, flush with the bend at the top.',
                      'Move each leg by hand through its walking range (not to the end stops): nothing rubs.'],
                     check=['All six legs match. Errors under 2° get trimmed in software later.'], img='8:s12', badge='×6', progress='s12_p',
                     wires=['The femur leads are under the plates from now on. Before any glue: tug each lead, swing each leg, and only then stick the plates down.'])


@page
def oneleg():
    def d(c):
        image(c, R + 'oneleg.png', 36, 52, 170, 230)
        fitdraw(c, leg_pose, 214, 62, 0.93)
        x, t = 36, 300
        txt(c, x, t, 'SERIAL MONITOR KEYS  ·  115200, "No line ending"', 'MonoSB', 7.6, ORA)
        table(c, x, t + 16, [('key', 60), ('does', 398)], [
            ('`1` `2` `3`', 'pick coxa / femur / tibia. That joint powers on at its HOME_US'),
            ('`+` `-`', 'jog the picked joint 10 µs'), ('`]` `[`', 'jog 50 µs'),
            ('`p`', 'print `int HOME_US[3] = {…};` to paste into the sketch'),
            ('`t`', 'test: each joint moves +15° and back, one at a time'),
            ('`h`', 'home: joints power on one by one, 400 ms apart'),
            ('`w`', 'walk in the air (ramps in over 1 s; `h` eases it back out)'),('`x`', 'everything off')], size=8.4)
        para(c, x, t + 196, 'Faster: lower `CYCLE_MS` (1200; not under ~500). Longer steps: raise `STRIDE` (40; up to ~100 on the full robot). Higher steps: `LIFT` (25).', 8.4, 458, col=MUTE)
    return step_page('C · build', CUR, 12, 'One-leg walk test', 'Optional, but it\'s the proof the leg works before the electronics go in. One leg on the bench controller.',
                     ['The bench controller from step 4', '`vanta_one_leg_s3` (or the Uno one)', 'One finished leg (on the robot is fine)'],
                     ['Plug its servos into **ch 15 coxa, ch 14 femur, ch 13 tibia**. Upload the sketch. Nothing moves at boot.',
                      'Type `1`. Jog until the leg points **straight out**. `2`: femur **level**. `3`: tibia **straight down**.',
                      'Type `p`. Paste the line it prints over the `int HOME_US[3]` line near the top of the sketch. Upload again.',
                      'Type `t`. Each joint should move the way the picture shows. One goes backwards: flip its number in `SIGN[3]`.',
                      'Type `h`, then `w`. The foot draws a loop in the air. `x` to stop.'],
                     check=['A smooth loop, no snap, no buzzing at rest. Then try another leg the same way.'],
                     careful=['Never `w` before step 3 here. With HOME_US still at 1500 the leg can fold into the body.'],
                     draw=d, kicker='STEP 12 · B')


@page
def s13():
    return step_page('D · electronics', CUR, 13, 'Electronics plate', 'Top stiffeners, the plate, then the boards on it. Read the wires box before you pick up a screw.',
                     ['Top stiffeners, electronics plate (4 inserts in the posts)', '2 PCA boards, SBEC, buck', '4× M3×6, 8× M2.5×6, 4 zip ties'],
                     ['Top stiffeners on: the 4 base columns go through their corner notches; the stiffeners rest on the coxa servos.',
                      'Gather all the leads (wires box), then lower the plate onto the columns: **4× M3×6** into the column inserts. It clamps the stiffeners.',
                      'PCA boards on the bosses, servo headers facing out. **Front board (camera end) = PCA #1, rear = PCA #2.** Label them with tape.',
                      'Zip-tie the buck to the rear slots, the SBEC to the front slots.'],
                     check=['Nothing touches the coxa caps when you turn a leg by its bracket. All 19 leads are above the plate.'], img='8:s13', progress='s13_p',
                     wires=['Before the plate goes down: feed **all 18 servo leads and the switch output lead** up through the plate\'s two long windows.',
                            'Once the plate is screwed on, the top of the base is sealed. A lead left underneath means taking the plate off again.'])


@page
def s14():
    return step_page('D · electronics', CUR, 14, 'Power, in the robot', 'The bench wiring moves in. Same connections, now on both boards. Finish and test it now: the Pi deck covers most of this.',
                     ['Everything from step 3', 'Zip ties'],
                     ['Switch output lead (from step 7) into the Wagos on the plate, beside the SBEC.',
                      'SBEC to **both** PCA green terminals (red V+, black GND).',
                      'Buck output waits for the Pi (step 16). Fan leads too (step 18).',
                      'Test: battery in, switch on, **6.0 V** at both PCA terminals, **5.1 V** at the buck output. Switch off, battery out.'],
                     careful=['Battery stays unplugged after the test, except for the quick buck check in step 16.'], check=['Every Wago lever closed, every wire tugged. No bare copper showing.'],
                     draw=lambda c: fitdraw(c, lambda c: power(c, 0, 0, robot=True), 36, 56, 0.85))


@page
def s15():
    return step_page('D · electronics', CUR, 15, 'Servo leads to the boards', 'All 18 leads, routed and plugged. Right legs on PCA #1, left legs on PCA #2. The channel map is on the next page.',
                     ['18 servo leads (tibias on their extensions)', 'Zip ties'],
                     ['Lay the 6 coxa leads flat on the plate, toward their board.',
                      'Each leg\'s femur and tibia leads come in over the coxa bracket and join the coxa lead.',
                      'Plug each leg\'s three leads into three channels in a row: coxa, femur, tibia. **Brown wire to the board edge**, every time.',
                      'Zip-tie each leg\'s bundle to the plate edge, leaving the slack loop at the joint.',
                      'Swing every leg through its full range: nothing pulls, nothing rubs a cap.'],
                     check=['18 leads in, no two on one channel. Next page: check each one against the map.'],
                     img='8:s15', progress='s15_p',
                     wires=['The leads came up **through** the two long windows (step 13); don\'t leave any lying **in** them. Pull each bundle clear: the Pi deck\'s jumpers come down through the left one at step 16.'])


@page
def s15b():
    return step_page('D · electronics', CUR, 15, 'Channel map', 'Seen from the top, camera at the front. Each leg has three channels in a row.',
                     None,
                     ['Right legs (FR, MR, RR) on **PCA #1**, the front board. Left legs (FL, ML, RL) on **PCA #2**.',
                      'Front legs: ch 0, 1, 2. Middle: 3, 4, 5. Rear: 6, 7, 8. Always coxa, femur, tibia in that order.',
                      'Write the leg name on a bit of tape on each bundle. You\'ll thank yourself at step 17.'],
                     check=['Walk round the robot once more with this page: every bundle on the right board, right channels.'],
                     draw=lambda c: fitdraw(c, leads, 36 + 12, -70, 0.82), kicker='STEP 15 · B')


@page
def s16():
    def d(c):
        image(c, imgpath('8:s16'), 36, 52, 458, 250)
        pi_wiring(c, 40, 318)
    return step_page('D · electronics', CUR, 16, 'Pi deck and camera', 'Do step 17A first: the Pi goes in with its SD card set up. The deck sits on the four posts; no screws yet, the hull bolts through it in step 18.',
                     ['Pi deck, Pi 4 (SD card from step 17A in), camera + ribbon', '4× M2.5×6, 4× M2×8 + nuts', '8 jumpers (Pi → PCAs) + 4 (buck → Pi), 2 Wago 221s'],
                     ['Pi on its bosses, USB ports to the back. Camera on the front wall, lens through the hole.',
                      'Ribbon into the Pi\'s camera port, **blue tab toward the USB ports**.',
                      'Jumpers onto the Pi pins first, exactly as the drawing. Then the other ends onto the PCAs, down through the left window.',
                      'Battery in, switch on: **5.1 V** at the buck output. Switch off, battery out.',
                      'Buck **+** and **−** each to its own Wago. Cut the plug off the buck end of the 4 buck → Pi jumpers, strip 11 mm: two into the + Wago (to **pins 2, 4**), two into the − Wago (**pins 6, 9**). Leave a free slot in each for the fans (step 18).',
                      'Deck onto the posts. Lay the servo wires flat before the Pi goes over them.'],
                     check=['Ribbon not pinched, jumpers not tight, nothing hanging into the legs.'], draw=d,
                     tip=['Use jumpers long enough that the deck can **lift 5 cm** off the posts with everything plugged in. That\'s how you get at the PCAs later without unplugging anything.'])


# ============ 25–28 brain ============
CODEBOX = Color(.09, .09, .10)


def code(c, x, top, w, lines, size=7.8):
    h = 14 + len(lines) * size * 1.45
    c.setFillColor(CODEBOX); c.rect(x, H - top - h, w, h, stroke=0, fill=1)
    for i, l in enumerate(lines):
        col = Color(.5, .5, .52) if l.startswith('#') else W
        txt(c, x + 10, top + 8 + i * size * 1.45, l, 'Mono', size, col)
    return top + h


@page
def pi_setup():
    b, c = new_page('E · brain', CUR)
    y = title_block(c, 50, 'STEP 17 · A', 'Set up the Pi', 'Once, before step 16. From your laptop; the Pi sits on the desk for this. Details: `4_SOFTWARE/hexapod-brain/PI_SETUP.md`.', w=700)
    L = 36; Rr = 404; w = 352
    t = y + 6
    txt(c, L, t, '1  FLASH THE SD CARD', 'MonoSB', 7.6, ORA)
    t = para(c, L, t + 14, 'Raspberry Pi Imager → **Raspberry Pi OS (64-bit)**. In its settings: hostname `vanta`, user `gio`, your Wi-Fi, **SSH on**. Boot the Pi, then from the laptop:', 9, w)
    t = code(c, L, t + 2, w, ['ssh gio@vanta.local']) + 12
    txt(c, L, t, '2  I2C, THE SECOND BUS, THE CAMERA', 'MonoSB', 7.6, ORA)
    t = code(c, L, t + 14, w, ['sudo raspi-config nonint do_i2c 0', 'sudo nano /boot/firmware/config.txt', '# add at the bottom:',
                              'dtparam=i2c_arm=on', 'dtparam=i2c_arm_baudrate=400000', 'dtoverlay=i2c-gpio,bus=3,i2c_gpio_sda=4,',
                              '    i2c_gpio_scl=5,i2c_gpio_delay_us=2', '# (that dtoverlay is ONE line)', 'sudo reboot'])
    t = para(c, L, t + 6, 'Bus 1 (pins 3, 5) = PCA #1, right legs. Bus 3 (pins 7, 29) = PCA #2, left legs. Both boards are 0x40, which is why they need two buses.', 8.6, w, col=MUTE)
    t = y + 6
    txt(c, Rr, t, '3  INSTALL', 'MonoSB', 7.6, ORA)
    t = code(c, Rr, t + 14, w, ['sudo apt update', 'sudo apt install -y python3-picamera2 \\', '    python3-opencv i2c-tools',
                               'python3 -m venv --system-site-packages ~/vanta-venv', 'source ~/vanta-venv/bin/activate',
                               '# on the laptop, from 4_SOFTWARE (unzip hexapod-brain.zip):', 'scp -r hexapod-brain gio@vanta.local:~',
                               '# back on the Pi:', 'cd ~/hexapod-brain', 'pip install -r requirements-pi.txt'])
    t = para(c, Rr, t + 6, 'Use `requirements-pi.txt`, not `requirements.txt`: OpenCV and the camera come from apt, and pip\'s OpenCV would clash.', 8.6, w, col=MUTE) + 10
    t = box(c, Rr, t, w, 'EVERY TIME YOU LOG IN', ['`source ~/vanta-venv/bin/activate` then `cd ~/hexapod-brain`. Every command after this page assumes you did.'], ORA, 8.8, bg=Color(.99, .95, .91))
    return done(b, c)


@page
def power_up():
    def d(c):
        image(c, imgpath('8:s17'), 36, 52, 458, 300)
        code(c, 40, 372, 450, ['i2cdetect -y 1          # shows 40  (PCA #1)', 'i2cdetect -y 3          # shows 40  (PCA #2)',
                               'vcgencmd get_throttled  # 0x0 = power is good', 'python tools/center_servos.py   # Ctrl+C releases'], 8.4)
        txt(c, 40, 450, 'A board missing: its SDA/SCL jumpers, or VCC not on 3.3 V. Bus 3 missing entirely: the dtoverlay line, or no reboot.', 'Sans', 8.3, MUTE)
    return step_page('E · brain', CUR, 17, 'First power-up', 'Hull off. Robot up on a box, legs in the air. Hand near the switch.',
                     ['The finished robot (hull off), charged battery', 'Laptop on the same Wi-Fi'],
                     ['Battery in, alarm on the balance lead, switch on. The Pi light blinks, the PCA LEDs light.',
                      'SSH in. Run the two `i2cdetect` lines: both show **40**.',
                      '`vcgencmd get_throttled` says **0x0**.',
                      'Run `center_servos.py`. Every servo goes to centre, one leg at a time: the step 12 pose.',
                      'They move in channel order: FR coxa, femur, tibia, then MR, RR, then the left legs. One moves out of order: it\'s on the wrong channel (step 15). Anything hits something: **Ctrl+C**.'],
                     check=['All 18 hold the centre pose; nothing buzzes hard or gets hot in a minute.'],
                     careful=['Shut the Pi down (`sudo shutdown now`) before switching off. Stop at the LiPo alarm (3.5 V a cell).'],
                     draw=d, kicker='STEP 17 · B')


@page
def calibrate_walk():
    b, c = new_page('E · brain', CUR)
    y = title_block(c, 50, 'STEP 17 · C', 'Calibrate, then walk', 'Calibration fixes the last few degrees on every joint and saves them in `calibration.json`. Once per build.', w=700)
    L, Rr, w = 36, 404, 352
    t = y + 6
    txt(c, L, t, 'CALIBRATE  ·  robot held up off the table', 'MonoSB', 7.6, ORA)
    t = code(c, L, t + 14, w, ['python tools/calibrate.py']) + 10
    t = numbered(c, L, t, w, ['It goes through all 18 joints, leg by leg: FR, MR, RR, FL, ML, RL.',
                              'Each joint moves +15° and back. It tells you which way it should have gone (coxa: counter-clockwise from above; femur: knee up; tibia: foot in). Wrong way? Type `n`: it flips that joint and tries again.',
                              'Then trim it straight: type `+1`, `-0.5`, `+3` … (degrees) until coxa points straight out, femur is level, tibia is straight down. **Enter** moves on.',
                              'It saves after every joint. Stop any time with Ctrl+C; redo legs with `--leg FR --leg ML`.',
                              'Optional, more accurate: `python tools/calibrate.py --scale` with a phone level app on the front-right femur.'], 9)
    txt(c, L, t + 6, 'WHAT IT LOOKS LIKE', 'MonoSB', 7.6, MUTE)
    code(c, L, t + 20, w, ['FR_coxa: moving +15 deg. It should swing', '  counterclockwise, seen from above.', '  Right way? [Y/n]', '  Now trim until: leg points straight out from the body.',
                           '  FR_coxa trim +0.0 deg > +2', '  FR_coxa trim +2.0 deg > -0.5', '  FR_coxa trim +1.5 deg >', '  saved'], 7.6)
    t = y + 6
    txt(c, Rr, t, 'WALK', 'MonoSB', 7.6, ORA)
    t = code(c, Rr, t + 14, w, ['python sim.py --robot', '# no camera:  python sim.py --robot --no-camera']) + 10
    t = numbered(c, Rr, t, w, ['It prints a **phone control** link. Open it on your phone (same Wi-Fi; at the fair, run it on your phone\'s hotspot so nobody else can drive it).',
                               'Start it **sitting on the table** on its battery. It powers the legs one at a time into a crouch, then rises to STAND over about a second.',
                               'Ctrl+C turns the servos off and the robot **sits down hard**. Keep a hand under it. If the I2C link drops, it does the same on its own.'], 9)
    t = box(c, Rr, t + 4, w, 'THE PHONE PAGE', ['**STOP** is the big button. Keep your thumb near it.', 'Modes: STAND, CROUCH, FOLLOW, FAST FOLLOW, FREE ROAM, DANCE, TRANSPORT. RAISE / LOWER change height.',
                                                   'Hand signs to the camera work too: open palm = STOP, fist = CROUCH, point = FOLLOW, OK = STAND.'], MUTE, 8.6) + 10
    t = box(c, Rr, t, w, 'START ON BOOT (optional)', ['`sudo cp vanta.service /etc/systemd/system/`', '`sudo systemctl enable --now vanta`',
                                                          'Watch it: `journalctl -u vanta -f`. Stop it: `sudo systemctl stop vanta`.'], MUTE, 8.6)
    return done(b, c)


@page
def s18():
    return step_page('E · brain', CUR, 18, 'Mech hull and fans', 'It hides everything. The legs never touch it.',
                     ['Mech hull (COLOR file, plate 1)', '2× 30 mm fans + their screws', '4× M3×10, a long 2.5 mm hex key'],
                     ['Fans under the roof grilles, **label side down**. 4 screws each through the roof.',
                      'Fan leads down the left slot into the **buck Wagos** from step 16: both reds into +, both blacks into −. Leave ~15 cm slack.',
                      'Servo leads out through the six slots along the bottom edge, one leg\'s bundle per slot.',
                      'Lower the hull straight down, camera lens in the visor.',
                      'Its 4 bosses land over the posts. **4× M3×10** down through the round ports, through the deck, into the post inserts. Snug only.'],
                     check=['Run `center_servos.py` and swing each leg through its range: nothing touches the hull. Both fans spin. The camera sees out.'],
                     img='8:s18', progress='s18_p',
                     wires=['Fan leads into the buck Wagos **before** the hull goes on, with 15 cm of slack so the hull can lift off for access.',
                            'Everything inside is now reached by: 4 hull screws out, hull off, deck up 5 cm. No leg has to come apart.'])


# ============ 29–30 troubleshooting ============
def trouble(num, title, rows, extra=None):
    b, c = new_page('reference', num)
    title_block(c, 50, 'WHEN SOMETHING\'S OFF', title)
    y = table(c, 36, 112, [('what you see', 230), ('why', 200), ('fix', 290)], rows, size=8.6)
    if extra: extra(c, y + 14)
    return done(b, c)


@page
def t1():
    def lipo(c, y):
        box(c, 36, y, 720, 'LIPO CARE', ['Charge on the balance lead, on a hard surface, never unattended.',
                                         'Stop at the alarm (3.5 V a cell). Unplug the alarm afterwards: it drains the pack.',
                                         'Storing it longer than a week: about half charged. Puffy, dented or hot means it\'s done: don\'t use or charge it.'], ORA, 8.6, bg=Color(.99, .95, .91))
    return trouble(CUR, 'Mechanical and power', [
        ('A joint clunks or wobbles at the cap', 'Cap too thin, or A\'s screws loose', 'Tighten A to B. Still loose: +3 caps (`stl_main/other_cap_sizes/`).'),
        ('A joint binds, grinds, or A won\'t close', 'Cap too thick, bearing not flush, or a crooked insert', 'Back the bracket screws off a quarter turn to find which. Bearing flush. +1 caps if needed.'),
        ('Horn holes never line up with B', 'Not enough tries', 'Lift, one tooth, press. 25 positions: one is always within 2°. Don\'t twist the shaft.'),
        ('A leg sags or slips under load', 'Horn centre screw loose, or the horn jumped a tooth', 'Tighten the centre screw. Re-check the step 12 pose.'),
        ('Servos jitter when several move', 'Voltage drops under load', 'Measure at a PCA terminal while moving: above 5.6 V is fine. Re-seat the Wagos, shorten thin wires.'),
        ('Pi reboots or throttles', 'Buck too low or one pin pair only', 'Buck to 5.1–5.2 V. Use both 5 V (2, 4) and both GND (6, 9) pins.'),
        ('Fuse blows', 'Something jammed or shorted', 'Unplug, find it. Replace with 20 A only.'),
        ('Femur servos get hot standing', 'It\'s heavy (~2.45 kg)', 'Don\'t stand for long. Pull `REACH` in `controller.py` from 145 to 135.'),
        ('A leg touches the hull', 'Hull not seated, or a joint off centre', 'Re-seat the hull. Re-run calibrate for that leg.')], lipo)


@page
def t2():
    return trouble(CUR, 'Servos, code and the Pi', [
        ('One servo slams to an end stop on any signal, even a 10 µs jog', 'The servo is dead (pot or gears)', 'Swap it. Confirm on the console alone: a good one goes to centre at 1500 and holds.'),
        ('A servo snaps only when all joints power at once', 'Current spike', 'Power one at a time (`h` does). SBEC at 6.0 V, on the terminal, never a board\'s 5 V.'),
        ('Leg folds into the body on the first walk', 'HOME_US still 1500s', 'Do the jog calibration (step 12 · B) before `w`.'),
        ('A joint moves the wrong way in `t`', 'Sign is flipped for that build', 'Sketch: flip it in `SIGN[3]`. Pi: answer `n` in calibrate.py.'),
        ('`redefinition of …` when compiling', 'Two .ino files in one folder', 'One sketch per folder, folder named like the sketch.'),
        ('Serial Monitor shows only ESP-ROM, or nothing', 'USB CDC off, or the board waits for reset', 'Press RST. USB CDC On Boot: Enabled. 115200 baud. Right port.'),
        ('Console page: "no Web Serial" or can\'t open the port', 'Wrong browser, or the port is busy', 'Chrome or Edge. Close the Serial Monitor first: one program per port.'),
        ('Console connects but nothing moves', 'No servo power, or I2C wiring', 'SBEC on the green terminal? SDA/SCL swapped? VCC on 3V3?'),
        ('Board missing in `i2cdetect`', 'Jumper loose or swapped', 'Check SDA/SCL and VCC on 3.3 V. Bus 3 absent: dtoverlay line, reboot.'),
        ('Every femur/tibia over- or undershoots', 'Degrees-per-pulse off', '`python tools/calibrate.py --scale`.')], swap)


def swap(c, y):
    box(c, 36, y, 720, 'SWAPPING A DEAD SERVO IN A BUILT LEG', [
        'Battery out. Axle screw out, bracket A\'s 2 screws out, the horn\'s 4 screws out. Lift the joint apart; slide the cap off and onto the new servo.',
        'Centre the new servo on the bench (step 4C) **before** its horn goes back on. Rebuild the joint at the same target as its step (8, 10 or 11).',
        'On the Pi: `python tools/calibrate.py --leg FR` (that leg\'s name) to re-trim it. One-leg sketch: redo its HOME_US.'], ORA, 8.6, bg=Color(.99, .95, .91))


# ============ 31 quick reference (back) ============
@page
def back():
    b, c = new_page('quick reference', CUR, dark=True)
    txt(c, 36, 50, 'Quick reference', 'Arch', 26, W)
    mu = Color(.6, .6, .62); rule = Color(.22, .22, .24)

    def sec(x, y, h): txt(c, x, y, h, 'MonoSB', 7.6, ORA); return y + 14
    x1, x2, x3 = 36, 290, 530
    y = sec(x1, 96, 'LEG (mm)')
    y = table(c, x1, y, [('', 90), ('', 140)], [('coxa', '68'), ('femur', '76.7'), ('tibia', '101 (with grip tape)'), ('stand height', '82.5'), ('foot reach', '145')], size=8.4, head=False, col=W, rule=rule) + 12
    y = sec(x1, y, 'JOINT LIMITS (°)')
    y = table(c, x1, y, [('', 90), ('', 140)], [('coxa', '−35 … +35'), ('femur', '−80 … +85'), ('tibia', '−52 … +73')], size=8.4, head=False, col=W, rule=rule) + 12
    y = sec(x1, y, 'PULSE')
    y = para(c, x1, y, '1500 µs + sign × deg × 11.1 µs. Signs: coxa −1, femur +1, tibia +1. Channels off at boot.', 8.4, 230, col=W) + 10
    y = sec(x1, y, 'VOLTAGES')
    y = table(c, x1, y, [('', 90), ('', 140)], [('SBEC', '6.0 V → PCA terminals'), ('buck', '5.1 V → Pi 2,4 / 6,9 + fans'), ('PCA VCC', '3.3 V (Uno: 5 V)'), ('LiPo alarm', '3.5 V a cell')], size=8.4, head=False, col=W, rule=rule)
    y = sec(x2, 96, 'CHANNELS (robot)')
    y = table(c, x2, y, [('leg', 40), ('board', 70), ('coxa · femur · tibia', 110)], [('FR', 'PCA #1', '0 · 1 · 2'), ('MR', 'PCA #1', '3 · 4 · 5'), ('RR', 'PCA #1', '6 · 7 · 8'),
                                                                                  ('FL', 'PCA #2', '0 · 1 · 2'), ('ML', 'PCA #2', '3 · 4 · 5'), ('RL', 'PCA #2', '6 · 7 · 8')], size=8.4, col=W, rule=rule) + 12
    y = sec(x2, y, 'BENCH (ESP32-S3)')
    y = table(c, x2, y, [('', 70), ('', 150)], [('3V3 / GND', 'PCA VCC / GND'), ('GPIO 8 / 9', 'PCA SDA / SCL'), ('one leg', 'ch 15 coxa · 14 femur · 13 tibia'), ('serial', '115200, No line ending')], size=8.4, head=False, col=W, rule=rule) + 12
    y = sec(x2, y, 'PI')
    y = table(c, x2, y, [('', 70), ('', 150)], [('bus 1', 'pins 3/5 → PCA #1, 0x40'), ('bus 3', 'GPIO 4/5 (pins 7/29) → PCA #2'), ('login', '`ssh gio@vanta.local`')], size=8.4, head=False, col=W, rule=rule)
    y = sec(x3, 96, 'COMMANDS')
    for k, v in [('centre all', '`python tools/center_servos.py`'), ('calibrate', '`python tools/calibrate.py`'), ('one leg again', '`… calibrate.py --leg FR`'),
                 ('walk', '`python sim.py --robot`'), ('service', '`sudo systemctl stop vanta`'), ('logs', '`journalctl -u vanta -f`')]:
        txt(c, x3, y, k, 'Sans', 8, mu); y = para(c, x3, y + 11, v, 8.4, 226, col=W) + 6
    y = sec(x3, y + 6, 'SKETCH KEYS')
    y = table(c, x3, y, [('', 60), ('', 166)], [('`1 2 3`', 'pick coxa / femur / tibia'), ('`+ -`  `] [`', 'jog 10 / 50 µs'), ('`p`  `t`', 'print HOME_US · test'),
                                                ('`h`  `w`  `x`', 'home · walk · off')], size=8.4, head=False, col=W, rule=rule) + 12
    y = sec(x3, y, 'PRINT')
    para(c, x3, y, 'Caps **+2**, plate 10. Inserts 44. M3×10: 110. Horn screws come with the horns.', 8.4, 226, col=W)
    txt(c, 36, 584, 'VANTA, made by Gio. Legs, base and stiffeners: ggldnl/Hexapod-Hardware (CERN-OHL-W-2.0). Keep CREDITS.md with the files if you share them.', 'Sans', 7.6, mu)
    return done(b, c)


if __name__ == '__main__':
    TOTAL[0] = len(PAGES)
    w = pypdf.PdfWriter()
    for i, f in enumerate(PAGES):
        CUR = i
        w.add_page(f())
    w.add_metadata({'/Title': 'VANTA assembly guide rev 9', '/Author': 'Gio'})
    w.write(sys.argv[1] if len(sys.argv) > 1 else G + 'VANTA_assembly_guide.pdf')
    print('pages', len(PAGES))
