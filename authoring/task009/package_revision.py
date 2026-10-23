"""Stage the one necessary native-import batch and retain source review evidence."""
import json,shutil,hashlib,base64
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'assets/victoria-memorial/interior/task009'
plan=json.loads((ROOT/'authoring/task009/final-plan.json').read_text());manifest=json.loads((BASE/'two-storey-manifest.json').read_text())
meshes=json.loads((ROOT/'authoring/task009/two-storey-meshes.json').read_text())
dest=ROOT/'exports/victoria_task009_rebuild';dest.mkdir(exist_ok=True,parents=True)
rows=[]
for a in manifest['assets']:
 src=BASE/a['export'];dst=dest/src.name;shutil.copy2(src,dst)
 sha=hashlib.sha256(dst.read_bytes()).hexdigest();prepared=next(m for m in meshes['assets'] if m['assetId']==a['assetId'])
 assert sha==prepared['fbxSha256'],a['assetId']
 rows.append(dict(assetId=a['assetId'],file=dst.name,sha256=sha,triangles=a['triangles']))
assert len(rows)==len(meshes['assets'])==26
(dest/'import-checksums.json').write_text(json.dumps(rows,indent=2)+'\n')
(dest/'README.md').write_text('''# Final revised Task009 native import batch

26 individual FBXs: the imported 24-file base plus two fitted Blender correction modules. This is the two-floor architecture plus room-specific exhibit support, hero art and courtyard repair/furniture designs. Existing Task008 shared meshes remain in Studio.

The current Hood Testing integration already uses all 26 designs. Do not import them again. Only for a fresh restoration without the stored masters, import all 26 FBXs using **Scale Unit Stud**, **Scale Factor 1**, **Merge Meshes off**, **Anchored on**. Leave models in Workspace, named `<AssetId>_Roblox`; the edit-only importer adopts uploaded MeshIds. The final active MeshIds are recorded in `docs/task009/mesh-ids.json`.

Do not import the whole VictoriaMemorial.blend as a replacement landmark. Do not delete the current landmark or gameplay markers. No public publishing is needed.

`import-checksums.json` identifies the exact current batch. Native importer access is the only manual mesh-upload step; Studio's engine mesh-upload API is unavailable to this session.
''')
review=ROOT/'artifacts/review/task009/blender';review.mkdir(exist_ok=True,parents=True)
for name in ['blender_fitted_drum_exterior','blender_portal_join_fixed']:
 src=ROOT/'artifacts/recovery/task009-captures'/(name+'.b64')
 if src.exists():(review/(name+'.png')).write_bytes(base64.b64decode(src.read_text()))
for filename,id in [('material.json','111127937664295'),('wall-material.json','74587698959678')]:
 p=BASE/'materials'/filename;data=json.loads(p.read_text());data['robloxImageId']='rbxassetid://'+id;data['uploadStatus']='Uploaded, assigned and visually reviewed in final Studio integration';p.write_text(json.dumps(data,indent=2)+'\n')
catalog={r['assetId']:r for r in json.loads((BASE.parent/'asset-manifest.json').read_text())['assets']+manifest['assets']}
used={p['assetId'] for p in plan['instances']}
stats=dict(plan['statistics'],uniqueUsedDesigns=len(used),uniqueUsedTriangles=sum(catalog[id]['triangles'] for id in used),reusedOriginalTreeUniqueTriangles=224,newDesigns=len(rows),newUniqueTriangles=sum(r['triangles'] for r in rows),visibleAdditiveTriangles=plan['statistics']['importedPlacedTriangles']+plan['statistics']['nativeVisualTriangles']+plan['statistics'].get('legacyPlacedTriangles',0),maximumNewMeshTriangles=max(p['triangles'] for a in meshes['assets'] for p in a['pieces']),newMaterialMeshes=sum(len(a['pieces']) for a in meshes['assets']),softReviewThreshold=60000,studioRevisionIntegrated=False)
stats['categories']={}
for p in plan['instances']:
 category=catalog[p['assetId']]['category'];r=stats['categories'].setdefault(category,dict(instances=0,placedTriangles=0));r['instances']+=1;r['placedTriangles']+=p['triangles']
evidence=ROOT/'docs/task009/integration.json'
if evidence.exists():stats['studioRevisionIntegrated']=json.loads(evidence.read_text()).get('fittedBlenderCorrections',False)
(ROOT/'docs/task009/source-statistics.json').write_text(json.dumps(stats,indent=2)+'\n')
print(json.dumps(stats))
