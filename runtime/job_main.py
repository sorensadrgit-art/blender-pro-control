#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from pathlib import Path

from disk_guard import disk_status
from job_file import run_job_file

ROOTS = (
    '/srv/blender-pro/projects',
    '/srv/blender-pro/assets',
    '/srv/blender-pro/previews',
    '/srv/blender-pro/renders',
)
JOB_ROOT = '/srv/blender-pro/jobs'
PHASE_CODES = {'preflight': 30, 'preview': 40, 'final': 60}


def _validate_instance(manifest_path, instance):
    path = Path(manifest_path)
    if path.stem != instance:
        raise ValueError('manifest filename must match worker instance')
    data = json.loads(path.read_text(encoding='utf-8-sig'))
    if data.get('project') != instance:
        raise ValueError('manifest project must match worker instance')
    preview_parent = Path(data.get('preview_output', '')).resolve(strict=False).parent
    render_parent = Path(data.get('render_output', '')).resolve(strict=False).parent
    expected_preview = Path('/srv/blender-pro/previews') / instance
    expected_render = Path('/srv/blender-pro/renders') / instance
    if preview_parent != expected_preview:
        raise ValueError('preview output directory must match worker instance')
    if render_parent != expected_render:
        raise ValueError('render output directory must match worker instance')


def main(argv=None, run_file=run_job_file, instance=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        return 64
    active_instance = os.environ.get('BLENDER_PRO_JOB_INSTANCE') if instance is None else instance
    try:
        if active_instance:
            _validate_instance(args[0], active_instance)
        result = run_file(
            args[0], ROOTS, subprocess.run, disk_status, JOB_ROOT,
        )
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f'BLENDER_PRO_JOB_ERROR={exc}', file=sys.stderr)
        return 10
    except RuntimeError as exc:
        print(f'BLENDER_PRO_JOB_ERROR={exc}', file=sys.stderr)
        return 90
    print('BLENDER_PRO_JOB=' + json.dumps(result, sort_keys=True))
    if result.get('status') == 'complete':
        return 0
    return PHASE_CODES.get(result.get('failed_phase'), 90)


if __name__ == '__main__':
    raise SystemExit(main())
