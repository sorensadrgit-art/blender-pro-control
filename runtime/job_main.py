#!/usr/bin/env python3
import json
import subprocess
import sys

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


def main(argv=None, run_file=run_job_file):
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        return 64
    try:
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
