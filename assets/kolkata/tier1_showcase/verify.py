"""Essential staging inventory, modular FBX sanity and new shrine-row round trip."""
import bpy
import json
import math
import sys
from collections import Counter
from pathlib import Path
from mathutils import Vector
from io_scene_fbx import parse_fbx

BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
from catalog import ROOT,EXPORT,MASTER,sha


def bounds(objects):
    points=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box]
    return [min(p[i] for p in points) for i in range(3)]+[max(p[i] for p in points) for i in range(3)]


def triangles(mesh):return sum(len(p.vertices)-2 for p in mesh.polygons)


def check_fbx(part):
    path=ROOT/part['file'];assert sha(path)==part['sha256'],path
    root,version=parse_fbx.parse(str(path))
    objects=next(e for e in root.elems if e.id==b'Objects')
    geometry=[e for e in objects.elems if e.id==b'Geometry']
    total=largest=0;uv_meshes=0
    for mesh in geometry:
        elements={e.id:e for e in mesh.elems}
        vertices=elements[b'Vertices'].props[0]
        assert all(math.isfinite(v) for v in vertices),(path,'nonfinite coordinates')
        indices=elements[b'PolygonVertexIndex'].props[0]
        count=sum(i<0 for i in indices)
        assert len(indices)==count*3 and count<15000,(path,'triangle limit or polygon format')
        for start in range(0,len(indices),3):
            ids=[i if i>=0 else -i-1 for i in indices[start:start+3]]
            a,b,c=[Vector(vertices[i*3:i*3+3]) for i in ids]
            assert (b-a).cross(c-a).length_squared>1e-16,(path,'degenerate triangle')
        normal_layer=elements[b'LayerElementNormal']
        normals=next(e for e in normal_layer.elems if e.id==b'Normals').props[0]
        assert all(math.isfinite(n) for n in normals),(path,'nonfinite normals')
        assert all(sum(n*n for n in normals[i:i+3])>.5 for i in range(0,len(normals),3)),(path,'zero normals')
        uv_meshes+=b'LayerElementUV' in elements
        total+=count;largest=max(largest,count)
    assert total==part['triangles'] and len(geometry)==part['meshObjects'],path
    assert largest==part['largestMeshTriangles'],path
    assert any(e.id==b'Material' for e in objects.elems),(path,'no materials')
    return dict(file=part['file'],triangles=total,meshObjects=len(geometry),largestMeshTriangles=largest,
        meshesWithUVs=uv_meshes,fbxVersion=version,defaultImport=part['defaultImport'])


def verify():
    manifest=json.loads((BASE/'export-manifest.json').read_text(encoding='utf8'))
    bpy.ops.wm.open_mainfile(filepath=str(MASTER));scene=bpy.context.scene
    assert len(bpy.data.scenes)==1 and scene.name==manifest['scene']
    assert scene.unit_settings.scale_length==1 and scene.unit_settings.system=='NONE'
    asset_collections=[c for c in scene.collection.children if c.get('AssetId')]
    assert len(asset_collections)==manifest['assetCount']==16
    reports=[];images=set();source_count=0;repeat_count=0;source_materials=set()
    for asset in manifest['assets']:
        aid=asset['assetId'];collection=bpy.data.collections[asset['collection']]
        pivot=bpy.data.objects[asset['pivot']]
        assert collection['AssetId']==aid and pivot['AssetId']==aid and pivot.get('StagingPivot')
        assert tuple(pivot.scale)==(1,1,1) and sum(abs(x) for x in pivot.rotation_euler)<1e-8
        assert max(abs(a-b) for a,b in zip(pivot.location,asset['stagingOffsetBlender']))<.001
        meshes=[o for o in collection.all_objects if o.type=='MESH' and o.get('Section')]
        assert len(meshes)==asset['sourceMeshInstances'],(aid,'mesh inventory')
        assert sum(triangles(o.data) for o in meshes)==asset['assembledTriangles'],aid
        unique={o.data for o in meshes};assert len(unique)==asset['sourceUniqueMeshCount'],aid
        assert sum(triangles(m) for m in unique)==asset['uniqueTrianglesMeasured'],aid
        assert asset['uniqueTrianglesMeasured']==asset['uniqueSourceTriangles'],aid
        assert sum(o.type=='LIGHT' for o in collection.all_objects)==asset['preservedArchitecturalLightCount'],aid
        assert max(abs(a-b) for a,b in zip(bounds(meshes),asset['stagingBoundsBlender']))<.002,aid
        for obj in meshes:
            parent=obj.parent
            while parent is not None and parent!=pivot:parent=parent.parent
            assert parent==pivot,(aid,obj.name,'outside landmark pivot')
            for material in obj.data.materials:
                assert material,(aid,obj.name,'empty material');source_materials.add(material)
                images.update(n.image for n in material.node_tree.nodes if n.type=='TEX_IMAGE' and n.image)
        source_count+=len(meshes);repeat_count+=len(meshes)-len(unique)
        assert sha(ROOT/asset['source'])==asset['sourceSha256'],aid
        assert sha(ROOT/asset['metadata'])==asset['metadataSha256'],aid
        for texture in asset['textures']:
            assert sha(ROOT/texture['file'])==texture['sha256']
        for helper in asset['helpers']:
            assert sha(ROOT/helper['file'])==sha(ROOT/helper['canonicalFile'])==helper['sha256']
        for part in asset['files']:reports.append(check_fbx(part))
        print('PACKAGE_OK',aid,len(asset['files']),'files',flush=True)
    assert all(im.packed_file for im in images),'Unpacked material image dependency'
    # Only the twelve-shrine row is newly exported; all other FBXs are byte copies
    # of previously validated completed exports. Round trip the new file once.
    dak=next(a for a in manifest['assets'] if a['assetId']=='KOL_T1_DAKSHINESHWAR')
    row_part=next(p for p in dak['files'] if p['section']=='10_Shiva_Temples')
    row_objects=[o for o in scene.objects if o.type=='MESH' and o.get('StagingAssetId')==dak['assetId'] and o.get('Section')=='10_Shiva_Temples']
    offset=Vector(dak['stagingOffsetBlender']);bb=bounds(row_objects)
    expected=[n-offset[i%3] for i,n in enumerate(bb)]
    temp=bpy.data.scenes.new('__SHRINE_ROW_ROUNDTRIP');bpy.context.window.scene=temp
    bpy.ops.import_scene.fbx(filepath=str(ROOT/row_part['file']))
    imported=[o for o in temp.objects if o.type=='MESH'];actual=bounds(imported)
    error=max(abs(a-b) for a,b in zip(expected,actual));assert error<.001,(expected,actual,error)
    assert sum(triangles(o.data) for o in imported)==18192 and len(imported)==48
    assert all(abs(s-1)<1e-5 for o in imported for s in o.scale)
    assert all(o.data.materials for o in imported)
    uv_inventory=lambda objects:Counter((triangles(o.data),len(o.data.uv_layers),len(o.data.materials)) for o in objects)
    assert uv_inventory(imported)==uv_inventory(row_objects),'Row material/UV inventory changed'
    assert len({o.data for o in row_objects})==4 and len({o.get('ShrineIndex') for o in row_objects})==12
    bpy.context.window.scene=scene
    for obj in list(temp.objects):bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.scenes.remove(temp)
    default=[r for r in reports if r['defaultImport']]
    assert sum(r['triangles'] for r in default)==manifest['totalAssembledTriangles']
    report=dict(status='passed',assetCount=16,sceneCount=1,sourceMeshInstances=source_count,
        preservedRepeatedMeshPlacements=repeat_count,materials=len(source_materials),packedMaterialImages=len(images),
        sourceFilesUnchanged=True,geometryAndUVFingerprintsUnchanged=manifest['geometryAndUVFingerprintsUnchanged'],
        preservedArchitecturalLights=sum(a['preservedArchitecturalLightCount'] for a in manifest['assets']),
        materialGraphsUnchanged=manifest['materialGraphsUnchanged'],minimumGapStuds=manifest['layout']['minimumMeasuredGapStuds'],
        defaultFBXCount=len(default),optionalModuleFBXCount=len(reports)-len(default),
        totalAssembledTriangles=manifest['totalAssembledTriangles'],totalUniqueSourceTriangles=manifest['totalUniqueSourceTriangles'],
        largestExportMeshTriangles=max(r['largestMeshTriangles'] for r in reports),
        finiteCoordinatesAndNormals=True,degenerateExportTriangles=0,
        shrineRowRoundTrip=dict(triangles=18192,meshObjects=48,boundsErrorStuds=error,unitScale=True,materialsAndUVInventoryPreserved=True),
        exports=reports,limitations='Offline staging/export checks only. Existing Studio world untouched; no Studio import, gameplay or device performance tests.')
    for target in [BASE/'validation.json',EXPORT/'validation.json']:
        target.write_text(json.dumps(report,indent=2),encoding='utf8')
    print('STAGING_VERIFIED',json.dumps({k:report[k] for k in ['assetCount','defaultFBXCount','optionalModuleFBXCount','totalAssembledTriangles','largestExportMeshTriangles']}),flush=True)


if __name__=='__main__':verify()
