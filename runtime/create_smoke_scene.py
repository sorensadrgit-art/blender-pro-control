from pathlib import Path
import bpy

OUT = Path("/srv/blender-pro/projects/work/smoke/scene.blend")
OUT.parent.mkdir(parents=True, exist_ok=True)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

bpy.ops.mesh.primitive_plane_add(size=12, location=(0, 0, 0))
plane = bpy.context.object
plane.name = "Ground"

bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
cube = bpy.context.object
cube.name = "HeroCube"
bevel = cube.modifiers.new(name="SoftEdges", type="BEVEL")
bevel.width = 0.12
bevel.segments = 3

bpy.ops.object.camera_add(location=(4.5, -5.5, 3.5))
camera = bpy.context.object
camera.name = "Camera_Main"
direction = (cube.location - camera.location).normalized()
camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

bpy.ops.object.light_add(type="AREA", location=(3, -2, 6))
key = bpy.context.object
key.name = "Key_Area"
key.data.energy = 900
key.data.shape = "DISK"
key.data.size = 4

bpy.ops.object.light_add(type="AREA", location=(-3, 1, 4))
fill = bpy.context.object
fill.name = "Fill_Area"
fill.data.energy = 350
fill.data.size = 3

scene = bpy.context.scene
scene.camera = camera
scene.render.engine = "CYCLES"
scene.cycles.samples = 8
scene.cycles.use_denoising = False
scene.render.resolution_x = 320
scene.render.resolution_y = 180
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.world.color = (0.01, 0.01, 0.01)
scene.frame_start = 1
scene.frame_end = 1

bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
print(f"BLENDER_PRO_SMOKE_SCENE={OUT}")
