"""Open pause -> settings -> controls (retries ESC until the pause overlay is dark)."""
import subprocess, sys, time
from PIL import Image
import statistics
def g(*a): return subprocess.run([sys.executable, "-I", "gamectl.py", *a], capture_output=True, text=True)
for _ in range(3):
    g("keys", "ESC"); time.sleep(1.5); g("cmd", "shot nav"); 
    im = Image.open(r"..\runtime_test\BepInEx\bpar\nav.png").convert("L").resize((48, 27))
    if statistics.mean(im.tobytes()) < 25: break
g("click", "1520", "652"); time.sleep(2); g("click", "1560", "610"); time.sleep(2); g("cmd", "scan", "shot nav2")
print("done")
