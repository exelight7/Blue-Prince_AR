"""Read-only source inspection. All generated files stay inside the project."""
import argparse
import collections
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/vendor'))


def sha256(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(value, ensure_ascii=True, indent=2).encode('utf-8') + b'\n'
    if path.exists():
        if path.read_bytes() != data:
            raise FileExistsError(f'Refusing to overwrite different data: {path}')
        return
    with path.open('xb') as stream:
        stream.write(data)


def safe_roots(game):
    game = game.resolve(strict=True)
    if game == ROOT or game in ROOT.parents or ROOT in game.parents:
        raise ValueError('Game and project must be separate, non-nested directories')
    return game


def inventory(game):
    rows = []
    for path in sorted(game.rglob('*')):
        if not path.is_file():
            continue
        if path.is_symlink():
            raise ValueError(f'Symlink requires manual review: {path}')
        stat = path.stat()
        rows.append(dict(path=path.relative_to(game).as_posix(), size=stat.st_size,
                         mtime_ns=stat.st_mtime_ns, sha256=sha256(path)))
    write_new(ROOT / 'reference/source_inventory.json', rows)
    print(json.dumps(dict(files=len(rows), bytes=sum(r['size'] for r in rows))))


def verify(game):
    rows = json.loads((ROOT / 'reference/source_inventory.json').read_text())
    expected = {r['path'] for r in rows}
    actual = {p.relative_to(game).as_posix() for p in game.rglob('*') if p.is_file()}
    failures = [{'path': p, 'reason': 'added or removed'} for p in sorted(expected ^ actual)]
    for row in rows:
        path = game / row['path']
        if path.is_file() and (path.stat().st_size != row['size'] or sha256(path) != row['sha256']):
            failures.append(dict(path=row['path'], reason='size/hash changed'))
    result = dict(status='FAIL' if failures else 'PASS', files=len(rows), failures=failures)
    print(json.dumps(result))
    return bool(failures)


def snapshot(game):
    rows = json.loads((ROOT / 'reference/source_inventory.json').read_text())
    selected = []
    for row in rows:
        rel = Path(row['path'])
        if ('BLUE PRINCE_Data' in rel.parts and
            (rel.suffix in ('.assets', '.bundle', '.json', '.xml', '.config', '.info') or
             rel.name in ('globalgamemanagers', 'level0', 'level1', 'level2', 'global-metadata.dat'))):
            selected.append(row)
        elif rel.name in ('GameAssembly.dll',):
            selected.append(row)
    for row in selected:
        src = game / row['path']
        dst = ROOT / 'backups/source' / row['path']
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            if sha256(dst) != row['sha256']:
                raise ValueError(f'Backup conflict: {dst}')
        else:
            with src.open('rb') as source, dst.open('xb') as target:
                shutil.copyfileobj(source, target)
        if sha256(dst) != row['sha256']:
            raise ValueError(f'Backup integrity failure: {dst}')
    write_new(ROOT / 'reference/snapshot_manifest.json', selected)
    print(f'PASS: {len(selected)} source files copied and hash-verified')


def extract():
    import UnityPy
    base = ROOT / 'backups/source/BLUE PRINCE_Data'
    sources = sorted(p for p in base.rglob('*') if p.is_file() and
                     (p.suffix in ('.assets', '.bundle') or p.name in
                      ('globalgamemanagers', 'level0', 'level1', 'level2')))
    scripts = {}
    env = UnityPy.load(str(base / 'globalgamemanagers.assets'))
    for obj in env.objects:
        if obj.type.name == 'MonoScript':
            d = obj.read()
            scripts[str(obj.path_id)] = dict(assembly=d.m_AssemblyName,
                namespace=d.m_Namespace, name=d.m_ClassName)
    write_new(ROOT / 'research/mono_scripts.json', scripts)
    summary = []
    for path in sources:
        env = UnityPy.load(str(path))
        rel = path.relative_to(base).as_posix()
        counts = collections.Counter(o.type.name for o in env.objects)
        records = []
        for obj in env.objects:
            kind = obj.type.name
            if kind not in ('MonoBehaviour', 'Font', 'TextAsset', 'VideoClip', 'Texture2D', 'AudioClip'):
                continue
            rec = dict(container=rel, asset=obj.assets_file.name,
                       path_id=obj.path_id, type=kind, bytes=obj.byte_size)
            try:
                if kind == 'MonoBehaviour':
                    d = obj.read_typetree(check_read=False)
                    rec.update(name=d.get('m_Name', ''), script=d.get('m_Script'))
                    ref = d.get('m_Script', {})
                    rec['script_hint'] = scripts.get(str(ref.get('m_PathID')), {})
                    rec['schema_status'] = 'COMMON_HEADER_ONLY'
                else:
                    d = obj.read()
                    rec['name'] = getattr(d, 'm_Name', '')
                    if kind == 'TextAsset':
                        payload = d.m_Script.encode('utf-8', 'surrogateescape')
                        out = ROOT / 'extracted/original/textassets' / Path(rel).name / f'{obj.path_id}.bin'
                        out.parent.mkdir(parents=True, exist_ok=True)
                        if out.exists() and out.read_bytes() != payload:
                            raise FileExistsError(str(out))
                        if not out.exists():
                            out.write_bytes(payload)
                        rec['payload'] = out.relative_to(ROOT).as_posix()
                    if kind == 'Texture2D':
                        rec.update(width=d.m_Width, height=d.m_Height, format=int(d.m_TextureFormat))
                    if kind == 'VideoClip':
                        rec['original_path'] = getattr(d, 'm_OriginalPath', '')
            except Exception as error:
                rec['error'] = str(error)
            records.append(rec)
        key = re.sub(r'[^a-zA-Z0-9_.-]', '_', rel)
        write_new(ROOT / f'research/asset_index/{key}.json', records)
        row = dict(container=rel, objects=sum(counts.values()), types=dict(counts),
                   versions=sorted(set(str(o.assets_file.unity_version) for o in env.objects)),
                   errors=sum('error' in r for r in records))
        summary.append(row)
        print(json.dumps(row), flush=True)
    write_new(ROOT / 'research/asset_summary.json', summary)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['inventory', 'snapshot', 'extract', 'verify'])
    parser.add_argument('--game', type=Path, default=ROOT.with_name('Blue Prince'))
    args = parser.parse_args()
    game = safe_roots(args.game)
    if args.command == 'extract':
        extract()
        return 0
    return globals()[args.command](game) or 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f'ERROR: {error}', file=sys.stderr)
        raise SystemExit(1)
