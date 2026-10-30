"""Offline preview of the intro overlay: black bar + shaped Arabic (Amiri) over the traced English strips; checks windows cover every English frame."""
import json, glob, os, re
import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont
import numpy as np
R = "../translation/"
ar = json.load(open(R + "arabic/ar.json", encoding="utf-8"))
subs = [l.rstrip("\n").split("\t") for l in open(R + "arabic/intro_subs.tsv", encoding="utf-8") if not l.startswith("#")]
subs = [(float(a), float(b), en) for a, b, en in subs]
H = 1080; BAR = int(H * 0.128); FS = int(H * 0.034 * 1.15)
font = ImageFont.truetype("../fonts/arabic/Amiri-Regular.ttf", FS)
rs = arabic_reshaper.ArabicReshaper(configuration={"delete_harakat": True})
def render(t):
    return get_display(rs.reshape(t), base_dir="R")
# 1) every frame with English text must fall inside a window
bad = []
for f in sorted(glob.glob(R + "work/introsubs/[0-9]*.png")):
    t = int(os.path.basename(f)[:-4]) / 100
    if t > 156 or t < 40: continue
    a = np.array(Image.open(f))
    if (a > 90).sum() > 150 and not any(s <= t <= e for s, e, _ in subs): bad.append(t)
print("uncovered English frames:", bad[:20], len(bad))
# 2) overlay sheet
rows = []
for s, e, en in subs:
    im = Image.new("L", (1920, BAR), 0); d = ImageDraw.Draw(im)
    txt = render(ar[en]); w = d.textlength(txt, font=font)
    d.text(((1920 - w) / 2, (BAR - FS) / 2 - 8), txt, font=font, fill=230)
    missing = [c for c in set(txt) if font.getmask(c).getbbox() is None and not c.isspace()]
    rows.append((s, e, im, w, missing))
    print(f"{s:6.1f}-{e:6.1f} width={w:.0f}/1536 {'TOO WIDE' if w > 1536 else ''} missing={missing}")
sheet = Image.new("L", (1920, BAR * 10), 0)
for i, (_, _, im, _, _) in enumerate(rows[:10]): sheet.paste(im, (0, i * BAR))
sheet.save(R + "work/intro_preview_0.png")
sheet = Image.new("L", (1920, BAR * 10), 0)
for i, (_, _, im, _, _) in enumerate(rows[10:]): sheet.paste(im, (0, i * BAR))
sheet.save(R + "work/intro_preview_1.png")
