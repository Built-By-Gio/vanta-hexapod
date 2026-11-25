"""Reuse the bench wiring diagram (v4 guide, step 4 page) as the picture for the v6 'reset servos to zero' step."""
import pypdfium2 as p
D = "./_dev/"
s = 3.0
im = p.PdfDocument(D + "legacy/v4_final_guide.pdf")[7].render(scale=s).to_pil()
im.crop((int(95 * s), int(118 * s), int(700 * s), int(352 * s))).save(D + "man6/r5/s04.png")
print("ok", flush=True)
