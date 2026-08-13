import hashlib
import json
import os
import re
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

SAFE_NAME = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._-]*$')
VERSION = re.compile(r'^v[0-9]{3,}$')
DEFAULT_WORK = Path('/srv/blender-pro/assets/work')
DEFAULT_PUBLISHED = Path('/srv/blender-pro/assets/published')

def _within(path: Path, root: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f'path outside approved root: {resolved}') from exc
    return resolved

def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()

def publish_asset(source, asset_type, asset_name, version, work_root=DEFAULT_WORK, published_root=DEFAULT_PUBLISHED):
    if not SAFE_NAME.fullmatch(asset_type) or not SAFE_NAME.fullmatch(asset_name):
        raise ValueError('asset type and name must be safe slugs')
    if not VERSION.fullmatch(version):
        raise ValueError('version must match vNNN or higher')
    work_root = Path(work_root)
    published_root = Path(published_root)
    source = _within(Path(source), work_root)
    if not source.is_file() or source.suffix.lower() != '.blend':
        raise ValueError('source must be an existing .blend file')
    target_parent = published_root / asset_type / asset_name
    target_dir = target_parent / version
    if target_dir.exists():
        raise FileExistsError(str(target_dir))
    target_parent.mkdir(parents=True, exist_ok=True)
    partial = target_parent / f'.{version}.partial-{uuid.uuid4().hex[:8]}'
    partial.mkdir()
    try:
        blend_dest = partial / f'{asset_name}.blend'
        shutil.copy2(source, blend_dest)
        metadata = {
            'asset_type': asset_type,
            'asset_name': asset_name,
            'version': version,
            'sha256': _sha256(blend_dest),
            'published_at': datetime.now(timezone.utc).isoformat(),
        }
        (partial / 'asset.json').write_text(json.dumps(metadata, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        os.replace(partial, target_dir)
    except Exception:
        shutil.rmtree(partial, ignore_errors=True)
        raise
    return {'blend': str(target_dir / f'{asset_name}.blend'), 'metadata': str(target_dir / 'asset.json'), 'version': version}
