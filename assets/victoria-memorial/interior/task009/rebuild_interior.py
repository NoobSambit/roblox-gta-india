"""Reconstruct interior INSIDE original Victoria source, preserving exterior data.

Background Blender only. Exports reusable modules, never a replacement landmark.
The untouched pre-task source is required for deterministic, repeatable rebuilds.
"""
import bpy,bmesh,json,math,sys,hashlib
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]
SOURCE=BASE.parents[1]/'VictoriaMemorial.blend'
BACKUP=ROOT/'artifacts/recovery/VictoriaMemorial-pre-Task009.blend'
sys.path.insert(0,str(BASE.parent));import pipeline
pipeline.BASE=BASE
from pipeline import Geo,Asset,bp
bpy.ops.wm.open_mainfile(filepath=str(BACKUP))
original=bpy.context.scene
def fingerprint():
 rows=[]
 for name in ['VM_Architecture','VM_Grounds','VM_CollisionOnly']:
  for o in sorted(bpy.data.collections[name].objects,key=lambda x:x.name):
   rows.append([name,o.name,[list(v) for v in o.matrix_world],[[*v.co] for v in o.data.vertices] if o.type=='MESH' else [],[list(p.vertices) for p in o.data.polygons] if o.type=='MESH' else [],[m.name for m in o.data.materials] if o.type=='MESH' else []])
 return hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()
before=fingerprint();assets=[];instances=[]
def save(code,name,g,cap=2000):
 a=Asset(code,'TwoStorey',name,cap,g,note='Task009 original-source interior reconstruction; approved exterior unchanged')
 for o in a.objects:
  bm=bmesh.new();bm.from_mesh(o.data)
  assert all(e.is_manifold and e.is_contiguous for e in bm.edges),(code,'open geometry')
  assert all(p.area>1e-9 for p in o.data.polygons),(code,'degenerate face')
  bm.free()
 a.scene['Task']='009';a.row['geometrySource']='Original-source Victoria two-storey reconstruction'
 a.save();assets.append(a);return a
def place(a,name,pos,yaw=0):instances.append(dict(assetId=a.id,instanceId=name,position=list(pos),yaw=yaw,triangles=a.row['triangles'],role='TwoStoreyArchitecture'))
# Retain the familiar twelve-bay lower arcade silhouette; replace the fake balcony.
g=Geo();g.arch((0,0,0),10.8,19,1,1.8,'Ivory',12)
for x in [-6.7,6.7]:g.column(x,-.9,0,25,.62,'Stone',8)
g.box((0,26.3,-2.0),(15,1.4,7.5),'Ivory');g.box((0,25.45,-1.0),(14.8,.35,5.2),'Ivory')
lower=save('VIC_B01_HALL_ARCADE','Rebuilt lower hall arcade and balcony corbel',g)
g=Geo();g.arch((0,0,0),10.8,6.0,.7,1.1,'Ivory',12)
for x in [-6.5,6.5]:
 g.box((x,6.2,0),(1.1,12.4,1.3),'Stone');g.box((x,12.35,0),(1.7,.4,1.8),'Ivory')
g.box((0,12.8,0),(14.9,.5,2),'Ivory')
upper=save('VIC_B02_UPPER_ARCADE','Accessible upper hall arcade',g)
# One 30-degree curved floor/rail module; twelve shared copies form the overlook.
g=Geo();segments=4
for j in range(segments):
 a=-math.pi/12+j*math.pi/6/segments;b=a+math.pi/6/segments
 p=[(23*math.sin(a),23*math.cos(a)),(30.8*math.sin(a),30.8*math.cos(a)),(30.8*math.sin(b),30.8*math.cos(b)),(23*math.sin(b),23*math.cos(b))]
 g.plan(p,-1.0,0,'Floor:Ivory')
 for y,w,d,role in [(.25,.5,.6,'Ivory'),(3.9,.4,.7,'Brass')]:
  g.beam((23.5*math.sin(a),y,23.5*math.cos(a)),(23.5*math.sin(b),y,23.5*math.cos(b)),w,d,role)
 for t in [a+(b-a)*.33,a+(b-a)*.67]:g.box((23.5*math.sin(t),2,23.5*math.cos(t)),(.22,3.4,.22),'Ivory',-t)
for t in [-math.pi/12,math.pi/12]:g.box((23.5*math.sin(t),2,23.5*math.cos(t)),(.65,4,.65),'Ivory',-t)
balcony=save('VIC_B03_BALCONY','Walkable curved floor and restrained balustrade',g)
def ringpanel(code,low,high):
 g=Geo()
 for j in range(4):
  a=-math.pi/12+j*math.pi/24;b=a+math.pi/24
  g.plan([(30.4*math.sin(a),30.4*math.cos(a)),(31*math.sin(a),31*math.cos(a)),(31*math.sin(b),31*math.cos(b)),(30.4*math.sin(b),30.4*math.cos(b))],low,high,'Ivory')
 return save(code,'Closed rotunda lining segment',g)
lining=ringpanel('VIC_B04_UPPER_LINING',48,69)
groundlining=ringpanel('VIC_B05_LOWER_LINING',7,32.8)
for i in range(12):
 a=i*math.tau/12
 place(lower,f'VIC_HALL_LOWER_{i:02}',(28.9*math.sin(a),7,28.9*math.cos(a)),a)
 place(upper,f'VIC_HALL_UPPER_{i:02}',(28.9*math.sin(a),34,28.9*math.cos(a)),a)
 place(balcony,f'VIC_HALL_BALCONY_{i:02}',(0,34,0),a)
 place(lining,f'VIC_HALL_LINING_{i:02}',(0,0,0),a)
 if i%3:place(groundlining,f'VIC_HALL_LOWER_WALL_{i:02}',(0,0,0),a)
# Full upper wing floor; two-level wall treatment and shallow upper barrel ceiling.
# Template courtyard is -Z; turn north wings by pi (symmetrical X allocation).
g=Geo();g.box((0,26.7,0),(57,1,34.6),'Floor:Ivory')
g.box((0,19.8,17.22),(57,39.6,.14),'Stone')
for x in [-16.75,16.75]:g.box((x,8.6,-17.22),(23.5,17.2,.14),'Stone')
g.box((0,28.4,-17.22),(57,22.4,.14),'Stone')
for z in [-16.95,16.95]:
 for y,h in [(25.85,.4),(27.7,.55),(38.8,.6)]:
  # Keep the central courtyard doorway free below its existing lintel.
  if z<0 and y<17.2:
   for x in [-16.75,16.75]:g.box((x,y,z),(23.5,h,.35),'Ivory')
  else:g.box((0,y,z),(57,h,.35),'Ivory')
v=Geo();v.vault((0,36.2,0),17.25,3.4,.4,57,'Ivory',16);g.merge(v,angle=math.pi/2)
wing=save('VIC_B06_WING_ENVELOPE','Two-storey wing floor, wall articulation and upper ceiling',g)
# Ground arch carries the floor; restrained upper pilasters articulate the second floor.
g=Geo();g.vault((0,0,0),16.35,8,.8,1.0,'Ivory',16,17.2)
for x in [-16.75,16.75]:
 g.box((x,31.6,0),(.8,8.8,.9),'Ivory');g.box((x,27.6,0),(1.2,.5,1.2),'Ivory');g.box((x,36.1,0),(1.3,.6,1.3),'Ivory')
g.vault((0,36.1,0),16.35,3.4,.5,.8,'Ivory',16)
rib=save('VIC_B07_WING_BAY','Ground structural arch and upper pilaster bay',g)
for side in [-1,1]:
 for sx in [-1,1]:
  place(wing,f'VIC_WING_{sx}_{side}',(sx*60.5,6.8,side*76),math.pi if side<0 else 0)
  for i,x in enumerate([34,51,72,88]):place(rib,f'VIC_WING_BAY_{sx}_{side}_{i}',(sx*x,6.8,side*76),math.pi/2)
# Double-flight stair: open underside, physical step silhouettes and continuous handrails.
g=Geo();rise=27.2/36
for lane,direction,base in [(5.25,-1,0),(-5.25,1,13.6)]:
 polygon=[]
 for i in range(18):
  z=direction*i*1.5 + (0 if direction<0 else -27)
  polygon.extend([(z,base+(i+1)*rise),(z+direction*1.5,base+(i+1)*rise)])
 polygon.extend([(polygon[-1][0],base+17*rise-.6),(polygon[0][0],base-.6)])
 n=len(polygon);verts=[(lane+x,y,z) for x in [-4.25,4.25] for z,y in polygon]
 g.solid(verts,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],'Ivory')
 for dx in [-4.15,4.15]:
  start=0 if direction<0 else -27;end=-27 if direction<0 else 0
  g.beam((lane+dx,base+rise+4,start),(lane+dx,base+18*rise+4,end),.24,.32,'Brass')
  for k in range(7):
   t=k/6;z=start+(end-start)*t;y=base+17*rise*t
   g.box((lane+dx,y+2.4,z),(.23,4.8,.23),'Charcoal')
g.box((0,13.1,-31.5),(19,1,9),'Landing:Ivory')
for x in [-9.25,9.25]:g.box((x,15.55,-31.5),(.35,3.9,9),'Ivory')
g.box((0,15.55,-35.75),(19,3.9,.4),'Ivory')
stair=save('VIC_B08_STAIR','8.5-stud two-flight museum stair and balustrades',g)
for sign in [-1,1]:place(stair,'VIC_STAIR_NORTH' if sign<0 else 'VIC_STAIR_SOUTH',(-sign*11.5,6.8,sign*48),0 if sign<0 else math.pi)
# Entrance-hall upper deck is split around the exact stair void; each component has box collision.
g=Geo()
for n,x,z,w,d in [('West',-14.25,-61.5,31.5,53),('East',25.75,-61.5,8.5,53),('North',11.5,-86.25,20,3.5),('South',11.5,-41.25,20,12.5)]:g.box((x,-.5,z),(w,1,d),'Floor'+n+':Ivory')
g.vault((0,12,-61.5),29.2,8,.5,53,'Ivory',20)
for x in [-29.2,29.2]:
 g.box((x,15.95,-61.5),(.45,10.9,53),'Stone')
 for z,d in [(-73.5,5),(-47,24)]:g.box((x,10.7,z),(.45,21.4,d),'Stone')
deck=save('VIC_B09_STAIR_HALL','Upper landing deck with stair void and finished vaulted ceiling',g)
for side in [-1,1]:place(deck,'VIC_UPPER_VESTIBULE_'+str(side),(0,34,0),0 if side<0 else math.pi)
# Paired upper doorways replace ONLY the four internal entry/gallery lintels.
g=Geo();g.box((0,31.6,0),(2,3.2,34),'Beam:Ivory')
for z,l in [(-14.5,5),(2.5,5),(17.5,1)]:g.box((0,40.5,z),(3.2,13,l),'Jambs:Stone')
g.box((0,45.75,0),(3.2,2.5,36),'Header:Ivory')
portal=save('VIC_B10_UPPER_DOORS','Paired twelve-stud upper wing doors and lower structural beam',g)
for sx in [-1,1]:
 for sz in [-1,1]:place(portal,f'VIC_WING_DOORS_{sx}_{sz}',(sx*31,0,sz*76),0 if sz<0 else math.pi)
# Hall north/south internal wall has a real upper opening; east/west facade walls stay untouched.
g=Geo();g.box((0,32.5,0),(28,1,4),'Beam:Ivory')
for x in [-21,21]:g.box((x,52,0),(28,28,4),'Jambs:Ivory')
g.box((0,57,0),(14,18,4),'Header:Ivory');g.box((0,33.5,0),(14,1,7.5),'Floor:Ivory')
hallDoor=save('VIC_B11_HALL_CONNECTION','Ground axial opening and genuine upper hall connection',g)
for s in [-1,1]:place(hallDoor,'VIC_HALL_CONNECTION_'+str(s),(0,0,s*33),0)
# Physical low-poly light fixture, with separate soft luminous diffuser.
g=Geo();g.box((0,0,0),(4,.35,1.4),'Charcoal');g.box((0,-.2,0),(3.6,.12,1.05),'Diffuser:Paper')
for x in [-1.7,1.7]:g.box((x,-.16,0),(.1,.25,1.2),'Brass')
fixture=save('VIC_B12_LIGHT','Reusable museum ceiling fixture / diffuser',g,200)
# Move old interior-only geometry out of the authored scene. Keep reusable sources intact.
archived=[];interior=bpy.data.collections['VM_Interior'];shell=bpy.data.collections['VM_Structure_Collision']
archive=bpy.data.collections.new('VM009_ArchivedInterior');archive.use_fake_user=True
for collection in [interior,shell]:
 for o in list(collection.objects):
  pos=o.location;localZ=-pos.y
  replace=collection==interior and (o.name.startswith('QueensHallArch_') or o.name.startswith('QueensHallInnerWall') or 'Vault_' in o.name)
  replace|=collection==shell and (o.name.startswith('EntryDoorLintel') or (o.name.startswith(('RotundaUpperWall','AxialPassageLintel')) and abs(localZ)>30))
  if replace:collection.objects.unlink(o);archive.objects.link(o);archived.append(o.name)
bpy.context.window.scene=original
assembly=bpy.data.collections.new('VM009_TwoStoreyInterior');original.collection.children.link(assembly)
for p in instances:
 a=next(a for a in assets if a.id==p['assetId']);o=bpy.data.objects.new(p['instanceId'],None);o.instance_type='COLLECTION';o.instance_collection=a.collection
 o.location=bp(p['position']);o.rotation_euler.z=p['yaw'];o['AssetId']=a.id;assembly.objects.link(o)
plan=json.loads((ROOT/'docs/task009/two-floor-plan.json').read_text())
for item in plan['upperLoot']:
 o=bpy.data.objects.new(item['lootId'],None);o.location=bp(item['rootPosition']);o['LootId']=item['lootId'];o['Floor']=2;bpy.data.collections['VM_Metadata'].objects.link(o)
assert before==fingerprint(),'Exterior data changed'
original['Task009']='Two-storey interior, ground layout and approved exterior preserved'
original['ExteriorFingerprint']=before
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE),compress=True)
manifest=dict(task='009 revised',assets=[a.row for a in assets],instances=instances,uniqueTriangles=sum(a.row['triangles'] for a in assets),placedTriangles=sum(p['triangles'] for p in instances),preservedExteriorFingerprint=before,originalInteriorArchived=archived,source=str(SOURCE.relative_to(ROOT)))
(BASE/'two-storey-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(ROOT/'authoring/task009/two-storey.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(dict(assets=len(assets),uniqueTriangles=manifest['uniqueTriangles'],placedTriangles=manifest['placedTriangles'],archived=len(archived),exteriorUnchanged=True)),flush=True)
