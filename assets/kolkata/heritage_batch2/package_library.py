"""Clean four-scene review library, leaving all asset transforms untouched."""
import bpy
import sys
from pathlib import Path
from types import SimpleNamespace

BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
from common import frame

bpy.ops.wm.read_factory_settings(use_empty=True)
initial=bpy.context.scene
scenes=[]
for key in ['writers','metropolitan','gpo','town_hall']:
    import json
    row=json.loads((BASE/key/'asset.json').read_text(encoding='utf8'))
    with bpy.data.libraries.load(str(BASE/key/row['source']),link=False) as (data,target):
        target.scenes=[row['assetId']]
    scenes.extend(target.scenes)
bpy.context.window.scene=scenes[0];bpy.data.scenes.remove(initial)
# Share identical palette materials when loading the independent source files.
canonical={}
for mat in list(bpy.data.materials):
    base=mat.name.split('.')[0]
    if base in canonical and tuple(mat.diffuse_color)==tuple(canonical[base].diffuse_color):mat.user_remap(canonical[base])
    else:canonical[base]=mat
root=next(c for c in scenes[0].collection.children if '__SOURCE' in c.name)
frame(SimpleNamespace(root=root))
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Heritage_Batch2_Live.blend'),compress=True)
print('CLEAN_LIBRARY_READY',[(s.name,len(s.objects)) for s in scenes],flush=True)
