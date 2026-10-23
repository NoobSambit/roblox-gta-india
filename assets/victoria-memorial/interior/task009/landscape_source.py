"""Latest authorized Victoria-only courtyard/grounds pass; keeps facade data intact."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]
scene=next(s for s in bpy.data.scenes if s.collection.children.get('VM009_TwoStoreyInterior'));bpy.context.window.scene=scene
plan=json.loads((ROOT/'authoring/task009/final-plan.json').read_text());manifest=json.loads((BASE/'two-storey-manifest.json').read_text())
def fingerprint(names):
 rows=[]
 for name in names:
  for o in sorted(bpy.data.collections[name].objects,key=lambda x:x.name):rows.append([name,o.name,[list(v) for v in o.matrix_world],[[*v.co] for v in o.data.vertices] if o.type=='MESH' else [],[list(p.vertices) for p in o.data.polygons] if o.type=='MESH' else [],[m.name for m in o.data.materials] if o.type=='MESH' else []])
 return hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()
if 'preservedFacadeFingerprint' not in manifest:
 assert fingerprint(['VM_Architecture','VM_Grounds','VM_CollisionOnly'])==manifest['preservedExteriorFingerprint']
 manifest['preservedFacadeFingerprint']=fingerprint(['VM_Architecture','VM_CollisionOnly'])
assert fingerprint(['VM_Architecture','VM_CollisionOnly'])==manifest['preservedFacadeFingerprint']
old=bpy.data.collections.get('VM009_Landscaping')
if old:
 for o in list(old.objects):bpy.data.objects.remove(o,do_unlink=True)
 bpy.data.collections.remove(old)
land=bpy.data.collections.new('VM009_Landscaping');scene.collection.children.link(land)
materials={}
def mat(role,color,noise=False):
 id='VIC009_Garden_'+role;m=bpy.data.materials.get(id)
 if m:return m
 m=bpy.data.materials.new(id);m.use_nodes=True
 rgb=[int(color[i:i+2],16)/255 for i in [0,2,4]];linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
 m.diffuse_color=(*linear,1);bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(*linear,1);bs.inputs['Roughness'].default_value=.95
 if noise:
  tex=m.node_tree.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=14;tex.inputs['Detail'].default_value=1
  ramp=m.node_tree.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=tuple(v*.8 for v in linear)+(1,);ramp.color_ramp.elements[1].color=tuple(min(1,v*1.12) for v in linear)+(1,)
  m.node_tree.links.new(tex.outputs['Fac'],ramp.inputs[0]);m.node_tree.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
 return m
for role,color in [('Lawn','78956C'),('Path','B4AD99'),('Leaf','426A45'),('LeafLight','72915B'),('FloorDark','505D5D'),('Bronze','3E504B')]:materials[role]=mat(role,color,role=='Lawn')
def assign(o,role):
 if not role and o.material_slots and o.material_slots[0].material:
  name=o.material_slots[0].material.name
  if name.startswith('VM_'):role=name[3:].split('.')[0]
 if role in materials and o.material_slots:o.material_slots[0].link='OBJECT';o.material_slots[0].material=materials[role]
master=bpy.data.collections.get('VIC009_GardenTree_Master')
if master is None:
 master=bpy.data.collections.new('VIC009_GardenTree_Master')
 for src in bpy.data.collections['VM_Library_Export'].objects:
  if src.name.startswith('GardenTree__'):
   o=src.copy();master.objects.link(o);o.hide_viewport=False;o.hide_render=False;assign(o,o.get('MaterialRole',''))
 assert len(master.objects)==3
for p in plan['legacyInstances']:
 o=bpy.data.objects.new(p['instanceId'],None);o.instance_type='COLLECTION';o.instance_collection=master;o.location=(p['position'][0],-p['position'][2],p['position'][1]);o.rotation_euler.z=p['yaw'];o.scale=(p['scale'],)*3;o['SourceTemplateId']=p['templateId'];land.objects.link(o)
changed=[]
for o in bpy.data.collections['VM_Grounds'].objects:
 if o.type!='MESH':continue
 factor=1.7 if o.name.startswith(('BoundaryPicket','BoundaryRail','BoundarySideRail')) else 1.35 if o.name.startswith(('BoundaryBase','BoundarySide')) else 1
 if factor!=1 and not o.get('Task009BoundaryRaised'):
  o.data=o.data.copy()
  for v in o.data.vertices:v.co.z*=factor
  o.location.z*=factor;o['Task009BoundaryRaised']=True;o['Task009BoundaryScale']=factor
 if factor!=1:changed.append(dict(name=o.name,heightScale=factor))
 assign(o,o.get('MaterialRole',''))
for o in bpy.data.collections['VM_Interior'].objects:
 if o.type=='MESH' and o.name.startswith('QuadrangleFloor_'):assign(o,'FloorDark')
manifest['authorizedGroundsRevision']=dict(reason=plan['groundsRevision']['authorizedBy'],boundaryParts=changed,newTrees=len(plan['legacyInstances']),newPlacedTreeTriangles=sum(p['triangles'] for p in plan['legacyInstances']),groundsMaterials=list(materials),facadePreserved=True)
(BASE/'two-storey-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(ROOT/'authoring/task009/two-storey.json').write_text(json.dumps(manifest,indent=2)+'\n')
(ROOT/'docs/task009/grounds-revision.json').write_text(json.dumps(manifest['authorizedGroundsRevision'],indent=2)+'\n')
assert fingerprint(['VM_Architecture','VM_CollisionOnly'])==manifest['preservedFacadeFingerprint']
bpy.ops.wm.save_as_mainfile(filepath=str(BASE.parents[1]/'VictoriaMemorial.blend'),compress=True)
print(json.dumps(dict(raisedBoundaryParts=len(changed),newTrees=len(plan['legacyInstances']),facadeUnchanged=True)))
