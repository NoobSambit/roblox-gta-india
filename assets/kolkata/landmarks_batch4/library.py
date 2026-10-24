"""Blender-only review library of three scenes, never a placed district."""
from pathlib import Path
import bpy
import json
BASE=Path(__file__).resolve().parent
for key in ['new_market','indian_museum','st_pauls']:
    r=json.loads((BASE/key/'asset.json').read_text())
    with bpy.data.libraries.load(str(BASE/key/r['source']),link=False) as (src,dst):
        dst.scenes=[r['assetId']]
for s in list(bpy.data.scenes):
    if not s.get('AssetId'):bpy.data.scenes.remove(s)
bpy.context.window.scene=bpy.data.scenes['KOL_T1_NEW_MARKET']
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Batch4_Live.blend'),compress=True)
print('BATCH4_LIBRARY_READY: three independent scenes, active New Market')
