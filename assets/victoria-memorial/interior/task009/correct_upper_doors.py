"""Rebuild the actual two shared meshes that covered the upper entrances."""
import bpy,bmesh,json,math,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]
sys.path.insert(0,str(BASE.parent));from pipeline import Geo,bp,material,triangles
win=bpy.context.window;original=next(s for s in bpy.data.scenes if s.collection.children.get('VM009_TwoStoreyInterior'))
g=Geo()
for n,x,z,w,d in [('West',-14.25,-61.5,31.5,53),('East',25.75,-61.5,8.5,53),('North',11.5,-86.25,20,3.5),('South',11.5,-41.25,20,12.5)]:g.box((x,-.5,z),(w,1,d),'Floor'+n+':Ivory')
g.vault((0,12,-61.5),29.2,8,.5,53,'Ivory',20)
for x in [-29.2,29.2]:
 g.box((x,15.95,-61.5),(.45,10.9,53),'Stone')
 for z,d in [(-73.5,5),(-47,24)]:g.box((x,10.7,z),(.45,21.4,d),'Stone')
jobs=[('VIC_B09_STAIR_HALL',g)]
g=Geo();g.box((0,31.6,0),(2,3.2,34),'Beam:Ivory')
for z,l in [(-14.5,5),(2.5,5),(17.5,1)]:g.box((0,40.5,z),(3.2,13,l),'Jambs:Stone')
g.box((0,45.75,0),(3.2,2.5,36),'Header:Ivory');jobs.append(('VIC_B10_UPPER_DOORS',g))
manifest=json.loads((BASE/'two-storey-manifest.json').read_text())
for id,g in jobs:
 col=bpy.data.collections[id];row=next(r for r in manifest['assets'] if r['assetId']==id)
 for key,(verts,faces) in g.groups.items():
  component,role=key.split(':',1) if ':' in key else ('Body',key);name=id+'__'+key.replace(':','__')
  obj=col.objects.get(name)
  if obj and obj.type!='MESH':bpy.data.objects.remove(obj,do_unlink=True);obj=None
  mesh=bpy.data.meshes.new(name+'_Corrected');mesh.from_pydata([bp(v) for v in verts],[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.triangulate(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);bm.to_mesh(mesh);bm.free();mesh.materials.append(material(role))
  if obj is None:obj=bpy.data.objects.new(name,mesh);col.objects.link(obj)
  else:obj.data=mesh
  obj['AssetId']=id;obj['PaletteRole']=role;obj['Component']=component;obj['CollisionRole']='Decoration'
 objs=[o for o in col.objects if o.type=='MESH'];row['triangles']=sum(triangles(o.data) for o in objs);row['materialMeshes']=len(objs)
 row['components']=[dict(name=o.name,component=o['Component'],material=o['PaletteRole'],translationStuds=[0,0,0],triangles=triangles(o.data)) for o in objs]
 points=[o.matrix_world@v.co for o in objs for v in o.data.vertices];low=[min(p[i] for p in points) for i in range(3)];high=[max(p[i] for p in points) for i in range(3)];row['dimensionsStuds']=dict(width=high[0]-low[0],height=high[2]-low[2],depth=high[1]-low[1]);row['boundsMinStuds']=[low[0],low[2],-high[1]];row['boundsMaxStuds']=[high[0],high[2],-low[1]]
 scene=bpy.data.scenes[id];win.scene=scene
 for o in scene.objects:o.select_set(o.type=='MESH')
 bpy.context.view_layer.objects.active=objs[0]
 bpy.ops.export_scene.fbx(filepath=str(BASE/row['export']),use_selection=True,object_types={'MESH'},global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',use_mesh_modifiers=False,bake_anim=False,path_mode='AUTO',mesh_smooth_type='FACE',use_custom_props=True,use_triangles=False)
 bpy.data.libraries.write(str(BASE/row['source']),{scene},fake_user=True,compress=True);(BASE/'TwoStorey'/id/'asset.json').write_text(json.dumps(row,indent=2)+'\n')
 for p in manifest['instances']:
  if p['assetId']==id:p['triangles']=row['triangles']
manifest['uniqueTriangles']=sum(r['triangles'] for r in manifest['assets']);manifest['placedTriangles']=sum(p['triangles'] for p in manifest['instances'])
(BASE/'two-storey-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(ROOT/'authoring/task009/two-storey.json').write_text(json.dumps(manifest,indent=2)+'\n')
win.scene=original;bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(BASE.parents[1]/'VictoriaMemorial.blend'),compress=True)
print('Cut two real 12 x 10.5 stud upper entrances per wing; rebuilt shared wall and portal geometry.')
