"""Isolated Task 005 authoring and the existing neutral-unit FBX pipeline."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from howrah_geometry import bp

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
PALETTE={'Steel':'AEBCC0','DarkSteel':'53696F','Asphalt':'596164','Concrete':'C8C7B9',
 'Stone':'B9AA8B','Cream':'E3D5B3','Oxide':'AD5746','Blue':'5B8DA5','White':'E6E2D2',
 'Yellow':'DCC174','Timber':'92704E','DarkWood':'5D4C3E','Green':'4F7060','Roof':'778781',
 'Window':'354B51','Canvas':'D3B779','Lamp':'F0D591','Ochre':'C5A064'}

def material(name):
 key='HBR_'+name
 if key in bpy.data.materials:return bpy.data.materials[key]
 h=PALETTE[name];s=[int(h[i:i+2],16)/255 for i in (0,2,4)]
 c=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in s]
 m=bpy.data.materials.new(key);m.diffuse_color=(*c,1);m.use_nodes=True
 node=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
 node.inputs['Base Color'].default_value=(*c,1);node.inputs['Roughness'].default_value=.78
 return m

class Asset:
 def __init__(self,asset_id,category,name,references,collision):
  self.id=asset_id;self.category=category;self.name=name;self.references=references;self.collision=collision;self.cache={};self.sockets={}
  scene=bpy.data.scenes.get(asset_id)
  if scene:
   for o in list(scene.objects):
    if o.get('AssetId')==asset_id:bpy.data.objects.remove(o,do_unlink=True)
   bpy.data.scenes.remove(scene)
  self.scene=bpy.data.scenes.new(asset_id)
  next(w for wm in bpy.data.window_managers for w in wm.windows).scene=self.scene
  self.scene.unit_settings.system='NONE';self.scene.unit_settings.scale_length=1
  self.scene['AssetId']=asset_id;self.scene['Task']='005';self.scene['Category']=category
  self.collection=bpy.data.collections.new(asset_id+'__Geometry');self.scene.collection.children.link(self.collection)
 def instance(self,key,geo=None,pos=(0,0,0),angle=0,collision_role='Decoration'):
  if key not in self.cache:
   assert geo is not None
   meshes=[]
   for role,(vertices,faces) in geo.groups.items():
    mesh=bpy.data.meshes.new(self.id+'__'+key+'__'+role)
    mesh.from_pydata([bp(p) for p in vertices],[],faces);mesh.update()
    bm=bmesh.new();bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>4])
    bm.to_mesh(mesh);bm.free();mesh.update();mesh.materials.append(material(role))
    meshes.append((role,mesh))
   self.cache[key]=meshes
  objects=[]
  for role,mesh in self.cache[key]:
   obj=bpy.data.objects.new(self.id+'__'+key+'__'+role,mesh);self.collection.objects.link(obj)
   obj.location=bp(pos);obj.rotation_euler=(0,0,angle)
   obj['AssetId']=self.id;obj['MeshKey']=self.id+'__'+key+'__'+role
   obj['PaletteRole']=role;obj['CollisionRole']=collision_role;objects.append(obj)
  return objects
 def finish(self,budget=None):
  folder=BASE/self.category/self.id;folder.mkdir(parents=True,exist_ok=True)
  objects=list(self.collection.objects)
  tri=lambda m:sum(len(p.vertices)-2 for p in m.polygons)
  total=sum(tri(o.data) for o in objects);unique={o.data for o in objects}
  largest=max(tri(m) for m in unique)
  assert largest<10000,(self.id,largest)
  if budget:assert budget[0]<=total<=budget[1],(self.id,total,budget)
  assembly=[]
  for obj in objects:
   assembly.append(dict(name=obj.name,meshKey=obj['MeshKey'],translationStuds=[round(obj.location.x,6),round(obj.location.z,6),round(-obj.location.y,6)],yawRadians=round(obj.rotation_euler.z,6),collisionRole=obj['CollisionRole']))
  source=folder/(self.id+'.blend');fbx=folder/(self.id+'.fbx')
  bpy.data.libraries.write(str(source),{self.scene},fake_user=True,compress=True)
  for o in self.scene.objects:o.select_set(False)
  for o in objects:o.select_set(True)
  bpy.context.view_layer.objects.active=objects[0]
  # Source has no modifiers or n-gons. Export the shared datablocks directly;
  # evaluating each object would duplicate linked FBX Geometry definitions.
  bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH'},
   global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',
   use_mesh_modifiers=False,bake_anim=False,path_mode='AUTO',mesh_smooth_type='FACE',use_custom_props=True,use_triangles=False)
  points=[obj.matrix_world@v.co for obj in objects for v in obj.data.vertices]
  low=[min(p[i] for p in points) for i in range(3)];high=[max(p[i] for p in points) for i in range(3)]
  dims=dict(width=round(high[0]-low[0],3),height=round(high[2]-low[2],3),depth=round(high[1]-low[1],3))
  rows=json.loads((BASE/'asset-manifest.json').read_text(encoding='utf8')) if (BASE/'asset-manifest.json').exists() else []
  row=dict(assetId=self.id,name=self.name,category=self.category,dimensionsStuds=dims,
   boundsMinStuds=[round(low[0],4),round(low[2],4),round(-high[1],4)],boundsMaxStuds=[round(high[0],4),round(high[2],4),round(-low[1],4)],
   assembledTriangles=total,uniqueGeometryTriangles=sum(tri(m) for m in unique),largestMeshTriangles=largest,
   meshInstances=len(objects),uniqueMeshes=len(unique),materials=sorted({o.data.materials[0].name for o in objects}),textures=[],
   source=str(source.relative_to(BASE)).replace('\\','/'),export=str(fbx.relative_to(BASE)).replace('\\','/'),
   references=self.references,collision=self.collision,sockets=self.sockets,assembly=assembly)
  (folder/'asset.json').write_text(json.dumps(row,indent=2),encoding='utf8')
  rows=[r for r in rows if r['assetId']!=self.id]+[row];rows.sort(key=lambda r:r['assetId'])
  (BASE/'asset-manifest.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
  print('SAVED '+self.id+' assembled='+str(total)+' unique='+str(row['uniqueGeometryTriangles'])+' meshes='+str(len(objects)),flush=True)
  return row

def save_master():
 scenes={s for s in bpy.data.scenes if s.get('Task')=='005'}
 bpy.data.libraries.write(str(BASE/'Howrah_Riverfront_Library.blend'),scenes,fake_user=True,compress=True)
