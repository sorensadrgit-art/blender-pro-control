#!/usr/bin/env python3
import json
import sys

from asset_publish import publish_asset


def main(argv=None, publish=publish_asset):
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 4:
        return 64
    source, asset_type, asset_name, version = args
    try:
        result = publish(source, asset_type, asset_name, version)
    except (ValueError, FileNotFoundError, FileExistsError, OSError) as exc:
        print(f'BLENDER_PRO_ASSET_ERROR={exc}', file=sys.stderr)
        return 20
    print('BLENDER_PRO_ASSET=' + json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
