"""Assembly guide v6 (mech hull, all-alu horns, leg armour, grip tape instead of TPU feet).
Pages that did not change (bench power, centring, power in robot, servo leads, first power-up, troubleshooting) come from the v4 guide.
python guide6.py <v4 guide pdf> <out pdf>"""
import io, sys, pypdf
from reportlab.pdfgen import canvas
from guide5 import (H, INK, MUTE, ORA, GRN, BOX, RULE, W, RED, CARD, R5, txt, tw, wrap, header, image, box, step_page, table, inserts_page)


def page():
    b = io.BytesIO(); return b, canvas.Canvas(b, pagesize=(792, 612))


def done(b, c):
    c.save(); b.seek(0); return pypdf.PdfReader(b).pages[0]


def cover():
    b, c = page()
    c.setFillColor(INK); c.rect(0, 0, 792, 612, stroke=0, fill=1)
    txt(c, 36, 41.4, 'VANTA', 'Arch', 64, W)
    txt(c, 40, 104.0, '18-DOF HEXAPOD  ·  ASSEMBLY GUIDE  ·  v6', 'MonoSB', 11, ORA)
    c.setFillColor(INK); image(c, R5 + 'hero_color.png', 36, 136, 720, 400)
    txt(c, 36, 548.0, 'Made by Gio.', 'Sans', 11, W)
    txt(c, 36, 565.5, 'Legs, base and stiffeners: ggldnl/Hexapod-Hardware (CERN-OHL-W-2.0). Caps, alu-horn brackets, hull, armour, electronics and software: VANTA.', 'Sans', 9, MUTE)
    return done(b, c)


def start():
    b, c = page(); header(c, 'start here', 1)
    txt(c, 36, 50, 'Start here', 'Arch', 26, INK)
    y = 92
    txt(c, 36, y, 'THREE RULES', 'MonoSB', 8, ORA); y += 16
    for r in ["Centre every servo before a horn goes on (step 4), and never turn a servo shaft by hand after that. It's how the legs end up straight.",
              "Battery unplugged whenever you're wiring or screwing anything. Only plug it in when a step says so.",
              "Snug, not tight. Screws into inserts or self-tap holes strip the plastic if you crank them. Stop when the part stops moving."]:
        for j, l in enumerate(wrap(r, 'Sans', 10, 330)): txt(c, 36, y, ('•  ' if j == 0 else '   ') + l, 'Sans', 10, INK); y += 13.4
        y += 5
    y += 8; txt(c, 36, y, 'HOW TO READ THE PICTURES', 'MonoSB', 8, ORA); y += 16
    for col, s in ((ORA, 'Orange: the part you add in this step'), (Color_(0.42), 'Grey: parts already on the robot'), (INK, 'Black: servos'),
                   (RED, 'Red disc: a heat-set insert goes here'), (Color_(0.75), 'Silver: alu horns and bearings')):
        c.setFillColor(col); c.rect(36, H - y - 9, 10, 10, stroke=0, fill=1); txt(c, 54, y, s, 'Sans', 10, INK); y += 16
    y += 10; txt(c, 36, y, 'TOOLS', 'MonoSB', 8, ORA); y += 16
    for s in ['Soldering iron with an insert tip (or a plain tip), 200 °C for PLA', '2.5mm hex key, plus a long one for the hull screws', 'Multimeter',
              'Flush cutters, zip ties, a small knife for cleaning prints', 'CA glue or double-sided tape (armour), grip tape (feet)', 'A laptop that can SSH into the Pi']:
        txt(c, 36, y, '•  ' + s, 'Sans', 10, INK); y += 14
    x = 420; y = 92
    txt(c, x, y, 'THE BUILD', 'MonoSB', 8, ORA); y += 18
    for n, s in [('1–2', 'Fit test, heat-set inserts'), ('3–4', 'Power on the bench, reset all servos to zero'), ('5–7', 'Caps, coxa servos, body'),
                 ('8–11', 'Legs: coxa, femur, tibia joints, grip tape'), ('12', 'Check the legs, fit the armour'), ('13–16', 'Electronics plate, wiring, Pi deck'),
                 ('17', 'First power-up'), ('18', 'Mech hull')]:
        txt(c, x, y, n, 'MonoSB', 10, ORA); txt(c, x + 52, y, s, 'Sans', 10.5, INK); y += 19
    y += 14
    for l in wrap("Every step is one page: a picture on the left, what to grab and what to do on the right. Do the steps in order. "
                  "Steps with a badge (×6, ×18) repeat: finish one, check it, then do the rest.", 'Sans', 9.5, 336):
        txt(c, x, y, l, 'Sans', 9.5, MUTE); y += 13
    return done(b, c)


def Color_(g):
    from reportlab.lib.colors import Color
    return Color(g, g, g * 1.03)


def parts():
    b, c = page(); header(c, 'parts', 2)
    txt(c, 36, 50, 'Printed parts', 'Arch', 26, INK)
    txt(c, 246, 60, 'All from VANTA_print_MAIN_A1.3mf, black PLA. Caps: only the size your test joint fit (step 1).', 'Sans', 10, MUTE)
    txt(c, 246, 73, 'Mech hull + logo letters: VANTA_print_COLOR_AMS_A1.3mf (step 18).', 'Sans', 10, ORA)
    P = [("01_base_x1", "Base", "×1"), ("02_top_stiffeners_x1", "Top stiffeners", "1 set"), ("03_bottom_stiffeners_x1", "Bottom stiffeners", "1 set"),
         ("04_battery_mount_x1", "Battery mount", "×1"), ("05_electronics_plate_x1", "Electronics plate", "×1"), ("06_pi_deck_x1", "Pi deck", "×1"),
         ("07_femur_x6", "Femur", "×6"), ("08_tibia_x6", "Tibia", "×6"), ("09_bracket_A_coxa_x6", "Bracket A coxa", "×6"),
         ("09_bracket_A_link_x12", "Bracket A femur/tibia", "×12"), ("10_bracket_B_alu_x18", "Bracket B alu", "×18"),
         ("11_servo_cap_plus0_x18", "Servo cap", "×18"), ("13_armor_femur_x12", "Armour, femur", "×12"), ("14_armor_shin_x6", "Armour, shin", "×6")]
    cw, ch = 96.5, 236
    for i, (k, name, q) in enumerate(P):
        r, col = divmod(i, 7); x, top = 36 + col * (cw + 7), 98 + r * (ch + 12)
        c.setFillColor(CARD); c.roundRect(x, H - top - ch, cw, ch, 5, stroke=0, fill=1)
        image(c, R5 + 't_' + k + '.png', x + 4, top + 26, cw - 8, 120)
        txt(c, x + 8, top + 8, q, 'MonoSB', 9, ORA)
        yy = top + 158
        for l in wrap(name, 'SansB', 9.5, cw - 14): txt(c, x + 8, yy, l, 'SansB', 9.5, INK); yy += 12
        for l in wrap(k.replace('_', ' ').replace(' x', '_x'), 'Mono', 6.6, cw - 12): txt(c, x + 8, yy + 2, l, 'Mono', 6.6, MUTE); yy += 9
    return done(b, c)


def hardware():
    b, c = page(); header(c, 'parts', 3)
    txt(c, 36, 50, 'Hardware', 'Arch', 26, INK); txt(c, 412, 50, 'Electronics', 'Arch', 26, INK)
    rows = [("18", "623ZZ bearing (3×10×4)", "One in every servo cap"),
            ("18", "Aluminium 25T disc horn", "Every joint. You have 10: buy 8 (BUY_LIST)"),
            ("44", "M3 heat-set insert (OD 5)", "Step 2 map. You have 50: 6 spare"),
            ("100", "M3 × 6", "Alu horn → bracket B (72), coxa outer tabs (12), femur knee tabs (12), plate → columns (4)"),
            ("48", "M3 × 8", "Femur servo tabs, self-tap (36), coxa B → A (12)"),
            ("110", "M3 × 10", "Axles (18), B → A femur and tibia (24), femur → coxa bracket (24), tibia → bracket A (24), coxa inner tabs (12), stiffener corners (4), hull (4)"),
            ("12", "M3 washer", "Under the coxa outer tab screws"),
            ("12", "M2.5 × 6", "Pi (4), PCA boards (8)"),
            ("4", "M2 × 8 + nut", "Camera"),
            ("6", "Grip tape strip", "Wrapped round each tibia tip (the feet)"),
            ("–", "CA glue or double-sided tape", "Armour plates")]
    y = table(c, 36, 92, 350, [("qty", 0), ("part", 34), ("where", 160)], rows)
    note = ["You have 92 M3×6: the 8 short come with the 8 new horns (horn kits include their screws) or see BUY_LIST.",
            "Ø2.8 self-tap holes: run the screw in once to cut the thread, back it out, then assemble. Snug, never tight.",
            "Alu horns: M3-threaded holes on an 18mm bolt circle assumed. Check yours before printing plate 9."]
    yy = y + 10
    for n in note:
        for l in wrap(n, 'Sans', 8.6, 350): txt(c, 36, yy, l, 'Sans', 8.6, MUTE); yy += 11
        yy += 3
    erow = [("18", "MG995 servo (6 need a 30cm extension lead: the tibias)"), ("1", "Raspberry Pi 4 + microSD"), ("2", "PCA9685 16-channel servo board"),
            ("1", "OV5647 camera + ribbon"), ("1", "20A SBEC (servo power)"), ("1", "XL4015 buck converter (Pi power)"),
            ("1–2", "2S LiPo, XT60 (the Zeee 5200 fits the mount)"), ("1", "20A inline fuse, XT60 rocker switch, LiPo alarm"),
            ("~8", "Wago 221 lever connectors, 16AWG wire, 3 XT60 pigtails"), ("12", "Female-female jumper wires"), ("1", "Velcro strap for the battery")]
    table(c, 412, 92, 344, [("qty", 0), ("part", 34)], erow)
    return done(b, c)


ALU = "Disc on the spline, servo horn screw in. Bracket B over the disc; turn the disc a tooth at a time until its 4 holes line up with B's 4 holes (25 teeth, 4 holes: one always lines up within 2°). 4× M3×6."
NEW = {
    0: cover, 1: start, 2: parts, 3: hardware, 5: inserts_page,
    4: lambda: step_page(1, 4, 'prep', 'Fit test: build one joint', "Plate 1. It decides which servo cap size you print, so do it before the big plates.",
        ["Plate 1: caps +0 … +3, bracket A femur/tibia, bracket B alu", "1 servo, 1 623ZZ bearing, 1 alu disc horn", "3× M3×10 (1 is the axle), 4× M3×6"],
        ["Press the bearing into the +0 cap's hex boss from the outside, flush.", "Slide the cap over the servo bottom, cable through the notch.", ALU,
         "Swing bracket A round: its boss into the bearing, 2× M3×10 through B into A's end (they self-tap). Axle: M3×10 through A's side.",
         "Look at the gap between A's boss and the bearing."],
        ["Gap 0.3–1mm: print the +0 caps. ~1.5mm: +1. ~2.5mm: +2. ~3.5mm: +3. Won't close: stop and measure."], 's01'),
    7: lambda: step_page(4, 7, 'bench', 'Reset all 18 servos to zero', "Every servo goes to its zero (centre) position before any horn goes on. This is what makes the legs come out straight.",
        ["The bench setup from step 3", "Pi with the hexapod-brain software", "All 18 servos, a marker pen"],
        ["Wire the Pi to both PCA boards like the picture (4 jumpers each).", "Plug the servos into ch0–8 of each board, brown wire to the board's outer edge.",
         "Switch on, SSH in, run python tools/center_servos.py. Every servo jumps to zero (centre) and holds there.",
         "Ctrl+C, switch off. Mark each servo's spline with a pen dot facing up.",
         "If a shaft ever gets turned by accident, plug that servo back in and run the script again before its horn goes on."],
        ["Every servo moved once and stopped; all 18 dots face the same way.", "From here on, don't turn any servo shaft by hand: steps 8–11 rely on it."], 's04'),
    20: lambda: step_page(17, 20, 'power-up', 'First power-up', "Hold it up off the table the first time, legs in the air.",
        ["The finished robot (hull off), charged battery", "A laptop on the same Wi-Fi"],
        ["Battery in, alarm on the balance lead, switch on. The Pi's light blinks, the boards' LEDs light.",
         "SSH in: i2cdetect -y 1 and i2cdetect -y 3 both show 40.", "vcgencmd get_throttled says 0x0.",
         "Run python tools/center_servos.py. Every servo goes to zero: the step 12 pose.",
         "A joint moves the wrong way or hits something: Ctrl+C. It's on the wrong channel."],
        ["All 18 servos hold the zero pose; nothing buzzes hard or gets hot."], 's12top',
        careful=["Shut the Pi down (sudo shutdown now) before switching off. Stop at the LiPo alarm (3.5V per cell)."]),
    8: lambda: step_page(5, 8, 'servos', 'Caps on all servos', "Same as the fit test, now for the rest. The hex boss is the outside of the cap.",
        ["18 servos (centred)", "18 caps (the size that fit)", "18 623ZZ bearings"],
        ["Press a bearing into each cap's hex boss from the outside, flush with the face.", "Slide the cap over the servo bottom, cable through the notch.",
         "If one is loose, a wrap of tape on the servo fixes it."],
        ["The bearing turns freely with a finger and the cap doesn't rotate on the servo."], 's05', '×18'),
    9: lambda: step_page(6, 9, 'body', 'Coxa servos into the base', "Upside down: output shaft pointing at the floor, cap on top.",
        ["Base (16 inserts in)", "6 capped servos", "12× M3×6 + washers"],
        ["Turn the base over. Push each servo up through its pocket from below, cap first, until the tabs sit flat.",
         "Outer tabs (toward the leg): M3×6 + washer into the inserts. The inner tabs wait for step 7."],
        ["All six output shafts face down, centred in the pocket."], 's06', '×6'),
    10: lambda: step_page(7, 10, 'body', 'Bottom stiffeners and battery mount', "The stiffeners clamp the inner servo tabs and hold the battery mount. They're not optional.",
        ["Bottom stiffeners, battery mount", "16× M3×10"],
        ["Battery mount under the middle: its 4 corner ears go between the base and the stiffeners.", "Stiffeners over the inner servo tabs and the ears.",
         "12× M3×10 through the counterbores, stiffener and tab into the base (they self-tap).", "4× M3×10 through the stiffener corners and battery ears.",
         "Battery in, Velcro strap through the slots. Leave it unplugged."],
        ["Press on each coxa servo: nothing wobbles. The battery mount doesn't rattle."], 's07'),
    11: lambda: step_page(8, 11, 'legs', 'Coxa joints', "Each leg's first joint. The servo is fixed, the bracket swings.",
        ["Per leg: bracket A COXA, bracket B alu, 1 alu disc horn", "4× M3×6, 2× M3×8, 1× M3×10"],
        [ALU + " Set it so B points straight out from the body.", "Bracket A over the top, its boss on the cap's bearing.",
         "A to B: 2× M3×8 through B's counterbores into A's inserts. Axle: M3×10."],
        ["Each bracket points straight out from the body."], 's08', '×6'),
    12: lambda: step_page(9, 12, 'legs', 'Femur frames', "Each femur carries two servos: the femur servo and the tibia servo.",
        ["Per leg: 1 femur (2 inserts in), 2 capped servos", "6× M3×8, 2× M3×6"],
        ["Drop both servos in cap first, from the insert face. The tabs rest on the frame.", "Both output shafts on the same side.",
         "The two knee-end holes have inserts: M3×6. The other six self-tap: M3×8."],
        ["Both shafts on the same side, both caps poking out the other side."], 's09', '×6'),
    13: lambda: step_page(10, 13, 'legs', 'Femur joints', "The femur bracket bolts to the coxa bracket. This time the servo body swings, not the bracket.",
        ["Per leg: bracket A femur/tibia, bracket B alu, alu disc horn, the femur frame", "4× M3×6, 7× M3×10"],
        ["Femur frame level. " + ALU, "A around the servo: boss on the cap bearing, 2× M3×10 through B into A, M3×10 axle.",
         "Bolt this A back-to-back onto the coxa A: 4× M3×10 from inside the coxa bracket. The heads sink into its counterbores."],
        ["With everything centred the femur sticks straight out, level."], 's10', '×6'),
    14: lambda: step_page(11, 14, 'legs', 'Tibia joints and grip feet', "Last joint, then grip tape on the tip. No TPU feet in this build.",
        ["Per leg: bracket A femur/tibia, bracket B alu, alu disc horn, 1 tibia", "4× M3×6, 7× M3×10, a strip of grip tape"],
        ["Same U round the outer servo of the femur frame, axle included. Set the horn so the tibia points straight down when the femur is level.",
         "Tibia onto A's 4-hole face: 4× M3×10 through the tibia's counterbores (they self-tap into A).",
         "Wrap grip tape round the bottom 25mm of the tibia tip, overlapping on the inner face. Trim the end."],
        ["Femur level, tibia straight down, tip wrapped tight."], 's11', '×6'),
    15: lambda: step_page(12, 15, 'legs', 'Check the legs, fit the armour', "Centred pose first, then the armour. The armour is cosmetic: glue or tape, no screws.",
        ["The robot from step 11", "12 femur plates, 6 shin plates", "CA glue or double-sided tape"],
        ["Check: coxa straight out, femur level, tibia straight down on every leg. A joint off: 4 horn screws out, next tooth that lines up, screws back.",
         "Femur plates: one on each side rail, rib and bolts outward, the cut corner toward the knee. Glue only where the plate touches the rail.",
         "Shin plates: on the outer face of each tibia, flush with the bend at the top.", "Move each leg by hand through its walking range (not to the end stops: the armour can touch there): nothing rubs."],
        ["All six legs match. Small errors (under 2°) get trimmed in software later."], 's12', '×6'),
    16: lambda: step_page(13, 16, 'electronics', 'Electronics plate', "Top stiffeners, the plate, then the boards on it.",
        ["Top stiffeners, electronics plate (4 inserts in the posts)", "2 PCA boards, SBEC, buck", "4× M3×6, 8× M2.5×6, 4 zip ties"],
        ["Top stiffeners on: the 4 base columns go through their corner notches, the stiffeners rest on the coxa servos.",
         "Plate on top: 4× M3×6 into the column inserts. It clamps the stiffeners.",
         "PCA boards on the bosses, servo headers facing out. Front board = PCA #1, rear = PCA #2. Label them.",
         "Zip-tie the buck to the rear slots, the SBEC to the front slots."],
        ["Nothing touches the coxa caps when you turn a leg by its bracket."], 's13'),
    19: lambda: step_page(16, 19, 'electronics', 'Pi deck and camera', "The deck sits on the four posts. No screws yet: the hull bolts through it in step 18.",
        ["Pi deck, Pi 4 (SD card in), camera + ribbon", "4× M2.5×6, 4× M2×8 + nuts", "8 jumpers (PCA signal) + 4 for buck → Pi"],
        ["Pi on the bosses, USB ports to the back. Camera on the front wall, lens through the hole.", "Ribbon into the Pi's camera port: blue tab toward the USB ports.",
         "Jumpers down through the left slot: Pi to both PCAs (step 4 picture). Buck output to pins 2, 4 and 6, 9.",
         "Deck onto the posts: the servo plugs on the PCAs come up through the two long windows. Lay their wires flat before the Pi goes over them."],
        ["Ribbon not pinched, jumpers not tight, no servo wire under tension, nothing hanging into the legs."], 's16'),
    21: lambda: step_page(18, 21, 'finish', 'Mech hull', "Hides everything. The legs never touch it: it sits inside the old shell's envelope.",
        ["Mech hull (COLOR file, plate 1)", "4× M3×10, a long 2.5mm hex key"],
        ["Feed the servo leads through the six slots along the bottom edge, one leg pair per slot.",
         "Lower the hull straight down, the camera lens in the visor at the front.",
         "Its 4 bosses land on the deck over the posts. 4× M3×10 down through the round ports in the armour, through the deck into the post inserts.",
         "Snug only. Battery and switch stay reachable from underneath."],
        ["Run tools/center_servos.py again and wiggle each leg through its range: no leg touches the hull. Camera sees through the visor."], 's18'),
}

if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    r = pypdf.PdfReader(src); w = pypdf.PdfWriter()
    for i in range(len(r.pages)):
        w.add_page(NEW[i]() if i in NEW else r.pages[i])
    w.add_metadata({"/Title": "VANTA v6 assembly guide", "/Author": "Gio"})
    w.write(out)
    print("pages", len(w.pages))
