BLENDER = '/opt/blender-pro/bin/blender-pro'
PREFLIGHT = '/opt/blender-pro/skills/preflight.py'
PREVIEW = '/opt/blender-pro/skills/preview.py'
FINAL = '/opt/blender-pro/skills/render_frame.py'


def _render_argv(script, manifest, output_key, exit_code):
    width, height = manifest['resolution']
    return [
        BLENDER,
        '--background',
        manifest['scene'],
        '--python-exit-code', str(exit_code),
        '--python', script,
        '--',
        str(manifest['frame']),
        str(width),
        str(height),
        manifest['engine'],
        manifest[output_key],
    ]


def build_job_plan(manifest):
    return {
        'preflight': [
            BLENDER, '--background', manifest['scene'],
            '--python-exit-code', '30', '--python', PREFLIGHT,
        ],
        'preview': _render_argv(PREVIEW, manifest, 'preview_output', 40),
        'final': _render_argv(FINAL, manifest, 'render_output', 60),
    }
