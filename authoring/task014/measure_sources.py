"""Read-only survey of finished Blender assets; run in background Blender."""
from pathlib import Path
import bpy, json, hashlib
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/kolkata/masterplan_task014'
OUT.mkdir(parents=True, exist_ok=True)
sources = {}
for group in ['tier1', 'heritage_batch2', 'cultural_batch', 'landmarks_batch4']:
    for meta in (ROOT / 'assets/kolkata' / group).glob('*/asset.json'):
        d = json.loads(meta.read_text())
        sources[d['assetId']] = meta.parent / d['source']
sources.update({
    'VICTORIA': ROOT / 'assets/victoria-memorial/VictoriaMemorial.blend',
    'HOWRAH': ROOT / 'assets/kolkata/howrah_bridge/bridge/KOL_HBR_HOWRAH/KOL_HBR_HOWRAH.blend',
    'GHAT': ROOT / 'assets/kolkata/howrah_bridge/ghat/KOL_HBR_GHAT/KOL_HBR_GHAT.blend',
    'KOL_T1_DAKSHINESHWAR': ROOT / 'assets/kolkata/dakshineshwar/KOL_T1_DAKSHINESHWAR.blend',
})
rows = []
for key, path in sources.items():
    bpy.ops.wm.open_mainfile(filepath=str(path))
    scene = bpy.context.scene
    cols = []
    for c in scene.collection.children:
        meshes = [o for o in c.all_objects if o.type == 'MESH']
        pts = [o.matrix_world @ Vector(v) for o in meshes for v in o.bound_box]
        bounds = [[round(f(p[i] for p in pts), 4) for i in range(3)] for f in [min,max]] if pts else None
        cols.append(dict(name=c.name, hidden=c.hide_render, meshes=len(meshes), bounds_blender=bounds,
                         children=[x.name for x in c.children]))
    row = dict(id=key, source=str(path.relative_to(ROOT)).replace('\\','/'),
               sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
               scene=scene.name, collections=cols, objects=len(scene.objects))
    rows.append(row)
    print('SURVEY', key, json.dumps(cols), flush=True)
(OUT / 'source-survey.json').write_text(json.dumps(rows, indent=2))
print('SURVEY_COMPLETE', len(rows), flush=True)
