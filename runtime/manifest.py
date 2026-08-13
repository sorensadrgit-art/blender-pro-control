from pathlib import Path

ALLOWED_FIELDS = {
    'schema', 'project', 'scene', 'engine', 'frame', 'resolution',
    'preview_output', 'render_output',
}
ALLOWED_ENGINES = {'CYCLES', 'BLENDER_EEVEE_NEXT'}

def _within(raw, roots, must_exist=False):
    path = Path(raw).resolve(strict=must_exist)
    for root in roots:
        try:
            path.relative_to(Path(root).resolve())
            return path
        except ValueError:
            pass
    raise ValueError(f'path outside approved roots: {path}')

def _safe_name(value, label):
    if not isinstance(value, str) or not value or any(ch not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-' for ch in value):
        raise ValueError(f'{label} must be a safe slug')
    return value

def validate_manifest(data, project_root, asset_root, preview_root, render_root):
    if not isinstance(data, dict):
        raise ValueError('manifest must be an object')
    unknown = set(data) - ALLOWED_FIELDS
    if unknown:
        raise ValueError(f'unknown manifest fields: {sorted(unknown)}')
    missing = ALLOWED_FIELDS - set(data)
    if missing:
        raise ValueError(f'missing manifest fields: {sorted(missing)}')
    if data['schema'] != 1:
        raise ValueError('unsupported manifest schema')
    project = _safe_name(data['project'], 'project')
    scene = _within(data['scene'], (project_root, asset_root), must_exist=True)
    if scene.suffix.lower() != '.blend':
        raise ValueError('scene must be a .blend file')
    engine = data['engine']
    if engine not in ALLOWED_ENGINES:
        raise ValueError('unsupported render engine')
    frame = data['frame']
    if isinstance(frame, bool) or not isinstance(frame, int) or frame < 1 or frame > 10_000_000:
        raise ValueError('frame must be an integer from 1 to 10000000')
    resolution = data['resolution']
    if not isinstance(resolution, list) or len(resolution) != 2:
        raise ValueError('resolution must contain width and height')
    if any(isinstance(v, bool) or not isinstance(v, int) or v < 1 or v > 16384 for v in resolution):
        raise ValueError('resolution dimensions must be integers from 1 to 16384')
    preview = _within(data['preview_output'], (preview_root,))
    render = _within(data['render_output'], (render_root,))
    if preview.suffix.lower() != '.png' or render.suffix.lower() != '.png':
        raise ValueError('preview and render outputs must be PNG')
    return {
        'schema': 1, 'project': project, 'scene': str(scene), 'engine': engine,
        'frame': frame, 'resolution': list(resolution),
        'preview_output': str(preview), 'render_output': str(render),
    }
