"""Watch bpar/trace/*.png (screenshots named by video time x100), keep only the bottom subtitle strip, delete the full frame.
usage: trace_strips.py [seconds_to_run]"""
import os, sys, time, glob
from PIL import Image
SRC = "../runtime_test/BepInEx/bpar/trace"
DST = "../translation/work/introsubs"
os.makedirs(DST, exist_ok=True)
end = time.time() + (float(sys.argv[1]) if len(sys.argv) > 1 else 300)
done = set()
while time.time() < end:
    for f in sorted(glob.glob(SRC + "/*.png")):
        if f in done or time.time() - os.path.getmtime(f) < 1.0: continue
        try:
            im = Image.open(f); im.load()
            h = im.size[1]
            im.crop((0, int(h * 0.872), im.size[0], h)).convert("L").save(os.path.join(DST, os.path.basename(f)))
            im.close(); os.remove(f); done.add(f)
        except Exception as e:
            pass
    time.sleep(1)
print("stopped; strips:", len(os.listdir(DST)))
