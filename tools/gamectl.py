"""Drive the runtime_test copy: launch/kill, plugin commands (BepInEx/bpar/cmd.txt) and key presses.

python gamectl.py launch | kill | cmd "shot a" "set NAME|text" ... | keys ENTER DOWN ... | log [n]
"""
import ctypes, os, subprocess, sys, time
from ctypes import wintypes

ROOT = r"D:\Games\Blue Prince_AR\runtime_test"
BPAR = os.path.join(ROOT, "BepInEx", "bpar")
CMD = os.path.join(BPAR, "cmd.txt")
user32 = ctypes.windll.user32

VK = {"ENTER": 0x0D, "ESC": 0x1B, "UP": 0x26, "DOWN": 0x28, "LEFT": 0x25, "RIGHT": 0x27, "SPACE": 0x20, "TAB": 0x09,
      "E": 0x45, "W": 0x57, "A": 0x41, "S": 0x53, "D": 0x44, "F10": 0x79, "F11": 0x7A, "F12": 0x7B}
for c in "0123456789":
    VK[c] = ord(c)


def launch():
    subprocess.Popen([os.path.join(ROOT, "BLUE PRINCE.exe")], cwd=ROOT)


def kill():
    # only the runtime_test copy: the user's real game may be running under the same image name
    ps = "Get-CimInstance Win32_Process -Filter \"Name='BLUE PRINCE.exe'\" | Where-Object { $_.ExecutablePath -like '*runtime_test*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True)


def focus():
    hwnd = user32.FindWindowW(None, "BLUE PRINCE")
    if not hwnd:
        raise SystemExit("game window not found")
    user32.ShowWindow(hwnd, 9)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.3)


def press(name, hold=0.3):
    vk = VK[name.upper()]
    sc = user32.MapVirtualKeyW(vk, 0)
    ext = 1 if vk in (0x26, 0x28, 0x25, 0x27) else 0
    user32.keybd_event(vk, sc, ext, 0)
    time.sleep(hold)
    user32.keybd_event(vk, sc, ext | 2, 0)
    time.sleep(0.25)


def click(x, y):
    """x,y in screenshot pixels (1920x1080 client); maps through the window rect."""
    hwnd = user32.FindWindowW(None, "BLUE PRINCE")
    r = wintypes.RECT(); user32.GetClientRect(hwnd, ctypes.byref(r))
    pt = wintypes.POINT(0, 0); user32.ClientToScreen(hwnd, ctypes.byref(pt))
    sx = pt.x + int(x * r.right / 1920); sy = pt.y + int(y * r.bottom / 1080)
    user32.SetCursorPos(sx, sy); time.sleep(0.4)
    user32.mouse_event(2, 0, 0, 0, 0); time.sleep(0.08); user32.mouse_event(4, 0, 0, 0, 0); time.sleep(0.5)


def send(lines):
    os.makedirs(BPAR, exist_ok=True)
    with open(CMD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    t = time.time()
    while os.path.exists(CMD) and time.time() - t < 30:
        time.sleep(0.3)
    time.sleep(1.2)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "launch":
        launch()
    elif a[0] == "kill":
        kill()
    elif a[0] == "cmd":
        send(a[1:])
    elif a[0] == "keys":
        focus()
        for k in a[1:]:
            n, _, h = k.partition(':')
            press(n, float(h) if h else 0.3)
    elif a[0] == "click":
        focus(); click(int(a[1]), int(a[2]))
    elif a[0] == "log":
        p = os.path.join(ROOT, "BepInEx", "LogOutput.log")
        print("".join(open(p, encoding="utf-8", errors="replace").readlines()[-int(a[1] if len(a) > 1 else 30):]))
