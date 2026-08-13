import json
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_settings import parse_render_args

args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
settings = parse_render_args(args)
out = Path(settings['output']).resolve()
root = Path('/srv/blender-pro/renders').resolve()
try:
    out.relative_to(root)
except ValueError as exc:
    raise RuntimeError(f'render output outside approved location: {out}') from exc

out.parent.mkdir(parents=True, exist_ok=True)
scene = bpy.context.scene
scene.frame_set(settings['frame'])
scene.render.engine = settings['engine']
scene.render.resolution_x = settings['width']
scene.render.resolution_y = settings['height']
scene.render.resolution_percentage = 100
scene.render.filepath = str(out)
scene.render.image_settings.file_format = 'PNG'

bpy.ops.render.render(write_still=True)
print('BLENDER_PRO_RENDER=' + json.dumps({
    'output': str(out),
    'frame': settings['frame'],
    'engine': scene.render.engine,
    'resolution': [scene.render.resolution_x, scene.render.resolution_y],
    'resolution_percentage': scene.render.resolution_percentage,
}, sort_keys=True))
