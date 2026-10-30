"""Create and hash-verify a disposable runtime copy; never modify the source."""
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import winreg
from project import ROOT, sha256, write_new


def main():
    source = ROOT.with_name('Blue Prince').resolve(strict=True)
    target = ROOT / 'runtime_test'
    if target.exists():
        raise FileExistsError('Runtime target already exists; inspect its manifest before reuse')
    if source == target or source in target.parents:
        raise ValueError('Runtime target must be separate from the original installation')
    baseline = json.loads((ROOT / 'reference/source_inventory.json').read_text())
    actual = {p.relative_to(source).as_posix() for p in source.rglob('*') if p.is_file()}
    if actual != {row['path'] for row in baseline}:
        raise ValueError('Source file set differs from the recorded build')
    target.mkdir()
    copied = []
    for row in baseline:
        src, dst = source / row['path'], target / row['path']
        if src.is_symlink() or sha256(src) != row['sha256']:
            raise ValueError(f'Unexpected source content: {src}')
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        digest = sha256(dst)
        if digest != row['sha256']:
            raise ValueError(f'Copy hash mismatch: {dst}')
        copied.append(dict(path=row['path'], source_sha256=row['sha256'],
                           copy_sha256=digest, size=row['size'], modified=False))
        if len(copied) % 10 == 0:
            print(f'Copied and verified {len(copied)}/{len(baseline)} files', flush=True)
    write_new(ROOT / 'tests/runtime_copy_manifest.json', dict(source=str(source),
        target=str(target), prepared_utc=datetime.now(timezone.utc).isoformat(),
        status='PASS', files=copied))
    candidates = [Path.home() / 'AppData/LocalLow/Dogubomb',
                  Path.home() / 'Documents/My Games/Blue Prince',
                  Path.home() / 'AppData/Local/BluePrince']
    saves = []
    backup = ROOT / 'backups/runtime_user_state_before_003'
    for i, candidate in enumerate(candidates):
        entry = dict(path=str(candidate), existed=candidate.exists(), files=[])
        if candidate.exists():
            for file in candidate.rglob('*'):
                if file.is_file():
                    rel = file.relative_to(candidate)
                    dst = backup / f'path_{i}' / rel
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file, dst)
                    if sha256(file) != sha256(dst):
                        raise ValueError('Save backup hash mismatch')
                    entry['files'].append(dict(path=rel.as_posix(), sha256=sha256(dst)))
        saves.append(entry)
    key_name = r'Software\Dogubomb\BLUE PRINCE'
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_name) as key:
            values = []
            for i in range(winreg.QueryInfoKey(key)[1]):
                name, value, typ = winreg.EnumValue(key, i)
                values.append(dict(name=name, value=value.hex() if isinstance(value, bytes) else value, type=typ))
            registry = dict(key='HKCU\\'+key_name, existed=True, values=values)
    except FileNotFoundError:
        registry = dict(key='HKCU\\'+key_name, existed=False, values=[])
    write_new(ROOT / 'tests/runtime_user_state_before.json', dict(paths=saves, registry=registry,
        note='Copied installation shares user save paths unless separately redirected; no existing known state found does not imply universal isolation.'))
    (ROOT / 'tests/screenshots').mkdir(exist_ok=True)
    (ROOT / 'tests/runtime_logs').mkdir(exist_ok=True)
    print('PASS: complete runtime copy and user-state baseline prepared')


if __name__ == '__main__':
    main()
