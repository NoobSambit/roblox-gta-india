"""One source/FBX sanity pass plus day, rear and night original renders."""
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE.parent/'tier1'))
from review_assets import validate,aim,add_area

KEYS=['writers','metropolitan','gpo','town_hall']


def bearings(scene):
    prefixes=('Giant_Corinthian_column','Street_Corinthian_column','Doric_portico_column','Doric_return_column')
    columns={};vertices=[];faces=[]
    for obj in scene.objects:
        if obj.type!='MESH':continue
        if obj.name.startswith(prefixes):columns.setdefault(tuple(obj.location),[]).append(obj);continue
        off=len(vertices);vertices.extend(obj.matrix_world@v.co for v in obj.data.vertices)
        faces.extend(tuple(off+i for i in p.vertices) for p in obj.data.polygons)
    tree=BVHTree.FromPolygons(vertices,faces,all_triangles=True)
    for pos,objects in columns.items():
        pts=[o.matrix_world@Vector(p) for o in objects for p in o.bound_box]
        bottom=min(p.z for p in pts);top=max(p.z for p in pts)
        lower=tree.ray_cast(Vector((pos[0],pos[1],bottom+2)),Vector((0,0,-1)),4)[0]
        upper=tree.ray_cast(Vector((pos[0],pos[1],top-2)),Vector((0,0,1)),4)[0]
        assert lower is not None and lower.z>=bottom-.03,('column base gap',objects[0].name,pos,bottom,lower)
        assert upper is not None and upper.z<=top+.03,('column head gap',objects[0].name,pos,top,upper)
    return len(columns)


def statue_bearings(scene):
    """Check actual statue base islands against the supporting pedestal mesh."""
    import bmesh
    feet=[];vertices=[];faces=[]
    for obj in scene.objects:
        if obj.type!='MESH' or not obj.name.startswith(('Pediment_allegorical_group','Pavilion_roof_statue')):continue
        bm=bmesh.new();bm.from_mesh(obj.data);unseen=set(bm.faces)
        while unseen:
            todo=[unseen.pop()];component=[]
            while todo:
                face=todo.pop();component.append(face)
                for edge in face.edges:
                    for other in edge.link_faces:
                        if other in unseen:unseen.remove(other);todo.append(other)
            pts=[obj.matrix_world@v.co for f in component for v in f.verts]
            lo=Vector([min(p[i] for p in pts) for i in range(3)]);hi=Vector([max(p[i] for p in pts) for i in range(3)])
            size=hi-lo
            if abs(size.x-1.8)<.001 and abs(size.y-1.6)<.001 and abs(size.z-.3)<.001:
                feet.append(((lo+hi)/2,lo.z));continue
            for face in component:
                off=len(vertices);vertices.extend(obj.matrix_world@v.co for v in face.verts);faces.append(tuple(range(off,len(vertices))))
        bm.free()
    tree=BVHTree.FromPolygons(vertices,faces,all_triangles=True)
    assert len(feet)==9,len(feet)
    for center,bottom in feet:
        hit=tree.ray_cast(Vector((center.x,center.y,bottom+.2)),Vector((0,0,-1)),1)[0]
        assert hit is not None and hit.z>=bottom-.001,('floating statue',center,bottom,hit)
    return len(feet)


def render_views(key,row,folder,scene,night_only=False):
    for old in list(scene.collection.children):
        if old.name.startswith('REVIEW_LIGHTS_CAMERA__'):
            for obj in list(old.objects):bpy.data.objects.remove(obj,do_unlink=True)
            bpy.data.collections.remove(old)
    rig=bpy.data.collections.new('REVIEW_LIGHTS_CAMERA__NOT_EXPORTED');scene.collection.children.link(rig)
    cam_data=bpy.data.cameras.new('Review Camera');cam=bpy.data.objects.new('Review Camera',cam_data);rig.objects.link(cam);scene.camera=cam
    cam_data.type='ORTHO';cam_data.clip_start=.1;cam_data.clip_end=3000
    scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True
    scene.render.resolution_x=1280;scene.render.resolution_y=900;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
    scene.world=bpy.data.worlds.new('Heritage review sky');bg=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND')
    sun_data=bpy.data.lights.new('Daylight','SUN');sun=bpy.data.objects.new('Daylight',sun_data);rig.objects.link(sun)
    sun.rotation_euler=(.5,-.45,-.6);sun_data.angle=.22
    meshes=[o for o in scene.objects if o.type=='MESH'];pts=[o.matrix_world@Vector(p) for o in meshes for p in o.bound_box]
    lo=Vector([min(p[i] for p in pts) for i in range(3)]);hi=Vector([max(p[i] for p in pts) for i in range(3)])
    target=(lo+hi)/2;span=max(hi-lo)
    installed=[o for o in scene.objects if o.type=='LIGHT' and o.get('NightWatts')]
    assert len(installed)==len(row['nightLights'])
    front=(-1,2,.8) if key=='gpo' else (1,2,.8)
    for name,direction,night in [('preview-day',front,False),('preview-rear',(-1,-2,.85),False),('preview-night',front,True),('preview-night-rear',(-1,-2,.85),True)]:
        if night_only and not night:continue
        cam.location=target+Vector(direction).normalized()*span*3;aim(cam,target)
        inverse=cam.rotation_euler.to_matrix().transposed();local=[inverse@(p-target) for p in pts]
        xs=[p.x for p in local];ys=[p.y for p in local]
        cam_data.ortho_scale=max(max(xs)-min(xs),(max(ys)-min(ys))*1280/900)*1.12
        cam.location+=cam.rotation_euler.to_matrix()@Vector(((max(xs)+min(xs))/2,(max(ys)+min(ys))/2,0))
        bg.inputs['Color'].default_value=(.09,.12,.18,1) if night else (.34,.43,.55,1)
        bg.inputs['Strength'].default_value=.5 if night else .7
        sun_data.energy=.18 if night else 2.5;sun_data.color=(.48,.6,1) if night else (1,.94,.84)
        for obj in installed:obj.data.energy=obj['NightWatts']*(1 if night else .03)
        scene.render.filepath=str(folder/(name+'.png'));bpy.ops.render.render(write_still=True)
    sun_data.energy=2.5;sun_data.color=(1,.94,.84);bg.inputs['Color'].default_value=(.34,.43,.55,1);bg.inputs['Strength'].default_value=.7
    for obj in installed:obj.data.energy=obj['NightWatts']
    # Final editable file opens on the useful front view, not the rear camera.
    cam.location=target+Vector(front).normalized()*span*3;aim(cam,target)
    cam_data.ortho_scale=max(hi.x-lo.x,(hi.z-lo.z)*1280/900)*1.2
    return ['preview-day.png','preview-rear.png','preview-night.png','preview-night-rear.png']


if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else KEYS
    night_only='--night-only' in args;args=[key for key in args if key!='--night-only']
    for key in args:
        folder=BASE/key;row=json.loads((folder/'asset.json').read_text(encoding='utf8'))
        bpy.ops.wm.open_mainfile(filepath=str(folder/row['source']))
        scene=bpy.context.scene
        if night_only:report=json.loads((folder/'validation.json').read_text(encoding='utf8'))
        else:
            report=validate(row,folder,scene);report['columnBearingPairs']=bearings(scene)
            if key=='writers':report['statueBaseContacts']=statue_bearings(scene)
        print('HERITAGE_CHECK_PASSED '+key,flush=True)
        report['previews']=render_views(key,row,folder,scene,night_only)
        scene['ProductionStage']='Reviewed exterior landmark; original day/rear/night previews saved'
        bpy.data.libraries.write(str(folder/row['source']),{scene},fake_user=True,compress=True)
        (folder/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
        print('HERITAGE_REVIEW_READY '+key,flush=True)
