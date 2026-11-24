"""Build the original Moon Moth and Moon Archive set for Godot/WebGL.

Run with Blender 5.x:
  blender -b --python tools/create_blender_assets.py

The set is authored as real, light-responsive geometry rather than a flat backdrop.
All models and materials are original to this project.
"""
import bpy
import math
import os
import random
from mathutils import Vector

random.seed(17)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "models")
os.makedirs(OUT, exist_ok=True)

def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

def mat(name, color, rough=0.75, metal=0.0, subsurface=0.0, emission=None):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    if "Subsurface Weight" in p.inputs:
        p.inputs["Subsurface Weight"].default_value = subsurface
    if emission:
        p.inputs["Emission Color"].default_value = (*emission[0], 1)
        p.inputs["Emission Strength"].default_value = emission[1]
    return m

INK = mat("Blue black lacquer", (0.028, 0.052, 0.09), .34, .22)
WALL = mat("Aged midnight plaster", (0.065, 0.10, 0.16), .9)
WALL_LIT = mat("Moonwashed plaster", (0.20, 0.27, 0.36), .82)
WOOD = mat("Smoked walnut", (0.16, 0.075, 0.043), .45)
WOOD_LIGHT = mat("Worn walnut edges", (0.34, 0.16, 0.075), .46)
WOOD_DARK = mat("Door recess", (0.07, 0.045, 0.05), .65)
BRASS = mat("Antique brushed brass", (0.54, 0.31, 0.10), .29, .74)
GOLD = mat("Soft brass inlay", (0.91, 0.65, 0.25), .26, .6)
GLASS = mat("Amber lantern glass", (0.95, 0.48, 0.095), .18, .08, emission=((1.0,.31,.055),1.7))
MOON_GLASS = mat("Stormlit blue glass", (0.12, 0.28, 0.44), .2, .12, emission=((0.06,.18,.32),.4))
VELVET = mat("Deep teal velvet", (0.035, 0.18, 0.19), .82, 0, .08)
VELVET_EDGE = mat("Teal velvet nap", (0.08, 0.31, 0.29), .76, 0, .1)
SKIN = mat("Warm porcelain fur", (0.76, 0.57, 0.36), .67, 0, .07)
WING = mat("Indigo plumage", (0.18, 0.19, 0.36), .72, 0, .04)
WING_LIT = mat("Lilac wing sheen", (0.39, 0.35, 0.58), .66, 0, .05)
SCARF = mat("Persimmon wool scarf", (0.62, 0.16, 0.10), .82, 0, .08)
EYE = mat("Obsidian eyes", (0.008, 0.014, 0.025), .13, .15)
LEAF = mat("Dream tree jade", (0.10, 0.29, 0.24), .85)
LEAF2 = mat("Dream tree sage", (0.26, 0.39, 0.30), .82)
STONE = mat("Blue grey stone", (0.13, 0.19, 0.25), .8)

def finish(obj, material, bevel=0, smooth=True):
    if material:
        obj.data.materials.append(material)
    if smooth and obj.type == "MESH":
        for p in obj.data.polygons: p.use_smooth = True
    if bevel and obj.type == "MESH":
        mod = obj.modifiers.new("Hand softened edges", "BEVEL")
        mod.width, mod.segments = bevel, 3
        mod2 = obj.modifiers.new("Weighted highlights", "WEIGHTED_NORMAL")
    return obj

def cube(name, loc, dims, material, bevel=.04):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(o, material, bevel, False)

def sphere(name, loc, scale, material, seg=32, rings=20):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    return finish(o, material)

def cylinder(name, loc, radius, depth, material, vertices=32, axis="Z", bevel=.02):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o=bpy.context.object; o.name=name
    if axis == "Y": o.rotation_euler[0] = math.pi/2
    if axis == "X": o.rotation_euler[1] = math.pi/2
    return finish(o, material, bevel, True)

def torus(name, loc, major, minor, material, rot=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
        major_segments=64, minor_segments=12, location=loc)
    o=bpy.context.object; o.name=name
    if rot: o.rotation_euler=rot
    return finish(o, material)

def curve(name, points, bevel, material, cyclic=False, resolution=12):
    c=bpy.data.curves.new(name,"CURVE"); c.dimensions="3D"; c.resolution_u=resolution
    c.bevel_depth=bevel; c.bevel_resolution=3
    s=c.splines.new("POLY"); s.points.add(len(points)-1)
    for p, co in zip(s.points,points): p.co=(*co,1)
    s.use_cyclic_u=cyclic
    o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o)
    return finish(o,material,0,False)

def arch_curve(name, cx, y, base, radius, material, thickness, steps=48):
    pts=[(cx-radius,y,base),(cx-radius,y,base+radius)]
    for i in range(steps+1):
        a=math.pi-i*math.pi/steps
        pts.append((cx+radius*math.cos(a),y,base+radius+radius*math.sin(a)))
    pts.append((cx+radius,y,base))
    return curve(name,pts,thickness,material)

def set_origin_all():
    bpy.ops.object.select_all(action="SELECT")
    bpy.context.scene.cursor.location=(0,0,0)

def export_glb(path, objects, lights=False):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objects:
        if o and o.name in bpy.context.scene.objects: o.select_set(True)
    bpy.context.view_layer.objects.active=next((o for o in objects if o and o.type=="MESH"),None)
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True,
        export_apply=True, export_materials="EXPORT", export_cameras=False,
        export_lights=lights, export_yup=True)

def make_moth():
    start=set(bpy.context.scene.objects)
    # A soft, tapered cloak gives the small hero a readable silhouette.
    verts=[]; faces=[]; N=40
    rings=[(0.12,.24,.20),(0.24,.36,.27),(.55,.44,.31),(.90,.38,.29),(1.18,.30,.25),(1.35,.24,.22)]
    for z,rx,ry in rings:
        for i in range(N):
            a=2*math.pi*i/N
            ripple=1+(.025*math.sin(a*7) if z<.3 else 0)
            verts.append((rx*math.cos(a)*ripple,ry*math.sin(a),z))
    for r in range(len(rings)-1):
        for i in range(N):
            a=r*N+i; b=r*N+(i+1)%N
            faces.append((a,b,b+N,a+N))
    faces.append(tuple(range(N-1,-1,-1)))
    me=bpy.data.meshes.new("Tailored cloak mesh"); me.from_pydata(verts,[],faces); me.update()
    cloak=bpy.data.objects.new("Aru | hand tailored moon cloak",me); bpy.context.collection.objects.link(cloak)
    finish(cloak,VELVET,.0)
    for p in me.polygons: p.use_smooth=True
    sub=cloak.modifiers.new("Soft cloth silhouette","SUBSURF"); sub.levels=1
    # Hem piping and small stitched accents.
    pts=[(.255*math.cos(2*math.pi*i/96),.21*math.sin(2*math.pi*i/96),.16) for i in range(96)]
    curve("Scalloped teal hem piping",pts,.022,VELVET_EDGE,True)
    for i in range(13):
        a=2*math.pi*i/13
        sphere("Hand sewn hem stitch",(.278*math.cos(a),.228*math.sin(a),.18),(.017,.017,.018),GOLD,12,8)
    # Hood and soft face.
    sphere("Deep hood",(0,.015,1.44),(.39,.34,.39),VELVET,40,28)
    sphere("Porcelain moth face",(0,-.17,1.38),(.265,.205,.285),SKIN,40,28)
    # Hood brim, lifted to keep both eyes clear.
    curve("Hood embroidered rim",[(.32*math.cos(a),-.235,1.4+.09*math.sin(a)) for a in [i*math.pi/36 for i in range(37)]],.022,VELVET_EDGE)
    # Eyes with tiny warm glints.
    for side in (-1,1):
        sphere("Polished dark eye",(side*.091,-.352,1.43),(.046,.026,.060),EYE,24,16)
        sphere("Eye catchlight",(side*.105,-.375,1.45),(.010,.008,.012),GOLD,12,8)
    sphere("Tiny nose",(0,-.376,1.34),(.025,.018,.019),WOOD_DARK,16,10)
    # Curled moth antennae.
    for side in (-1,1):
        pts=[]
        for i in range(17):
            t=i/16; pts.append((side*(.12+.17*t+.045*math.sin(t*math.pi)), -.14, 1.68+.31*t-.1*t*t))
        curve("Curled velvet antenna",pts,.021,WOOD)
        sphere("Antenna gold tuft",pts[-1],(.055,.045,.067),GOLD,20,12)
    # Layered moth wings and sculpted vein lines.
    for side in (-1,1):
        w=sphere("Moon moth upper wing",(side*.50,.15,1.02),(.39,.10,.53),WING,36,24)
        w.rotation_euler[1]=side*math.radians(-17)
        w2=sphere("Moon moth lower wing",(side*.48,.13,.72),(.30,.085,.35),WING_LIT,32,20)
        w2.rotation_euler[1]=side*math.radians(19)
        for j in range(4):
            x=side*(.26+j*.07)
            curve("Wing embossed vein",[(side*.22,.045,1.17),(x,.045,1.30-j*.045),(side*(.64+j*.035),.055,1.42-j*.08)],.012,GOLD)
    # Warm scarf and flowing end.
    torus("Wool scarf collar",(0,-.015,1.12),.267,.083,SCARF)
    tail=sphere("Scarf trailing end",(.25,.08,1.02),(.30,.11,.08),SCARF,28,16); tail.rotation_euler[1]=-.38
    # Two short boots and toe caps.
    for side in (-1,1):
        sphere("Little boot",(side*.15,-.015,.14),(.13,.22,.15),INK,24,16)
        sphere("Boot brass toe",(side*.15,-.205,.12),(.10,.035,.07),BRASS,20,12)
    # Leather satchel and embossed crescent.
    cube("Traveler satchel",(-.35,-.08,.73),(.24,.19,.29),WOOD,.065)
    torus("Satchel brass clasp",(-.35,-.188,.76),.042,.009,GOLD,(math.pi/2,0,0))
    curve("Satchel shoulder strap",[(-.28,-.08,1.06),(-.38,-.11,.96),(-.43,-.12,.68),(-.36,-.10,.54)],.026,BRASS)
    # Detailed hand held lantern with framed glass and hanging loop.
    lx,ly=.57,-.11
    cube("Lantern inner glow",(lx,ly,.66),(.24,.23,.30),GLASS,.045)
    for z in (.48,.84): cube("Lantern brass cap",(lx,ly,z),(.32,.30,.055),GOLD,.024)
    for x in (lx-.145,lx+.145):
        cube("Lantern frame upright",(x,ly,.66),(.035,.30,.36),BRASS,.015)
    for y in (ly-.13,ly+.13):
        cube("Lantern frame bar",(lx,y,.66),(.29,.026,.34),BRASS,.012)
    torus("Lantern crown loop",(lx,ly,.91),.10,.018,GOLD,(math.pi/2,0,0))
    cube("Lantern handle grip",(.40,-.11,.94),(.06,.07,.25),WOOD,.025)
    # Gentle face markings and tiny cloak buttons.
    for z in (.98,.83):
        sphere("Brass cloak button",(.02,-.314,z),(.028,.013,.028),GOLD,16,10)
    return [o for o in bpy.context.scene.objects if o not in start]

def make_archive():
    start=set(bpy.context.scene.objects)
    # Broad stage floor, tall enclosing walls, beams, and dark ceiling shadow.
    cube("Archive floor",(0,0,-.30),(22,17,.55),STONE,.10)
    cube("Rear wall",(0,-5.35,4.5),(22,.45,10),WALL,.10)
    cube("Left side wall",(-10.5,0,4.0),(.55,11,9),WALL,.10)
    cube("Right side wall",(10.5,0,4.0),(.55,11,9),WALL,.10)
    for z in (0.0,7.8):
        cube("Carved wall rail",(0,-5.05,z),(21,.30,.24),WOOD_LIGHT,.06)
    for x in range(-9,10,3):
        cube("Tall wall pilaster",(x,-5.0,3.8),(.28,.42,7.4),WOOD,.05)
        cube("Pilaster brass capital",(x,-4.96,7.35),(.48,.50,.20),BRASS,.035)
    # Giant arched, paneled moon door and glowing porthole.
    dx,dy=-2.5,-4.72
    cube("Monumental door shadow",(dx,dy,2.35),(3.10,.44,4.7),WOOD_DARK,.12)
    cube("Door leaf",(dx,dy-.25,2.28),(2.66,.23,4.45),WOOD,.11)
    arch_curve("Door raised arch carving",dx,dy-.43,.12,1.34,GOLD,.055)
    for x in (dx-1.09,dx,dx+1.09):
        cube("Door inset raised panel",(x,dy-.41,2.32),(.75,.08,3.65),WOOD_LIGHT,.06)
        cube("Door panel dark inset",(x,dy-.47,2.32),(.60,.03,3.48),WOOD_DARK,.05)
        cube("Door panel inner walnut",(x,dy-.50,2.32),(.50,.025,3.32),WOOD,.045)
    torus("Door moon medallion",(dx,dy-.54,3.94),.44,.044,GOLD,(math.pi/2,0,0))
    sphere("Door moon center",(dx,dy-.56,3.94),(.29,.045,.29),WALL_LIT,32,20)
    sphere("Door brass knob",(dx+1.02,dy-.56,1.42),(.095,.07,.095),GOLD,24,16)
    for z in (.32,4.2):
        cube("Door brass strap hinge",(dx-1.30,dy-.57,z),(.16,.06,.55),BRASS,.025)
    # Giant clock face with individual ticks and hands.
    cx,cy,cz=-7.2,-4.65,5.55
    cylinder("Clock dark backing",(cx,cy,cz),1.47,.20,WOOD,64,"Y",.035)
    cylinder("Clock face porcelain",(cx,cy-.13,cz),1.28,.08,WALL_LIT,64,"Y",.025)
    torus("Clock brass bezel",(cx,cy-.19,cz),1.37,.075,GOLD,(math.pi/2,0,0))
    for i in range(12):
        a=math.pi/2-2*math.pi*i/12
        sphere("Clock raised index",(cx+1.04*math.cos(a),cy-.215,cz+1.04*math.sin(a)),(.055,.035,.055),BRASS,16,10)
    curve("Clock minute hand",[(cx,cy-.27,cz),(cx+.12,cy-.28,cz+.70)],.035,INK)
    curve("Clock hour hand",[(cx,cy-.29,cz),(cx-.55,cy-.30,cz-.22)],.055,INK)
    sphere("Clock central pin",(cx,cy-.32,cz),(.105,.045,.105),GOLD,24,14)
    # Rain window with deep, blue glazing and mullions.
    wx,wy=5.7,-5.02
    cube("Tall storm window recess",(wx,wy,3.2),(3.1,.35,5.5),INK,.10)
    cube("Storm window blue glass",(wx,wy-.21,3.2),(2.72,.07,5.12),MOON_GLASS,.06)
    arch_curve("Window brass arch",wx,wy-.27,.48,1.34,BRASS,.07)
    for x in (wx-1.29,wx,wx+1.29): cube("Window vertical mullion",(x,wy-.31,3.2),(.065,.10,4.95),GOLD,.02)
    for z in (2.0,3.25,4.5): cube("Window cross mullion",(wx,wy-.33,z),(2.68,.10,.07),GOLD,.02)
    # Dusty floorboards, inlaid brass lines, and a tiny scale cue near the hero.
    for x in range(-10,11):
        cube("Floor board seam",(x*.94,1.1,-.008),(.022,11,.014),WOOD_LIGHT,.002)
    for y in (-2.0,1.2,4.2):
        cube("Floor brass inlay",(0,y,.006),(19,.028,.018),BRASS,.004)
    # Towering bookcases and individual books create miniature scale.
    for side in (-1,1):
        bx=side*8.5; by=-3.8
        cube("Tall archive bookcase",(bx,by,3.45),(2.25,.72,6.75),WOOD,.08)
        for z in (.35,1.65,2.95,4.25,5.55,6.72):
            cube("Carved bookshelf ledge",(bx,by-.30,z),(2.36,.22,.13),WOOD_LIGHT,.025)
            cube("Shelf brass lip",(bx,by-.425,z+.035),(2.26,.025,.025),GOLD,.008)
        for shelf in range(5):
            x=bx-1.0
            while x < bx+1.0:
                width=random.uniform(.17,.34); height=random.uniform(.58,1.05)
                z=.40+shelf*1.30+height/2
                book=cube("Old ledger spine",(x+width/2,by-.20,z),(width,.30,height),random.choice([WOOD_DARK,VELVET,BRASS,INK,SCARF]),.018)
                book.rotation_euler[1]=random.uniform(-.035,.035)
                x += width+.055
    # An oversized set of gears peeks from the back wall.
    for (gx,gz,r) in ((-5.45,2.15,.88),(6.8,6.2,.74),(1.8,7.0,.43)):
        torus("Clockwork brass gear ring",(gx,-5.00,gz),r,.065,BRASS,(math.pi/2,0,0))
        cylinder("Gear dark core",(gx,-4.98,gz),r*.17,.12,WOOD,48,"Y",.01)
        for i in range(12):
            a=2*math.pi*i/12
            cube("Gear tooth",(gx+(r+.075)*math.cos(a),-5.02,gz+(r+.075)*math.sin(a)),(.13,.17,.23),GOLD,.025).rotation_euler[1]=-a
        for i in range(8):
            a=math.tau*i/8
            sphere("Gear pin",(gx+r*.72*math.cos(a),-5.10,gz+r*.72*math.sin(a)),(.035,.025,.035),WOOD_DARK,12,8)
    # Savings tree planters, symbolic rather than realistic finance guarantees.
    for x,leafmat,variant in ((4.5,LEAF,"Northwind"),(7.0,LEAF2,"Raindrop")):
        cube(variant+" dream tree plinth",(x,-.9,.13),(1.75,.95,.35),WOOD,.08)
        for i in range(3):
            cylinder(variant+" twisting trunk",(x+(i-1)*.16,-1.02,.86+i*.23),.10,.96,WOOD_LIGHT,12,"Z",.025)
        for j,(dx,dz,r) in enumerate(((-.44,1.45,.67),(.10,1.73,.78),(.52,1.42,.58),(-.22,2.05,.52))):
            sphere(variant+" dream canopy",(x+dx,-1.0,dz),(r*.84,r*.6,r),leafmat,28,18)
        for j in range(5):
            a=j*2.4
            sphere("Tree golden fruit",(x+math.cos(a)*.48,-1.47,1.35+(j%3)*.28),(.065,.055,.08),GOLD,16,10)
    # Oversized coins and a glass savings jar; strong readable learning props.
    for i,(x,z) in enumerate(((3.7,.34),(5.1,.34),(6.4,.34))):
        cylinder("Oversized star coin",(x,-2.10,z),.38,.10,GOLD,48,"Y",.018)
        sphere("Coin embossed star",(x,-2.17,z),(.17,.035,.17),GOLD,24,16)
    # Warm lanterns with metal cages, varied depth and scale.
    for i,(x,z) in enumerate(((-9,2.0),(-5,1.4),(0.1,2.7),(9,3.0),(7,5.5))):
        y=-4.60 if i<4 else -2.0
        sphere("Floating amber lantern glass",(x,y,z),(.17,.17,.25),GLASS,24,16)
        torus("Lantern brass cage",(x,y-.02,z),.20,.025,BRASS,(math.pi/2,0,0))
        torus("Lantern upper guard",(x,y,z+.20),.13,.018,GOLD)
        for dx in (-.14,.14): cylinder("Lantern cage rail",(x+dx,y,z),.016,.36,BRASS,10,"Z",.005)
    # Small stepping stones and a central perspective path.
    for i in range(7):
        y=4.7-i*1.15
        cube("Worn moonstone path",(0,y,.035),(2.8+i*.18,.10,.07),WALL_LIT,.035)
    # Tiny motes are static, emissive and intentionally sparse.
    for i in range(35):
        x=random.uniform(-9.4,9.4); y=random.uniform(-4.6,2.4); z=random.uniform(.6,6.7)
        sphere("Suspended moon dust",(x,y,z),(.018,.018,.018),GOLD,10,6)
    return [o for o in bpy.context.scene.objects if o not in start]

def make_render(scene_objects, moth_objects):
    scene=bpy.context.scene
    scene.render.engine="BLENDER_WORKBENCH"
    scene.display.shading.light="STUDIO"
    scene.display.shading.color_type="MATERIAL"
    scene.display.shading.show_cavity=True
    scene.display.shading.cavity_type="BOTH"
    scene.display.shading.curvature_ridge_factor=1.2
    scene.display.shading.cavity_valley_factor=1.1
    scene.render.resolution_x=1600; scene.render.resolution_y=900; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    scene.render.filepath=os.path.join(OUT,"moon_archive_preview.png")
    scene.world.color=(.025,.04,.07)
    scene.view_settings.view_transform="AgX"
    scene.view_settings.look="AgX - Medium High Contrast"
    scene.view_settings.exposure=-0.35
    scene.render.image_settings.color_mode="RGBA"
    camera_data=bpy.data.cameras.new("Archive Preview Camera")
    camera=bpy.data.objects.new("Archive Preview Camera",camera_data); scene.collection.objects.link(camera)
    camera.location=(0,-13.5,4.0); target=Vector((0,.8,2.4)); direction=target-Vector(camera.location)
    camera.rotation_euler=direction.to_track_quat("-Z","Y").to_euler(); camera_data.lens=28
    scene.camera=camera
    def area(name,loc,color,power,size,target):
        d=bpy.data.lights.new(name,"AREA"); d.energy=power; d.color=color; d.shape="DISK"; d.size=size
        d.use_shadow=True
        o=bpy.data.objects.new(name,d); scene.collection.objects.link(o); o.location=loc
        o.rotation_euler=(Vector(target)-o.location).to_track_quat("-Z","Y").to_euler()
    area("Cold moon key",(-4,-4,9),(.42,.60,1.0),1800,8,(0,4,1))
    area("Amber lantern bounce",(3,-3,3),(1.0,.43,.14),900,4,(2,4,1))
    area("Soft front fill",(0,-9,5),(.55,.67,1.0),1100,7,(0,4,2))
    scene.world.use_nodes=True
    bg=scene.world.node_tree.nodes.get("Background"); bg.inputs[0].default_value=(.008,.014,.028,1); bg.inputs[1].default_value=.2
    scene.render.filepath=os.path.join(OUT,"moon_archive_preview.png")
    bpy.ops.render.render(write_still=True)

def main():
    clear_scene()
    hero=make_moth()
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,"moon_moth.blend"))
    export_glb(os.path.join(OUT,"moon_moth.glb"),hero)
    clear_scene()
    set_objects=make_archive()
    # GLTF converts Blender's forward axis into Godot's -Z. Reflect the static set
    # depth so the rear wall stays behind the hero when viewed by Godot's +Z camera.
    for o in set_objects:
        if o.type == "MESH":
            o.location.y = -o.location.y
        elif o.type == "CURVE":
            for spline in o.data.splines:
                for point in spline.points:
                    point.co.y = -point.co.y
    # Place the original moth just right of the UI panel, on the front stage plane.
    hero=make_moth()
    # The archive is authored around a 2.4 m child. Shift the character into the clear,
    # warmly lit foreground next to the learning panel.
    for o in hero:
        o.location.x += 3.15
        o.location.y -= 1.35
    # Save hero and room as one instantiable Godot scene; distinct collection names aid inspection.
    full=[o for o in bpy.context.scene.objects if o.type in {"MESH","CURVE"}]
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,"moon_archive.blend"))
    export_glb(os.path.join(OUT,"moon_archive.glb"),full)
    if os.environ.get("MOON_RENDER_PREVIEW") == "1":
        make_render(set_objects,hero)
    print("Created moon_moth.glb and moon_archive.glb")

if __name__=="__main__": main()
