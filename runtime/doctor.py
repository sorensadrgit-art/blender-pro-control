#!/usr/bin/env python3
import hashlib
import json
import os
import tomllib
from pathlib import Path

from disk_guard import disk_status

OPT = Path('/opt/blender-pro')
STATE = Path('/var/lib/blender-pro')


def _sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def _item(name, ok, detail):
    return {'name': name, 'ok': bool(ok), 'detail': detail}


def run_doctor():
    checks = []
    blender_lock = json.loads((OPT/'locks/blender.lock.json').read_text())
    expected = (OPT/'releases'/blender_lock['version']).resolve()
    current = (OPT/'current').resolve()
    checks.append(_item('current_release', current == expected, str(current)))

    archive = OPT/'packages/blender'/blender_lock['archive']
    blender_hash = _sha256(archive) if archive.is_file() else None
    checks.append(_item('blender_archive', blender_hash == blender_lock['sha256'], blender_hash))

    extensions = json.loads((OPT/'locks/extensions.lock.json').read_text())
    bkit = extensions['external']['blenderkit']
    bkit_archive = OPT/'packages/extensions'/bkit['package']
    bkit_hash = _sha256(bkit_archive) if bkit_archive.is_file() else None
    checks.append(_item('blenderkit_archive', bkit_hash == bkit['sha256'], bkit_hash))

    manifest = Path(bkit['install_root'])/'blender_manifest.toml'
    manifest_data = tomllib.loads(manifest.read_text()) if manifest.is_file() else {}
    manifest_ok = manifest_data.get('version') == bkit['manifest_version']
    checks.append(_item('blenderkit_asset_fetch', manifest_ok, manifest_data.get('version')))
    render_safe_manifest = STATE/'extensions/render-safe/user_default/blenderkit/blender_manifest.toml'
    checks.append(_item('blenderkit_render_safe_absent', not render_safe_manifest.exists(), str(render_safe_manifest)))

    capabilities = json.loads((STATE/'state/capabilities.json').read_text())
    cap_hash = capabilities['blender']['build_hash']
    checks.append(_item('capabilities_hash', cap_hash == blender_lock['build_hash'], cap_hash))

    unit = Path('/etc/systemd/system/blender-pro-render@.service')
    target = (OPT/'blender-pro-render@.service').resolve()
    unit_ok = unit.exists() and unit.resolve() == target
    checks.append(_item('systemd_unit', unit_ok, str(unit.resolve()) if unit.exists() else 'missing'))

    job = OPT/'bin/blender-job'
    agent = OPT/'bin/blender-agent-mcp'
    checks.append(_item('job_launcher', job.is_file() and os.access(job, os.X_OK), str(job)))
    checks.append(_item('agent_launcher', agent.is_file() and os.access(agent, os.X_OK), str(agent)))

    disk = disk_status('/srv/blender-pro')
    checks.append(_item('disk_state', disk['status'] in {'ok', 'warn'}, disk))
    return {'ok': all(item['ok'] for item in checks), 'checks': checks}


def main():
    result = run_doctor()
    print('BLENDER_PRO_DOCTOR=' + json.dumps(result, sort_keys=True))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
