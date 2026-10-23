"""Pack only the two reviewed compounds, leaving unrelated asset libraries intact."""
import bpy
import sys
import json
from pathlib import Path
from types import SimpleNamespace
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
import estate_common as C

if __name__=='__main__':
    bpy.ops.wm.read_factory_settings(use_empty=True)
    old=bpy.context.scene;loaded=[]
    for key in ['rajbari','jorasanko']:
        folder=BASE/key;row=json.loads((folder/'asset.json').read_text(encoding='utf8'))
        with bpy.data.libraries.load(str(folder/row['source']),link=False) as (src,dst):dst.scenes=list(src.scenes)
        loaded.extend(dst.scenes)
    bpy.context.window.scene=loaded[0];bpy.data.scenes.remove(old)
    # Merge identical shared palette materials introduced by appending each source.
    seen={}
    for mat in list(bpy.data.materials):
        key=(mat.name.split('.')[0],tuple(round(v,6) for v in mat.diffuse_color))
        if key in seen:mat.user_remap(seen[key]);bpy.data.materials.remove(mat)
        else:seen[key]=mat
    C.H.frame(SimpleNamespace(root=loaded[0].collection))
    bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Cultural_Batch_Live.blend'),compress=True)
    print('CULTURAL_LIBRARY_READY '+str([s.name for s in loaded]),flush=True)
