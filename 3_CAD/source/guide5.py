"""Assembly guide v5: unchanged pages come from the v4 guide, everything that changed is rebuilt in the same style.
python guide5.py <v4 guide pdf> <out pdf>"""
import io, sys, pypdf
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import Color
from reportlab.lib.utils import ImageReader
from PIL import Image

D = "./_dev/"
F, R5 = D + "fonts/", D + "man6/r5/"
for n, f in [('Arch', 'Archivo-ExtraBold'), ('Sans', 'PlexSans'), ('SansB', 'PlexSans-Bold'), ('Mono', 'PlexMono'), ('MonoSB', 'PlexMono-SemiBold'), ('DJ', 'DejaVuSans')]:
    pdfmetrics.registerFont(TTFont(n, F + f + '.ttf'))
INK = Color(.086, .090, .102); MUTE = Color(.408, .424, .451); ORA = Color(.722, .384, .059); GRN = Color(.184, .490, .275)
BOX = Color(.953, .945, .925); RULE = Color(.863, .851, .824); W = Color(1, 1, 1); RED = Color(.70, .16, .12); CARD = Color(.953, .945, .925)
H = 612


def tw(s, f, size): return sum(pdfmetrics.stringWidth(ch, 'DJ' if ch in '×→Ø±≈' else f, size) for ch in s)


def txt(c, x, top, s, font, size, col):
    y = H - top - size * 0.8; c.setFillColor(col)
    for ch in s:
        f = 'DJ' if ch in '×→Ø±≈' else font
        c.setFont(f, size); c.drawString(x, y, ch); x += pdfmetrics.stringWidth(ch, f, size)


def wrap(s, font, size, width):
    out, line = [], ""
    for w in s.split():
        t = (line + " " + w).strip()
        if tw(t, font, size) > width and line: out.append(line); line = w
        else: line = t
    return out + [line]


def header(c, section, num):
    txt(c, 36, 18.1, 'VANTA', 'Arch', 10, INK); txt(c, 82, 20.2, 'ASSEMBLY GUIDE  ·  ' + section, 'Mono', 8, MUTE)
    txt(c, 756 - tw(f'{num:02d}', 'Mono', 8), 20.2, f'{num:02d}', 'Mono', 8, MUTE)
    c.setStrokeColor(RULE); c.setLineWidth(.8); c.line(36, H - 34, 756, H - 34)


def image(c, f, x, top, w, h):
    im = ImageReader(f); iw, ih = im.getSize()
    s = min(w / iw, h / ih); dw, dh = iw * s, ih * s
    c.drawImage(im, x + (w - dw) / 2, H - top - (h - dh) / 2 - dh, dw, dh, mask='auto')


def box(c, y, label, lines, col, bg, width=244, x=512, bullet=True, k=1.0):
    ls = [l2 for l in lines for l2 in wrap(l, 'Sans', 9.5 * k, width - 26)]
    bh = 26 + len(ls) * 13.1 * k
    c.setFillColor(bg); c.rect(x, H - y - bh, width, bh, stroke=0, fill=1); c.setFillColor(col); c.rect(x, H - y - bh, 3, bh, stroke=0, fill=1)
    txt(c, x + 11, y + 10, label, 'MonoSB', 8, col)
    i = 0
    for l in lines:
        for j, l2 in enumerate(wrap(l, 'Sans', 9.5 * k, width - 26)):
            txt(c, x + 11, y + 24.5 + i * 13.1 * k, ('•  ' if j == 0 and bullet else '   ') + l2, 'Sans', 9.5 * k, INK); i += 1
    return y + bh


def step_page(*a, **kw):
    for k in (1.0, 0.93, 0.87, 0.82):   # shrink the right column until it clears the bottom margin
        page, bottom = _step_page(*a, k=k, **kw)
        if bottom < 592: return page
    print("WARNING: step", a[0], "still overflows"); return page


def _step_page(num, page, section, title, sub, need, steps, check, img, badge=None, careful=None, k=1.0):
    b = io.BytesIO(); c = canvas.Canvas(b, pagesize=(792, 612))
    header(c, section, page)
    image(c, R5 + img + '.png', 36, 60, 458, 500)
    txt(c, 512, 57.5, 'STEP', 'MonoSB', 9, ORA); txt(c, 509, 71.3, str(num), 'Arch', 54, INK)
    if badge:
        x = 512 + tw(str(num), 'Arch', 54) + 12; bw = tw(badge, 'SansB', 11) + 22
        c.setFillColor(ORA); c.roundRect(x, H - 111, bw, 24, 12, stroke=0, fill=1); txt(c, x + 11, 91.5, badge, 'SansB', 11, W)
    y = 132.2
    for l in wrap(title, 'Arch', 20, 244): txt(c, 512, y, l, 'Arch', 20, INK); y += 22
    y += 2
    for l in wrap(sub, 'Sans', 9.5, 244): txt(c, 512, y, l, 'Sans', 9.5, MUTE); y += 13.1
    y = box(c, y + 8, 'YOU NEED', need, MUTE, BOX, k=k) + 14
    txt(c, 512, y, 'DO THIS', 'MonoSB', 8, ORA); y += 14.6
    for i, s in enumerate(steps):
        c.setFillColor(INK); c.circle(519, H - y - 5, 7, stroke=0, fill=1)
        txt(c, 516.5 if i < 9 else 514, y + 1, str(i + 1), 'SansB', 8.5, W)
        for l in wrap(s, 'Sans', 10.2 * k, 222): txt(c, 532, y, l, 'Sans', 10.2 * k, INK); y += 13.6 * k
        y += 6 * k
    y += 6
    if careful: y = box(c, y, 'CAREFUL', careful, RED, Color(.98, .93, .92), k=k) + 10
    if check: y = box(c, y, 'CHECK', check, GRN, Color(.925, .957, .933), k=k)
    c.save(); b.seek(0); return pypdf.PdfReader(b).pages[0], y


def cover():
    b = io.BytesIO(); c = canvas.Canvas(b, pagesize=(792, 612))
    c.setFillColor(INK); c.rect(0, 0, 792, 612, stroke=0, fill=1)
    txt(c, 36, 41.4, 'VANTA', 'Arch', 64, W)
    txt(c, 40, 104.0, '18-DOF HEXAPOD  ·  ASSEMBLY GUIDE  ·  v5', 'MonoSB', 11, ORA)
    c.setFillColor(W); c.roundRect(36, H - 536, 720, 400, 8, stroke=0, fill=1)
    image(c, R5 + 'hero.png', 46, 142, 700, 388)
    txt(c, 36, 548.0, 'Made by Gio.', 'Sans', 11, W)
    txt(c, 36, 565.5, 'Legs, base and stiffeners: ggldnl/Hexapod-Hardware (CERN-OHL-W-2.0). Caps, alu-horn brackets, electronics, feet and software: VANTA.', 'Sans', 9, MUTE)
    c.save(); b.seek(0); return pypdf.PdfReader(b).pages[0]


def table(c, x, top, w, cols, rows, size=9.3):
    txt(c, x, top, cols[0][0], 'MonoSB', 8, MUTE)
    for (h, cx) in cols[1:]: txt(c, x + cx, top, h, 'MonoSB', 8, MUTE)
    y = top + 14
    c.setStrokeColor(RULE); c.setLineWidth(.6)
    for r in rows:
        c.line(x, H - y + 3, x + w, H - y + 3)
        lines = [wrap(r[i], 'Sans', size, (cols[i + 1][1] if i + 1 < len(cols) else w) - cols[i][1] - 8) for i in range(len(cols))]
        for i, ls in enumerate(lines):
            for j, l in enumerate(ls): txt(c, x + cols[i][1], y + 4 + j * 12.1, l, 'Sans', size, INK)
        y += 8 + max(len(l) for l in lines) * 12.1
    c.line(x, H - y + 3, x + w, H - y + 3)
    return y


def parts_page():
    b = io.BytesIO(); c = canvas.Canvas(b, pagesize=(792, 612)); header(c, 'parts', 2)
    txt(c, 36, 50, 'Printed parts', 'Arch', 26, INK)
    txt(c, 246, 60, 'All from VANTA_print_MAIN_A1.3mf. Caps: only the size(s) your test joints asked for (step 1).', 'Sans', 10, MUTE)
    txt(c, 246, 73, 'Top shell + logo letters: VANTA_print_COLOR_AMS_A1.3mf (step 18).', 'Sans', 10, ORA)
    P = [("01_base_x1", "Base", "×1"), ("02_top_stiffeners_x1", "Top stiffeners", "1 set"), ("03_bottom_stiffeners_x1", "Bottom stiffeners", "1 set"),
         ("04_battery_mount_x1", "Battery mount", "×1"), ("05_electronics_plate_x1", "Electronics plate", "×1"), ("06_pi_deck_x1", "Pi deck", "×1"),
         ("07_femur_x6", "Femur", "×6"), ("08_tibia_x6", "Tibia", "×6"), ("09_bracket_A_coxa_x6", "Bracket A coxa", "×6"),
         ("09_bracket_A_link_x12", "Bracket A femur/tibia", "×12"), ("10_bracket_B_stock_x8", "Bracket B stock", "×8"),
         ("10_bracket_B_alu_x10", "Bracket B alu", "×10"), ("11_servo_cap_plus0_x18", "Servo cap", "×18"), ("12_foot_TPU_x6", "Foot (TPU)", "×6")]
    cw, ch = 96.5, 236
    for i, (k, name, q) in enumerate(P):
        r, col = divmod(i, 7); x, top = 36 + col * (cw + 7), 98 + r * (ch + 12)
        c.setFillColor(CARD); c.roundRect(x, H - top - ch, cw, ch, 5, stroke=0, fill=1)
        image(c, R5 + 't_' + k + '.png', x + 4, top + 26, cw - 8, 120)
        txt(c, x + 8, top + 8, q, 'MonoSB', 9, ORA)
        yy = top + 158
        for l in wrap(name, 'SansB', 9.5, cw - 14): txt(c, x + 8, yy, l, 'SansB', 9.5, INK); yy += 12
        for l in wrap(k.replace('_', ' ').replace(' x', '_x'), 'Mono', 6.6, cw - 12): txt(c, x + 8, yy + 2, l, 'Mono', 6.6, MUTE); yy += 9
    c.save(); b.seek(0); return pypdf.PdfReader(b).pages[0]


def hardware_page():
    b = io.BytesIO(); c = canvas.Canvas(b, pagesize=(792, 612)); header(c, 'parts', 3)
    txt(c, 36, 50, 'Hardware', 'Arch', 26, INK); txt(c, 412, 50, 'Electronics', 'Arch', 26, INK)
    rows = [("18", "623ZZ bearing (3×10×4)", "One in every servo cap"),
            ("10", "Aluminium 25T disc horn", "Femur joints ×6, tibia joints FR MR ML FL"),
            ("8", "Stock single-arm horn", "Coxa joints ×6, tibia joints RR RL"),
            ("44", "M3 heat-set insert (OD 5)", "Step 2 map. You have 50: 6 spare"),
            ("68", "M3 × 6", "Alu horn → bracket B (40), coxa outer tabs (12), femur knee tabs (12), plate → columns (4)"),
            ("48", "M3 × 8", "Femur servo tabs, self-tap (36), coxa B → A (12)"),
            ("110", "M3 × 10", "Axles (18), B → A femur and tibia (24), femur → coxa bracket (24), tibia → bracket A (24), coxa inner tabs (12), stiffener corners (4), shell (4)"),
            ("12", "M3 washer", "Under the coxa outer tab screws"),
            ("12", "M2.5 × 6", "Pi (4), PCA boards (8)"),
            ("4", "M2 × 8 + nut", "Camera")]
    y = table(c, 36, 92, 350, [("qty", 0), ("part", 34), ("where", 160)], rows)
    note = ["Everything comes from what you already have. Left over: 24× M3×6, 2× M3×8, 10× M3×10, 2× M3×12, 6 inserts.",
            "Ø2.8 self-tap holes: run the screw in once to cut the thread, back it out, then assemble. Snug, never tight.",
            "Alu horns: assumed M3-threaded holes. If yours are plain holes you need nuts (see BUY_LIST)."]
    yy = y + 10
    for n in note:
        for l in wrap(n, 'Sans', 8.6, 350): txt(c, 36, yy, l, 'Sans', 8.6, MUTE); yy += 11
        yy += 3
    erow = [("18", "MG995 servo (6 need a 30cm extension lead: the tibias)"), ("1", "Raspberry Pi 4 + microSD"), ("2", "PCA9685 16-channel servo board"),
            ("1", "OV5647 camera + ribbon"), ("1", "20A SBEC (servo power)"), ("1", "XL4015 buck converter (Pi power)"),
            ("1–2", "2S LiPo, XT60 (the Zeee 5200 fits the mount)"), ("1", "20A inline fuse, XT60 rocker switch, LiPo alarm"),
            ("~8", "Wago 221 lever connectors, 16AWG wire, 3 XT60 pigtails"), ("12", "Female-female jumper wires"), ("1", "Velcro strap for the battery")]
    table(c, 412, 92, 344, [("qty", 0), ("part", 34)], erow)
    c.save(); b.seek(0); return pypdf.PdfReader(b).pages[0]


def inserts_page():
    b = io.BytesIO(); c = canvas.Canvas(b, pagesize=(792, 612)); header(c, 'prep', 5)
    txt(c, 512 - 476, 57.5, 'STEP', 'MonoSB', 9, ORA); txt(c, 33, 71.3, '2', 'Arch', 54, INK)
    txt(c, 80, 76, 'Heat-set inserts: 44 of your 50', 'Arch', 22, INK)
    for i, l in enumerate(wrap("Red discs: an insert goes here, from that face. Iron at 200 °C, let it sink under its own weight, stop flush. "
                               "Every other M3 hole is a Ø2.8 self-tap hole: no insert, the screw cuts its own thread.", 'Sans', 10, 660)):
        txt(c, 80, 104 + i * 13, l, 'Sans', 10, INK)
    panels = [("i_base_under", "Base, underside", "12: the outer tab holes of the six coxa pockets (base turned over)"),
              ("i_base_top", "Base, columns", "4: top of the plate columns"),
              ("i_femur", "Femur ×6", "2 each: the knee-end tab holes, from the tab face"),
              ("i_acoxa", "Bracket A COXA ×6", "2 each in the end face. Its 4-hole face is clearance + counterbore: nothing there"),
              ("i_plate", "Electronics plate", "4: top of the deck posts")]
    pw = 140
    for i, (img, t, s) in enumerate(panels):
        x = 36 + i * (pw + 5)
        c.setFillColor(CARD); c.roundRect(x, H - 560, pw, 420, 6, stroke=0, fill=1)
        image(c, R5 + img + '.png', x + 6, 160, pw - 12, 250)
        txt(c, x + 10, 440, t, 'SansB', 10.5, INK)
        for j, l in enumerate(wrap(s, 'Sans', 9, pw - 20)): txt(c, x + 10, 458 + j * 12, l, 'Sans', 9, MUTE)
    txt(c, 36, 574, 'Not shown: the Ø2.8 self-tap holes (femur 6 each, base inner tabs and corners, femur/tibia bracket A end and 4-hole faces, the axles).', 'Sans', 8.6, MUTE)
    c.save(); b.seek(0); return pypdf.PdfReader(b).pages[0]


NEW = {
    0: cover, 2: parts_page, 3: hardware_page, 5: inserts_page,
    4: lambda: step_page(1, 4, 'prep', 'Fit test: one joint per horn type', "Plate 1. It decides which servo caps you print. Build a stock-arm joint, then swap to the alu disc.",
        ["Plate 1: caps +0 … +3, bracket A femur/tibia, B stock, B alu", "1 servo, 1 623ZZ, 1 stock arm horn, 1 alu disc horn", "3× M3×10 (1 is the axle), 4× M3×6"],
        ["Press the bearing into the +0 cap's hex boss from outside, flush.", "Cap over the servo bottom, cable through the notch.",
         "Stock: arm horn into B's slot, spline into the horn, horn screw.", "A around: boss in the bearing, 2× M3×10 through B into A (they self-tap), M3×10 axle through A's side.",
         "Note the gap between A's boss and the bearing.", "Alu: disc on the spline, B alu over it, turn the disc a tooth at a time until all 4 holes show in the slots, 4× M3×6. Refit A, note the gap again."],
        ["Gap 0.3–1mm: +0. ~1.5mm: +1. ~2.5mm: +2. ~3.5mm: +3.", "Write down one size for the 8 stock joints and one for the 10 alu joints. Same size: print that cap plate twice."], 's01'),
    8: lambda: step_page(5, 8, 'servos', 'Caps on all servos', "Same as the fit test. The caps print skirt-down; the hex boss is the outside.",
        ["18 servos (centred)", "18 caps: 10 in the alu size, 8 in the stock size", "18 623ZZ bearings"],
        ["Press a bearing into each cap's hex boss from the outside, flush with the face.", "Slide the cap over the servo bottom, cable through the notch.",
         "If one is loose, a wrap of tape on the servo fixes it.", "Mark the 10 alu-size servos: femur ×6, tibia FR MR ML FL."],
        ["The bearing turns freely with a finger and the cap doesn't rotate on the servo."], 's05', '×18'),
    9: lambda: step_page(6, 9, 'body', 'Coxa servos into the base', "Upside down: output shaft pointing at the floor, cap on top.",
        ["Base (16 inserts in)", "6 capped servos (stock size)", "12× M3×6 + washers"],
        ["Turn the base over. Push each servo up through its pocket from below, cap first, until the tabs sit flat.",
         "Outer tabs (toward the leg): M3×6 + washer into the inserts. The inner tabs wait for step 7."],
        ["All six output shafts face down, centred in the pocket."], 's06', '×6'),
    10: lambda: step_page(7, 10, 'body', 'Bottom stiffeners and battery mount', "The stiffeners clamp the inner servo tabs and hold the battery mount. They're not optional.",
        ["Bottom stiffeners, battery mount", "16× M3×10"],
        ["Battery mount under the middle: its 4 corner ears go between the base and the stiffeners.", "Stiffeners over the inner servo tabs and the ears.",
         "12× M3×10 through the counterbores, stiffener and tab into the base (they self-tap).", "4× M3×10 through the stiffener corners and battery ears.",
         "Battery in, Velcro strap through the slots. Leave it unplugged."],
        ["Press on each coxa servo: nothing wobbles. The battery mount doesn't rattle."], 's07'),
    11: lambda: step_page(8, 11, 'legs', 'Coxa joints', "Each leg's first joint, stock arm horn. The servo is fixed, the bracket swings.",
        ["Per leg: bracket A COXA, bracket B stock, 1 arm horn", "2× M3×8, 1× M3×10"],
        ["Arm horn into B's slot.", "Hold B under the coxa servo, spline into the horn so the arm points straight out. Horn screw in.",
         "Bracket A over the top, its boss on the cap's bearing.", "A to B: 2× M3×8 through B's counterbores into A's inserts. Axle: M3×10."],
        ["Each bracket points straight out from the body, give or take one tooth (14°)."], 's08', '×6'),
    12: lambda: step_page(9, 12, 'legs', 'Femur frames', "Each femur carries two servos: the femur servo and the tibia servo.",
        ["Per leg: 1 femur (2 inserts in), 2 capped servos: femur servo alu size; tibia servo alu size on FR MR ML FL, stock size on RR RL", "6× M3×8, 2× M3×6"],
        ["Drop both servos in cap first, from the insert face. The tabs rest on the frame.", "Both output shafts on the same side.",
         "The two knee-end holes have inserts: M3×6. The other six self-tap: M3×8."],
        ["Both shafts on the same side, both caps poking out the other side."], 's09', '×6'),
    13: lambda: step_page(10, 13, 'legs', 'Femur joints (alu)', "The femur bracket bolts to the coxa bracket. This time the servo body swings, not the bracket.",
        ["Per leg: bracket A femur/tibia, bracket B ALU, alu disc horn, the femur frame", "4× M3×6, 7× M3×10"],
        ["Femur frame level. Disc on the inner servo's spline, servo horn screw in.",
         "B alu over the disc. Turn the disc a tooth at a time until all 4 holes show in B's slots (25 teeth, 4 holes: there's always one within 2°). 4× M3×6.",
         "A around the servo: boss on the cap bearing, 2× M3×10 through B into A, M3×10 axle.",
         "Bolt this A back-to-back onto the coxa A: 4× M3×10 from inside the coxa bracket. The heads sink into its counterbores."],
        ["With everything centred the femur sticks straight out, level."], 's10', '×6'),
    14: lambda: step_page(11, 14, 'legs', 'Tibia joints and feet', "FR, MR, ML, FL get the alu disc (like step 10). RR and RL keep the stock arm (like step 8).",
        ["Per leg: bracket A femur/tibia, tibia, TPU foot", "Alu legs: B alu, disc horn, 4× M3×6", "Stock legs: B stock, arm horn", "7× M3×10"],
        ["Same U around the outer servo, 2× M3×10 B to A, axle included.", "Set the horn so the tibia points straight down when the femur is level.",
         "Tibia onto A's 4-hole face: 4× M3×10 through the tibia's counterbores (they self-tap into A).", "Push the TPU foot onto the tip. A drop of super glue if it slips."],
        ["Femur level, tibia straight down, foot on."], 's11', '×6'),
    15: lambda: step_page(12, 15, 'legs', 'Check the legs', "This is the pose every servo is centred in. Look at it from above.",
        ["The robot from step 11", "A hex key for the horn screws"],
        ["Coxa: every leg points straight out from the body, like the picture.", "Femur: level with the table.", "Tibia: straight down.",
         "Stock joint more than one tooth off: horn screw out, lift the horn, turn it one tooth, put it back.",
         "Alu joint off: 4 horn screws out, turn the disc to the next tooth whose holes line up with the slots, screws back in."],
        ["All six legs match. Leftovers (under 7° on stock joints, under 2° on alu) get trimmed in software later."], 's12'),
    16: lambda: step_page(13, 16, 'electronics', 'Electronics plate', "Top stiffeners, the plate, then the boards on it.",
        ["Top stiffeners, electronics plate (4 inserts in the posts)", "2 PCA boards, SBEC, buck", "4× M3×6, 8× M2.5×6, 4 zip ties"],
        ["Top stiffeners on: the 4 base columns go through their corner notches, the stiffeners rest on the coxa servos.",
         "Plate on top: 4× M3×6 into the column inserts. It clamps the stiffeners.",
         "PCA boards on the bosses, servo headers facing out. Front board = PCA #1, rear = PCA #2. Label them.",
         "Zip-tie the buck to the rear slots, the SBEC to the front slots."],
        ["Nothing touches the coxa caps when you turn a leg by its bracket."], 's13'),
    19: lambda: step_page(16, 19, 'electronics', 'Pi deck and camera', "The deck sits on the four posts. No screws yet: the top shell bolts through it in step 18.",
        ["Pi deck, Pi 4 (SD card in), camera + ribbon", "4× M2.5×6, 4× M2×8 + nuts", "8 jumpers (PCA signal) + 4 for buck → Pi"],
        ["Pi on the bosses, USB ports to the back. Camera on the front wall, lens through the hole.", "Ribbon into the Pi's camera port: blue tab toward the USB ports.",
         "Jumpers down through the left slot: Pi to both PCAs (step 4 picture). Buck output to pins 2, 4 and 6, 9.", "Deck onto the posts. No screws yet (step 18)."],
        ["Ribbon not pinched, jumpers not tight, nothing hanging into the legs."], 's16'),
    21: lambda: step_page(18, 21, 'finish', 'Top shell', "Hides everything. The legs never touch it (1.3mm closest), it only sits on the deck and plate.",
        ["Top shell (COLOR file, plate 1)", "4× M3×10"],
        ["Feed the servo leads through the six slots along the bottom edge, one leg pair per slot.", "Lower the shell straight down, lens hole at the front over the camera.",
         "Its 4 tubes land on the deck holes. 4× M3×10 through tube + deck into the post inserts.", "Snug only. Battery and switch stay reachable from underneath."],
        ["Run tools/center_servos.py again and wiggle each leg through its range: no leg touches the shell. Camera still sees through the hole."], 's18'),
}

if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    r = pypdf.PdfReader(src); w = pypdf.PdfWriter()
    for i in range(len(r.pages)):
        w.add_page(NEW[i]() if i in NEW else r.pages[i])
    w.add_metadata({"/Title": "VANTA v5 assembly guide", "/Author": "Gio"})
    w.write(out)
    print("pages", len(w.pages))
