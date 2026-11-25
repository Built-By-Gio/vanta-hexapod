"""Code-glyph rendering of a transparent PNG: the object is drawn with lines of real VANTA source code on black,
brightness from the render, with a few horizontal scan streaks. glyph(in, out, width_px)"""
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

import os

_DEV = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
FONT = _DEV + 'fonts/PlexMono.ttf'
SRC = [_DEV + 'brain_src/robot/servos.py', _DEV + 'brain_src/tools/calibrate.py',
       _DEV + '../VANTA/5_ELECTRONICS_TEST/arduino_uno/vanta_one_leg/vanta_one_leg.ino']


def code_stream():
    s = []
    for f in SRC:
        for l in open(f, encoding='utf-8').read().splitlines():
            l = l.strip()
            if l: s.append(l)
    return '   '.join(s)


def glyph(src, out, W=3000, fs=11, seed=4, bg=(9, 9, 10), gamma=0.9, base=0.22):
    random.seed(seed)
    im = Image.open(src).convert('RGBA')
    im = im.resize((W, int(im.height * W / im.width)), Image.LANCZOS)
    a = np.asarray(im.split()[3], float) / 255
    g = np.asarray(im.convert('L'), float) / 255
    # local contrast so dark PLA still reads: normalise inside the silhouette, then edge boost
    m = a > 0.5
    lo, hi = np.percentile(g[m], 2), np.percentile(g[m], 98)
    v = np.clip((g - lo) / (hi - lo + 1e-6), 0, 1) ** gamma
    edge = np.asarray(Image.fromarray((a * 255).astype('uint8')).filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(2)), float) / 255
    v = np.clip(0.06 + 0.94 * v ** 1.1 + edge * 0.7, 0, 1) * a
    font = ImageFont.truetype(FONT, fs)
    cw = font.getlength('M'); ch = int(fs * 1.18)
    stream = code_stream(); p = 0
    out_im = Image.new('RGB', im.size, bg)
    # faint shading underneath so the form holds together
    shade = (9 + np.stack([v] * 3, -1) * 255 * base).clip(0, 255).astype('uint8')
    out_im.paste(Image.fromarray(shade))
    d = ImageDraw.Draw(out_im)
    rows = im.height // ch
    for r in range(rows):
        y = r * ch
        band = v[y:y + ch]
        x = 0
        cols = int(W // cw)
        line = []
        for k in range(cols):
            x0 = int(k * cw); val = band[:, x0:int(x0 + cw)].mean() if x0 < W else 0
            line.append(val)
        # scan streak: a few rows get a smeared run of '-' where the object is bright
        streak = random.random() < 0.06
        for k, val in enumerate(line):
            if val < 0.10: continue
            c = stream[p % len(stream)]; p += 1
            if streak and val > 0.45 and random.random() < 0.8: c = random.choice('-—=_')
            if c == ' ' and val > 0.6: c = '.'
            lv = int(255 * min(1, 0.25 + val * 1.2))
            d.text((k * cw, y), c, font=font, fill=(lv, lv, lv))
    out_im.save(out)
    return out


def code_column(W, H, fs=10, seed=1, col=(150, 150, 150), bg=(0, 0, 0), width_chars=46):
    """A ragged column of code lines, like the left edge of the reference image."""
    random.seed(seed)
    font = ImageFont.truetype(FONT, fs); ch = int(fs * 1.25)
    lines = [l for f in SRC for l in open(f, encoding='utf-8').read().splitlines()]
    im = Image.new('RGB', (W, H), bg); d = ImageDraw.Draw(im)
    i = random.randrange(len(lines))
    for y in range(0, H, ch):
        l = lines[i % len(lines)].strip()[:width_chars]; i += 1
        if not l: continue
        f = 0.35 + 0.65 * random.random()
        d.text((0, y), l, font=font, fill=tuple(int(c * f) for c in col))
    return im


if __name__ == '__main__':
    import sys
    glyph(sys.argv[1], sys.argv[2])
