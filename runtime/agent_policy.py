import re
from pathlib import Path

SCENE_ROOTS = (
    Path('/srv/blender-pro/projects'),
    Path('/srv/blender-pro/assets'),
)
JOB_ROOT = Path('/srv/blender-pro/jobs')
VERIFY = '/opt/blender-pro/bin/blender-verify'
SUDO = '/usr/bin/sudo'
RENDER_START = '/opt/blender-pro/bin/blender-render-start'
SAFE_INSTANCE = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._-]*$')


def _within(raw, roots, strict=True):
    try:
        path = Path(raw).resolve(strict=strict)
    except OSError as exc:
        raise ValueError(f'path cannot be resolved: {raw}') from exc
    for root in roots:
        try:
            path.relative_to(root.resolve())
            return path
        except ValueError:
            continue
    raise ValueError(f'path outside approved roots: {path}')


class AgentPolicy:
    def scene_path(self, raw):
        path = _within(raw, SCENE_ROOTS)
        if path.suffix.lower() != '.blend':
            raise ValueError('scene must be a .blend file')
        return str(path)

    def job_path(self, raw):
        path = _within(raw, (JOB_ROOT,))
        if path.suffix.lower() != '.json' or path.name.endswith('.result.json'):
            raise ValueError('job must be a manifest JSON file')
        if not SAFE_INSTANCE.fullmatch(path.stem):
            raise ValueError('job name must be a safe instance slug')
        return str(path)

    def verify_argv(self, raw):
        return [VERIFY, self.scene_path(raw)]

    def job_argv(self, raw):
        manifest = Path(self.job_path(raw))
        return [SUDO, '-n', RENDER_START, manifest.stem]

    def result_path(self, raw):
        manifest = Path(self.job_path(raw))
        return str(manifest.with_suffix('.result.json'))
