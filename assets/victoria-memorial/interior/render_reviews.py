"""Original asset previews and a small, explicitly offline review set."""
import bpy
import argparse
import json
import math
import sys
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
from pipeline import bp, material

def setup():
    scene=bpy.data.scenes.new('VIC_Review_Only')
    bpy.context.window.scene=scene
    scene.render.engine='BLENDER_EEVEE'
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.view_settings.view_transform='Standard'
    world=bpy.data.worlds.new('VIC_ReviewWorld')
    if world.node_tree is None:world.use_nodes=True
    node=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND')
    node.inputs['Color'].default_value=(.45,.50,.52,1)
    node.inputs['Strength'].default_value=.7
    scene.world=world
    camera=bpy.data.objects.new('VIC_ReviewCamera',bpy.data.cameras.new('VIC_ReviewCamera'))
    scene.collection.objects.link(camera);scene.camera=camera
    sun=bpy.data.objects.new('VIC_ReviewSun',bpy.data.lights.new('VIC_ReviewSun','SUN'))
    sun.data.energy=2.0;sun.data.angle=.3;sun.rotation_euler=(.45,-.5,-.35)
    scene.collection.objects.link(sun)
    fill=bpy.data.objects.new('VIC_ReviewFill',bpy.data.lights.new('VIC_ReviewFill','AREA'))
    fill.location=(0,5,12);fill.data.energy=550;fill.data.shape='DISK';fill.data.size=12
    scene.collection.objects.link(fill)
    return scene

def frame_camera(scene,points,w=600,h=600):
    lo=Vector(tuple(min(p[i] for p in points) for i in range(3)))
    hi=Vector(tuple(max(p[i] for p in points) for i in range(3)))
    target=(lo+hi)/2
    radius=max(hi-lo)
    scene.render.resolution_x=w;scene.render.resolution_y=h
    cam=scene.camera;cam.data.type='ORTHO'
    cam.location=target+Vector((1,1.6,.85)).normalized()*max(radius,1)*3
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.clip_end=2000
    bpy.context.view_layer.update()
    inv=cam.matrix_world.inverted();projected=[inv@p for p in points]
    spanX=max(p.x for p in projected)-min(p.x for p in projected)
    spanY=max(p.y for p in projected)-min(p.y for p in projected)
    cam.data.ortho_scale=max(spanX,spanY*w/h)*1.17

def render_assets(scene,rows):
    for row in rows:
        collection=bpy.data.collections[row['assetId']]
        scene.collection.children.link(collection)
        bpy.context.view_layer.update()
        objects=[o for o in collection.objects if o.type=='MESH']
        points=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
        frame_camera(scene,points)
        scene.render.filepath=str(BASE/row['preview'])
        bpy.ops.render.render(write_still=True)
        scene.collection.children.unlink(collection)
        print('PREVIEW '+row['assetId'],flush=True)

def instance(scene,asset_id,pos,yaw=0,collection=None):
    obj=bpy.data.objects.new(asset_id+'_review',None)
    obj.instance_type='COLLECTION';obj.instance_collection=collection or bpy.data.collections[asset_id]
    obj.location=bp(pos);obj.rotation_euler=(0,0,yaw)
    scene.collection.objects.link(obj)
    return obj

def render_vignettes(scene,placements,selected_rooms=None):
    review_dir=BASE/'review';review_dir.mkdir(exist_ok=True)
    # Read-only linked approved shell provides honest proportion/context. It is
    # excluded from all new-library counts and is never rewritten or exported.
    source=BASE.parent/'VictoriaMemorial.blend'
    with bpy.data.libraries.load(str(source),link=True) as (available,load):
        load.collections=['VM_Architecture','VM_Structure_Collision','VM_Interior']
    for collection in load.collections:scene.collection.children.link(collection)
    layout=bpy.data.collections.new('AssemblyHelpers_Task007Partitions')
    scene.collection.children.link(layout)
    def block(name,pos,size):
        bpy.ops.mesh.primitive_cube_add(size=1,location=bp(pos))
        obj=bpy.context.object;obj.name=name;obj.dimensions=(size[0],size[2],size[1])
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        for c in list(obj.users_collection):c.objects.unlink(obj)
        layout.objects.link(obj);obj.data.materials.append(material('Stone'))
    for x in [-66,69]:
        for lo,hi in [(-93,-89),(-79,-71),(-61,-59)]:block('ApprovedPartition',(x,17,(lo+hi)/2),(1,20.4,hi-lo))
        for z in [-84,-66]:block('ApprovedDoorLintel',(x,24,z),(1,6.4,10))
    art_manifest=json.loads((BASE/'artwork/manifest.json').read_text())
    images={r['artworkId']:r for r in art_manifest['artworks']}
    artwork_for_frame={r['frameInstance']:r['artworkId'] for r in placements['artworkBindings']}
    variants={}
    for p in placements['instances']:
        collection=None
        if p['instanceId'] in artwork_for_frame:
            aid=artwork_for_frame[p['instanceId']]
            if aid not in variants:
                collection=bpy.data.collections.new('ReviewOnly_'+aid)
                for original in bpy.data.collections[p['assetId']].objects:
                    copy=original.copy()
                    if original.type=='MESH' and original.get('Component')=='Canvas':
                        copy.data=original.data.copy()
                        mat=bpy.data.materials.new('ReviewOnly_'+aid)
                        if mat.node_tree is None:mat.use_nodes=True
                        shader=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
                        shader.inputs['Roughness'].default_value=.88
                        image=bpy.data.images.load(str(BASE/images[aid]['texture']),check_existing=True)
                        image.pack()
                        texture=mat.node_tree.nodes.new('ShaderNodeTexImage');texture.image=image
                        mat.node_tree.links.new(texture.outputs['Color'],shader.inputs['Base Color'])
                        copy.data.materials.clear();copy.data.materials.append(mat)
                    collection.objects.link(copy)
                variants[aid]=collection
            collection=variants[aid]
        instance(scene,p['assetId'],p['position'],p.get('yaw',0),collection)
    fill=bpy.data.objects.new('ReviewRoomFill',bpy.data.lights.new('ReviewRoomFill','AREA'))
    fill.data.energy=2200;fill.data.size=22;fill.rotation_euler=(0,0,0)
    fill.data.color=(1.0,.90,.74)
    scene.collection.objects.link(fill)
    cameras=[]
    specs=[
        dict(name='hall_language',camera=(0,15,-24),target=(0,21,2),fill=(0,55,0)),
        dict(name='public_display_language',camera=(-28,15,-76),target=(-54,11,-76),fill=(-48,28,-76)),
        dict(name='painting_gallery_language',camera=(-24,15,76),target=(-62,11,76),fill=(-60,28,76)),
        dict(name='sculpture_gallery_language',camera=(26,15,76),target=(62,11,76),fill=(60,28,76)),
        dict(name='high_security_language',camera=(33,15,-76),target=(59,11,-76),fill=(50,28,-76)),
        dict(name='archive_language',camera=(71,15,-66),target=(82,11,-79),fill=(79,28,-76)),
        dict(name='collections_language',camera=(-69,15,-84),target=(-82,11,-76),fill=(-78,28,-76)),
    ]
    scene.render.resolution_x=1400;scene.render.resolution_y=900
    scene.render.engine='CYCLES'
    scene.cycles.samples=16;scene.cycles.use_denoising=True
    for spec in specs:
        cam=bpy.data.objects.new('ReviewCamera_'+spec['name'],bpy.data.cameras.new('ReviewCamera_'+spec['name']))
        scene.collection.objects.link(cam);cameras.append(cam);scene.camera=cam
        cam.data.type='PERSP';cam.data.lens=22
        cam.location=bp(spec['camera']);target=Vector(bp(spec['target']))
        cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
        fill.location=bp(spec['fill'])
        if selected_rooms and spec['name'] not in selected_rooms:continue
        scene.render.filepath=str(review_dir/(spec['name']+'.png'))
        bpy.ops.render.render(write_still=True)
        print('ASSEMBLED REVIEW '+spec['name'],flush=True)
    scene.camera=cameras[1]
    fill.location=bp(specs[1]['fill'])
    scene.name='VIC_Offline_ArtPreview'
    scene['Scope']='Read-only original shell + exact Task007 partitions + proposed art. Not Studio integration.'
    for library in bpy.data.libraries:
        if Path(library.filepath).name=='VictoriaMemorial.blend':library.filepath='//../VictoriaMemorial.blend'
    bpy.data.libraries.write(str(BASE/'VIC_Interior_ArtPreview.blend'),{scene},fake_user=True,compress=True)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--assets',nargs='*')
    parser.add_argument('--rooms',nargs='*')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    with bpy.data.libraries.load(str(BASE/'VIC_Interior_Library.blend')) as (available,load):load.scenes=list(available.scenes)
    scene=setup()
    rows=json.loads((BASE/'asset-manifest.json').read_text())['assets']
    render_assets(scene,[r for r in rows if args.assets is None or r['assetId'] in args.assets])
    placement_path=BASE/'placement-manifest.json'
    if placement_path.exists():render_vignettes(scene,json.loads(placement_path.read_text()),args.rooms)

if __name__=='__main__':main()
