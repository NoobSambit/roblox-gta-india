"""Finish the shared bay's arch spring with substantial simplified classical columns."""
import bpy,bmesh,json,math,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]
sys.path.insert(0,str(BASE.parent));from pipeline import Geo,bp,material,triangles
win=bpy.context.window;original=next(s for s in bpy.data.scenes if s.collection.children.get('VM009_TwoStoreyInterior'))
id='VIC_B07_WING_BAY';g=Geo();g.vault((0,17.2,0),16.35,8,1.0,1,'Ivory',16)
g.vault((0,36.0,0),16.35,3.0,.6,.8,'Ivory',16)
for x in [-16.75,16.75]:
 g.column(x,0,0,17.2,.68,'Ivory',8)
 g.box((x,31.6,0),(.8,8.8,.9),'Ivory');g.box((x,27.6,0),(1.2,.5,1.2),'Ivory');g.box((x,36.1,0),(1.3,.6,1.3),'Ivory')
m=json.loads((BASE/'two-storey-manifest.json').read_text());row=next(r for r in m['assets'] if r['assetId']==id);col=bpy.data.collections[id]
for key,(verts,faces) in g.groups.items():
 obj=next(o for o in col.objects if o.type=='MESH' and o.get('PaletteRole')==key)
 mesh=bpy.data.meshes.new(id+'_Finished');mesh.from_pydata([bp(v) for v in verts],[],faces);mesh.update()
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.triangulate(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);bm.to_mesh(mesh);bm.free();mesh.materials.append(material(key));obj.data=mesh
row['triangles']=sum(triangles(o.data) for o in col.objects if o.type=='MESH');assert row['triangles']<1200
for c in row['components']:c['triangles']=row['triangles']
row['name']='Finished ground gallery arch, column bases and capitals, upper pilaster bay'
scene=bpy.data.scenes[id];win.scene=scene
for o in scene.objects:o.select_set(o.type=='MESH')
bpy.context.view_layer.objects.active=next(o for o in scene.objects if o.type=='MESH')
bpy.ops.export_scene.fbx(filepath=str(BASE/row['export']),use_selection=True,object_types={'MESH'},global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',use_mesh_modifiers=False,bake_anim=False,path_mode='AUTO',mesh_smooth_type='FACE',use_custom_props=True,use_triangles=False)
bpy.data.libraries.write(str(BASE/row['source']),{scene},fake_user=True,compress=True)
(BASE/'TwoStorey'/id/'asset.json').write_text(json.dumps(row,indent=2)+'\n')
for p in m['instances']:
 if p['assetId']==id:p['triangles']=row['triangles']
m['uniqueTriangles']=sum(r['triangles'] for r in m['assets']);m['placedTriangles']=sum(p['triangles'] for p in m['instances'])
(BASE/'two-storey-manifest.json').write_text(json.dumps(m,indent=2)+'\n');(ROOT/'authoring/task009/two-storey.json').write_text(json.dumps(m,indent=2)+'\n')
win.scene=original;bpy.ops.wm.save_as_mainfile(filepath=str(BASE.parents[1]/'VictoriaMemorial.blend'),compress=True);print(id,row['triangles'])
