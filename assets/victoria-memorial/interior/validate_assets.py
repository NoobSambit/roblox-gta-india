"""Minimal mesh/pivot/budget/export inspection; no Studio or gameplay tests."""
import bpy
import bmesh
import hashlib
import json
import math
from pathlib import Path
from io_scene_fbx import parse_fbx

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]

def bounds(objects):
    bpy.context.view_layer.update()
    points=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
    return [[min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]]

def validate():
    manifest=json.loads((BASE/'asset-manifest.json').read_text())
    rows=manifest['assets']
    assert len(rows)==37 and len({r['assetId'] for r in rows})==37
    with bpy.data.libraries.load(str(BASE/'VIC_Interior_Library.blend')) as (available,load):
        load.scenes=list(available.scenes)
    assert len(load.scenes)==38
    results=[]
    for row in rows:
        scene=bpy.data.scenes[row['assetId']]
        bpy.context.window.scene=scene
        assert scene.unit_settings.system=='NONE' and scene.unit_settings.scale_length==1
        objects=[o for o in scene.objects if o.type=='MESH']
        count=0;components=0
        for obj in objects:
            assert obj.rotation_euler.to_matrix().is_identity
            assert all(abs(s-1)<1e-7 for s in obj.scale)
            assert not obj.modifiers
            assert all(math.isfinite(c) for v in obj.data.vertices for c in v.co)
            assert all(p.area>1e-9 and len(p.vertices)==3 for p in obj.data.polygons),(row['assetId'],'degenerate')
            count+=len(obj.data.polygons)
            bm=bmesh.new();bm.from_mesh(obj.data)
            assert all(e.is_manifold and e.is_contiguous for e in bm.edges),(obj.name,'normals/edges')
            unseen=set(bm.faces)
            while unseen:
                seed=unseen.pop();stack=[seed];group=[seed]
                while stack:
                    f=stack.pop()
                    for e in f.edges:
                        for adjacent in e.link_faces:
                            if adjacent in unseen:
                                unseen.remove(adjacent);stack.append(adjacent);group.append(adjacent)
                volume=sum(f.calc_center_median().dot(f.normal)*f.calc_area()/3 for f in group)
                assert volume>1e-10,(obj.name,'inward component',volume)
                components+=1
            bm.free()
            assert len(obj.data.materials)==1
            assert not any(n.type=='TEX_IMAGE' for n in obj.data.materials[0].node_tree.nodes)
        assert count==row['triangles']<=row['triangleCap']
        assert row['boundsMinStuds'][1]>=-1e-6,(row['assetId'],'below ground')
        for key in ['source','export']:
            assert (BASE/row[key]).is_file()
        tree,version=parse_fbx.parse(str(BASE/row['export']))
        elements=next(e for e in tree.elems if e.id==b'Objects').elems
        models=[e for e in elements if e.id==b'Model']
        geometries=[e for e in elements if e.id==b'Geometry']
        assert len(models)==len(geometries)==len(objects)
        exported=0
        for geo in geometries:
            verts=next(e for e in geo.elems if e.id==b'Vertices').props[0]
            assert all(math.isfinite(v) for v in verts)
            indices=next(e for e in geo.elems if e.id==b'PolygonVertexIndex').props[0]
            assert len(indices)%3==0 and sum(i<0 for i in indices)*3==len(indices)
            exported+=len(indices)//3
        assert exported==count
        for model in models:
            for props in model.elems:
                if props.id==b'Properties70':
                    for p in props.elems:
                        if p.props and p.props[0]==b'Lcl Scaling':assert all(abs(v-1)<1e-6 for v in p.props[-3:])
        assert not any(e.id in [b'Texture',b'Video'] for e in elements)
        results.append(dict(assetId=row['assetId'],triangles=count,closedOutwardComponents=components,fbxVersion=version,status='passed'))
    # Small representative export roundtrip: arch opening, transparent premium case,
    # and the intentional moving-head component pivot, rather than an integration pass.
    roundtrips=[]
    for asset_id in ['VIC_A03_ARCH_10','VIC_E03_CASE_PREMIUM','VIC_S02_MOVING_HOUSING']:
        row=next(r for r in rows if r['assetId']==asset_id)
        original=bpy.data.scenes[asset_id]
        bpy.context.window.scene=original
        expected=bounds([o for o in original.objects if o.type=='MESH'])
        review=bpy.data.scenes.new('Roundtrip_'+asset_id)
        bpy.context.window.scene=review
        bpy.ops.import_scene.fbx(filepath=str(BASE/row['export']))
        objects=[o for o in review.objects if o.type=='MESH']
        actual=bounds(objects)
        error=max(abs(a-b) for x,y in zip(expected,actual) for a,b in zip(x,y))
        assert error<.001,(asset_id,error)
        assert sum(len(o.data.polygons) for o in objects)==row['triangles']
        roundtrips.append(dict(assetId=asset_id,maxBoundsErrorStuds=error,triangles=row['triangles']))
        for o in list(review.objects):bpy.data.objects.remove(o,do_unlink=True)
        bpy.context.window.scene=original;bpy.data.scenes.remove(review)
    locked=json.loads((BASE/'layout-lock.json').read_text())
    hashes={rel:hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==expected for rel,expected in locked['sourceHashes'].items()}
    assert all(hashes.values()),'Approved Task007/exterior source changed'
    art=json.loads((BASE/'artwork/manifest.json').read_text())
    assert len(art['artworks'])==4
    for item in art['artworks']:
        image=bpy.data.images.load(str(BASE/item['texture']),check_existing=True)
        assert list(image.size)==[480,320]
        assert image.size[0]/image.size[1]==item['aspectRatio']==1.5
        assert item['robloxImageId'].startswith('rbxassetid://')
        bpy.data.images.remove(image)
    report=dict(assetCount=len(rows),uniqueLibraryTriangles=sum(r['triangles'] for r in rows),
        largestAsset=max(rows,key=lambda r:r['triangles'])['assetId'],largestTriangleCount=max(r['triangles'] for r in rows),
        categories={c:dict(assets=sum(r['category']==c for r in rows),triangles=sum(r['triangles'] for r in rows if r['category']==c)) for c in ['Architecture','Exhibition','Loot','Security']},
        physicalKitTextureDependencies=0,artworkTextures=4,artworkReleasePixels=[480,320],sourceFilesUnchanged=hashes,representativeFbxRoundtrips=roundtrips,assets=results,
        scope='Mesh, normals, transforms/pivots, triangle caps, FBX completeness; three representative roundtrips. No Studio import, gameplay, multiplayer or device testing.')
    (BASE/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='assets'}),flush=True)

if __name__=='__main__':validate()
