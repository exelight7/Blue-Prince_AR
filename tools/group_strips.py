"""Group traced subtitle strips (translation/work/introsubs/NNNNN.png, name = video time x100) into subtitle segments.
Writes translation/work/introsubs_segments.json and a contact sheet per ~12 segments (sheet_N.png) for reading the English text."""
import os, glob, json
from PIL import Image, ImageDraw
import numpy as np
D = "../translation/work/introsubs"
files = sorted(glob.glob(D + "/[0-9]*.png"))
frames = []
for f in files:
    t = int(os.path.basename(f)[:-4]) / 100.0
    a = np.array(Image.open(f))
    m = a > 90
    ys, xs = np.where(m)
    frames.append((t, a, m, (xs.min(), ys.min(), xs.max(), ys.max()) if m.sum() > 150 else None))
segs = []
cur = None
for t, a, m, bb in frames:
    if bb is None:
        if cur: cur["end"] = t; segs.append(cur); cur = None
        continue
    if cur is not None:
        pm = cur["mask"]; inter = (pm & m).sum(); uni = (pm | m).sum()
        if uni and inter / uni > 0.55:
            cur["end"] = t
            if m.sum() > pm.sum(): cur["mask"] = m; cur["img"] = a; cur["bb"] = bb  # keep the fullest frame
            continue
        cur["end"] = t; segs.append(cur)
    cur = {"start": t, "end": t, "mask": m, "img": a, "bb": bb}
if cur: segs.append(cur)
out = []
for i, s in enumerate(segs):
    out.append({"i": i, "start": s["start"], "end": round(s["end"] + 0.25, 2), "bb": [int(x) for x in s["bb"]]})
json.dump(out, open("../translation/work/introsubs_segments.json", "w"), indent=0)
print(len(segs), "segments")
# contact sheets
PER = 10
for n in range(0, len(segs), PER):
    chunk = segs[n:n + PER]
    W = 1920; H = 60 * len(chunk)
    sheet = Image.new("L", (W, H), 0); dr = ImageDraw.Draw(sheet)
    for k, s in enumerate(chunk):
        x0, y0, x1, y1 = s["bb"]
        crop = Image.fromarray(s["img"]).crop((max(0, x0 - 10), max(0, y0 - 6), min(1920, x1 + 10), y1 + 6))
        sheet.paste(crop, (150, k * 60))
        dr.text((5, k * 60 + 20), f'#{n + k} {s["start"]:.1f}-{s["end"]:.1f}', fill=255)
    sheet.save(f"{D}/../introsubs_sheet_{n // PER}.png")
