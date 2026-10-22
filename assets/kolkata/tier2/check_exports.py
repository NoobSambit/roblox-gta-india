"""One minimal saved-source / export inspection, run in Blender.

Does not import into Studio, run gameplay, benchmark, or roundtrip the scenes.
"""
import bpy,json,math
from pathlib import Path
from io_scene_fbx import parse_fbx

BASE=Path(r'C:\Users\Sambit Pradhan\Documents\Indian_Hood\assets\kolkata\tier2')
rows=json.loads((BASE/'library-summary.json').read_text(encoding='utf8'))
report=[]
for row in rows:
 folder=BASE/Path(row['path']).name
 source=folder/row['source'];export=folder/row['fbx']
 with bpy.data.libraries.load(str(source),link=False) as (available,unused):
  scenes=list(available.scenes)
 assert len(scenes)==1,(source,scenes)
 root,version=parse_fbx.parse(str(export))
 objects=next(e for e in root.elems if e.id==b'Objects')
 models=[e for e in objects.elems if e.id==b'Model']
 assert len(models)==row['meshObjects']
 scales=[]
 for model in models:
  for e in model.elems:
   if e.id==b'Properties70':
    for p in e.elems:
     if p.props and p.props[0]==b'Lcl Scaling':scales.append(tuple(p.props[-3:]))
 assert all(all(abs(v-1)<1e-5 for v in s) for s in scales)
 scene=next(s for s in bpy.data.scenes if s.get('AssetId')=='kolkata.tier2.'+folder.name)
 assert scene.unit_settings.system=='NONE' and scene.unit_settings.scale_length==1
 assert max(row['boundsStuds'])<512 and row['largestMeshTriangles']<20000
 report.append(dict(building=row['building'],savedSourceScene=scenes[0],fbxVersion=version,exportObjectCount=len(models),objectScalesAllOne=True,sourceUnits='None / 1',boundsStuds=row['boundsStuds'],largestMeshTriangles=row['largestMeshTriangles'],status='passed'))
(BASE/'export-check.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report))
