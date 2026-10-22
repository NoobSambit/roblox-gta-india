"""Run in Blender; call render_view(name). Presentation lights are not game assets."""
import bpy
from mathutils import Vector
from pathlib import Path

OUT=Path(r"C:\Users\Sambit Pradhan\Documents\Indian_Hood\artifacts\review\victoria")
VIEWS={
    "north-elevation": ((0,31,-420),(0,62,0),40),
    "south-elevation": ((0,34,420),(0,62,0),40),
    "east-quadrangle": ((400,58,-30),(0,55,0),40),
    "west-quadrangle": ((-400,58,30),(0,55,0),40),
    "hero-exterior": ((285,186,-350),(0,47,0),43),
    "campus-overview": ((420,430,-470),(0,15,0),42),
    "queens-hall": ((0,13,-24),(0,18,0),19),
    "queens-dome": ((0,11,-1),(0,106,0),14),
    "entrance-hall": ((0,12,-87),(0,26,-28),20),
    "gallery-shell": ((-35,12,-76),(-87,22,-76),21),
    "courtyard-walk": ((84,12,-36),(19,45,18),25),
    "corner-tower-close": ((185,105,-180),(105,84,-77),40),
}

def bv(p):return (p[0],-p[2],p[1])

def render_view(name):
    scene=bpy.context.scene
    camera=scene.camera
    pos,target,lens=VIEWS[name]
    camera.location=bv(pos)
    camera.rotation_euler=(Vector(bv(target))-camera.location).to_track_quat("-Z","Y").to_euler()
    camera.data.lens=lens
    scene.render.resolution_x=1200;scene.render.resolution_y=850
    scene.render.resolution_percentage=100
    scene.render.engine="BLENDER_EEVEE"
    scene.render.filepath=str(OUT/(name+".png"))
    bpy.ops.render.render(write_still=True)
    print("Saved",name)

if not bpy.data.objects.get("VM_InteriorPresentation"):
    light=bpy.data.lights.new("VM_InteriorPresentation","AREA")
    light.energy=125000;light.size=25;light.color=(1,.91,.76)
    obj=bpy.data.objects.new("VM_InteriorPresentation",light)
    bpy.data.collections["VM_Presentation"].objects.link(obj)
    obj.location=bv((0,61,0));obj.rotation_euler=(0,0,0)
