import json
import os
import tempfile
from pathlib import Path

from job_runner import execute_job


def _within_job_root(path, job_root):
    resolved = Path(path).resolve(strict=True)
    root = Path(job_root).resolve(strict=True)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f'manifest outside job root: {resolved}') from exc
    if resolved.suffix.lower() != '.json':
        raise ValueError('manifest must be JSON')
    if resolved.name.endswith('.result.json'):
        raise ValueError('result file cannot be executed as a manifest')
    return resolved


def _write_json_atomic(path, data):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f'.{target.name}.', suffix='.tmp', dir=str(target.parent))
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as handle:
            json.dump(data, handle, indent=2, sort_keys=True)
            handle.write('\n')
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, target)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def run_job_file(manifest_path, roots, executor, disk_probe, job_root):
    manifest = _within_job_root(manifest_path, job_root)
    data = json.loads(manifest.read_text(encoding='utf-8-sig'))
    result = execute_job(data, roots, executor, disk_probe)
    result_path = manifest.with_suffix('.result.json')
    _write_json_atomic(result_path, result)
    return result
