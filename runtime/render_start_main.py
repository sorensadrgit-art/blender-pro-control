#!/usr/bin/env python3
import re
import subprocess
import sys

SYSTEMCTL = '/usr/bin/systemctl'
SAFE_INSTANCE = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._-]*$')


def main(argv=None, run=subprocess.run):
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        return 64
    instance = args[0]
    if not SAFE_INSTANCE.fullmatch(instance):
        return 65
    unit = f'blender-pro-render@{instance}.service'
    completed = run(
        [SYSTEMCTL, 'start', unit],
        check=False,
        shell=False,
    )
    return completed.returncode


if __name__ == '__main__':
    raise SystemExit(main())
