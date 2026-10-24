"""Read-only consolidation of completed masters into one inspectable staging scene."""
import array
import bpy
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path
from mathutils import Matrix,Vector

BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
from catalog import catalog,ROOT,EXPORT,MASTER,relative,sha
from reexport import export_section


def floats(collection,property_,count):
    out=array.array('f',[0])*count;collection.foreach_get(property_,out);return out.tobytes()


def mesh_digest(mesh):
    h=hashlib.sha256(floats(mesh.vertices,'co',len(mesh.vertices)*3))
    indices=array.array('i',[0])*len(mesh.loops);mesh.loops.foreach_get('vertex_index',indices);h.update(indices.tobytes())
    for prop in ['material_index','loop_total']:
        values=array.array('i',[0])*len(mesh.polygons);mesh.polygons.foreach_get(prop,values);h.update(values.tobytes())
    values=array.array('b',[0])*len(mesh.polygons);mesh.polygons.foreach_get('use_smooth',values);h.update(values.tobytes())
    for uv in mesh.uv_layers:h.update(floats(uv.data,'uv',len(mesh.loops)*2))
    h.update(str([m.as_pointer() for m in mesh.materials if m]).encode())
    return h.hexdigest()


def material_digest(mat):
    data=[tuple(mat.diffuse_color),mat.use_nodes]
    if mat.use_nodes:
        for node in mat.node_tree.nodes:
            values=[]
            for socket in node.inputs:
                if hasattr(socket,'default_value'):
                    value=socket.default_value
                    if hasattr(value,'__iter__'):value=list(value)
                    elif not isinstance(value,(str,int,float,bool,type(None))):value=str(value)
                    values.append((socket.identifier,value))
            data.append((node.bl_idname,node.name,values,getattr(getattr(node,'image',None),'name',None)))
        data.append([(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in mat.node_tree.links])
    return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()


def bounds(objects):
    pts=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box]
    return [min(p[i] for p in pts) for i in range(3)]+[max(p[i] for p in pts) for i in range(3)]


def tris(mesh):return sum(len(p.vertices)-2 for p in mesh.polygons)


def texture_dependencies(objects):
    images=set()
    for obj in objects:
        for mat in obj.data.materials:
            if mat and mat.use_nodes:
                images.update(n.image for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image)
    result=[]
    for im in images:
        if not im.packed_file:
            path=Path(bpy.path.abspath(im.filepath))
            assert path.is_file(),('Missing material image',im.name,str(path))
            im.pack()
        blob=bytes(im.packed_file.data);digest=hashlib.sha256(blob).hexdigest()
        name=Path(im.filepath).name or im.name+'.png'
        out=EXPORT/'shared/textures'/(digest[:12]+'_'+name)
        out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(blob)
        result.append(dict(image=im.name,file=relative(out),sha256=digest,packedInMaster=True))
    return result


def copy_package(entry):
    dest=EXPORT/entry['packageKey'];dest.mkdir(parents=True,exist_ok=True)
    files=[]
    for part in entry['exports']:
        master_only=part['section']=='10_Shiva_Temple_Master'
        target=dest/('modules' if master_only else '')/Path(part['canonicalFile']).name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/part['canonicalFile'],target)
        assert sha(target)==part['sha256'],target
        files.append(dict(section=part['section'],file=relative(target),sha256=part['sha256'],
            triangles=part['triangles'],meshObjects=part['meshInstances'],largestMeshTriangles=part['largestExportMeshTriangles'],
            defaultImport=not master_only,provenance='Unchanged copy of completed modular export'))
    helpers=[]
    if entry['row']['assetId']=='KOL_T1_DAKSHINESHWAR':
        for name in ['shiva-placements.json','AssembleShivaRow.luau','InstallNightLights.luau','night-lights.json']:
            original=ROOT/('assets/kolkata/dakshineshwar' if name=='night-lights.json' else 'exports/dakshineshwar')/name
            target=dest/('modules' if name in ['shiva-placements.json','AssembleShivaRow.luau'] else '')/name
            shutil.copy2(original,target);helpers.append(dict(file=relative(target),canonicalFile=relative(original),sha256=sha(target)))
    if entry['batch']=='Heritage':
        original=ROOT/'exports/kolkata_heritage_batch2/InstallHeritageLights.luau'
        target=EXPORT/'shared'/original.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(original,target)
        helpers.append(dict(file=relative(target),canonicalFile=relative(original),sha256=sha(target)))
    if entry['batch']=='Cultural':
        for name in ['CulturalLighting.luau','lighting-zones.json']:
            original=ROOT/'exports/kolkata_cultural'/name
            target=EXPORT/'shared'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(original,target)
            helpers.append(dict(file=relative(target),canonicalFile=relative(original),sha256=sha(target)))
    return files,helpers


def build():
    entries=catalog();EXPORT.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    stage=bpy.context.scene;stage.name='KOLKATA_TIER1_ASSET_STAGING'
    stage.unit_settings.system='NONE';stage.unit_settings.scale_length=1
    stage['Purpose']='Offline asset staging and inspection; not a city layout or Studio world'
    stage['AuthoringUnits']='1 neutral Blender unit = 1 Roblox stud; front +Y / Roblox -Z'
    stage['AssetCount']=len(entries)
    loaded=[];mesh_fingerprints={};material_fingerprints={}
    for entry in entries:
        aid=entry['row']['assetId']
        with bpy.data.libraries.load(str(ROOT/entry['source']),link=False) as (source,target):target.scenes=[aid]
        scene=target.scenes[0];bpy.context.window.scene=scene;bpy.context.view_layer.update()
        assert abs(scene.unit_settings.scale_length-1)<1e-8,(aid,'unit mismatch')
        source=next(c for c in scene.collection.children if '__SOURCE' in c.name)
        meshes=[o for o in source.all_objects if o.type=='MESH']
        unique={o.data for o in meshes}
        actual=sum(tris(o.data) for o in meshes)
        assert actual==entry['row']['assembledTriangles'],(aid,'source inventory mismatch',actual,entry['row']['assembledTriangles'])
        assert len(meshes)==entry['row']['meshInstances'],(aid,'object inventory mismatch')
        bb=bounds(meshes);extent=[bb[i+3]-bb[i] for i in range(3)]
        expected=entry['row']['dimensionsStuds']
        error=max(abs(a-b) for a,b in zip(extent,[expected['width'],expected['depth'],expected['height']]))
        assert error<.005,(aid,'source bounds mismatch',extent,expected)
        for mesh in unique:
            assert all(math.isfinite(c) for v in mesh.vertices for c in v.co),mesh.name
            assert all(p.area>1e-8 for p in mesh.polygons),mesh.name
            mesh_fingerprints[mesh]=mesh_digest(mesh)
            for mat in mesh.materials:
                assert mat,(aid,'missing material');material_fingerprints[mat]=material_digest(mat)
        entry['sourceBoundsBlender']=bb;entry['sourceUniqueMeshCount']=len(unique)
        entry['sourceMeshInstances']=len(meshes);entry['uniqueTrianglesMeasured']=sum(tris(m) for m in unique)
        entry['sourceSectionCount']=len({o.get('Section') for o in meshes})
        entry['textures']=texture_dependencies(meshes)
        files,helpers=copy_package(entry);entry['files']=files;entry['helpers']=helpers
        loaded.append((entry,scene,source,meshes))
        print('SOURCE_OK '+aid+' '+str(actual)+' triangles',flush=True)
    width=max(e['sourceBoundsBlender'][3]-e['sourceBoundsBlender'][0] for e in entries)+180
    depth=max(e['sourceBoundsBlender'][4]-e['sourceBoundsBlender'][1] for e in entries)+180
    bpy.context.window.scene=stage
    for index,(entry,scene,source,meshes) in enumerate(loaded):
        aid=entry['row']['assetId'];bb=entry['sourceBoundsBlender']
        offset=Vector(((index%4-1.5)*width-(bb[0]+bb[3])/2,
            (1.5-index//4)*depth-(bb[1]+bb[4])/2,0))
        collection=bpy.data.collections.new(f'{index+1:02} | {entry["label"]}');stage.collection.children.link(collection)
        collection['AssetId']=aid;collection['CanonicalSource']=entry['source']
        collection.children.link(source)
        guides=[c for c in scene.collection.children if 'COLLISION' in c.name.upper()]
        for col in guides:collection.children.link(col)
        lights=[c for c in scene.collection.children if 'NIGHT_LIGHTS' in c.name.upper()]
        for col in lights:collection.children.link(col)
        pivot=bpy.data.objects.new('PIVOT | '+entry['label'],None);collection.objects.link(pivot)
        pivot.empty_display_type='PLAIN_AXES';pivot.empty_display_size=6
        pivot['StagingPivot']=True;pivot['AssetId']=aid;pivot['LocalOrigin']='Original ground origin; reset location to zero for native placement'
        objects=list(source.all_objects)
        for extra in guides+lights:objects.extend(o for o in extra.all_objects if o not in objects)
        # Disabled collision collections do not update matrix_world in Blender's
        # dependency graph. Evaluate them briefly while applying the shared pivot.
        guide_visibility={}
        for guide in guides:
            for col in [guide,*guide.children_recursive]:
                guide_visibility[col]=col.hide_viewport;col.hide_viewport=False
        bpy.context.view_layer.update()
        originals={o:o.matrix_world.copy() for o in objects}
        member_set=set(objects)
        for obj in objects:
            obj['StagingAssetId']=aid
            if obj.parent not in member_set:
                obj.parent=pivot;obj.matrix_parent_inverse=Matrix.Identity(4);obj.matrix_basis=originals[obj]
            if obj.type=='LIGHT':
                obj['StagingOriginalHideRender']=obj.hide_render;obj.hide_render=True
        pivot.location=offset;bpy.context.window.scene=stage;bpy.context.view_layer.update()
        transform_error=max(abs(a-b) for obj in objects for ra,rb in zip(obj.matrix_world,Matrix.Translation(offset)@originals[obj]) for a,b in zip(ra,rb))
        assert transform_error<.001,(aid,'local transforms changed',transform_error)
        for col,hidden in guide_visibility.items():col.hide_viewport=hidden
        entry['collection']=collection.name;entry['pivot']=pivot.name;entry['stagingOffsetBlender']=list(offset)
        entry['stagingBoundsBlender']=bounds(meshes);entry['transformErrorStuds']=transform_error
        entry['guideCollections']=[c.name for c in guides]
        entry['lightCollections']=[c.name for c in lights]
        entry['preservedArchitecturalLightCount']=sum(o.type=='LIGHT' for o in objects)
        if aid=='KOL_T1_DAKSHINESHWAR':
            row=[o for o in meshes if o.get('Section')=='10_Shiva_Temples']
            assert len({o.get('ShrineIndex') for o in row})==12
            path=EXPORT/entry['packageKey']/(aid+'__10_Shiva_Temples.fbx')
            export_section(stage,pivot,row,path)
            entry['files'].append(dict(section='10_Shiva_Temples',file=relative(path),sha256=sha(path),
                triangles=sum(tris(o.data) for o in row),meshObjects=len(row),largestMeshTriangles=max(tris(o.data) for o in row),
                defaultImport=True,provenance='Existing twelve linked shrine placements exported at original ground origin'))
        bpy.context.window.scene=stage
        bpy.data.scenes.remove(scene)
    # Data have only been moved by parent pivots; their geometry and shading must match.
    assert all(mesh_digest(m)==before for m,before in mesh_fingerprints.items()),'Mesh or UV content changed'
    assert all(material_digest(m)==before for m,before in material_fingerprints.items()),'Material graph changed'
    for entry in entries:
        assert sha(ROOT/entry['source'])==entry['sourceSha256']
        assert sha(ROOT/entry['metadata'])==entry['metadataSha256']
    # Each footprint has a 180-stud minimum gap along at least one grid axis.
    minimum=float('inf')
    for i,a in enumerate(entries):
        for b in entries[i+1:]:
            aa=a['stagingBoundsBlender'];bb=b['stagingBoundsBlender']
            separation=max(bb[0]-aa[3],aa[0]-bb[3],bb[1]-aa[4],aa[1]-bb[4])
            minimum=min(minimum,separation);assert separation>=179.99,(a['label'],b['label'],separation)
    rigs=bpy.data.collections.new('00 | Staging presentation — never export');stage.collection.children.link(rigs)
    data=bpy.data.lights.new('Staging daylight','SUN');data.energy=2.7;data.angle=.18
    sun=bpy.data.objects.new(data.name,data);rigs.objects.link(sun);sun.rotation_euler=(-.55,.4,-.4)
    stage.world=bpy.data.worlds.new('Staging neutral sky')
    bg=next(n for n in stage.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.45,.52,.6,1);bg.inputs['Strength'].default_value=.65
    points=[Vector((bb[x],bb[y],bb[z])) for e in entries for bb in [e['stagingBoundsBlender']]
        for x in [0,3] for y in [1,4] for z in [2,5]]
    lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)]);center=(lo+hi)/2
    cam_data=bpy.data.cameras.new('Staging overview');cam=bpy.data.objects.new(cam_data.name,cam_data);rigs.objects.link(cam)
    cam_data.type='ORTHO';cam_data.clip_end=20000
    cam.location=center+Vector((.45,2.5,3.2)).normalized()*max(hi-lo)*3
    cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();stage.camera=cam
    inv=cam.rotation_euler.to_matrix().transposed();ps=[inv@(p-center) for p in points]
    xmin,xmax=min(p.x for p in ps),max(p.x for p in ps);ymin,ymax=min(p.y for p in ps),max(p.y for p in ps)
    cam_data.ortho_scale=max(xmax-xmin,(ymax-ymin)*1.5)*1.1
    cam.location+=cam.rotation_euler.to_matrix()@Vector(((xmin+xmax)/2,(ymin+ymax)/2,0))
    stage.render.engine='CYCLES';stage.cycles.samples=12;stage.cycles.use_denoising=True
    stage.render.resolution_x=2400;stage.render.resolution_y=1600;stage.render.resolution_percentage=100
    stage.render.image_settings.file_format='PNG';stage.view_settings.view_transform='AgX'
    stage.render.filepath=str(BASE/'preview-overview.png')
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                sp=area.spaces.active;sp.clip_start=.5;sp.clip_end=20000;sp.shading.type='MATERIAL'
                sp.overlay.show_floor=False;sp.overlay.show_extras=False
                sp.region_3d.view_location=center;sp.region_3d.view_distance=max(hi-lo)*1.2
                sp.region_3d.view_rotation=cam.rotation_euler.to_quaternion();sp.region_3d.view_perspective='CAMERA'
    bpy.ops.object.select_all(action='DESELECT')
    instructions=bpy.data.texts.new('START HERE — staging and modular export')
    instructions.write('16 finished landmark collections; one scene, original linked modules.\nSelect a PIVOT and use Select Hierarchy to select a whole landmark.\nOnly the pivot position is a staging offset. Local object transforms and geometry are preserved.\nUse the packaged per-asset FBXs for Studio (Stud/1, Merge Meshes off).\nDo not export the whole scene.\nFor edited assets, run reexport.py -- KOL_T1_ASSET_ID to export their sections at the original local origin.\nPreserved per-asset lights are disabled for this daylight overview; fixtures and light data remain.\nThis is an asset review grid, not Kolkata city assembly.\n')
    for path in [BASE/'reexport.py']:
        text=bpy.data.texts.new(path.name);text.write(path.read_text(encoding='utf8'))
    manifest=dict(scene=stage.name,master=relative(MASTER),purpose=stage['Purpose'],units='Neutral Blender/Stud 1',
        front='Blender +Y; Roblox -Z',layout=dict(columns=4,rows=4,cellWidthStuds=width,cellDepthStuds=depth,minimumMeasuredGapStuds=minimum),
        assetCount=len(entries),totalAssembledTriangles=sum(e['row']['assembledTriangles'] for e in entries),
        totalUniqueSourceTriangles=sum(e['row']['uniqueSourceTriangles'] for e in entries),
        geometryAndUVFingerprintsUnchanged=True,materialGraphsUnchanged=True,sourceFilesUnchanged=True,
        checkedUniqueMeshDatablocks=len(mesh_fingerprints),checkedMaterials=len(material_fingerprints),assets=[])
    for entry in entries:
        record={k:v for k,v in entry.items() if k not in ['row','exports']}
        record['assetId']=entry['row']['assetId'];record['name']=entry['row']['name']
        record['dimensionsStuds']=entry['row']['dimensionsStuds'];record['assembledTriangles']=entry['row']['assembledTriangles']
        record['uniqueSourceTriangles']=entry['row']['uniqueSourceTriangles']
        record['nightLights']=entry['row'].get('nightLights',[])
        if entry['row']['assetId']=='KOL_T1_DAKSHINESHWAR':
            record['nightLights']=json.loads((ROOT/entry['folder']/'night-lights.json').read_text(encoding='utf8'))['lights']
        record['reusedModules']=entry['row'].get('reusedModules',{})
        record['defaultImportTriangles']=sum(f['triangles'] for f in entry['files'] if f['defaultImport'])
        assert record['defaultImportTriangles']==record['assembledTriangles'],record['assetId']
        manifest['assets'].append(record)
    (BASE/'export-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
    (EXPORT/'export-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
    bpy.ops.wm.save_as_mainfile(filepath=str(MASTER),compress=True)
    print('STAGING_READY '+json.dumps({k:manifest[k] for k in ['assetCount','totalAssembledTriangles','totalUniqueSourceTriangles']}),flush=True)
    if '--skip-render' not in sys.argv:
        bpy.ops.render.render(write_still=True)
        print('OVERVIEW_READY',flush=True)


if __name__=='__main__':build()
