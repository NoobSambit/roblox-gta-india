"""One focused source/export sanity checkpoint; no gameplay or benchmark tests."""
import bpy,bmesh,json,hashlib,math,sys
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]
bpy.ops.wm.open_mainfile(filepath=str(BASE.parents[1]/'VictoriaMemorial.blend'))
manifest=json.loads((BASE/'two-storey-manifest.json').read_text());plan=json.loads((ROOT/'authoring/task009/final-plan.json').read_text())
rows=[]
preserved=['VM_Architecture','VM_CollisionOnly'] if manifest.get('preservedFacadeFingerprint') else ['VM_Architecture','VM_Grounds','VM_CollisionOnly']
for name in preserved:
 for o in sorted(bpy.data.collections[name].objects,key=lambda x:x.name):
  rows.append([name,o.name,[list(v) for v in o.matrix_world],[[*v.co] for v in o.data.vertices] if o.type=='MESH' else [],[list(p.vertices) for p in o.data.polygons] if o.type=='MESH' else [],[m.name for m in o.data.materials] if o.type=='MESH' else []])
fingerprint=hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()
assert fingerprint==manifest.get('preservedFacadeFingerprint',manifest['preservedExteriorFingerprint']),'Approved facade/shell changed'
assets=[];issues=[]
for row in manifest['assets']:
 col=bpy.data.collections[row['assetId']];tris=0;parts=[]
 for o in col.objects:
  if o.type!='MESH':continue
  bm=bmesh.new();bm.from_mesh(o.data);tri=sum(len(f.verts)-2 for f in bm.faces);tris+=tri
  holes=sum(not e.is_manifold for e in bm.edges);degenerate=sum(f.calc_area()<1e-9 for f in bm.faces);badNormal=sum(not e.is_contiguous for e in bm.edges)
  if holes or degenerate or badNormal:issues.append(dict(asset=row['assetId'],mesh=o.name,nonmanifold=holes,zeroArea=degenerate,inconsistentNormals=badNormal))
  assert all(math.isfinite(v) for p in o.data.vertices for v in p.co)
  assert o.scale[:]==(1,1,1)
  parts.append(dict(name=o.name,triangles=tri));bm.free()
 assert tris==row['triangles'],row['assetId']
 assert (BASE/row['source']).exists() and (BASE/row['export']).exists()
 assets.append(dict(assetId=row['assetId'],triangles=tris,parts=parts))
assert not issues,issues
drum=bpy.data.collections['VIC_B15_DRUM_TRANSITION']
for o in drum.objects:
 if o.type!='MESH':continue
 for v in o.data.vertices:
  p=o.matrix_world@v.co;y=p.z;r=math.hypot(p.x,p.y)
  if abs(y-64)<.01:assert r<29.15,'Transition outside original drum base'
  if 67.59<=y<=88.81:assert r<28.2,'Transition protrudes through original exterior drum'
for row in plan['instances']:
 if row['instanceId'].startswith('VIC_HALL_LINING_'):
  top=row['position'][1]+69*row['stretch'][1];assert abs(top-63.5)<.001,'Wide lower lining extends above original roof'
markers=bpy.data.collections['VM009_GameplayMarkers'].objects
loot=[o for o in markers if o.get('LootId')];security=[o for o in markers if o.get('SecurityId')];routes=[o for o in markers if o.get('RouteId')]
assert len(loot)==28 and len({o['LootId'] for o in loot})==28
assert len(security)==16 and len(routes)==4
for item in plan['upperLayout']['groundFloorOriginal']['loot']:
 o=next(o for o in loot if o['LootId']==item['lootId']);p=item['rootPosition'];assert (o.location-Vector((p[0],-p[2],p[1]))).length<.001
result=dict(scope='Source geometry/export sanity; Studio evidence is recorded separately in inspection.json',approvedFacadeFingerprint=fingerprint,facadeUnchanged=True,groundsRevision=manifest.get('authorizedGroundsRevision',{}),assets=assets,issues=issues,lootMarkers=len(loot),securityMarkers=len(security),externalRoutes=len(routes),newUniqueTriangles=sum(a['triangles'] for a in assets),newMeshes=sum(len(a['parts']) for a in assets),largestNewMeshTriangles=max(p['triangles'] for a in assets for p in a['parts']),museumLights=len(bpy.data.collections['VM009_Lighting'].objects),sourceSha256=hashlib.sha256((BASE.parents[1]/'VictoriaMemorial.blend').read_bytes()).hexdigest(),robloxMeshSpecification='https://create.roblox.com/docs/art/modeling/specifications')
(ROOT/'docs/task009/source-inspection.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='assets'}))
