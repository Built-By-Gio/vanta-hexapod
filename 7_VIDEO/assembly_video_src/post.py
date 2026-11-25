"""Compositor: Blender frame (transparent PNG) -> halftone ink on paper + poster overlays (after the 'The Vine Has Called' template).
python post.py all | frames f1 f2 ... | seg <id>"""
import os, sys, json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = r"."
FR, OUT, FONTS = S + r"\frames", S + r"\out", S + r"\fonts"
TL = json.load(open(S + r"\timeline.json"))
W, H, FPS = TL["W"], TL["H"], TL["fps"]
PAPER, INK, RED, MUTE = (236, 230, 216), (26, 24, 21), (200, 52, 32), (120, 112, 100)
CELL = 4
_fc = {}


def font(kind, size):
    k = (kind, size)
    if k in _fc: return _fc[k]
    if kind == "display": f = ImageFont.truetype(FONTS + r"\PlayfairVar.ttf", size); f.set_variation_by_axes([900])
    elif kind == "display_i": f = ImageFont.truetype(FONTS + r"\PlayfairItalicVar.ttf", size); f.set_variation_by_axes([700])
    elif kind == "serif_b": f = ImageFont.truetype(FONTS + r"\OldStandard-Bold.ttf", size)
    elif kind == "serif_i": f = ImageFont.truetype(FONTS + r"\OldStandard-Italic.ttf", size)
    elif kind == "serif": f = ImageFont.truetype(FONTS + r"\OldStandard-Regular.ttf", size)
    elif kind == "mono_b": f = ImageFont.truetype(FONTS + r"\SpaceMono-Bold.ttf", size)
    elif kind == "mono": f = ImageFont.truetype(FONTS + r"\SpaceMono-Regular.ttf", size)
    elif kind == "anton": f = ImageFont.truetype(FONTS + r"\Anton-Regular.ttf", size)
    _fc[k] = f; return f


def wrap(d, text, f, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= width: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines


# ---------- static layers ----------
rng = np.random.default_rng(7)
GRAIN = np.clip(np.array(PAPER, np.float32)[None, None] + rng.normal(0, 4.5, (H, W, 1)) + rng.normal(0, 1.5, (H, W, 3)), 0, 255).astype(np.uint8)
yy, xx = np.mgrid[0:H, 0:W]
DIST = np.sqrt(((yy % CELL) - (CELL - 1) / 2) ** 2 + ((xx % CELL) - (CELL - 1) / 2) ** 2).astype(np.float32)
del yy, xx


def dotted_panel(d, box, alpha=90, pitch=6, r=1.1, border=True, red_bar=None):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=PAPER)
    layer = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
    for y in range(3, y1 - y0, pitch):
        for x in range(3, x1 - x0, pitch): ld.ellipse((x - r, y - r, x + r, y + r), fill=INK + (alpha,))
    d._image.alpha_composite(layer, (x0, y0))
    if border: d.rectangle(box, outline=INK, width=1)
    if red_bar: d.rectangle(red_bar, fill=RED)


def ornaments(d):
    for i in range(3): d.ellipse((1696, 296 + i * 18, 1704, 304 + i * 18), fill=INK)
    for i in range(3): d.ellipse((26, 716 + i * 18, 34, 724 + i * 18), fill=INK)
    for i in range(2):
        for j in range(2):
            if (i + j) % 2 == 0: d.rectangle((1846 + i * 11, 876 + j * 11, 1856 + i * 11, 886 + j * 11), fill=INK)
    d.rectangle((1886, 60, 1892, 66), fill=RED)


def halftone(canvas, png, ghost=False):
    """ink the render onto the canvas (numpy, in place)."""
    if not os.path.exists(png): return
    im = Image.open(png).convert("RGBA")
    if im.size != (W, H): im = im.resize((W, H))
    a = np.asarray(im).astype(np.float32) / 255
    alpha = a[..., 3]; r, g, b = a[..., 0], a[..., 1], a[..., 2]
    lum = 0.3 * r + 0.59 * g + 0.11 * b
    red = (r > 1.6 * g + 0.04) & (r > 0.11) & (alpha > 0.4)
    lum = np.where(red, r * 0.95, lum)
    dark = np.clip((1 - lum - 0.06) / 0.78, 0, 1) ** 1.1 * alpha
    if ghost: dark *= 0.32
    D = dark.reshape(H // CELL, CELL, W // CELL, CELL).mean(axis=(1, 3))
    R = np.repeat(np.repeat(CELL * 0.62 * np.sqrt(D), CELL, 0), CELL, 1)
    dots = (DIST < R) & (alpha > 0.1)
    lines = (lum < 0.14) & (alpha > 0.5) & ~red
    if ghost: lines &= (lum < 0.06)
    ink = dots | lines
    redm = red
    # light red tint under red parts (duotone block), then dots in red
    tint = redm & ~ink
    canvas[tint] = (canvas[tint] * 0.62 + np.array(RED, np.float32) * 0.38).astype(np.uint8)
    canvas[ink & ~redm] = INK
    canvas[ink & redm] = (170, 34, 20)


# ---------- overlay pieces ----------
def headline(d, title, sub, lt, big=False):
    f = font("display", 196 if big else 86); x = 1860
    t1, t2 = title
    prog = min(1.0, max(0.0, lt / 0.55)) if lt is not None else 1.0
    y = 22 if big else 30
    halo = dict(stroke_width=7, stroke_fill=PAPER)
    if big:
        n = max(0, int(round(prog * len(t1)))); txt = t1[:n]
        d.text((x, y), txt, font=f, fill=INK, anchor="ra", stroke_width=10, stroke_fill=PAPER)
        if prog >= 1: d.rectangle((x - d.textlength(t1, font=f), y + 215, x, y + 226), fill=RED)
        ysub = y + 240
    else:
        d.text((x, y), t1, font=f, fill=INK, anchor="ra", **halo); d.text((x, y + 96), t2, font=f, fill=INK, anchor="ra", **halo); ysub = y + 210
    if sub and (lt is None or lt > 0.5): d.text((x, ysub), sub, font=font("display_i", 27), fill=INK, anchor="ra", stroke_width=4, stroke_fill=PAPER)


def tag(d, text):
    f = font("anton", 26); d.text((60, 44), text, font=f, fill=INK)
    w = d.textlength(text, font=f); d.rectangle((60 + w + 14, 50, 60 + w + 46, 66), outline=INK, width=1)


def panel_list(d, label, items, y0, fnt_size=20, width=440):
    """dotted GRAB panel; returns bottom y"""
    fb, fi = font("mono_b", 15), font("serif", fnt_size)
    lines = []
    for it in items: lines += [(j == 0, l) for j, l in enumerate(wrap(d, it, fi, width - 44))]
    h = 40 + len(lines) * (fnt_size + 6) + 12
    dotted_panel(d, (60, y0, 60 + width, y0 + h), alpha=55, red_bar=(60, y0, 60 + width, y0 + 5))
    d.text((76, y0 + 16), label, font=fb, fill=RED)
    y = y0 + 40
    for first, l in lines:
        d.text((76 if first else 92, y), ("• " if first else "") + l, font=fi, fill=INK); y += fnt_size + 6
    return y0 + h


def callout_full(d, num, lead, body, y0, width=440, leader_to=None, number=True):
    fb, fr = font("serif_b", 23), font("serif", 20)
    lines = wrap(d, body, fr, width - 32)
    h = 16 + 30 + len(lines) * 25 + 14
    box = (60, y0, 60 + width, y0 + h)
    d.rectangle(box, fill=PAPER, outline=INK, width=2)
    d.rectangle((60, y0 - 9, 60 + 110, y0 - 1), fill=RED)
    if number: d.text((76, y0 + 14), f"{num:02d}", font=font("mono_b", 15), fill=RED)
    d.text((76 + (36 if number else 0), y0 + 10), lead, font=fb, fill=INK)
    y = y0 + 46
    for l in lines: d.text((76, y), l, font=fr, fill=INK); y += 25
    if leader_to:
        ax, ay = leader_to; bx, by = 60 + width, y0 + h // 2
        d.line((bx, by, bx + 28, by), fill=INK, width=2)
        d.line((bx + 28, by, bx + 28, ay), fill=INK, width=2)
        d.line((bx + 28, ay, ax, ay), fill=INK, width=2)
        d.ellipse((ax - 7, ay - 7, ax + 7, ay + 7), fill=RED, outline=INK, width=2)
    return y0 + h


def callout_done(d, num, lead, y0, width=440):
    f = font("serif", 19); d.rectangle((60, y0, 60 + width, y0 + 28), fill=PAPER, outline=INK, width=1)
    d.text((72, y0 + 4), f"{num:02d}", font=font("mono_b", 13), fill=RED); d.text((104, y0 + 3), lead, font=f, fill=INK)
    d.rectangle((60 + width - 22, y0 + 10, 60 + width - 12, y0 + 18), fill=INK)
    return y0 + 34


def numeral(d, text, cap, badge=""):
    f = font("display", 150); d.text((54, 690), text, font=f, fill=INK)
    w = d.textlength(text, font=f)
    if badge: d.text((54 + w + 16, 735), badge, font=font("mono_b", 30), fill=RED)
    d.polygon([(66, 858), (78, 858), (72, 870)], fill=RED); d.ellipse((66, 848, 78, 860), fill=RED)
    d.text((90, 846), cap, font=font("anton", 22), fill=INK)


def red_word(d, word):
    size = 160
    while d.textlength(word, font=font("display", size)) > 560 and size > 60: size -= 8
    d.text((1860, 1046), word, font=font("display", size), fill=RED, anchor="rs", stroke_width=5, stroke_fill=PAPER)


def vertical(d, text):
    f = font("serif", 20); w = int(d.textlength(text, font=f)) + 10
    im = Image.new("RGBA", (w, 30), (0, 0, 0, 0)); ImageDraw.Draw(im).text((4, 2), text, font=f, fill=INK, stroke_width=3, stroke_fill=PAPER)
    im = im.rotate(-90, expand=True); d._image.alpha_composite(im, (1868, 330))
    d.line((1876, 300, 1876, 322), fill=INK, width=1); d.line((1876, 338 + w, 1876, 360 + w), fill=INK, width=1)


def quote(d, lines, attrib, y0=900, width=600):
    fi, fr = font("serif_i", 21), font("serif", 17)
    y = y0
    for text in lines:
        for l in wrap(d, "\u201c" + text + "\u201d", fi, width): d.text((60, y), l, font=fi, fill=INK); y += 26
        y += 4
    d.text((60, y + 2), attrib, font=fr, fill=MUTE)


def credit(d):
    d.text((1120, 1012), "MADE BY GIO", font=font("mono_b", 15), fill=INK, stroke_width=3, stroke_fill=PAPER)
    d.text((1120, 1032), "VANTA v6 · 2026", font=font("mono", 13), fill=MUTE, stroke_width=3, stroke_fill=PAPER)


# ---------- per-frame ----------
def seg_at(f):
    for s in TL["segments"]:
        if s["f0"] <= f <= s["f1"]: return s
    return TL["segments"][-1]


def compose(f):
    seg = seg_at(f); lt = (f - seg["f0"]) / FPS + seg.get("t_offset", 0); kind = seg["kind"]
    canvas = GRAIN.copy()
    img = Image.fromarray(canvas).convert("RGBA"); d = ImageDraw.Draw(img)
    if kind == "step": dotted_panel(d, (1240, 120, 1620, 560), alpha=38, border=True)
    canvas = np.array(img)[..., :3].copy()
    halftone(canvas, FR + rf"\f_{f:05d}.png", ghost=seg.get("ghost", False))
    img = Image.fromarray(canvas).convert("RGBA"); d = ImageDraw.Draw(img); d._image = img
    ornaments(d); vertical(d, "VANTA · 18-DOF HEXAPOD · ASSEMBLY GUIDE v6 · MADE BY GIO"); credit(d)
    if kind == "title" and seg["id"] == "explode":
        seg = TL["segments"][0]
    if kind == "title":
        tag(d, seg["tag"]); headline(d, seg["title"], seg["sub"], lt, big=True)
        if lt > 0.6: panel_list(d, seg["grab_label"], seg["grab"], 300)
        if lt > 0.3: numeral(d, seg["numeral"], seg["numeral_cap"])
        if lt > 0.9: red_word(d, seg["red"])
        if lt > 1.2: quote(d, seg["check"], "— credits", y0=930)
    elif kind == "card":
        tag(d, seg["tag"]); headline(d, seg["title"], seg["sub"], lt)
        numeral(d, seg["numeral"], seg["numeral_cap"]); red_word(d, seg["red"])
        if seg["id"] == "rules":
            y = panel_list(d, seg["grab_label"], seg["grab"], 110, fnt_size=19) + 22
            for j, (lead, body) in enumerate(seg["do"]):
                if lt > 1.0 + 1.6 * j: y = callout_full(d, j + 1, lead, body, y + 10)
            if lt > 6.5: quote(d, seg["check"], "— tools", y0=930, width=640)
        else:
            fb, fq = font("serif", 21), font("mono_b", 15)
            dotted_panel(d, (60, 110, 560, 660), alpha=45, red_bar=(60, 110, 560, 115))
            d.text((76, 126), "MAIN FILE · BLACK PLA · 15 PLATES", font=fq, fill=RED)
            for j, (q, name) in enumerate(seg["parts"]):
                if lt < 0.8 + 0.3 * j: break
                col, row = divmod(j, 8); x, y = 76 + col * 250, 160 + row * 60
                d.text((x, y), q, font=fq, fill=RED); d.text((x, y + 20), name, font=fb, fill=INK)
            if lt > 6.0: quote(d, seg["check"], "— hardware", y0=930, width=640)
    else:   # step
        tag(d, seg["tag"] + (f"  {seg['badge']}" if seg["badge"] else ""))
        headline(d, seg["title"], f"— step {seg['n']} of 18 · {seg['blurb']}" if len(seg["blurb"]) < 70 else f"— step {seg['n']} of 18", lt)
        if lt > 0.5 and len(seg["blurb"]) >= 70:
            fi = font("display_i", 22)
            for j, l in enumerate(wrap(d, seg["blurb"], fi, 760)): d.text((1860, 272 + j * 28), l, font=fi, fill=INK, anchor="ra", stroke_width=4, stroke_fill=PAPER)
        y = 300
        if lt > 0.5: y = panel_list(d, "GRAB", seg["grab"], 110, fnt_size=19)
        y = max(y + 24, 300)
        j_act = int((lt - 2.4) // 2.4) if lt >= 2.4 else -1
        j_act = min(j_act, len(seg["do"]) - 1)
        for j in range(j_act): y = callout_done(d, j + 1, seg["do"][j][0], y)
        if j_act >= 0:
            anchor = None
            row = seg["anchors"][min(f - seg["f0"], len(seg["anchors"]) - 1)]
            if row and j_act < len(row) and row[j_act]: anchor = tuple(int(v) for v in row[j_act])
            lead, body = seg["do"][j_act]
            callout_full(d, j_act + 1, lead, body, y + 10, leader_to=anchor)
        if lt > 0.3: numeral(d, f"{seg['n']:02d}", seg["cat"] + (" · " + seg["badge"] if seg["badge"] else ""))
        if lt > 0.4: red_word(d, seg["cat"].split("-")[0] if len(seg["cat"]) > 8 else seg["cat"])
        if lt > seg["dur"] - 3.6: quote(d, seg["check"], f"— check, step {seg['n']}", y0=905, width=620)
    return img.convert("RGB")


def do_frame(f):
    p = OUT + rf"\o_{f:05d}.jpg"
    if os.path.exists(p): return
    compose(f).save(p, quality=93, subsampling=0)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode == "frames":
        for a in sys.argv[2:]:
            f = int(a); compose(f).save(S + rf"\test\o_{f:05d}.png"); print("ok", f)
    else:
        frames = [f for f in range(1, TL["total"] + 1) if os.path.exists(FR + rf"\f_{f:05d}.png")]
        if mode == "seg": frames = [f for f in frames if seg_at(f)["id"] == sys.argv[2]]
        from multiprocessing import Pool
        with Pool(10) as p:
            for i, _ in enumerate(p.imap_unordered(do_frame, frames, chunksize=8)):
                if i % 500 == 0: print(i, "/", len(frames), flush=True)
        print("done", len(frames))

