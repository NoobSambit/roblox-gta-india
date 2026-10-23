"""One focused geometry/export pass and original day/court/night previews."""
import bpy
import json
import sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
import estate_common as C
sys.path.insert(0,str(BASE.parent/'tier1'))
from review_assets import validate,aim


def layout_sanity(row,scene):
    verts=[];faces=[]
    for obj in scene.objects:
        if obj.type!='MESH':continue
        start=len(verts);verts.extend(obj.matrix_world@v.co for v in obj.data.vertices)
        faces.extend(tuple(start+i for i in p.vertices) for p in obj.data.polygons)
    tree=BVHTree.FromPolygons(verts,faces,all_triangles=True)
    for x,z in row['layout']['openSkyChecksXZ']:
        hit=tree.ray_cast(Vector(C.bv((x,150,z))),Vector((0,0,-1)),148)[0]
        assert hit is None,('court is roofed/obstructed',x,z,hit)
    rays=[row['layout']['entryRay']]
    if row['assetId']=='KOL_T1_JORASANKO':
        assert scene['MainBuildingCount']==2
        assert all(any(s['section']==b['collection'] for s in row['exports']) for b in row['layout']['buildings'])
        rays.extend([dict(origin=[0,7,-140],direction=[0,0,1],length=45),
                     dict(origin=[65,7,135],direction=[0,0,-1],length=34),
                     dict(origin=[0,7,-27],direction=[0,0,1],length=75)])
    for ray in rays:
        origin=Vector(C.bv(ray['origin']));direction=Vector(C.bv(ray['direction']))
        hit=tree.ray_cast(origin,direction,ray['length'])[0]
        assert hit is None,('entry route blocked',ray,hit)
    assert max(s['rangeStuds'] for s in row['nightLights'])<=60
    return dict(openSkyCourts=len(row['layout']['openSkyChecksXZ']),clearHeadHeightEntryRays=len(rays),
        mainBuildingCount=row['layout'].get('mainBuildingCount',1),nightLights=len(row['nightLights']))


def render_views(key,row,scene,only=None):
    folder=BASE/key
    for col in list(scene.collection.children):
        if col.name.startswith('REVIEW_CAMERA_SUN__NOT_FBX'):
            for obj in list(col.objects):bpy.data.objects.remove(obj,do_unlink=True)
            bpy.data.collections.remove(col)
    rig=bpy.data.collections.new('REVIEW_CAMERA_SUN__NOT_FBX');scene.collection.children.link(rig)
    data=bpy.data.cameras.new('Cultural review camera');cam=bpy.data.objects.new(data.name,data);rig.objects.link(cam);scene.camera=cam
    data.type='ORTHO';data.clip_start=.1;data.clip_end=2000
    scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True
    scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
    scene.world=bpy.data.worlds.new('Cultural daylight')
    bg=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND')
    sd=bpy.data.lights.new('Review sun','SUN');sun=bpy.data.objects.new(sd.name,sd);rig.objects.link(sun)
    sun.rotation_euler=(.45,-.4,-.6);sd.angle=.22
    installed=[o for o in scene.objects if o.type=='LIGHT' and o.get('NightWatts')]
    pts=[o.matrix_world@Vector(p) for o in scene.objects if o.type=='MESH' for p in o.bound_box]
    lo=Vector([min(p[i] for p in pts) for i in range(3)]);hi=Vector([max(p[i] for p in pts) for i in range(3)])
    center=(lo+hi)/2;span=max(hi-lo)
    overview=(1,2,1.65)
    views=[('preview-day',overview,False,None,None),('preview-rear',(-1,-2,1.6),False,None,None),
        ('preview-courtyard',(1,2,.8),False,(0,35,24) if key=='rajbari' else (0,20,0),138 if key=='rajbari' else 185),
        ('preview-night',overview,True,None,None)]
    if key=='jorasanko':views.append(('preview-front',(1,2,.8),False,(0,27,-119),160))
    outputs=[]
    for name,direction,night,target_,scale in views:
        if only and name not in only:continue
        target=Vector(C.bv(target_)) if target_ else center
        cam.location=target+Vector(direction).normalized()*span*3;aim(cam,target)
        if scale:data.ortho_scale=scale
        else:
            inv=cam.rotation_euler.to_matrix().transposed();local=[inv@(p-target) for p in pts]
            xs=[p.x for p in local];ys=[p.y for p in local]
            data.ortho_scale=max(max(xs)-min(xs),(max(ys)-min(ys))*1.4)*1.08
            cam.location+=cam.rotation_euler.to_matrix()@Vector(((max(xs)+min(xs))/2,(max(ys)+min(ys))/2,0))
        if target_:
            # Court camera is physically inside the compound, rather than looking
            # through the opaque street wing with a long-distance orthographic ray.
            cam.location=Vector(C.bv((85,50,-225) if name=='preview-front' else (25,40,-49) if key=='rajbari' else (30,34,-81)))
            aim(cam,target);data.type='PERSP';data.lens=25
        else:data.type='ORTHO'
        bg.inputs['Color'].default_value=(.09,.12,.18,1) if night else (.34,.43,.55,1)
        bg.inputs['Strength'].default_value=.5 if night else .7
        sd.energy=.18 if night else 2.5;sd.color=(.48,.6,1) if night else (1,.94,.84)
        for obj in installed:obj.data.energy=obj['NightWatts']*(1 if night else .03)
        scene.render.filepath=str(folder/(name+'.png'));bpy.ops.render.render(write_still=True);outputs.append(name+'.png')
    for obj in installed:obj.data.energy=obj['NightWatts']
    sd.energy=2.5;sd.color=(1,.94,.84);bg.inputs['Color'].default_value=(.34,.43,.55,1);bg.inputs['Strength'].default_value=.7
    scene['ProductionStage']='Reviewed cultural compound; day, courtyard, rear and night originals saved'
    bpy.data.libraries.write(str(folder/row['source']),{scene},fake_user=True,compress=True)
    return outputs


if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['rajbari','jorasanko']
    only=[arg.split('=',1)[1] for arg in args if arg.startswith('--view=')]
    keys=[arg for arg in args if not arg.startswith('--view=')]
    for key in keys:
        folder=BASE/key;row=json.loads((folder/'asset.json').read_text(encoding='utf8'))
        bpy.ops.wm.open_mainfile(filepath=str(folder/row['source']));scene=bpy.context.scene
        if only:report=json.loads((folder/'validation.json').read_text(encoding='utf8'))
        else:
            report=validate(row,folder,scene);report.update(layout_sanity(row,scene))
            print('CULTURAL_CHECK_PASSED '+key,flush=True)
        report['previews']=list(dict.fromkeys(report.get('previews',[])+render_views(key,row,scene,only)))
        (folder/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
        print('CULTURAL_REVIEW_READY '+key,flush=True)
