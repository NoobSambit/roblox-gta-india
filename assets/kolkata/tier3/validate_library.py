"""Required file, mesh and FBX sanity pass only; no Studio/gameplay tests."""
import bpy,bmesh,json,math
from pathlib import Path
from io_scene_fbx import parse_fbx

BASE=Path(r'C:\Users\Sambit Pradhan\Documents\Indian_Hood\assets\kolkata\tier3')
ROOT=BASE.parents[2]

def validate():
    rows=json.loads((BASE/'asset-manifest.json').read_text(encoding='utf8'))
    expected={'old_kolkata':10,'modern':9,'mixed_use':5,'informal':3}
    assert len(rows)==27 and len({r['id'] for r in rows})==27
    assert {f:sum(r['family']==f for r in rows) for f in expected}==expected
    assert len({r['reference']['photoUrl'] for r in rows})==27
    report=[]
    for row in rows:
        ref=row['reference'];source=BASE/row['source'];export=BASE/row['export']
        assert ref['photographExamined'] and (ROOT/ref['localPhoto']).is_file(),row['id']
        assert source.is_file() and source.stat().st_size>10000
        assert export.is_file() and export.stat().st_size>1000
        with bpy.data.libraries.load(str(source),link=False) as (available,unused):
            saved_scenes=list(available.scenes)
        assert saved_scenes==[row['id']],saved_scenes
        scene=bpy.data.scenes[row['id']]
        assert scene.unit_settings.system=='NONE' and scene.unit_settings.scale_length==1
        objects=[o for o in scene.objects if o.type=='MESH']
        assert len(objects)==row['meshGroups']<=5
        total=0;components=0
        for obj in objects:
            assert obj.location.length<1e-7 and obj.rotation_euler.to_matrix().is_identity
            assert all(abs(v-1)<1e-7 for v in obj.scale)
            assert not obj.modifiers and len(obj.data.materials)==1
            assert all(math.isfinite(v) for p in obj.data.vertices for v in p.co)
            assert all(p.area>1e-7 for p in obj.data.polygons),(row['id'],obj.name,'degenerate')
            tris=sum(len(p.vertices)-2 for p in obj.data.polygons);total+=tris
            assert tris<20000
            bm=bmesh.new();bm.from_mesh(obj.data)
            assert all(e.is_manifold and e.is_contiguous for e in bm.edges),(row['id'],obj.name,'edge/normals')
            remaining=set(bm.faces)
            while remaining:
                seed=remaining.pop();stack=[seed];component=[seed]
                while stack:
                    face=stack.pop()
                    for edge in face.edges:
                        for adjacent in edge.link_faces:
                            if adjacent in remaining:
                                remaining.remove(adjacent);stack.append(adjacent);component.append(adjacent)
                volume=sum(f.calc_center_median().dot(f.normal)*f.calc_area()/3 for f in component)
                assert volume>1e-7,(row['id'],obj.name,'inward component',volume)
                components+=1
            bm.free()
            mat=obj.data.materials[0]
            assert mat.diffuse_color[3]==1
            assert not any(n.type=='TEX_IMAGE' for n in mat.node_tree.nodes)
        assert total==row['triangles']<=2000
        assert row['boundsMinStuds'][1]>=-.00001 and min(row['dimensionsStuds'].values())>0
        assert max(row['dimensionsStuds'].values())<100
        # Parse actual FBX geometry, transforms, materials and object inventory.
        root,version=parse_fbx.parse(str(export))
        fbx_objects=next(e for e in root.elems if e.id==b'Objects')
        models=[e for e in fbx_objects.elems if e.id==b'Model']
        geometries=[e for e in fbx_objects.elems if e.id==b'Geometry']
        assert len(models)==len(geometries)==len(objects)
        exported_tris=0
        for geometry in geometries:
            vertices=next(e for e in geometry.elems if e.id==b'Vertices').props[0]
            assert all(math.isfinite(v) for v in vertices)
            indices=next(e for e in geometry.elems if e.id==b'PolygonVertexIndex').props[0]
            count=0
            for index in indices:
                count+=1
                if index<0:
                    assert count>=3;exported_tris+=count-2;count=0
            assert count==0
        assert exported_tris==total,(row['id'],exported_tris,total)
        for model in models:
            for e in model.elems:
                if e.id==b'Properties70':
                    for p in e.elems:
                        if p.props and p.props[0]==b'Lcl Scaling':
                            assert all(abs(v-1)<1e-6 for v in p.props[-3:])
        assert not any(e.id in [b'Texture',b'Video'] for e in fbx_objects.elems)
        report.append(dict(assetId=row['id'],triangles=total,meshGroups=len(objects),
            closedComponents=components,savedSourceScene=saved_scenes[0],fbxVersion=version,
            exportedTriangleCount=exported_tris,groundPivot=True,unitObjectTransforms=True,
            closedManifoldComponents=True,outwardNormals=True,textureDependencies=0,status='passed'))
    result=dict(assetCount=27,counts=expected,referenceCoverage=27,
        totalTriangles=sum(r['triangles'] for r in rows),
        highestTriangles=max(r['triangles'] for r in rows),
        largestAsset=max(rows,key=lambda r:r['triangles'])['id'],
        scope='Saved source inventory, mesh integrity/normals/scale, FBX parsing. No Studio import or gameplay testing.',
        assets=report)
    (BASE/'validation.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in result.items() if k!='assets'}))
    return result

if __name__=='__main__':validate()
