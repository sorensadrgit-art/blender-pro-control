import json
import bpy

prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.get_devices()
devices = []
for device in prefs.devices:
    devices.append({
        'name': device.name,
        'type': device.type,
        'id': device.id,
    })
print('BLENDER_PRO_CYCLES_DEVICES=' + json.dumps(devices, sort_keys=True))
