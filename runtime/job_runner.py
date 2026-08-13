from job_plan import build_job_plan
from manifest import validate_manifest

TIMEOUTS = {
    'preflight': 120,
    'preview': 600,
    'final': 7200,
}


def execute_job(data, roots, executor, disk_probe):
    project_root, asset_root, preview_root, render_root = roots
    manifest = validate_manifest(
        data,
        project_root,
        asset_root,
        preview_root,
        render_root,
    )
    disk = disk_probe()
    if disk['status'] in {'reject', 'emergency'}:
        raise RuntimeError(f"render refused by disk guard: {disk['status']}")

    plan = build_job_plan(manifest)
    result = {
        'status': 'running',
        'disk': disk,
        'manifest': manifest,
        'phases': [],
    }

    for phase in ('preflight', 'preview', 'final'):
        completed = executor(
            plan[phase],
            capture_output=True,
            text=True,
            timeout=TIMEOUTS[phase],
        )
        phase_result = {
            'phase': phase,
            'exit_code': completed.returncode,
            'stdout': completed.stdout,
            'stderr': completed.stderr,
        }
        result['phases'].append(phase_result)
        if completed.returncode != 0:
            result['status'] = 'failed'
            result['failed_phase'] = phase
            return result

    result['status'] = 'complete'
    return result
