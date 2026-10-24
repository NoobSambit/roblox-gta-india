"""Render saved review cameras only; keep source and scene content unchanged."""
from pathlib import Path
import bpy, sys, json, hashlib
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'assets/kolkata/masterplan_task014'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Kolkata_Masterplan_Stage_A.blend'))
s=bpy.context.scene
names=[o.name for o in s.objects if o.type=='CAMERA']
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
reviews=[]
for name in sorted(names):
    if args and not any(name.startswith(a) for a in args):continue
    s.frame_set(int(name[:2]))
    s.camera=bpy.data.objects[name]
    bpy.data.collections['Planning Markers Boundaries'].hide_render=not (name.startswith('01_') or name.startswith('07_'))
    s.render.filepath=str(OUT/(name+'.png'))
    bpy.ops.render.render(write_still=True)
    if s.camera.name!=name:raise RuntimeError('Timeline camera override: '+s.camera.name+' vs '+name)
    reviews.append(dict(file=name+'.png',actual_camera=s.camera.name,frame=s.frame_current,
                        sha256=hashlib.sha256((OUT/(name+'.png')).read_bytes()).hexdigest()))
    print('REVIEW_SAVED',name,flush=True)
if args and (OUT/'review-views.json').exists():
    previous=json.loads((OUT/'review-views.json').read_text())
    updated={r['file']:r for r in previous};updated.update({r['file']:r for r in reviews})
    reviews=sorted(updated.values(),key=lambda r:r['file'])
if len(reviews)==8:
    if len(set(r['sha256'] for r in reviews))!=8:raise RuntimeError('Review cameras produced duplicate images')
    (OUT/'review-views.json').write_text(json.dumps(reviews,indent=2))
