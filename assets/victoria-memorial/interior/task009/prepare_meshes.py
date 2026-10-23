"""Read individual validated FBXs in Blender and prepare exact engine upload data.

This avoids relying on native UI access. Each material/component stays separate;
the resulting permanent mesh asset IDs are reused for all placed instances.
"""
import bpy
import hashlib
import json
from pathlib import Path

BASE=Path(__file__).resolve().parent
KIT=BASE.parent
ROOT=BASE.parents[3]
OUT=ROOT/'authoring/task009'
plan=json.loads((OUT/'final-plan.json').read_text())
used={p['assetId'] for p in plan['instances']}
original=json.loads((KIT/'asset-manifest.json').read_text())
repairs=json.loads((BASE/'two-storey-manifest.json').read_text())
two_storey='--two-storey' in __import__('sys').argv
jobs=[(BASE,r) for r in repairs['assets']] if two_storey else [(KIT,r) for r in original['assets'] if r['assetId'] in used]+[(BASE,r) for r in repairs['assets'] if r['assetId'] in used]
payload=[]
def rv(v):return [round(v.x,7),round(v.z,7),round(-v.y,7)]
for folder,row in jobs:
    scene=bpy.data.scenes.new(row['assetId']);bpy.context.window.scene=scene
    path=folder/row['export']
    bpy.ops.import_scene.fbx(filepath=str(path))
    bpy.context.view_layer.update()
    pieces=[]
    for obj in sorted(scene.objects,key=lambda o:o.name):
        if obj.type!='MESH':continue
        mesh=obj.data;mesh.calc_loop_triangles()
        points=[obj.matrix_world@v.co for v in mesh.vertices]
        low=[min(p[i] for p in points) for i in range(3)]
        high=[max(p[i] for p in points) for i in range(3)]
        center=tuple((a+b)/2 for a,b in zip(low,high))
        from mathutils import Vector
        center=Vector(center)
        pieces.append(dict(name=obj.name,component=obj.get('Component','Body'),material=obj.get('PaletteRole','Ivory'),
            center=rv(center),size=[round(high[0]-low[0],7),round(high[2]-low[2],7),round(high[1]-low[1],7)],triangles=len(mesh.loop_triangles)))
    assert sum(p['triangles'] for p in pieces)==row['triangles'],row['assetId']
    payload.append(dict(assetId=row['assetId'],category=row['category'],triangles=row['triangles'],
        sourceFbx=str(path.relative_to(ROOT)).replace('\\','/'),fbxSha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        componentPivots=row.get('componentPivots',{}),pieces=pieces))
    for obj in list(scene.objects):bpy.data.objects.remove(obj,do_unlink=True)
    bpy.context.window.scene=bpy.data.scenes[0];bpy.data.scenes.remove(scene)
    print('PREPARED '+row['assetId'],flush=True)
(OUT/('two-storey-meshes.json' if two_storey else 'meshes.json')).write_text(json.dumps(dict(assets=payload,palette=original['palette']),separators=(',',':'))+'\n')
print(json.dumps(dict(assets=len(payload),meshes=sum(len(r['pieces']) for r in payload),triangles=sum(r['triangles'] for r in payload))),flush=True)
