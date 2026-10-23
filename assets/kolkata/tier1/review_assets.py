"""One source/export sanity pass and day/reverse/night Blender review images."""
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


def aim(obj,target):obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()


def add_area(scene,rig,name,position,target,power,size,color):
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;data.color=color
    o=bpy.data.objects.new(name,data);rig.objects.link(o);o.location=position;aim(o,target)
    return o


def closed_mesh(mesh):
    """Require solid, consistently wound triangle components for import."""
    bm=bmesh.new();bm.from_mesh(mesh)
    bad_edges=sum(not e.is_manifold for e in bm.edges)
    bad_winding=sum(e.is_manifold and not e.is_contiguous for e in bm.edges)
    bm.free()
    assert not bad_edges,(mesh.name,'nonmanifold edges',bad_edges)
    assert not bad_winding,(mesh.name,'inconsistent winding',bad_winding)
    assert all(len(p.vertices)==3 and p.area>1e-8 for p in mesh.polygons),mesh.name


def bounds(objects):
    points=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box]
    return [min(p[i] for p in points) for i in range(3)]+[max(p[i] for p in points) for i in range(3)]


def column_contacts(scene,folder):
    columns={};vertices=[];faces=[]
    for obj in scene.objects:
        if obj.type!='MESH':continue
        key=obj.name.split('__')[0]
        if key.startswith(('RB_column_','RB_loggia_column_','RB_arrival_column')):
            columns.setdefault((key,tuple(obj.location)),[]).append(obj)
            continue
        offset=len(vertices)
        vertices.extend(obj.matrix_world@v.co for v in obj.data.vertices)
        faces.extend(tuple(offset+i for i in p.vertices) for p in obj.data.polygons)
    tree=BVHTree.FromPolygons(vertices,faces,all_triangles=True);report=[]
    for (key,location),objects in columns.items():
        box=bounds(objects);bottom=box[2];top=box[5]
        lower=tree.ray_cast(Vector((*location[:2],bottom+.25)),Vector((0,0,-1)),1)[0]
        upper=tree.ray_cast(Vector((*location[:2],top-.25)),Vector((0,0,1)),1)[0]
        assert lower is not None and upper is not None,('unsupported column',key,location)
        overlaps=(round(lower.z-bottom,4),round(top-upper.z,4))
        assert min(overlaps)>=-.001,('column bearing gap',key,location,overlaps)
        report.append(dict(column=key,location=location,bottom=bottom,top=top,
            lowerBearingOverlap=overlaps[0],upperBearingOverlap=overlaps[1]))
    assert len(report)==44,('missing Royal columns',len(report))
    (folder/'column-bearings.json').write_text(json.dumps(dict(checkedColumns=len(report),failed=[],bearings=report),indent=2),encoding='utf8')
    return len(report)


def validate(row,folder,scene):
    objects=[o for o in scene.objects if o.type=='MESH']
    assert len(objects)==row['meshInstances'],(row['name'],'missing source objects')
    unique={o.data for o in objects}
    for mesh in unique:
        assert all(all(math.isfinite(v) for v in vert.co) for vert in mesh.vertices)
        closed_mesh(mesh)
    checked_columns=column_contacts(scene,folder) if row['assetId']=='KOL_T1_ROYAL' else None
    exports=[]
    for part in row['exports']:
        path=folder/part['file'];root,version=parse_fbx.parse(str(path))
        fbx_objects=next(e for e in root.elems if e.id==b'Objects')
        models=[e for e in fbx_objects.elems if e.id==b'Model']
        geometry=[e for e in fbx_objects.elems if e.id==b'Geometry']
        assert len(models)==part['meshInstances'],(part['file'],len(models),part['meshInstances'])
        count=0
        for mesh in geometry:
            idx=next(e for e in mesh.elems if e.id==b'PolygonVertexIndex').props[0]
            coords=next(e for e in mesh.elems if e.id==b'Vertices').props[0]
            vertices=[tuple(coords[i:i+3]) for i in range(0,len(coords),3)]
            face=[];faces=[];tri=0
            for index in idx:
                face.append(-index-1 if index<0 else index)
                if index<0:
                    assert len(face)==3,(part['file'],'non-triangle face')
                    faces.append(face);tri+=1;face=[]
            assert tri<=5500,(part['file'],tri)
            assert all(all(math.isfinite(v) for v in p) for p in vertices)
            check=bpy.data.meshes.new('__FBX_CHECK')
            check.from_pydata(vertices,[],faces);check.update()
            closed_mesh(check);bpy.data.meshes.remove(check)
            count+=tri
        assert count==part['triangles'],(part['file'],count,part['triangles'])
        exports.append(dict(file=part['file'],meshObjects=len(models),triangles=count,fbxVersion=version))
    # One representative section per project is round-tripped, including
    # material assignment and bounds. Other sections get direct FBX inventory.
    sample=max(row['exports'],key=lambda p:p['triangles'])
    source_bounds=bounds([o for o in objects if o.get('Section')==sample['section']])
    imported_scene=bpy.data.scenes.new('__ROUNDTRIP')
    bpy.context.window.scene=imported_scene
    bpy.ops.import_scene.fbx(filepath=str(folder/sample['file']))
    imported=[o for o in imported_scene.objects if o.type=='MESH']
    expected=sum(o.type=='MESH' for o in imported)
    assert expected==sample['meshInstances']
    assert all(len(o.data.materials)==1 and o.data.materials[0] for o in imported)
    assert all(all(abs(s-1)<1e-5 for s in o.scale) for o in imported)
    assert all(o.matrix_world.determinant()>0 for o in imported)
    for o in imported:
        closed_mesh(o.data)
    imported_bounds=bounds(imported)
    error=max(abs(a-b) for a,b in zip(source_bounds,imported_bounds))
    assert error<.001,('FBX bounds/scale mismatch',error,source_bounds,imported_bounds)
    bpy.context.window.scene=scene
    for o in list(imported_scene.objects):bpy.data.objects.remove(o,do_unlink=True)
    bpy.data.scenes.remove(imported_scene)
    return dict(status='passed',sourceMeshInstances=len(objects),sourceUniqueMeshes=len(unique),
        degenerateFaces=0,finiteVertices=True,largestSourceMeshTriangles=row['largestMeshTriangles'],
        nonManifoldEdges=0,inconsistentWindingEdges=0,allExportMeshesClosed=True,exports=exports,
        columnBearingContactsPassed=checked_columns,
        representativeRoundTrip=sample['file'],materialSlotsPresent=True,objectScalesOne=True,
        roundTripBoundsErrorStuds=error,
        validationScope='Blender source, FBX inventory and one section round trip. No Studio import, collisions, gameplay or device benchmark.')


def render_views(row,folder,scene):
    meshes=[o for o in scene.objects if o.type=='MESH']
    points=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box]
    height=row['dimensionsStuds']['height'];span=max(row['dimensionsStuds'].values())
    rig=bpy.data.collections.new('PREVIEW_ONLY__not_exported');scene.collection.children.link(rig)
    cam_data=bpy.data.cameras.new('Review Camera');cam=bpy.data.objects.new('Review Camera',cam_data);rig.objects.link(cam)
    cam_data.type='ORTHO';cam_data.clip_start=1;cam_data.clip_end=6000;scene.camera=cam
    scene.render.resolution_x=1100;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
    scene.world=bpy.data.worlds.new('Original studio sky');scene.world.use_nodes=True
    bg=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND')
    sun_data=bpy.data.lights.new('Preview sun','SUN');sun_data.energy=2.7;sun_data.angle=.25
    sun=bpy.data.objects.new('Preview sun',sun_data);rig.objects.link(sun);sun.rotation_euler=(math.radians(28),math.radians(-24),math.radians(-35))
    target=Vector((0,0,height*.46))
    key=add_area(scene,rig,'Arrival wash',(0,span*.7,height*.4),target,span*span*8,span*.8,(1,.79,.52))
    fill=add_area(scene,rig,'Cool fill',(-span,0,height),target,span*span*4,span,(.55,.72,1))
    previews=[]
    for name,direction,night in [('preview-day',(1.15,2.2,.95),False),('preview-reverse',(-1.5,-2.2,1.2),False),('preview-night',(1.15,2.2,.95),True)]:
        direction=Vector(direction).normalized();cam.location=target+direction*span*3;aim(cam,target)
        bpy.context.view_layer.update()
        inverse=cam.rotation_euler.to_matrix().transposed()
        local=[inverse@(p-target) for p in points]
        xs=[p.x for p in local];ys=[p.y for p in local]
        cam_data.ortho_scale=max(max(xs)-min(xs),max(ys)-min(ys))*1.15
        # Center the projected bounds, not an assumed height or footprint.
        cam.location+=cam.rotation_euler.to_matrix()@Vector(((max(xs)+min(xs))/2,(max(ys)+min(ys))/2,0))
        bg.inputs['Color'].default_value=(.014,.025,.052,1) if night else (.28,.36,.43,1)
        bg.inputs['Strength'].default_value=.24 if night else .7
        sun_data.energy=.1 if night else 2.7;sun_data.color=(.4,.55,1) if night else (1,.94,.83)
        key.data.energy=span*span*(5 if night else 2)
        fill.data.energy=span*span*(.8 if night else 3)
        for mat in bpy.data.materials:
            if not mat.use_nodes:continue
            node=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
            if node and mat.name.startswith('KOL_T1_'):
                if 'WarmWindow' in mat.name:node.inputs['Emission Strength'].default_value=2.8 if night else 0
                if 'Accent' in mat.name:node.inputs['Emission Strength'].default_value=3.5 if night else 0
        scene.render.filepath=str(folder/(name+'.png'))
        bpy.ops.render.render(write_still=True)
        previews.append(name+'.png')
    # Return the editable file to a day-lit review camera. The rig is explicitly
    # separate from source geometry and is excluded by the export builder.
    for mat in bpy.data.materials:
        if mat.use_nodes and ('Accent' in mat.name or 'WarmWindow' in mat.name):
            node=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
            if node:node.inputs['Emission Strength'].default_value=0
    sun_data.energy=2.7;sun_data.color=(1,.94,.83)
    key.data.energy=span*span*2;fill.data.energy=span*span*3
    bg.inputs['Color'].default_value=(.28,.36,.43,1);bg.inputs['Strength'].default_value=.7
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                sp=area.spaces.active;sp.clip_start=1;sp.clip_end=5000;sp.shading.type='MATERIAL'
                sp.region_3d.view_location=target;sp.region_3d.view_rotation=cam.rotation_euler.to_quaternion();sp.region_3d.view_distance=span*1.7
    bpy.ops.wm.save_as_mainfile(filepath=str(folder/row['source']))
    return previews


if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    rows=[json.loads((BASE/key/'asset.json').read_text(encoding='utf8')) for key in args] if args else json.loads((BASE/'batch-manifest.json').read_text(encoding='utf8'))
    for row in rows:
        key=row['source'].split('KOL_T1_')[1].split('.blend')[0].lower()
        if args and key not in args:continue
        folder=BASE/key
        bpy.ops.wm.open_mainfile(filepath=str(folder/row['source']))
        scene=bpy.context.scene
        report=validate(row,folder,scene)
        report['previews']=render_views(row,folder,scene)
        (folder/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
        print('REVIEW_READY '+key,flush=True)
