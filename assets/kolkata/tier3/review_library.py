"""One front/corner thumbnail per asset for the required brief family review."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector

BASE=Path(r'C:\Users\Sambit Pradhan\Documents\Indian_Hood\assets\kolkata\tier3')
ROOT=BASE.parents[2];OUT=ROOT/'artifacts/review/tier3';OUT.mkdir(parents=True,exist_ok=True)

def setup():
    scene=bpy.data.scenes.get('T3_AUTHORING_REVIEW')
    if scene:return scene
    scene=bpy.data.scenes.new('T3_AUTHORING_REVIEW')
    scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True
    # Low-sample CPU thumbnails avoid platform-specific viewport render failures.
    scene.render.resolution_x=480;scene.render.resolution_y=480;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='Standard'
    world=bpy.data.worlds.new('T3_Review_World');world.use_nodes=True
    bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND')
    bg.inputs['Color'].default_value=(.45,.52,.57,1)
    bg.inputs['Strength'].default_value=.8;scene.world=world
    camera=bpy.data.objects.new('T3_Review_Camera',bpy.data.cameras.new('T3_Review_Camera'))
    scene.collection.objects.link(camera);scene.camera=camera;camera.data.type='ORTHO'
    light=bpy.data.objects.new('T3_Review_Key',bpy.data.lights.new('T3_Review_Key','AREA'))
    light.data.energy=18000;light.data.shape='DISK';light.data.size=55
    light.location=(30,25,65);light.rotation_euler=(Vector((0,0,15))-light.location).to_track_quat('-Z','Y').to_euler()
    scene.collection.objects.link(light)
    mesh=bpy.data.meshes.new('T3_Review_Ground');mesh.from_pydata([(-140,-140,-.08),(140,-140,-.08),(140,140,-.08),(-140,140,-.08)],[],[(0,1,2,3)])
    floor=bpy.data.objects.new('T3_Review_Ground',mesh);scene.collection.objects.link(floor)
    m=bpy.data.materials.new('T3_Review_Ground');m.diffuse_color=(.16,.2,.21,1);m.use_nodes=True
    next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'].default_value=(.16,.2,.21,1);mesh.materials.append(m)
    return scene

def render_family(family,only=None):
    scene=setup();bpy.context.window.scene=scene
    rows=json.loads((BASE/'asset-manifest.json').read_text(encoding='utf8'))
    for row in rows:
        if row['family']!=family or (only and row['id'] not in only):continue
        asset=bpy.data.scenes[row['id']];collection=next(iter(asset.collection.children))
        for c in list(scene.collection.children):scene.collection.children.unlink(c)
        scene.collection.children.link(collection)
        dims=row['dimensionsStuds'];w,h,d=(dims[k] for k in ['width','height','depth'])
        target=Vector((0,0,h*.46))
        scene.camera.location=target+Vector((.95,1.6,.73))*max(w,h,d)*1.5
        scene.camera.rotation_euler=(target-scene.camera.location).to_track_quat('-Z','Y').to_euler()
        scene.camera.data.ortho_scale=max(h*1.25,(w+d)*.86)
        scene.render.filepath=str(OUT/(row['id']+'.png'))
        bpy.ops.render.render(write_still=True)
        print('REVIEW '+row['id'],flush=True)
    for c in list(scene.collection.children):scene.collection.children.unlink(c)

if __name__=='__main__':
    for family in ['old_kolkata','modern','mixed_use','informal']:render_family(family)
