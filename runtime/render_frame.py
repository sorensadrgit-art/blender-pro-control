import json
import sys
from pathlib import Path
import bpy

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if not args:
    raise RuntimeError("render output path is required")
out = Path(args[0]).resolve()
frame = int(args[1]) if len(args) > 1 else bpy.context.scene.frame_current
root = Path("/srv/blender-pro/renders").resolve()
try:
    out.relative_to(root)
except ValueError as exc:
    raise RuntimeError(f"render output outside approved location: {out}") from exc
out.parent.mkdir(parents=True, exist_ok=True)
scene = bpy.context.scene
scene.frame_set(frame)
scene.render.filepath = str(out)
scene.render.image_settings.file_format = "PNG"
bpy.ops.render.render(write_still=True)
print("BLENDER_PRO_RENDER=" + json.dumps({"output": str(out), "frame": frame, "engine": scene.render.engine}, sort_keys=True))
