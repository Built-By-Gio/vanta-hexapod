"""VANTA guide v7: style + layout helpers. Monochrome, one orange accent, faint code texture."""
import io, json, os, random, re
import pypdf
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import Color
from reportlab.lib.utils import ImageReader

# paths relative to this folder (_dev/guide_v8), so it runs from the handoff layout on any machine
_HERE = os.path.dirname(os.path.abspath(__file__)) + '/'
_DEV = os.path.dirname(_HERE.rstrip('/\\')) + '/'
FD = _DEV + 'fonts/'
for n, f in [('Arch', 'Archivo-ExtraBold'), ('Sans', 'PlexSans'), ('SansB', 'PlexSans-Bold'), ('SansSB', 'PlexSans-SemiBold'),
             ('Mono', 'PlexMono'), ('MonoSB', 'PlexMono-SemiBold'), ('DJ', 'DejaVuSans')]:
    pdfmetrics.registerFont(TTFont(n, FD + f + '.ttf'))
G = _HERE; R = G + 'r/'; J = _DEV + 'joint_pages/'
BRAIN = _DEV + 'brain_src/'; SKETCH = _DEV + '../VANTA/5_ELECTRONICS_TEST/'
H, WPAGE = 612, 792
INK = Color(.075, .078, .086); MUTE = Color(.42, .43, .45); FAINT = Color(.80, .80, .81); GHOST = Color(.885, .885, .89)
ORA = Color(.80, .40, .06); W = Color(1, 1, 1); BLACK = Color(.035, .035, .04)
BOX = Color(.955, .955, .955); RULE = Color(.86, .86, .87); RED = Color(.72, .16, .12); PLUS = Color(.78, .18, .14)
SILVER = Color(.78, .79, .81); DARK = Color(.12, .12, .13); GREY = Color(.62, .63, .65)
FALLBACK = set('→✓≈≤≥')

# ---------- text ----------

def _runs(s, font):
    out, cur, curf = [], '', None
    for ch in s:
        f = 'DJ' if ch in FALLBACK else font
        if f != curf and cur: out.append((cur, curf)); cur = ''
        cur += ch; curf = f
    if cur: out.append((cur, curf))
    return out


def tw(s, font, size): return sum(pdfmetrics.stringWidth(t, f, size) for t, f in _runs(s, font))


def txt(c, x, top, s, font, size, col, anchor='l'):
    w = tw(s, font, size)
    if anchor == 'r': x -= w
    elif anchor == 'c': x -= w / 2
    y = H - top - size * 0.8; c.setFillColor(col)
    for t, f in _runs(s, font):
        c.setFont(f, size); c.drawString(x, y, t); x += pdfmetrics.stringWidth(t, f, size)
    return w


# rich text: **bold**  `mono`
BODY = {'n': 'Sans', 'b': 'SansSB', 'm': 'Mono'}


def _words(s):
    """list of words; each word = list of (text, style) segments. Breaks only at spaces."""
    words, cur = [], []
    for part in re.split(r'(\*\*[^*]+\*\*|`[^`]+`)', s):
        if not part: continue
        st = 'b' if part.startswith('**') else 'm' if part.startswith('`') else 'n'
        body = part[2:-2] if st == 'b' else part[1:-1] if st == 'm' else part
        pieces = body.split(' ')
        for i, p in enumerate(pieces):
            if i > 0:
                if cur: words.append(cur); cur = []
            if p: cur.append((p, st))
    if cur: words.append(cur)
    return words


def _sw(seg, size):
    t, st = seg; return tw(t, BODY[st], size * (0.93 if st == 'm' else 1))


def rwrap(s, size, width):
    lines, line, lw = [], [], 0
    sp = tw(' ', 'Sans', size)
    for w in _words(s):
        ww = sum(_sw(g, size) for g in w)
        if line and lw + sp + ww > width:
            lines.append(line); line, lw = [], 0
        if line: line.append((' ', 'n')); lw += sp
        line += w; lw += ww
    if line: lines.append(line)
    return lines


def rdraw(c, x, top, line, size, col=None):
    col = col or INK
    for w, st in line:
        f = BODY[st]; sz = size * (0.93 if st == 'm' else 1)
        txt(c, x, top + (0.4 if st == 'm' else 0), w, f, sz, col)
        x += tw(w, f, sz)


def para(c, x, top, s, size, width, lead=None, col=None):
    lead = lead or size * 1.36
    for l in rwrap(s, size, width): rdraw(c, x, top, l, size, col); top += lead
    return top


def wrap(s, font, size, width):
    out, line = [], ''
    for w in s.split(' '):
        t = (line + ' ' + w).strip()
        if tw(t, font, size) > width and line: out.append(line); line = w
        else: line = t
    return out + [line]


# ---------- page furniture ----------
_CODE = None


def code_lines():
    global _CODE
    if _CODE is None:
        src = [BRAIN + 'robot/servos.py', BRAIN + 'robot/kinematics.py',
               SKETCH + 'esp32s3/vanta_one_leg_s3/vanta_one_leg_s3.ino', BRAIN + 'tools/calibrate.py']
        _CODE = [l.rstrip() for f in src for l in open(f, encoding='utf-8').read().splitlines() if l.strip() and len(l.strip()) > 6]
    return _CODE


def margin_code(c, seed, dark=False):
    """Faint code running up the left edge: the texture from the reference image, kept quiet."""
    rnd = random.Random(seed); L = code_lines(); i = rnd.randrange(len(L))
    c.saveState(); c.translate(17, 36); c.rotate(90)
    col = Color(.17, .17, .18) if dark else GHOST
    x = 0
    while x < 540:
        s = L[i % len(L)].strip()[:90]; i += 1
        w = tw(s, 'Mono', 5.2)
        if x + w > 540: s = s[:max(0, int(len(s) * (540 - x) / w))]
        txt_raw(c, x, 0, s, 'Mono', 5.2, col); x += w + 14
    c.restoreState()


def txt_raw(c, x, y, s, font, size, col):
    c.setFillColor(col)
    for t, f in _runs(s, font): c.setFont(f, size); c.drawString(x, y, t); x += pdfmetrics.stringWidth(t, f, size)


TOTAL = [32]


def header(c, section, num, dark=False):
    fg = W if dark else INK; mu = Color(.55, .55, .57) if dark else MUTE
    txt(c, 36, 18.1, 'VANTA', 'Arch', 10, fg)
    txt(c, 82, 20.2, '// ' + section, 'Mono', 8, mu)
    txt(c, 756, 20.2, f'{num:02d} / {TOTAL[0] - 1:02d}', 'Mono', 8, mu, 'r')
    c.setStrokeColor(Color(.25, .25, .27) if dark else RULE); c.setLineWidth(.6); c.line(36, H - 32, 756, H - 32)
    margin_code(c, num, dark)


def new_page(section=None, num=None, dark=False):
    b = io.BytesIO(); c = canvas.Canvas(b, pagesize=(WPAGE, H))
    if dark: c.setFillColor(BLACK); c.rect(0, 0, WPAGE, H, stroke=0, fill=1)
    if section: header(c, section, num, dark)
    return b, c


def done(b, c):
    c.save(); b.seek(0); return pypdf.PdfReader(b).pages[0]


def edge_fade(im, px=90):
    """fade the sides where the picture is cut off at the frame"""
    import numpy as np
    a = np.asarray(im.split()[3], float); Hh, Ww = a.shape
    if a.max() == 0: return im
    ys, xs = np.where(a > 8)
    ramp = np.ones((Hh, Ww))
    g = np.linspace(0, 1, px)
    if xs.min() < 3: ramp[:, :px] *= g[None, :]
    if xs.max() > Ww - 4: ramp[:, Ww - px:] *= g[None, ::-1]
    if ys.min() < 3: ramp[:px, :] *= g[:, None]
    if ys.max() > Hh - 4: ramp[Hh - px:, :] *= g[::-1, None]
    out = im.copy(); out.putalpha(Image.fromarray((a * ramp).astype('uint8'))); return out


def image(c, path, x, top, w, h, pad=10, align='c', fade=False):
    im = Image.open(path).convert('RGBA')
    if fade: im = edge_fade(im)
    bb = im.split()[3].getbbox()
    if bb:
        crop = (max(bb[0] - pad, 0), max(bb[1] - pad, 0), min(bb[2] + pad, im.width), min(bb[3] + pad, im.height)); im = im.crop(crop)
    else: crop = (0, 0)
    iw, ih = im.size; s = min(w / iw, h / ih); dw, dh = iw * s, ih * s
    ox = x + (w - dw) / 2 if align == 'c' else x; oy = top + (h - dh) / 2
    c.drawImage(ImageReader(im), ox, H - oy - dh, dw, dh, mask='auto')
    return ox - crop[0] * s, oy - crop[1] * s, s, (ox, oy, dw, dh)


def box(c, x, top, w, label, lines, accent=None, size=9.4, bullet=True, bg=None):
    accent = accent or MUTE; bg = bg or BOX
    rows = []
    for l in lines:
        ls = rwrap(l, size, w - 30 if bullet else w - 22)
        rows += [(j == 0, t) for j, t in enumerate(ls)]
    lead = size * 1.36
    h = 25 + len(rows) * lead
    c.setFillColor(bg); c.rect(x, H - top - h, w, h, stroke=0, fill=1)
    c.setFillColor(accent); c.rect(x, H - top - h, 2.5, h, stroke=0, fill=1)
    txt(c, x + 11, top + 9, label, 'MonoSB', 7.6, accent)
    for i, (first, l) in enumerate(rows):
        yy = top + 23 + i * lead
        if bullet and first: txt(c, x + 11, yy, '–', 'Sans', size, MUTE)
        rdraw(c, x + (20 if bullet else 11), yy, l, size)
    return top + h


def box_h(w, lines, size=9.4, bullet=True):
    return 25 + sum(len(rwrap(l, size, w - 30 if bullet else w - 22)) for l in lines) * size * 1.36


def numbered(c, x, top, w, steps, size=10, gap=5.5, start=1):
    lead = size * 1.36
    for i, s in enumerate(steps):
        n = str(i + start)
        c.setFillColor(INK); c.circle(x + 7, H - top - 5.2, 7, stroke=0, fill=1)
        txt(c, x + 7, top + 1.2, n, 'SansB', 8.2, W, 'c')
        top = para(c, x + 21, top, s, size, w - 21, lead) + gap
    return top


def numbered_h(w, steps, size=10, gap=5.5):
    return sum(len(rwrap(s, size, w - 21)) * size * 1.36 + gap for s in steps)


def title_block(c, top, kicker, title, sub=None, x=36, w=720, size=26):
    txt(c, x, top, kicker, 'MonoSB', 8.5, ORA); top += 15
    for l in wrap(title, 'Arch', size, w): txt(c, x, top, l, 'Arch', size, INK); top += size * 1.08
    if sub: top = para(c, x, top + 4, sub, 10, w, col=MUTE) + 2
    return top


def table(c, x, top, cols, rows, size=8.9, head=True, col=None, rule=None, bold0=False, lead=None):
    """cols: [(header, width)], rows: list of tuples of rich strings"""
    col = col or INK; rule = rule or RULE; lead = lead or size * 1.33
    w = sum(cw for _, cw in cols)
    if head:
        xx = x
        for h, cw in cols: txt(c, xx, top, h.upper(), 'MonoSB', 7, MUTE); xx += cw
        top += 13
    c.setStrokeColor(rule); c.setLineWidth(.5)
    for r in rows:
        c.line(x, H - top + 2, x + w, H - top + 2)
        xx = x; hmax = 1
        for i, (cell, (h, cw)) in enumerate(zip(r, cols)):
            ls = rwrap(cell, size, cw - 8)
            for j, l in enumerate(ls):
                if bold0 and i == 0: l = [(t, 'b' if s == 'n' else s) for t, s in l]
                rdraw(c, xx, top + 5 + j * lead, l, size, col)
            hmax = max(hmax, len(ls)); xx += cw
        top += 9 + hmax * lead
    c.line(x, H - top + 2, x + w, H - top + 2)
    return top


# ---------- step page ----------
RX, RW = 512, 244


R8 = G + 'r8/'


def imgpath(img):
    if '/' in img: return img
    if img.startswith('8:'):
        f = R8 + img[2:] + '.png'
        return f if os.path.exists(f) else R8 + 'stub.png'
    return R + img + '.png'


def step_page(sec, num, step, title, sub, need, steps, check=None, careful=None, tip=None, img=None, draw=None, badge=None, kicker='STEP',
              progress=None, wires=None, plabel=None):
    for k in (1.0, .95, .9, .85, .8):
        b, c = new_page(sec, num)
        bottom = _step(c, step, title, sub, need, steps, check, careful, tip, img, draw, badge, kicker, k, progress, wires, plabel)
        if bottom < 590: return done(b, c)
    print('WARNING overflow', num, title); return done(b, c)


def progress_strip(c, top, progress, wires, plabel):
    """bottom-left: progress inset + legend, and the WIRES NOW box"""
    if progress:
        c.setFillColor(BOX); c.rect(36, H - top - 150, 176, 150, stroke=0, fill=1)
        pf = R8 + progress + '.png'
        image(c, pf if os.path.exists(pf) else R8 + 'stub.png', 38, top + 14, 172, 134, pad=2)
        txt(c, 42, top + 5, 'PROGRESS', 'MonoSB', 6.8, MUTE)
        if plabel: txt(c, 42, top + 139, plabel, 'Mono', 6.4, MUTE)
        lx = 36
        for col, s in ((ORA, 'this step'), (Color(.36, .37, .40), 'built'), (Color(.86, .86, .87), 'not yet')):
            c.setFillColor(col); c.rect(lx, H - top - 160, 7, 7, stroke=0, fill=1); txt(c, lx + 10, top + 152.5, s, 'Sans', 7.2, MUTE); lx += 16 + tw(s, 'Sans', 7.2) + 8
    if wires:
        box(c, 226, top, 268, 'WIRES NOW  ·  do this before the next step closes it in', wires, ORA, 8.6, bg=Color(.99, .95, .91))


def _step(c, step, title, sub, need, steps, check, careful, tip, img, draw, badge, kicker, k, progress=None, wires=None, plabel=None):
    strip = bool(progress or wires)
    if img: image(c, imgpath(img), 36, 52, 458, 360 if strip else 520, fade=img.startswith('8:'))
    if draw: draw(c)
    if strip: progress_strip(c, 428, progress, wires, plabel)
    txt(c, RX, 50, kicker, 'MonoSB', 8.5, ORA)
    sw = txt(c, RX - 2, 62, str(step), 'Arch', 46, INK)
    if badge:
        bx = RX + sw + 10; bw = tw(badge, 'MonoSB', 10) + 18
        c.setStrokeColor(INK); c.setLineWidth(1); c.roundRect(bx, H - 100, bw, 21, 10.5, stroke=1, fill=0)
        txt(c, bx + 9, 84.8, badge, 'MonoSB', 10, INK)
    y = 116
    for l in wrap(title, 'Arch', 18 * min(1, k + .05), RW): txt(c, RX, y, l, 'Arch', 18 * min(1, k + .05), INK); y += 19.5 * min(1, k + .05)
    if sub: y = para(c, RX, y + 3, sub, 9.2 * k, RW, col=MUTE)
    y += 8
    if need: y = box(c, RX, y, RW, 'YOU NEED', need, MUTE, 8.8 * k) + 12
    txt(c, RX, y, 'DO THIS', 'MonoSB', 7.6, ORA); y += 14
    y = numbered(c, RX, y, RW, steps, 9.6 * k, 5 * k) + 4
    if tip: y = box(c, RX, y, RW, 'TIP', tip, MUTE, 8.8 * k) + 8
    if careful: y = box(c, RX, y, RW, 'CAREFUL', careful, ORA, 8.8 * k, bg=Color(.99, .95, .91)) + 8
    if check: y = box(c, RX, y, RW, 'CHECK  ✓', check, INK, 8.8 * k)
    return y
