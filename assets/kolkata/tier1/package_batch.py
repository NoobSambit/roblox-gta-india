"""Assemble saved, validated sources into a clean Blender review library."""
import bpy
import json
from pathlib import Path
from mathutils import Vector

BASE=Path(__file__).resolve().parent
KEYS=['atmosphere','trump','urbana','royal','sonar','jw']

bpy.ops.wm.read_factory_settings(use_empty=True)
rows=[];scenes=[]
for key in KEYS:
    folder=BASE/key;row=json.loads((folder/'asset.json').read_text(encoding='utf8'))
    validation=json.loads((folder/'validation.json').read_text(encoding='utf8'))
    assert validation['status']=='passed',key
    listed={(folder/p['file']).resolve() for p in row['exports']}
    for path in (folder/'exports').glob('*.fbx'):
        if path.resolve() not in listed:
            assert path.name.startswith(row['assetId']+'__') and path.parent==folder/'exports'
            path.unlink()
    with bpy.data.libraries.load(str(folder/row['source']),link=False) as (src,dst):
        dst.scenes=[row['assetId']]
    scene=dst.scenes[0];scene.name=row['assetId'];scene['ReviewStatus']='Exterior source / minimal export checks passed; Studio import unverified'
    scenes.append(scene);rows.append(row)

showroom=bpy.data.scenes.new('Kolkata Tier 1 - Asset Showroom')
showroom['Purpose']='Asset review grid only; not a proposed city layout or game scene'
for index,scene in enumerate(scenes):
    source=next(c for c in scene.collection.children if '__SOURCE' in c.name)
    instance=bpy.data.objects.new(rows[index]['name'],None)
    instance.instance_type='COLLECTION';instance.instance_collection=source
    showroom.collection.objects.link(instance);instance.location=((index%3-1)*560,(index//3)*560,0)

bpy.context.window.scene=next(s for s in scenes if s.name=='KOL_T1_JW')
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active;space.clip_start=1;space.clip_end=6000
            space.shading.type='MATERIAL';space.overlay.show_floor=False
            space.overlay.show_axis_x=False;space.overlay.show_axis_y=False
            space.region_3d.view_perspective='CAMERA'
(BASE/'batch-manifest.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Kolkata_Tier1_Library.blend'),compress=True)
print('PACKAGED six independent scenes and an asset review grid',flush=True)
