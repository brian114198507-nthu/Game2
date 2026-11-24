"""Create the original Moon Moth protagonist in Blender and export GLB."""

import bpy
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "models")
os.makedirs(OUT, exist_ok=True)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)


def material(name, color, metallic=0.0, roughness=0.75):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


cloak = material("Midnight teal cloak", (0.075, 0.22, 0.28))
face = material("Warm moth face", (0.78, 0.62, 0.40))
wing = material("Dusty violet wings", (0.38, 0.34, 0.55))
gold = material("Lantern brass", (0.95, 0.62, 0.19), 0.55, 0.32)
glow = material("Lantern glass", (1.0, 0.78, 0.35), 0.05, 0.2)
dark = material("Boots and eyes", (0.055, 0.075, 0.12))
scarf = material("Scarf coral", (0.72, 0.28, 0.22))


def smooth(obj, mat, bevel=0.0):
    obj.data.materials.append(mat)
    if obj.type == "MESH":
        for poly in obj.data.polygons:
            poly.use_smooth = True
    if bevel > 0:
        mod = obj.modifiers.new("Soft hand-shaped edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return obj


def uv_sphere(name, location, scale, mat, segments=16, rings=10):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    return smooth(obj, mat)


def cube(name, location, scale, mat, bevel=0.08):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return smooth(obj, mat, bevel)


def cone(name, location, radius, depth, mat, vertices=12):
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius, radius2=0.04, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    return smooth(obj, mat, 0.035)


# Soft-winged guide, designed as an original child-friendly silhouette.
uv_sphere("Cloak body", (0, 0, 0.92), (0.43, 0.34, 0.62), cloak)
uv_sphere("Moth face", (0, 0.015, 1.72), (0.39, 0.33, 0.39), face)
cone("Short hood", (0, 0.0, 2.03), 0.4, 0.58, cloak)
uv_sphere("Left eye", (-0.14, -0.295, 1.75), (0.043, 0.026, 0.055), dark, 12, 8)
uv_sphere("Right eye", (0.14, -0.295, 1.75), (0.043, 0.026, 0.055), dark, 12, 8)

# Two small, rounded wings sit behind the cloak rather than copying a raincoat character.
left_wing = uv_sphere("Left velvet wing", (-0.48, 0.14, 1.16), (0.34, 0.10, 0.52), wing)
left_wing.rotation_euler[1] = math.radians(-24)
right_wing = uv_sphere("Right velvet wing", (0.48, 0.14, 1.16), (0.34, 0.10, 0.52), wing)
right_wing.rotation_euler[1] = math.radians(24)

cube("Coral scarf", (0, -0.03, 1.38), (0.66, 0.46, 0.13), scarf, 0.045)
cube("Left boot", (-0.19, -0.015, 0.24), (0.24, 0.36, 0.32), dark, 0.07)
cube("Right boot", (0.19, -0.015, 0.24), (0.24, 0.36, 0.32), dark, 0.07)

# The hand lantern becomes the warm focal point in the blue scene.
cube("Lantern handle", (0.64, 0.0, 0.97), (0.13, 0.15, 0.52), gold, 0.04)
cube("Lantern glass", (0.64, -0.015, 0.91), (0.33, 0.27, 0.35), glow, 0.05)
uv_sphere("LanternGlow", (0.64, -0.2, 0.93), (0.09, 0.045, 0.11), glow, 12, 8)
cube("Satchel", (-0.38, -0.02, 0.89), (0.27, 0.26, 0.31), gold, 0.06)

# A few floating, individually named star stitches add a readable silhouette.
for i, loc in enumerate([(-0.22, -0.34, 1.14), (0.0, -0.35, 1.05), (0.21, -0.34, 1.17)]):
    uv_sphere("Star stitch %d" % i, loc, (0.035, 0.02, 0.035), gold, 8, 6)

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 512
scene.render.resolution_y = 512
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = os.path.join(OUT, "moon_moth_preview.png")

# Place the model on the ground and select all modeled objects for reliable GLB export.
bpy.ops.object.select_all(action="SELECT")
for obj in bpy.context.selected_objects:
    obj.location.z -= 0.04
bpy.ops.object.select_all(action="DESELECT")
for obj in bpy.context.scene.objects:
    if obj.type == "MESH":
        obj.select_set(True)
bpy.context.view_layer.objects.active = bpy.data.objects.get("Cloak body")

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "moon_moth.blend"))
bpy.ops.export_scene.gltf(
    filepath=os.path.join(OUT, "moon_moth.glb"),
    export_format="GLB",
    use_selection=True,
    export_apply=True,
    export_materials="EXPORT",
    export_cameras=False,
    export_lights=False,
)
