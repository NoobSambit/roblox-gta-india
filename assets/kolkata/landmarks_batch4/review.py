"""One essential source/FBX sanity pass and four final review views per landmark."""
import bpy
import bmesh
import json
import math
import sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from io_scene_fbx import parse_fbx
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
from common import bv


def aim(obj,target):obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()


def bounds(objects):
    pts=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box]
    return [min(p[i] for p in pts) for i in range(3)]+[max(p[i] for p in pts) for i in range(3)]


def sanity(row,scene,folder):
    source=bpy.data.collections[row['sourceCollection']]
    objects=[o for o in source.all_objects if o.type=='MESH']
    unique={o.data for o in objects};errors=[]
    for m in unique:
        assert all(math.isfinite(c) for v in m.vertices for c in v.co),m.name
        bm=bmesh.new();bm.from_mesh(m)
        bad=sum(not e.is_manifold for e in bm.edges);winding=sum(e.is_manifold and not e.is_contiguous for e in bm.edges)
        bm.free()
        degenerate=sum(p.area<1e-8 for p in m.polygons)
        if bad or winding or degenerate:errors.append(dict(mesh=m.name,nonmanifold=bad,winding=winding,degenerate=degenerate))
        assert len(m.uv_layers)>0,m.name
    assert not errors,errors
    reports=[]
    for part in row['exports']:
        root,version=parse_fbx.parse(str(folder/part['file']))
        obs=next(e for e in root.elems if e.id==b'Objects')
        geo=[e for e in obs.elems if e.id==b'Geometry'];total=0;largest=0
        for m in geo:
            indices=next(e for e in m.elems if e.id==b'PolygonVertexIndex').props[0]
            count=sum(i<0 for i in indices)
            assert len(indices)==count*3,(part['file'],'non-triangle data')
            assert count<15000,(part['file'],count)
            assert any(e.id==b'LayerElementUV' for e in m.elems),(part['file'],'UV missing')
            total+=count;largest=max(largest,count)
        assert total==part['triangles']
        assert len(geo)==part['meshInstances']
        reports.append(dict(file=part['file'],triangles=total,meshObjects=len(geo),largestMeshTriangles=largest,fbxVersion=version))
    sample=max(row['exports'],key=lambda r:r['triangles'])
    expected=bounds([o for o in objects if o['Section']==sample['section']])
    temp=bpy.data.scenes.new('BATCH4_ROUNDTRIP');bpy.context.window.scene=temp
    bpy.ops.import_scene.fbx(filepath=str(folder/sample['file']))
    imported=[o for o in temp.objects if o.type=='MESH'];actual=bounds(imported)
    err=max(abs(a-b) for a,b in zip(expected,actual));assert err<.001,(expected,actual,err)
    assert all(abs(s-1)<1e-5 for o in imported for s in o.scale)
    assert all(o.data.materials and o.data.uv_layers for o in imported)
    bpy.context.window.scene=scene
    for o in list(temp.objects):bpy.data.objects.remove(o,do_unlink=True)
    bpy.data.scenes.remove(temp)
    extra={}
    if row['assetId']=='KOL_T1_NEW_MARKET':
        def tree_for(obs):
            vs=[];fs=[]
            for o in obs:
                off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices)
                fs.extend(tuple(off+i for i in p.vertices) for p in o.data.polygons)
            return BVHTree.FromPolygons(vs,fs,all_triangles=True)
        roof=tree_for([o for o in objects if o.name.startswith('Long_ridged_market_roof')])
        rays=0
        for z in [-55,70]:
            for x in [-128,-104,-80,-56,-32,-8,16,40,64,88,112,128]:
                assert roof.ray_cast(Vector(bv((x,80,z))),Vector((0,0,-1)),65)[0] is not None,('roof strip open',x,z)
                rays+=1
        shell=tree_for(objects)
        for x in [18,27,36]:
            assert shell.ray_cast(Vector(bv((x,7,-80))),Vector(bv((0,0,1))),35)[0] is None,('entry blocked',x)
        extra=dict(frontRearRoofCoverageRays=rays,clearEntranceRays=3,entranceWidthStuds=scene['MainEntranceWidthStuds'],entranceDepthStuds=scene['MainEntranceDepthStuds'])
    return dict(status='passed',sourceUniqueMeshes=len(unique),sourceMeshInstances=len(objects),finiteVertices=True,
        nonManifoldEdges=0,inconsistentWinding=0,degenerateFaces=0,sourceUVsPresent=True,allExportMeshesUnder15000=True,
        exports=reports,representativeRoundTrip=sample['file'],roundTripBoundsErrorStuds=err,roundTripMaterialsAndUVs=True,
        limitations='No Studio integration, collision/player traversal test, gameplay test, or device performance measurement.',**extra)


def render(key,row,scene,only=None):
    old_pose=(scene.camera.location.copy(),scene.camera.rotation_euler.copy(),scene.camera.data.ortho_scale) if scene.camera else None
    for col in list(scene.collection.children):
        if col.name.startswith('99_ReviewRig_NOT_FBX'):
            for o in list(col.objects):bpy.data.objects.remove(o,do_unlink=True)
            bpy.data.collections.remove(col)
    source=bpy.data.collections[row['sourceCollection']]
    pts=[o.matrix_world@Vector(v) for o in source.all_objects if o.type=='MESH' for v in o.bound_box]
    lo=Vector([min(v[i] for v in pts) for i in range(3)]);hi=Vector([max(v[i] for v in pts) for i in range(3)])
    span=max(hi-lo);center=(hi+lo)/2
    rig=bpy.data.collections.new('99_ReviewRig_NOT_FBX');scene.collection.children.link(rig)
    cd=bpy.data.cameras.new('Architectural_review');cam=bpy.data.objects.new(cd.name,cd);rig.objects.link(cam);scene.camera=cam
    cd.type='ORTHO';cd.clip_start=.1;cd.clip_end=4000
    scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
    scene.render.resolution_x=1600;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
    scene.world=bpy.data.worlds.new('Batch4_preview_sky')
    bg=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND')
    sd=bpy.data.lights.new('Daylight_only','SUN');sun=bpy.data.objects.new(sd.name,sd);rig.objects.link(sun)
    sun.rotation_euler=(-.55,.4,-.4);sd.angle=.16
    lights=[o for o in scene.objects if o.type=='LIGHT' and o.get('NightWatts')]
    # Museum grounds view also exposes the complete quadrangle; cathedral hero shows
    # its nave and crossing together rather than hiding its length behind the west end.
    hero=(.6,2,.36) if key=='new_market' else (.6,2,.65) if key=='indian_museum' else (2,1.2,.85)
    elev=(1.25,2,1.7) if key!='st_pauls' else (1.7,1.5,1.8)
    ground=(.5,1,3.7)
    reverse=(-1,-2,.9) if key!='st_pauls' else (-2,-1.2,.9)
    views=[('hero',hero,False),('elevated',elev,False),('grounds',ground,False),('night-rear',reverse,True),('night',hero,True)]
    outputs=[]
    for name,direction,night in views:
        if only and name not in only:continue
        target=center.copy();cam.location=target+Vector(direction).normalized()*span*3;aim(cam,target)
        inv=cam.rotation_euler.to_matrix().transposed();ps=[inv@(v-target) for v in pts]
        xmin,xmax=min(v.x for v in ps),max(v.x for v in ps);ymin,ymax=min(v.y for v in ps),max(v.y for v in ps)
        aspect=scene.render.resolution_x/scene.render.resolution_y
        cd.ortho_scale=max(xmax-xmin,(ymax-ymin)*aspect)*1.08
        cam.location+=cam.rotation_euler.to_matrix()@Vector(((xmin+xmax)/2,(ymin+ymax)/2,0))
        bg.inputs['Color'].default_value=(.12,.17,.27,1) if night else (.48,.56,.65,1)
        bg.inputs['Strength'].default_value=.55 if night else .6
        sd.energy=.22 if night else 2.7;sd.color=(.5,.64,1) if night else (1,.94,.84)
        for o in lights:o.data.energy=o['NightWatts']*(1 if night else 0)
        scene.render.filepath=str(BASE/key/('preview-'+name+'.png'));bpy.ops.render.render(write_still=True)
        outputs.append('preview-'+name+'.png')
    # Return the stored presentation to daylight, not the last night render.
    sd.energy=2.7;sd.color=(1,.94,.84);bg.inputs['Color'].default_value=(.48,.56,.65,1);bg.inputs['Strength'].default_value=.6
    for o in lights:o.data.energy=0
    if only and old_pose:cam.location=old_pose[0];cam.rotation_euler=old_pose[1];cd.ortho_scale=old_pose[2]
    scene['ProductionStage']='Essential geometry/FBX check and original review views saved'
    # Normal master files reopen on their asset scene, rather than as append-only
    # library files. Only this landmark has been opened by the review process.
    for other in list(bpy.data.scenes):
        if other!=scene:bpy.data.scenes.remove(other)
    bpy.context.window.scene=scene
    bpy.ops.wm.save_as_mainfile(filepath=str(BASE/key/row['source']),compress=True)
    return outputs


if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['new_market','indian_museum','st_pauls']
    only=[a.split('=',1)[1] for a in args if a.startswith('--view=')]
    for key in [a for a in args if not a.startswith('--')]:
        folder=BASE/key;row=json.loads((folder/'asset.json').read_text())
        bpy.ops.wm.open_mainfile(filepath=str(folder/row['source']));scene=bpy.data.scenes[row['assetId']];bpy.context.window.scene=scene
        report=sanity(row,scene,folder) if not only else json.loads((folder/'validation.json').read_text())
        print('BATCH4_SANITY '+key+' '+report['status'],flush=True)
        report['previews']=list(dict.fromkeys(report.get('previews',[])+render(key,row,scene,only)))
        (folder/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
        print('BATCH4_REVIEW_READY '+key,flush=True)
