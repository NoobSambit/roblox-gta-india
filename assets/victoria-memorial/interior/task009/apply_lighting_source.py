"""Mirror final authored light settings; leave every architectural object intact."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]
source=BASE.parents[1]/'VictoriaMemorial.blend'
if bpy.data.filepath!=str(source):bpy.ops.wm.open_mainfile(filepath=str(source))
scene=next(s for s in bpy.data.scenes if s.collection.children.get('VM009_TwoStoreyInterior'))
bpy.context.window.scene=scene
plan=json.loads((ROOT/'authoring/task009/final-plan.json').read_text())
col=bpy.data.collections['VM009_Lighting']
before={o.name:(o.matrix_world.copy(),len(o.data.vertices) if o.type=='MESH' else None) for o in scene.objects if o.type!='LIGHT' and o.get('AssetId')!='VIC_B12_LIGHT'}
for row in plan['lights']:
    o=col.objects[row['id']+'_PreviewLight'];d=o.data
    kind='SPOT' if row['kind']=='Spot' else 'POINT'
    if d.type!=kind:
        d=bpy.data.lights.new(row['id']+'_Final',kind);o.data=d
    d.energy=row.get('blenderPower',2000 if row['kind']=='Spot' else 1000)
    d.color=tuple(v/255 for v in row['color'])
    d.use_custom_distance=True;d.cutoff_distance=row['range']
    if d.type=='SPOT':d.spot_size=math.radians(row['angle']);d.spot_blend=.65
    o['RobloxRange']=row['range'];o['RobloxBrightness']=row['brightness'];o['RobloxShadows']=row['shadows']
    o.location=(row['position'][0],-row['position'][2],row['position'][1])
    if row.get('target'):
        o.location.z+=.35 if row['target'][1]>=row['position'][1] else -.35
        t=row['target'];o.rotation_euler=(Vector((t[0],-t[2],t[1]))-o.location).to_track_quat('-Z','Y').to_euler()
    else:o.rotation_euler=(0,0,0)
    if not row.get('fixtureId'):
        fixture=bpy.data.objects.get(row['id'])
        assert fixture and fixture.get('AssetId')=='VIC_B12_LIGHT'
        fixture.location=(row['position'][0],-row['position'][2],row['position'][1])
m=bpy.data.materials.get('VIC009_LampDiffuser')
if m:
    bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bs.inputs['Emission Strength'].default_value=.08
for name,(matrix,vertices) in before.items():
    o=bpy.data.objects[name];assert o.matrix_world==matrix
    if vertices is not None:assert len(o.data.vertices)==vertices
bpy.ops.wm.save_as_mainfile(filepath=str(BASE.parents[1]/'VictoriaMemorial.blend'),compress=True)
print('Lighting mirrored; architecture unchanged.')
