"""Generate the small asset index from the saved production manifest."""
import csv,json
from pathlib import Path

BASE=Path(__file__).resolve().parent
rows=json.loads((BASE/'asset-manifest.json').read_text(encoding='utf8'))
lines=['# Tier 3 asset index','','Dimensions include balconies and roof projections; X width, Y height, Z depth in studs. Source photos are reference only.','','| Asset | Floors | W x H x D | Triangles | Groups | Files | Reference |','|---|---:|---|---:|---:|---|---|']
for r in rows:
 d=r['dimensionsStuds'];dims=' x '.join(str(d[k]) for k in ['width','height','depth'])
 lines.append('| '+r['id']+' | '+str(r['floors'])+' | '+dims+' | '+str(r['triangles'])+' | '+str(r['meshGroups'])+' | [Blender]('+r['source']+') / [FBX]('+r['export']+') | [Photo source]('+r['reference']['sourcePage']+') |')
(BASE/'asset-index.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
groups={}
for family in ['old_kolkata','modern','mixed_use','informal']:
 group=[r for r in rows if r['family']==family]
 groups[family]=dict(count=len(group),minimumTriangles=min(r['triangles'] for r in group),maximumTriangles=max(r['triangles'] for r in group),totalTriangles=sum(r['triangles'] for r in group))
print(json.dumps(dict(families=groups,totalTriangles=sum(r['triangles'] for r in rows),meshGroups=sum(r['meshGroups'] for r in rows),materialNames=sorted({m for r in rows for m in r['materials']})),indent=2))
