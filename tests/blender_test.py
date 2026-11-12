import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_monkey_add(location=(0, 0, 0))
obj = bpy.context.active_object
bpy.ops.object.shade_smooth()
mat = bpy.data.materials.new("M"); mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.9, 0.35, 0.1, 1)
obj.data.materials.append(mat)
bpy.ops.object.light_add(type="AREA", location=(3, -3, 4)); bpy.context.active_object.data.energy = 800
bpy.ops.object.camera_add(location=(0, -4, 1), rotation=(1.35, 0, 0)); bpy.context.scene.camera = bpy.context.active_object
s = bpy.context.scene
s.render.engine = "CYCLES"; s.cycles.device = "CPU"; s.cycles.samples = 16
s.render.resolution_x, s.render.resolution_y = 640, 360
import os; s.render.filepath = os.path.abspath("out/blender_test.png")
bpy.ops.render.render(write_still=True)
print("BLENDER_OK")
