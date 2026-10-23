"""Remove the superseded white bottom band so continuous mushroom dado is visible."""
import bpy,bmesh,json,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]
sys.path.insert(0,str(BASE.parent));from pipeline import triangles
win=bpy.context.window;original=next(s for s in bpy.data.scenes if s.collection.children.get('VM009_TwoStoreyInterior'))
id='VIC_B06_WING_ENVELOPE';col=bpy.data.collections[id]
removed=0
for o in col.objects:
 if o.type!='MESH' or o.get('PaletteRole')!='Ivory' or o.get('Component')=='Floor':continue
 bm=bmesh.new();bm.from_mesh(o.data);pending=set(bm.verts);delete=[]
 while pending:
  start=pending.pop();group={start};stack=[start]
  while stack:
   for e in stack.pop().link_edges:
    for v in e.verts:
     if v in pending:pending.remove(v);group.add(v);stack.append(v)
  if min(v.co.z for v in group)>-.001 and max(v.co.z for v in group)<2.201:delete.extend(group)
 removed+=len(delete)
 if delete:bmesh.ops.delete(bm,geom=delete,context='VERTS');bm.to_mesh(o.data)
 bm.free()
m=json.loads((BASE/'two-storey-manifest.json').read_text())
for assetId in [id,'VIC_B07_WING_BAY']:
 row=next(r for r in m['assets'] if r['assetId']==assetId);c=bpy.data.collections[assetId];objs=[o for o in c.objects if o.type=='MESH']
 row['triangles']=sum(triangles(o.data) for o in objs)
 for component in row['components']:
  obj=next(o for o in objs if o.name==component['name']);component['triangles']=triangles(obj.data)
 points=[o.matrix_world@v.co for o in objs for v in o.data.vertices];lo=[min(p[i] for p in points) for i in range(3)];hi=[max(p[i] for p in points) for i in range(3)]
 row['dimensionsStuds']=dict(width=hi[0]-lo[0],height=hi[2]-lo[2],depth=hi[1]-lo[1]);row['boundsMinStuds']=[lo[0],lo[2],-hi[1]];row['boundsMaxStuds']=[hi[0],hi[2],-lo[1]]
 scene=bpy.data.scenes[assetId];win.scene=scene
 for o in scene.objects:o.select_set(o.type=='MESH')
 bpy.context.view_layer.objects.active=objs[0]
 bpy.ops.export_scene.fbx(filepath=str(BASE/row['export']),use_selection=True,object_types={'MESH'},global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',use_mesh_modifiers=False,bake_anim=False,path_mode='AUTO',mesh_smooth_type='FACE',use_custom_props=True,use_triangles=False)
 bpy.data.libraries.write(str(BASE/row['source']),{scene},fake_user=True,compress=True)
 (BASE/'TwoStorey'/assetId/'asset.json').write_text(json.dumps(row,indent=2)+'\n')
 for p in m['instances']:
  if p['assetId']==assetId:p['triangles']=row['triangles']
m['uniqueTriangles']=sum(r['triangles'] for r in m['assets']);m['placedTriangles']=sum(p['triangles'] for p in m['instances'])
(BASE/'two-storey-manifest.json').write_text(json.dumps(m,indent=2)+'\n');(ROOT/'authoring/task009/two-storey.json').write_text(json.dumps(m,indent=2)+'\n')
win.scene=original;bpy.ops.wm.save_as_mainfile(filepath=str(BASE.parents[1]/'VictoriaMemorial.blend'),compress=True);print('Removed superseded dado vertices',removed)
