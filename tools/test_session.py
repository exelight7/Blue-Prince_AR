"""Safe test runs of runtime_test: back up the user's saves and PlayerPrefs before, restore them exactly after.

python test_session.py begin    refuses while any BLUE PRINCE.exe runs; copies the save folder and exports the registry key
python test_session.py end      stops the runtime_test game (only that one), then restores both from the last backup
The real game and the test copy share LocalLow/Dogubomb/BLUE PRINCE and HKCU/Software/Dogubomb/BLUE PRINCE.
"""
import os, shutil, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAVES = Path(os.environ["USERPROFILE"]) / "AppData" / "LocalLow" / "Dogubomb" / "BLUE PRINCE"
REGKEY = "HKCU\\Software\\Dogubomb\\BLUE PRINCE"
STATE = ROOT / "backups" / "saves_current.txt"


def running():
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq BLUE PRINCE.exe", "/FO", "CSV", "/NH"], capture_output=True, text=True).stdout
    return "BLUE PRINCE.exe" in out


def stop_test_copy():
    ps = "Get-CimInstance Win32_Process -Filter \"Name='BLUE PRINCE.exe'\" | Where-Object { $_.ExecutablePath -like '*runtime_test*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True)


def begin():
    if running():
        sys.exit("BLUE PRINCE.exe is running - close the game first (the test copy shares your saves).")
    dest = ROOT / "backups" / time.strftime("saves_%Y%m%d_%H%M%S")
    dest.mkdir(parents=True)
    if SAVES.exists():
        shutil.copytree(SAVES, dest / "BLUE PRINCE")
    r = subprocess.run(["reg", "export", REGKEY, str(dest / "prefs.reg"), "/y"], capture_output=True, text=True)
    STATE.write_text(str(dest), encoding="utf-8")
    print("backup ->", dest, "| saves:", SAVES.exists(), "| registry export rc", r.returncode)


def end():
    if not STATE.exists():
        sys.exit("no backup recorded (run begin first)")
    src = Path(STATE.read_text(encoding="utf-8"))
    stop_test_copy(); time.sleep(3)
    if running():
        sys.exit("a BLUE PRINCE.exe outside runtime_test is running - close it, then run end again")
    if SAVES.exists():
        shutil.rmtree(SAVES)
    if (src / "BLUE PRINCE").exists():
        shutil.copytree(src / "BLUE PRINCE", SAVES)
    subprocess.run(["reg", "delete", REGKEY, "/f"], capture_output=True)
    r = subprocess.run(["reg", "import", str(src / "prefs.reg")], capture_output=True, text=True)
    print("restored from", src, "| registry import rc", r.returncode)


if __name__ == "__main__":
    {"begin": begin, "end": end}[sys.argv[1]]()
