import json
from pathlib import Path

import bpy

SCENE_ROOTS = [Path("/srv/blender-pro/projects"), Path("/srv/blender-pro/assets")]

def is_within(path: Path, roots) -> bool:
    resolved = path.resolve()
    for root in roots:
        try:
            resolved.relative_to(root.resolve())
            return True
        except ValueError:
            pass
    return False

errors = []
warnings = []
scene = bpy.context.scene
blend_path = Path(bpy.data.filepath).resolve() if bpy.data.filepath else None

if blend_path is None:
    errors.append("scene has not been saved")
elif not is_within(blend_path, SCENE_ROOTS):
    errors.append(f"scene path outside approved locations: {blend_path}")
if scene.camera is None:
    errors.append("active camera is missing")
if scene.render.resolution_x <= 0 or scene.render.resolution_y <= 0:
    errors.append("render resolution is invalid")

for image in bpy.data.images:
    if image.source == "FILE" and image.filepath:
        image_path = Path(bpy.path.abspath(image.filepath))
        if not image_path.exists():
            errors.append(f"missing image: {image_path}")

for library in bpy.data.libraries:
    library_path = Path(bpy.path.abspath(library.filepath))
    if not library_path.exists():
        errors.append(f"missing linked library: {library_path}")

if bpy.data.texts:
    warnings.append(f"scene contains {len(bpy.data.texts)} text block(s)")

result = {
    "ok": not errors,
    "scene": str(blend_path) if blend_path else None,
    "engine": scene.render.engine,
    "camera": scene.camera.name if scene.camera else None,
    "resolution": [scene.render.resolution_x, scene.render.resolution_y],
    "errors": errors,
    "warnings": warnings,
}
print("BLENDER_PRO_PREFLIGHT=" + json.dumps(result, sort_keys=True))
if errors:
    raise RuntimeError("preflight failed")
