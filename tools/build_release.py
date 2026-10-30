"""Assemble release/BluePrince_Arabic from runtime_test + current translations.

payload/ = exactly the files that get added to the game folder (BepInEx 6 IL2CPP + the Arabic plugin).
manifest.json = relative path + sha256 + size of every payload file (install.ps1 verifies it, uninstall.ps1 removes by it).
Run after: sh tools/deploy_plugin.sh ar.json
"""
import hashlib, json, os, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "runtime_test"
OUT = ROOT / "release" / "BluePrince_Arabic"
PAYLOAD = OUT / "payload"

ROOT_FILES = ["winhttp.dll", "doorstop_config.ini", ".doorstop_version"]
TREES = ["dotnet", "BepInEx/core", "BepInEx/plugins/BluePrinceArabic"]
CONFIGS = ["BepInEx/config/BepInEx.cfg", "BepInEx/config/local.blueprince.arabic.cfg"]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    if OUT.exists():
        # clear the contents, not the folder itself: Windows refuses to delete it while another program has it open
        for child in OUT.iterdir():
            shutil.rmtree(child) if child.is_dir() else child.unlink()
    PAYLOAD.mkdir(parents=True, exist_ok=True)
    files = []
    for rel in ROOT_FILES + CONFIGS:
        files.append(rel)
    for t in TREES:
        for p in sorted((SRC / t).rglob("*")):
            if p.is_file():
                files.append(p.relative_to(SRC).as_posix())
    manifest = []
    for rel in files:
        dst = PAYLOAD / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SRC / rel, dst)
        manifest.append({"path": rel.replace("/", "\\"), "sha256": sha(dst), "size": dst.stat().st_size})
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    # scripts and readme are maintained next to this file
    for name in ("install.ps1", "uninstall.ps1", "README_AR.txt"):
        s = ROOT / "tools" / "release_src" / name
        if s.exists():
            shutil.copy2(s, OUT / name)
    total = sum(m["size"] for m in manifest)
    print(len(manifest), "files,", round(total / 1e6, 1), "MB ->", OUT)


if __name__ == "__main__":
    main()
