import addon_utils
import bpy
import json
import os

found = []
for module in addon_utils.modules():
    name = module.__name__
    if "rigify" in name.lower() or "node_wrangler" in name.lower():
        info = getattr(module, "bl_info", {}) or {}
        found.append({
            "module": name,
            "name": info.get("name"),
            "version": info.get("version"),
        })

result = {
    "blender_version": bpy.app.version_string,
    "build_hash": bpy.app.build_hash.decode(),
    "addons_found": found,
    "user_config": bpy.utils.user_resource("CONFIG"),
    "user_scripts": bpy.utils.user_resource("SCRIPTS"),
    "tmpdir": os.environ.get("TMPDIR"),
    "cache_home": os.environ.get("XDG_CACHE_HOME"),
}
print("BLENDER_PRO_RUNTIME=" + json.dumps(result, sort_keys=True, default=list))
