"""One focused asset/export check and four original review renders."""
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'tier2'))
sys.path.insert(0,str(HERE.parent/'tier1'))
from review_assets import validate,aim
from geometry import bv


def focused_check(scene,row):
    modules=[o for o in scene.objects if o.get('ShrineIndex')]
    placements={o['ShrineIndex']:tuple(o.location) for o in modules}
    assert len(placements)==12 and len(set(placements.values()))==12
    for mesh in {o.data for o in modules}:
        assert sum(o.data==mesh for o in modules)==12,('Shiva mesh not shared',mesh.name)
    spires={tuple(o.location) for o in scene.objects if o.name.startswith('Ratna_')}
    assert len(spires)==9
    lights=[o for o in scene.objects if o.type=='LIGHT']
    assert len(lights)==20 and sum(o.data.use_shadow for o in lights)==1
    verts=[];faces=[]
    for obj in scene.objects:
        if obj.type!='MESH':continue
        offset=len(verts);verts.extend(obj.matrix_world@v.co for v in obj.data.vertices)
        faces.extend(tuple(offset+i for i in p.vertices) for p in obj.data.polygons)
    tree=BVHTree.FromPolygons(verts,faces,all_triangles=True)
    # Eye-height access through both the main front bay and shrine doorway.
    hit=tree.ray_cast(Vector(bv((0,12,-34))),Vector(bv((0,0,1))),51)[0]
    assert hit is None,('central shrine approach blocked',hit)
    # Measure actual exposed elevations at the courtyard/ghat junction.
    def top(x,z):
        hit=tree.ray_cast(Vector(bv((x,50,z))),Vector((0,0,-1)),70)[0]
        assert hit is not None
        return hit.z
    heights={'courtyard':top(110,-80),'threshold':top(110,-84),'firstStep':top(110,-88)}
    assert abs(heights['courtyard']-.8)<.001 and abs(heights['threshold']-1)<.001
    assert abs(heights['firstStep']-.5)<.001
    # Stair tread solids overlap both separator edges; no narrow open slits.
    for x in [52.4,55.6,-52.4,-55.6]:assert abs(top(x,-88)-.5)<.001
    # Sample the actual red panel face, formerly coplanar with its wall.
    red=[o for o in scene.objects if o.name.startswith('Lower_curved_cornice') and 'TempleRed' in o.name]
    rv=[];rf=[]
    for obj in red:
        off=len(rv);rv.extend(obj.matrix_world@v.co for v in obj.data.vertices)
        rf.extend(tuple(off+i for i in p.vertices) for p in obj.data.polygons)
    redtree=BVHTree.FromPolygons(rv,rf,all_triangles=True)
    hit=redtree.ray_cast(Vector(bv((0,46,-20))),Vector(bv((0,0,1))),10)[0]
    assert hit and abs(hit.y-16.75)<.001,('frieze panel is not proud of wall',hit)
    assert row['uniqueSourceTriangles']<=55000 and row['assembledTriangles']<=95000
    return dict(mainSpires=9,linkedShivaPlacements=12,workingBlenderLights=20,shadowCastingLights=1,
        mainApproachOpenAtEyeHeight=True,groundExposedHeightsStuds=heights,friezeFaceProjectionStuds=.45)


def render_views(scene):
    rig=bpy.data.collections.new('PREVIEW_ONLY__NOT_EXPORTED');scene.collection.children.link(rig)
    camera_data=bpy.data.cameras.new('Original asset preview');cam=bpy.data.objects.new('Original asset preview',camera_data)
    rig.objects.link(cam);scene.camera=cam;camera_data.clip_start=.1;camera_data.clip_end=2000
    sun_data=bpy.data.lights.new('Preview daylight','SUN');sun=bpy.data.objects.new('Preview daylight',sun_data)
    rig.objects.link(sun);sun.rotation_euler=(math.radians(28),math.radians(-30),math.radians(-28));sun_data.angle=.25
    scene.world=bpy.data.worlds.new('Dakshineshwar preview sky')
    bg=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND')
    scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
    scene.render.resolution_x=1400;scene.render.resolution_y=950;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
    scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.3
    original_lights=[o for o in scene.objects if o.type=='LIGHT' and o.get('NightWatts')]
    configs=[
        ('preview-campus',(260,450,255),(0,10,55),'ORTHO',480,False),
        ('preview-river',(-160,350,55),(0,-10,55),'PERSP',48,False),
        ('preview-shrine',(0,4,19),(0,-28,20),'PERSP',24,True),
        ('preview-night',(230,420,210),(0,10,55),'ORTHO',480,True),
    ]
    previews=[]
    for name,position,target,kind,size,night in configs:
        camera_data.type=kind
        if kind=='ORTHO':camera_data.ortho_scale=size
        else:camera_data.lens=size
        cam.location=position;aim(cam,target)
        bg.inputs['Color'].default_value=(.025,.04,.08,1) if night else (.34,.43,.55,1)
        bg.inputs['Strength'].default_value=.22 if night else .65
        sun_data.energy=.08 if night else 2.5;sun_data.color=(.5,.65,1) if night else (1,.93,.8)
        for obj in original_lights:obj.data.energy=obj['NightWatts']*(1 if night else .1)
        scene.render.filepath=str(HERE/(name+'.png'));bpy.ops.render.render(write_still=True);previews.append(name+'.png')
    # Keep installed lights usable, return the editable app to the overall day view.
    for obj in original_lights:obj.data.energy=obj['NightWatts']
    bg.inputs['Color'].default_value=(.34,.43,.55,1);bg.inputs['Strength'].default_value=.65
    sun_data.energy=2.5;sun_data.color=(1,.93,.8)
    cam.location=configs[0][1];aim(cam,configs[0][2]);camera_data.type='ORTHO';camera_data.ortho_scale=480
    return previews


if __name__=='__main__':
    bpy.ops.wm.open_mainfile(filepath=str(HERE/'KOL_T1_DAKSHINESHWAR.blend'))
    scene=bpy.context.scene;row=json.loads((HERE/'asset.json').read_text(encoding='utf8'))
    report=validate(row,HERE,scene);report['focusedChecks']=focused_check(scene,row)
    print('FOCUSED_GEOMETRY_EXPORT_CHECK_PASSED',flush=True)
    report['previews']=render_views(scene)
    scene['ProductionStage']='Reviewed landmark; day/night previews and modular export checks saved'
    # Save only this authored asset scene, excluding earlier live drafting scenes.
    bpy.data.libraries.write(str(HERE/row['source']),{scene},fake_user=True,compress=True)
    (HERE/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print('DAKSHINESHWAR_REVIEW_READY',flush=True)
