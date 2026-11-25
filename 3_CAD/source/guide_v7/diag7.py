"""Vector diagrams for guide v7."""
import math
from lib7 import *


def Y(top): return H - top


def fitdraw(c, fn, x, top, s):
    """Draw fn (which uses page coords with its own origin at x=0, top=0) at (x, top), scaled by s."""
    c.saveState(); c.translate(x, H - top); c.scale(s, s); c.translate(0, -H); fn(c); c.restoreState()


def rbox(c, x, top, w, h, title, sub=None, fill=None, stroke=None, tsize=9.5, dark=False):
    c.setFillColor(fill or W); c.setStrokeColor(stroke or INK); c.setLineWidth(.9)
    c.roundRect(x, Y(top + h), w, h, 4, stroke=1, fill=1)
    tc = W if dark else INK
    txt(c, x + w / 2, top + h / 2 - (8 if sub else 4.5), title, 'SansB', tsize, tc, 'c')
    if sub: txt(c, x + w / 2, top + h / 2 + 4, sub, 'Mono', 7, MUTE, 'c')


def wire(c, pts, col, w=1.6, dash=None):
    c.setStrokeColor(col); c.setLineWidth(w)
    if dash: c.setDash(*dash)
    p = c.beginPath(); p.moveTo(pts[0][0], Y(pts[0][1]))
    for x, t in pts[1:]: p.lineTo(x, Y(t))
    c.drawPath(p, stroke=1, fill=0); c.setDash()


def wago(c, x, t):
    c.setFillColor(W); c.setStrokeColor(ORA); c.setLineWidth(1.2); c.rect(x - 3.5, Y(t + 3.5), 7, 7, stroke=1, fill=1)


def legend(c, x, top, items):
    for col, dash, s in items:
        wire(c, [(x, top + 4), (x + 18, top + 4)], col, 1.6, dash); txt(c, x + 24, top, s, 'Sans', 8, MUTE); x += 30 + tw(s, 'Sans', 8) + 14


# ---------------- power ----------------

def power(c, x0=40, top0=70, robot=False):
    legend(c, x0, top0, [(PLUS, None, '+'), (INK, None, '−'), (ORA, None, ''), ])
    txt(c, x0 + 118, top0, 'orange square = Wago lever connector', 'Sans', 8, MUTE)
    t = top0 + 30
    bx = [(x0, 'Battery', '2S LiPo · XT60'), (x0 + 112, 'Fuse', '20A'), (x0 + 200, 'Switch', 'XT60 rocker')]
    for x, a, b in bx: rbox(c, x, t + 110, 80 if a != 'Battery' else 88, 44, a, b)
    # + chain
    wire(c, [(x0 + 88, t + 124), (x0 + 112, t + 124)], PLUS); wago(c, x0 + 100, t + 124)
    wire(c, [(x0 + 192, t + 124), (x0 + 200, t + 124)], PLUS)
    wire(c, [(x0 + 88, t + 142), (x0 + 96, t + 142), (x0 + 96, t + 172), (x0 + 240, t + 172), (x0 + 240, t + 154)], INK)
    # split
    sx = x0 + 300
    wire(c, [(x0 + 280, t + 124), (sx, t + 124)], PLUS); wire(c, [(x0 + 280, t + 142), (sx + 8, t + 142)], INK)
    wago(c, sx, t + 124); wago(c, sx + 8, t + 142)
    # SBEC
    rbox(c, x0 + 330, t + 10, 92, 50, 'SBEC 20A', 'set to 6.0 V')
    wire(c, [(sx, t + 124), (sx, t + 24), (x0 + 330, t + 24)], PLUS); wire(c, [(sx + 8, t + 142), (sx + 8, t + 44), (x0 + 330, t + 44)], INK)
    # Buck
    rbox(c, x0 + 330, t + 200, 92, 50, 'Buck XL4015', 'set to 5.1 V')
    wire(c, [(sx, t + 124), (sx, t + 214), (x0 + 330, t + 214)], PLUS); wire(c, [(sx + 8, t + 142), (sx + 8, t + 234), (x0 + 330, t + 234)], INK)
    # PCAs
    px = x0 + 452
    for i, tt in enumerate((t - 10, t + 50)):
        rbox(c, px, tt, 80 if not robot else 80, 42, f'PCA #{i + 1}', 'V+ / GND terminal', fill=W)
    wire(c, [(x0 + 422, t + 24), (px - 14, t + 24), (px - 14, t + 4), (px, t + 4)], PLUS)
    wire(c, [(px - 14, t + 24), (px - 14, t + 64), (px, t + 64)], PLUS)
    wire(c, [(x0 + 422, t + 44), (px - 6, t + 44), (px - 6, t + 20), (px, t + 20)], INK)
    wire(c, [(px - 6, t + 44), (px - 6, t + 80), (px, t + 80)], INK)
    wago(c, px - 14, t + 24); wago(c, px - 6, t + 44)
    # Pi
    rbox(c, px, t + 198, 80, 54, 'Pi 4', 'pins 2,4 / 6,9')
    wire(c, [(x0 + 422, t + 214), (px, t + 214)], PLUS); wire(c, [(x0 + 422, t + 234), (px, t + 234)], INK)
    if robot:
        rbox(c, px, t + 268, 80, 34, '2 fans', 'step 18')
        wire(c, [(px - 14, t + 214), (px - 14, t + 278), (px, t + 278)], PLUS); wire(c, [(px - 6, t + 234), (px - 6, t + 292), (px, t + 292)], INK)
    # alarm
    rbox(c, x0, t + 230, 88, 36, 'LiPo alarm', 'on the balance lead')
    wire(c, [(x0 + 44, t + 154), (x0 + 44, t + 230)], GREY, 1.2)
    txt(c, x0 + 50, t + 186, 'balance lead', 'Mono', 7, MUTE)


# ---------------- PCA board + controller ----------------

def pca_board(c, x, top, w=210, h=96, name='PCA9685', left_pins=True, highlight=None):
    c.setFillColor(Color(.93, .93, .94)); c.setStrokeColor(INK); c.setLineWidth(.9); c.roundRect(x, Y(top + h), w, h, 4, stroke=1, fill=1)
    txt(c, x + w / 2, top + 30, name, 'SansB', 9.5, INK, 'c')
    # screw terminal
    c.setFillColor(Color(.30, .55, .35)); c.rect(x + w / 2 - 16, Y(top + 14), 32, 14, stroke=0, fill=1)
    txt(c, x + w / 2 - 8, top + 15.5, 'V+', 'Mono', 6, INK, 'c'); txt(c, x + w / 2 + 8, top + 15.5, 'GND', 'Mono', 6, INK, 'c')
    # left header
    pins = ['GND', 'OE', 'SCL', 'SDA', 'VCC', 'V+']
    for i, p in enumerate(pins):
        yy = top + 18 + i * 11.5
        c.setFillColor(INK); c.rect(x + 3, Y(yy + 3), 6, 6, stroke=0, fill=1)
        txt(c, x + 13, yy - 3.2, p, 'Mono', 6.3, MUTE if p in ('OE', 'V+') else INK)
    # servo headers along bottom
    for ch in range(16):
        gx = x + 46 + ch * 9.6 + (ch // 4) * 3
        for r, col in enumerate((Color(.85, .55, .1), PLUS, INK)):
            c.setFillColor(col); c.rect(gx, Y(top + h - 30 + r * 8 + 5), 5, 5, stroke=0, fill=1)
        if ch % 4 == 0 or ch == 15: txt(c, gx + 2.5, top + h - 40, str(ch), 'Mono', 5.6, MUTE, 'c')
    txt(c, x + 41, top + h - 28.5, 'PWM', 'Mono', 5.2, MUTE, 'r'); txt(c, x + 41, top + h - 20.5, 'V+', 'Mono', 5.2, MUTE, 'r'); txt(c, x + 41, top + h - 12.5, 'GND', 'Mono', 5.2, MUTE, 'r')
    return {p: (x + 6, top + 18 + i * 11.5) for i, p in enumerate(pins)}


def controller(c):
    x0, t0 = 36, 56
    t = t0 + 34
    c.setFillColor(DARK); c.roundRect(x0, Y(t + 130), 74, 130, 4, stroke=0, fill=1)
    txt(c, x0 + 37, t + 70, 'ESP32-S3', 'SansB', 8.5, W, 'c'); txt(c, x0 + 37, t + 82, 'DevKitC', 'Mono', 6.5, Color(.7, .7, .7), 'c')
    c.setFillColor(Color(.6, .6, .62)); c.rect(x0 + 27, Y(t + 138), 20, 10, stroke=0, fill=1); txt(c, x0 + 37, t + 141, 'USB-C to laptop', 'Mono', 6.3, MUTE, 'c')
    epins = [('3V3', 12, PLUS, 'VCC'), ('GND', 24, INK, 'GND'), ('GPIO 8', 36, MUTE, 'SDA'), ('GPIO 9', 48, MUTE, 'SCL')]
    pins = pca_board(c, x0 + 246, t, 210, 100)
    for i, (n, dy, col, to) in enumerate(epins):
        yy = t + dy
        c.setFillColor(W); c.circle(x0 + 70, Y(yy), 2.2, stroke=0, fill=1)
        txt(c, x0 + 64, yy - 3.5, n, 'Mono', 6.5, W, 'r')
        px, pt = pins[to]
        wire(c, [(x0 + 72, yy), (x0 + 150 + i * 14, yy), (x0 + 150 + i * 14, pt), (px, pt)], col, 1.5, (3, 2) if to == 'SCL' else None)
    sx = x0 + 246 + 105
    wire(c, [(sx - 8, t), (sx - 8, t - 14), (sx - 70, t - 14)], PLUS); wire(c, [(sx + 8, t), (sx + 8, t - 24), (sx - 70, t - 24)], INK)
    txt(c, sx - 74, t - 22, 'from the SBEC, 6.0 V', 'Mono', 6.8, MUTE, 'r')
    tt = t + 160
    tt = table(c, x0, tt, [('PCA9685 pin', 78), ('ESP32-S3', 70), ('Uno', 50), ('what it is', 260)], [
        ('`VCC`', '`3V3`', '`5V`', 'logic power for the PCA chip only'),
        ('`GND`', '`GND`', '`GND`', 'common ground'),
        ('`SDA`', '`GPIO 8`', '`A4`', 'I2C data'),
        ('`SCL`', '`GPIO 9`', '`A5`', 'I2C clock (dashed in the drawing)'),
        ('`OE`, `V+`', 'nothing', 'nothing', 'leave empty: servo power goes in the green terminal')], size=8.6)
    return tt


def plug(c, x, top, w=210):
    """Servo plug orientation on a PCA header column."""
    txt(c, x, top, 'PLUG ORIENTATION  ·  every servo, every board', 'MonoSB', 7.6, ORA)
    t = top + 18
    c.setFillColor(Color(.93, .93, .94)); c.setStrokeColor(INK); c.setLineWidth(.8); c.rect(x, Y(t + 70), 90, 70, stroke=1, fill=1)
    txt(c, x + 45, t + 8, 'board', 'Mono', 7, MUTE, 'c')
    rows = [('PWM', Color(.85, .55, .1), 'orange / yellow wire'), ('V+', PLUS, 'red wire (middle)'), ('GND', INK, 'brown / black wire')]
    for i, (lab, col, s) in enumerate(rows):
        yy = t + 30 + i * 13
        c.setFillColor(col); c.rect(x + 70, Y(yy + 4), 8, 8, stroke=0, fill=1)
        txt(c, x + 64, yy - 3, lab, 'Mono', 6.5, INK, 'r')
        wire(c, [(x + 78, yy), (x + 140, yy)], col, 3)
        txt(c, x + 146, yy - 3.6, s, 'Sans', 7.8, INK)
    c.setStrokeColor(ORA); c.setLineWidth(1.2); c.line(x + 90, Y(t + 66), x + 90, Y(t + 22))
    txt(c, x + 93, t + 72, 'board edge: brown goes here', 'Mono', 6.6, ORA)


# ---------------- servo leads, top view ----------------

def leads(c):
    cx, cy = 265, 300
    c.setFillColor(Color(.93, .93, .94)); c.setStrokeColor(INK); c.setLineWidth(.9)
    c.roundRect(cx - 55, Y(cy + 90), 110, 180, 10, stroke=1, fill=1)
    wire(c, [(cx, cy - 40), (cx, cy - 78)], ORA, 1.6); c.setFillColor(ORA)
    p = c.beginPath(); p.moveTo(cx - 5, Y(cy - 76)); p.lineTo(cx + 5, Y(cy - 76)); p.lineTo(cx, Y(cy - 86)); p.close(); c.drawPath(p, stroke=0, fill=1)
    txt(c, cx, cy - 100, 'FRONT  (camera)', 'MonoSB', 7.6, ORA, 'c')
    txt(c, cx, cy - 4, 'PCA #1', 'Mono', 7, MUTE, 'c'); txt(c, cx, cy + 8, 'PCA #2', 'Mono', 7, MUTE, 'c')
    legs = [('FR', 1, -1, 'PCA #1', 0), ('MR', 1, 0, 'PCA #1', 3), ('RR', 1, 1, 'PCA #1', 6), ('FL', -1, -1, 'PCA #2', 0), ('ML', -1, 0, 'PCA #2', 3), ('RL', -1, 1, 'PCA #2', 6)]
    for n, sx, sy, board, ch in legs:
        ax, ay = cx + sx * 55, cy + sy * 70
        ang = math.radians(sy * 38)
        ex, ey = ax + sx * 70 * math.cos(ang), ay + 70 * math.sin(ang)
        wire(c, [(ax, ay), (ex, ey)], GREY, 7)
        lx = ex + sx * 8; anchor = 'l' if sx > 0 else 'r'
        txt(c, lx, ey - 18, n, 'Arch', 13, INK, anchor)
        txt(c, lx, ey - 2, board, 'MonoSB', 7.2, ORA, anchor)
        txt(c, lx, ey + 9, f'ch{ch} coxa · ch{ch + 1} femur · ch{ch + 2} tibia', 'Mono', 7, INK, anchor)
    txt(c, cx, cy + 150, 'Top view. Right legs: PCA #1 (front board). Left legs: PCA #2 (rear board).', 'Sans', 8.5, MUTE, 'c')
    plug(c, 140, cy + 180)


# ---------------- Pi wiring ----------------

def pi_wiring(c, x0=40, t0=330, compact=False):
    txt(c, x0, t0, 'PI → BOTH PCA BOARDS  ·  4 female-female jumpers per board', 'MonoSB', 7.6, ORA)
    t = t0 + 18
    c.setFillColor(Color(.90, .95, .91)); c.setStrokeColor(INK); c.setLineWidth(.9); c.roundRect(x0, Y(t + 190), 120, 190, 4, stroke=1, fill=1)
    txt(c, x0 + 8, t + 6, 'Raspberry Pi 4', 'SansB', 9, INK)
    rows = [(1, '3.3V', PLUS, 0, 'VCC'), (3, 'SDA', MUTE, 0, 'SDA'), (5, 'SCL', MUTE, 0, 'SCL'), (14, 'GND', INK, 0, 'GND'),
            (17, '3.3V', PLUS, 1, 'VCC'), (7, 'GPIO4 · SDA3', MUTE, 1, 'SDA'), (29, 'GPIO5 · SCL3', MUTE, 1, 'SCL'), (20, 'GND', INK, 1, 'GND')]
    pcas = [pca_board(c, x0 + 250, t - 4, 196, 86, 'PCA #1 · bus 1 · right legs'), pca_board(c, x0 + 250, t + 102, 196, 86, 'PCA #2 · bus 3 · left legs')]
    for i, (pin, lab, col, b, to) in enumerate(rows):
        yy = t + 24 + i * 15 + (10 if b else 0)
        txt(c, x0 + 114, yy - 3.4, f'pin {pin}  {lab}', 'Mono', 6.6, INK, 'r')
        c.setFillColor(INK); c.circle(x0 + 118, Y(yy), 1.8, stroke=0, fill=1)
        px, pt = pcas[b][to]
        xx = x0 + 150 + (i % 4) * 16 + b * 6
        wire(c, [(x0 + 120, yy), (xx, yy), (xx, pt), (px, pt)], col, 1.4, (3, 2) if to == 'SCL' else None)
    txt(c, x0, t + 204, 'Buck OUT + → pins 2 and 4.  Buck OUT − → pins 6 and 9.  Camera ribbon: blue tab toward the USB ports.', 'Sans', 8, MUTE)


# ---------------- leg home pose ----------------

def leg_pose(c):
    """Side view of one leg at home, with + directions. Local box ~300 x 230."""
    c.setFillColor(Color(.90, .90, .91)); c.setStrokeColor(INK); c.setLineWidth(.9); c.rect(0, Y(72), 56, 34, stroke=1, fill=1)
    txt(c, 28, 52, 'body', 'Mono', 7, MUTE, 'c')
    hip, k1, k2, ft = (56, 55), (96, 55), (196, 55), (196, 190)
    wire(c, [hip, k1], Color(.5, .5, .52), 8); wire(c, [k1, k2], INK, 8); wire(c, [k2, ft], INK, 8)
    for p in (k1, k2): c.setFillColor(ORA); c.circle(p[0], Y(p[1]), 5.5, stroke=0, fill=1)
    txt(c, 76, 38, 'coxa', 'Mono', 7, MUTE, 'c')
    txt(c, 146, 66, 'femur: LEVEL', 'MonoSB', 7.4, INK, 'c')
    txt(c, 206, 116, 'tibia:', 'Mono', 7.4, MUTE); txt(c, 206, 127, 'STRAIGHT DOWN', 'MonoSB', 7.4, INK)
    c.setStrokeColor(RULE); c.setLineWidth(1); c.line(0, Y(196), 300, Y(196))
    txt(c, 206, 182, 'grip-tape foot', 'Mono', 6.8, MUTE)

    def arc(cx, cy, r, a0, a1):
        c.setStrokeColor(ORA); c.setLineWidth(1.3); p = c.beginPath()
        for i in range(17):
            a = math.radians(a0 + (a1 - a0) * i / 16); X, T = cx + r * math.cos(a), cy - r * math.sin(a)
            (p.moveTo if i == 0 else p.lineTo)(X, Y(T))
        c.drawPath(p, stroke=1, fill=0)
        a = math.radians(a1); c.setFillColor(ORA); c.circle(cx + r * math.cos(a), Y(cy - r * math.sin(a)), 2.8, stroke=0, fill=1)
    arc(k1[0], k1[1], 36, 8, 50); txt(c, 122, 2, 'femur +  knee lifts', 'Sans', 8, ORA)
    arc(k2[0], k2[1], 96, -86, -112); txt(c, 70, 150, 'tibia +  foot swings in', 'Sans', 8, ORA)
    txt(c, 0, 210, 'coxa +  leg swings counter-clockwise, seen from above', 'Sans', 8, ORA)


# ---------------- joint section ----------------

def joint_section(c, x0, top0):
    def Rr(x, t, w, h, fill, stroke=None):
        c.setFillColor(fill); c.setStrokeColor(stroke or fill); c.setLineWidth(.6); c.rect(x0 + x, H - top0 - t - h, w, h, stroke=1 if stroke else 0, fill=1)
    cx = 110
    Rr(cx - 46, 0, 92, 9, GREY)
    Rr(cx - 22, 7, 44, 3, SILVER, INK); Rr(cx - 6, 10, 12, 8, SILVER, INK)
    Rr(cx - 60, 18, 120, 82, DARK)
    Rr(cx - 64, 96, 128, 14, ORA)
    Rr(cx - 11, 104, 22, 6, SILVER, INK)
    Rr(cx - 74, -2, 28, 11, GREY); Rr(cx - 74, -2, 12, 132, GREY); Rr(cx - 74, 120, 148, 12, GREY); Rr(cx - 4, 116, 8, 4, GREY)
    Rr(cx - 2.5, 104, 5, 26, RED); Rr(cx - 5.5, 130, 11, 5, RED)
    lab = [(4, -6, 'Bracket B'), (9, 6, 'Ø20 alu horn (disc in B\'s pocket)'), (55, 40, 'Servo'), (100, 76, 'Servo cap (+2)'),
           (107, 92, '623ZZ bearing, flush'), (126, 108, 'Bracket A (the L), its foot'), (132, 124, 'Axle M3×10 · tip in bearing')]
    for t, ly, s in lab:
        c.setStrokeColor(RULE); c.setLineWidth(.5); c.line(x0 + cx + 66, H - top0 - t - 3, x0 + cx + 86, H - top0 - ly - 3)
        txt(c, x0 + cx + 89, top0 + ly - 1, s, 'Sans', 7.6, INK)
