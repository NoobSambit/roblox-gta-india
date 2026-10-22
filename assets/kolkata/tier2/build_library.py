"""Original Tier 2 Kolkata architecture. Run in Blender, not ordinary Python.

Coordinates are Roblox studs: X right, Y up, front -Z. Blender mapping
(x,-z,y) is a rotation. Exports are complete assembled buildings, not templates.
Only this library's T2_ scenes are generated. No Studio world edits occur.
"""
import bpy, bmesh, math, json, sys
from pathlib import Path
from mathutils import Vector

ROOT=Path(r'C:\Users\Sambit Pradhan\Documents\Indian_Hood')
BASE=ROOT/'assets/kolkata/tier2'
if str(BASE) not in sys.path:sys.path.insert(0,str(BASE))
from geometry import Geometry as G, bv, rotate

PALETTE={
 'Ivory':(.88,.86,.75,1),'White':(.96,.95,.88,1),
 'Red':(.47,.065,.038,1),'RedLight':(.62,.13,.075,1),
 'Shadow':(.21,.24,.22,1),'Glass':(.035,.095,.10,1),
 'Green':(.035,.18,.085,1),'GreenLight':(.065,.27,.13,1),
 'Slate':(.105,.145,.16,1),'Gold':(.66,.43,.12,1),
 'Stone':(.48,.47,.40,1),'Court':(.57,.52,.42,1),
 'Grass':(.18,.34,.16,1),'Wood':(.24,.12,.055,1),
 'Saffron':(.94,.29,.035,1),'Blue':(.015,.07,.28,1),
}
MATERIALS={}
for role,rgba in PALETTE.items():
 mat=bpy.data.materials.get('T2_'+role) or bpy.data.materials.new('T2_'+role)
 mat.diffuse_color=rgba;mat.use_nodes=True
 node=mat.node_tree.nodes.get('Principled BSDF')
 node.inputs['Base Color'].default_value=rgba
 node.inputs['Roughness'].default_value=.7
 node.inputs['Metallic'].default_value=.25 if role=='Gold' else 0
 MATERIALS[role]=mat

def prism(g,points,depth,z,mat):
 """Closed extrusion of a counterclockwise polygon in the XY plane."""
 front=[(x,y,z-depth/2) for x,y in points]
 back=[(x,y,z+depth/2) for x,y in points]
 g.polygon(list(reversed(front)),mat);g.polygon(back,mat)
 for i in range(len(points)):
  j=(i+1)%len(points)
  g.polygon([front[i],front[j],back[j],back[i]],mat)

def arch_panel(g,x,y,z,w,h,mat='Glass',segments=10):
 r=w/2;spring=h-r
 points=[(x-r,y),(x+r,y)]+[(x+r*math.cos(i*math.pi/segments),y+spring+r*math.sin(i*math.pi/segments)) for i in range(segments+1)]
 prism(g,points,.18,z,mat)

def window(g,x,y,z,w,h,arched=True,trim='Ivory',shutters=False):
 if arched:
  arch_panel(g,x,y,z,w,h)
  g.arch(w,h-w/2,.28,.3,(x,y,z-.19),trim,10)
 else:
  g.box((x,y+h/2,z),(w,h,.18),'Glass')
  for dx in [-w/2-.14,w/2+.14]:g.box((x+dx,y+h/2,z-.19),(.28,h+.55,.32),trim)
  for yy in [y-.14,y+h+.14]:g.box((x,yy,z-.19),(w+.55,.28,.32),trim)
 g.box((x,y-.35,z-.3),(w+1,.4,.9),trim)
 g.box((x,y+h*.44,z-.22),(.11,h*.85,.13),trim)
 g.box((x,y+h*.48,z-.24),(w,.11,.12),trim)
 if shutters:
  for side in [-1,1]:
   xx=x+side*w*.255
   g.box((xx,y+h*.39,z-.29),(w*.43,h*.76,.16),'Green')
   for j in range(2):g.box((xx,y+h*(.24+j*.28),z-.4),(w*.4,.17,.1),'GreenLight')

def col(g,x,z,bottom,height,r=1,mat='Ivory',doric=False,gilt=False):
 g.box((x,bottom+.22,z),(r*2.9,.44,r*2.9),mat)
 g.lathe([(0,r*1.2),(.4,r*1.2),(.7,r),(height-1.55,r*.86),(height-1.25,r*1.15),(height-.7,r*1.3)],12 if r>=1 else 8,mat,(x,bottom+.44,z))
 g.box((x,bottom+height-.1,z),(r*2.9,.5,r*2.9),mat)
 if not doric:
  for side in [-1,1]:
   g.box((x+side*r*.95,bottom+height-.9,z),(r*.75,.65,r*1.7),'Gold' if gilt else mat)
   g.box((x,bottom+height-.9,z+side*r*.95),(r*1.7,.65,r*.75),'Gold' if gilt else mat)

def balustrade(g,w,y,z,mat='Ivory',height=2.3,spacing=2.2):
 g.box((0,y,z),(w,.32,.6),mat)
 g.box((0,y+height,z),(w+.25,.35,.75),mat)
 count=max(2,int(w/spacing))
 for i in range(count+1):
  x=-w/2+i*w/count
  g.lathe([(0,.21),(height*.5,.13),(height-.15,.21)],4,mat,(x,y+.16,z))

def pediment(g,w,y,z,rise,mat='Red'):
 prism(g,[(-w/2,y),(w/2,y),(0,y+rise)],1.4,z,mat)
 g.box((0,y-.25,z-.3),(w+1.7,.9,2),'Ivory')
 for side in [-1,1]:
  a=Vector((side*(w/2+.3),y+.3,z-.9));b=Vector((0,y+rise+.65,z-.9))
  d=b-a;angle=math.atan2(d.y,d.x)
  # Rectangular cornice along the raking edge, avoiding round pipes.
  points=[]
  for p in [(0,-.43),(d.length,-.43),(d.length,.43),(0,.43)]:
   points.append((a.x+p[0]*math.cos(angle)-p[1]*math.sin(angle),a.y+p[0]*math.sin(angle)+p[1]*math.cos(angle)))
  prism(g,points,1.9,z-.9,'Ivory')

def clock(g,x,y,z,r):
 points=[(x+r*math.cos(i*math.tau/24),y+r*math.sin(i*math.tau/24)) for i in range(24)]
 prism(g,points,.2,z,'Ivory')
 for i in range(24):
  a,b=i*math.tau/24,(i+1)*math.tau/24
  prism(g,[(x+r*math.cos(a),y+r*math.sin(a)),(x+(r+.23)*math.cos(a),y+(r+.23)*math.sin(a)),(x+(r+.23)*math.cos(b),y+(r+.23)*math.sin(b)),(x+r*math.cos(b),y+r*math.sin(b))],.24,z-.13,'Gold')
 for i in range(12):
  t=i*math.tau/12
  g.box((x+r*.8*math.sin(t),y+r*.8*math.cos(t),z-.25),(.15,.24,.06),'Slate')
 g.beam((x,y,z-.31),(x+r*.18,y+r*.67,z-.31),.10,'Slate',4)
 g.beam((x,y,z-.34),(x-r*.50,y+r*.18,z-.34),.13,'Slate',4)

def figure(g,x,y,z,h=4.5,mat='Ivory'):
 g.box((x,y+.2,z),(1.7,.4,1.4),mat)
 g.lathe([(0,.65),(h*.45,.35),(h*.65,.55)],8,mat,(x,y+.4,z))
 g.ellipsoid((x,y+h*.85,z),(.34,.43,.34),mat,8,4)
 for side in [-1,1]:g.beam((x,y+h*.62,z),(x+side*1.1,y+h*(.85 if side>0 else .45),z),.18,mat,6)

def flat_flag(g,x,y,z):
 g.cylinder((x,y+4,z),.075,8,'Slate',6)
 for yy,mat in [(6.9,'Saffron'),(5.9,'White'),(4.9,'Green')]:g.box((x+2.05,y+yy,z),(4.1,1,.05),mat)
 points=[(x+2.05+.36*math.cos(i*math.tau/12),y+5.9+.36*math.sin(i*math.tau/12)) for i in range(12)]
 prism(g,points,.02,z-.04,'Blue')

def outline_slab(g,outline,y,height,mat='Ivory',expand=0):
 points=[(x+math.copysign(expand,x),z+math.copysign(expand,z)) for x,z in outline]
 g.polygon([(x,y-height/2,z) for x,z in points],mat)
 g.polygon([(x,y+height/2,z) for x,z in reversed(points)],mat)
 for i,(x,z) in enumerate(points):
  xx,zz=points[(i+1)%len(points)]
  g.polygon([(x,y-height/2,z),(x,y+height/2,z),(xx,y+height/2,zz),(xx,y-height/2,zz)],mat)

def foundation(a):
 """Small continuous footings, without filling Jorasanko's courtyard/passage."""
 top=.65;thickness=.8;center=top-thickness/2
 if a.slug=='writers_building':
  a.box('Foundation',(0,center,0),(240,thickness,60),'Stone',group='Foundation')
  a.box('PorticoFooting',(0,center,-30),(58,thickness,9),'Stone',group='Foundation')
 elif a.slug=='gpo':
  a.box('EastFoundation',(24,center,-17),(108,thickness,61),'Stone',group='Foundation')
  a.box('ReturnFoundation',(-47,center,24),(58,thickness,116),'Stone',group='Foundation')
  g=G();g.cylinder((-44,center,-28),27,thickness,'Stone',32)
  a.add('RotundaFoundation',g,'Foundation')
 elif a.slug=='metropolitan_building':
  outline=[(-65,-44),(49,-44),(65,-28),(65,44),(-65,44)]
  g=G();outline_slab(g,outline,center,thickness,'Stone',1.3)
  a.add('Foundation',g,'Foundation')
  a.box('FrontPorticoFooting',(-15,center,-46),(31,thickness,8),'Stone',group='Foundation')
  a.box('SidePorticoFooting',(67,center,13),(8,thickness,31),'Stone',group='Foundation')
 elif a.slug=='town_hall':
  a.box('Foundation',(0,center,2),(95,thickness,63),'Stone',group='Foundation')
  a.box('PorticoFooting',(0,center,-35),(79,thickness,23),'Stone',group='Foundation')
 else:
  for side in [-1,1]:
   a.box('SideFoundation_'+str(side),(side*57,center,0),(20,thickness,114),'Stone',group='Foundation')
   a.box('EntranceFoundation_'+str(side),(side*30,center,-48),(48,thickness,18),'Stone',group='Foundation')
  a.box('RearFoundation',(0,center,48),(98,thickness,18),'Stone',group='Foundation')

class Asset:
 def __init__(self,slug,label,prefix):
  self.slug,self.label,self.prefix=slug,label,prefix
  self.path=BASE/slug;self.path.mkdir(parents=True,exist_ok=True)
  (self.path/'exports').mkdir(exist_ok=True)
  self.scene=bpy.data.scenes.new('T2_'+label.replace(' ',''))
  bpy.context.window.scene=self.scene
  self.scene.unit_settings.system='NONE';self.scene.unit_settings.scale_length=1
  self.root=bpy.data.collections.new(prefix+'_Asset');self.scene.collection.children.link(self.root)
  self.groups={};self.objects=[];self.templates={};self.placements=[];self.collisions=[]
  self.scene['AssetId']='kolkata.tier2.'+slug;self.scene['Units']='Roblox studs; Y up in manifest; front -Z'
 def group(self,name):
  if name not in self.groups:
   c=bpy.data.collections.new(self.prefix+'_'+name);self.root.children.link(c);self.groups[name]=c
  return self.groups[name]
 def template(self,key,g):
  meshes={}
  for mat in dict.fromkeys(g.mat):
   vertices=[];faces=[];smooth=[]
   for f,role,sm in zip(g.f,g.mat,g.smooth):
    if role!=mat:continue
    offset=len(vertices);vertices.extend(bv(g.v[i]) for i in f)
    faces.append(tuple(range(offset,offset+len(f))));smooth.append(sm)
   mesh=bpy.data.meshes.new(self.prefix+'_'+key+'__'+mat)
   mesh.from_pydata(vertices,[],faces);mesh.materials.append(MATERIALS[mat]);mesh.update()
   for p,sm in zip(mesh.polygons,smooth):p.use_smooth=sm
   bm=bmesh.new();bm.from_mesh(mesh)
   bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00005)
   bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.000001)
   bm.to_mesh(mesh);bm.free();mesh.update()
   meshes[mat]=mesh
  self.templates[key]=meshes
  return key
 def inst(self,key,name,pos=(0,0,0),yaw=0,group='Facades'):
  for role,mesh in self.templates[key].items():
   obj=bpy.data.objects.new(self.prefix+'_'+name+'__'+role,mesh)
   self.group(group).objects.link(obj);obj.location=bv(pos);obj.rotation_euler[2]=yaw
   obj['MeshKey']=key+'__'+role;obj['MaterialRole']=role;obj['Static']=True
   self.objects.append(obj)
   self.placements.append(dict(name=obj.name,meshKey=obj['MeshKey'],position=list(pos),yaw=yaw,group=group))
 def add(self,key,g,group='Structure',pos=(0,0,0),yaw=0):
  self.template(key,g);self.inst(key,key,pos,yaw,group)
 def box(self,name,pos,size,mat='Ivory',group='Structure',solid=True):
  g=G();g.box((0,0,0),size,mat);self.add(name,g,group,pos)
  if solid:self.collider(name,pos,size)
 def collider(self,name,pos,size,yaw=0):self.collisions.append(dict(name=name,position=list(pos),size=list(size),yaw=yaw,shape='Block'))
 def bands(self,w,d,ys,center=(0,0,0),mat='Ivory'):
  g=G()
  for y in ys:
   for yy,extra,h in [(y,0,.48),(y+.5,.8,.5),(y+1.05,1.5,.35)]:g.box((center[0],yy,center[2]),(w+extra,h,d+extra),mat)
  self.add('CorniceBands',g,'Roofline')
 def rear_windows(self,w,d,floors,spacing=12):
  g=G()
  for y in floors:window(g,0,y,-.2,3.9,6.5,False)
  self.template('RearWindow',g)
  for i in range(int(w/spacing)-1):self.inst('RearWindow',f'RearWindow_{i}',(-w/2+(i+1)*spacing,0,d/2+.02),math.pi,'Rear')
 def finish(self):
  foundation(self)
  bpy.context.view_layer.update()
  coords=[o.matrix_world@Vector(v) for o in self.objects for v in o.bound_box]
  lo=[min(p[i] for p in coords) for i in range(3)];hi=[max(p[i] for p in coords) for i in range(3)]
  unique={o.data for o in self.objects};triangles=0;max_tri=0
  for mesh in unique:
   mesh.calc_loop_triangles();max_tri=max(max_tri,len(mesh.loop_triangles))
   if len(mesh.loop_triangles)>20000:raise RuntimeError('Roblox per-mesh triangle limit: '+mesh.name)
  for o in self.objects:triangles+=len(o.data.loop_triangles)
  if any(any(abs(v-1)>1e-6 for v in o.scale) for o in self.objects):raise RuntimeError('Unapplied scale')
  self.bounds=[round(hi[0]-lo[0],3),round(hi[2]-lo[2],3),round(hi[1]-lo[1],3)]
  manifest=dict(assetId=self.scene['AssetId'],label=self.label,units='Roblox studs',front='-Z',pivot=[0,0,0],bounds=self.bounds,palette=PALETTE,objects=self.placements,collisionBoxes=self.collisions,meshes={m.name:len(m.loop_triangles) for m in unique},notes='Exterior asset; no full rooms. No runtime generator. Clone repeated MeshKeys with shared mesh IDs during later integration.')
  (self.path/'assembly.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
  staging=bpy.data.collections.new(self.prefix+'_ExportTemporary');self.scene.collection.children.link(staging)
  bpy.ops.object.select_all(action='DESELECT');copies=[]
  for source in self.objects:
   obj=source.copy();obj.data=source.data.copy();obj.name=source.name+'_RBX'
   staging.objects.link(obj);obj.select_set(True);copies.append(obj)
  bpy.context.view_layer.update()
  fbx=self.path/'exports'/f'{self.prefix}_{self.slug}_Roblox.fbx'
  bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH'},global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',use_mesh_modifiers=True,bake_anim=False,path_mode='AUTO',mesh_smooth_type='FACE',use_custom_props=True)
  for obj in copies:
   mesh=obj.data;bpy.data.objects.remove(obj,do_unlink=True);bpy.data.meshes.remove(mesh)
  bpy.data.collections.remove(staging)
  # Simplified collision helpers are saved for authoring, never in the visual FBX.
  c=self.group('CollisionGuides');c.hide_render=True;c.hide_viewport=True
  for i,entry in enumerate(self.collisions):
   g=G();g.box((0,0,0),entry['size'],'Shadow')
   mesh=bpy.data.meshes.new(self.prefix+'_CollisionMesh_'+str(i));mesh.from_pydata([bv(v) for v in g.v],[],g.f)
   obj=bpy.data.objects.new(self.prefix+'_COL_'+entry['name'],mesh);c.objects.link(obj)
   obj.location=bv(entry['position']);obj.rotation_euler[2]=entry['yaw'];obj.display_type='WIRE';obj.hide_render=True
  self.presentation(lo,hi)
  self.blend=self.path/f'{self.prefix}_{self.slug}.blend'
  bpy.data.libraries.write(str(self.blend),{self.scene},fake_user=True,compress=True)
  self.summary=dict(building=self.label,path=str(self.path.relative_to(ROOT)),source=self.blend.name,fbx=str(fbx.relative_to(self.path)),meshObjects=len(self.objects),uniqueMeshes=len(unique),triangles=triangles,largestMeshTriangles=max_tri,boundsStuds=self.bounds,collisionBoxes=len(self.collisions),sourceBytes=self.blend.stat().st_size,exportBytes=fbx.stat().st_size,sourceSaved=True,exportSucceeded=True)
  (self.path/'asset-summary.json').write_text(json.dumps(self.summary,indent=2),encoding='utf8')
  print('ASSET_FINISHED '+json.dumps(self.summary),flush=True)
 def presentation(self,lo,hi):
  c=self.group('Presentation_ONLY');self.presentation_collection=c
  scene=self.scene;scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=1100;scene.render.resolution_y=780;scene.render.resolution_percentage=100
  scene.render.image_settings.file_format='PNG';scene.world=bpy.data.worlds.new(self.prefix+'_StudioWorld');scene.world.use_nodes=True
  scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.35,.43,.49,1)
  scene.world.node_tree.nodes['Background'].inputs[1].default_value=.3
  scene.view_settings.view_transform='AgX'
  camera_data=bpy.data.cameras.new(self.prefix+'_ReviewCamera');camera=bpy.data.objects.new(self.prefix+'_ReviewCamera',camera_data);c.objects.link(camera);scene.camera=camera
  extent=max(self.bounds[0],self.bounds[2],self.bounds[1]*1.45)
  target=Vector(((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,(hi[2]+lo[2])*.42))
  camera.location=target+Vector((extent*1.02,extent*1.48,extent*.86))
  camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=extent*1.65
  for name,loc,energy,size in [('Key',(-extent*.6,extent*.8,extent*1.6),extent*extent*28,extent*.65),('Fill',(extent,0,extent),extent*extent*5,extent*.8)]:
   data=bpy.data.lights.new(self.prefix+'_'+name,'AREA');data.energy=energy;data.shape='DISK';data.size=size
   obj=bpy.data.objects.new(data.name,data);c.objects.link(obj);obj.location=loc;obj.rotation_euler=(target-obj.location).to_track_quat('-Z','Y').to_euler()
  mesh=bpy.data.meshes.new(self.prefix+'_BackdropMesh');s=extent*2
  mesh.from_pydata([(-s,-s,-.16),(s,-s,-.16),(s,s,-.16),(-s,s,-.16)],[],[(0,1,2,3)])
  mat=bpy.data.materials.get('T2_Backdrop') or bpy.data.materials.new('T2_Backdrop');mat.diffuse_color=(.105,.15,.17,1)
  mesh.materials.append(mat);obj=bpy.data.objects.new(self.prefix+'_Backdrop_NOT_EXPORTED',mesh);c.objects.link(obj)

def writers():
 a=Asset('writers_building',"Writers' Building",'WB')
 a.box('MainEnvelope',(0,26.5,0),(236,53,56),'Red')
 a.box('StoneBase',(0,1,0),(238,2,58),'Stone')
 a.bands(236,56,[2,18,36.5,53])
 # One linked facade module supplies three distinct window registers.
 g=G()
 window(g,0,4,-.23,5.8,11.2,True,shutters=True)
 window(g,0,21,-.23,5.8,11.6,True,shutters=True)
 window(g,0,40,-.23,4.9,9,False,shutters=True)
 for x in [-4.65,4.65]:g.box((x,27,-.16),(.6,47,.45),'RedLight')
 balustrade(g,6.7,20,-1.3,spacing=1.8)
 for y in [17.5,35.5,50.5]:g.box((0,y,-.33),(9.6,.5,.8),'Ivory')
 a.template('ThreeStoreyBay',g)
 for side in [-1,1]:
  for i in range(9):a.inst('ThreeStoreyBay',f'StreetBay_{side}_{i}',(side*(32+i*9.5),0,-28.02))
  for i in range(4):a.inst('ThreeStoreyBay',f'EndBay_{side}_{i}',(side*118.02,0,-17+i*11.2),-side*math.pi/2,'SideReturns')
 # The six giant columns and triangular central crown define the civic facade.
 g=G()
 for x in [-16,-8,0,8,16]:
  window(g,x,5,-.25,5,10.5,True,shutters=True)
  window(g,x,22,-.25,5,11.5,True)
  window(g,x,40,-.25,4.4,8,False)
  g.arch(4.8,10,.45,4.2,(x,2,-2),'Ivory',10)
 # Ground-storey masonry supports the two-storey columns, with a continuous
 # projecting floor slab below their bases rather than unsupported capitals.
 for x in [-20,-12,-4,4,12,20]:
  g.box((x,9.65,-2.4),(3.25,18.7,5.5),'Red')
  g.box((x,18.65,-2.5),(3.8,.7,6),'Ivory')
  col(g,x,-3.4,19,31,1.05)
 g.box((0,18.55,-2.5),(53,.9,6.6),'Ivory')
 g.box((0,50.6,-2.2),(53,2.2,5.6),'Ivory');pediment(g,56,52.5,-2.7,10.6)
 # Emblem represented as a readable original relief, not tiny lettering.
 g.ellipsoid((0,57,-3.8),(1.25,2.1,.25),'Gold',8,4)
 figure(g,0,63.3,-2.8,5.7)
 a.add('CentralPortico',g,'Facades',(0,0,-28))
 for side in [-1,1]:
  g=G();g.box((0,2,0),(25,4,5),'RedLight')
  figure(g,0,4,0,4.6);figure(g,3.8,4,0,3.6)
  a.add('RoofSculpture_'+str(side),g,'Roofline',(side*70,54.5,-26))
 # Shallow mansard silhouette, separate from the facade kit.
 g=G()
 lower=[(-118,55,-28),(118,55,-28),(118,55,28),(-118,55,28)]
 upper=[(-112,63,-21.5),(112,63,-21.5),(112,63,21.5),(-112,63,21.5)]
 for i in range(4):
  j=(i+1)%4;g.polygon([lower[i],upper[i],upper[j],lower[j]],'Slate')
 g.polygon(list(reversed(upper)),'Slate')
 a.add('MansardRoof',g,'Roofline')
 g=G()
 for x in range(-112,113,4):g.box((x,54.3,-28.7),(1.4,.65,1.2),'Ivory')
 for x in range(-108,109,12):
  g.box((x,58,-25),(4.4,4,1.5),'Red');window(g,x,56.5,-26,2.5,2.8,False)
 a.add('DormersAndCornice',g,'Roofline')
 a.rear_windows(236,56,[5,23,40],16)
 a.finish();return a

def gpo():
 a=Asset('gpo','General Post Office','GPO')
 a.box('EastWing',(24,19.5,-16),(104,39,48),'Ivory')
 a.box('ReturnWing',(-44,19.5,24),(48,39,112),'Ivory')
 g=G();g.cylinder((-44,20,-28),19.4,40,'Ivory',32);g.cylinder((-44,1.6,-28),25.4,3.2,'Stone',32)
 g.cylinder((-44,.95,-28),26.2,1.9,'Stone',32)
 a.add('CornerRotundaBody',g)
 a.collider('RotundaEnvelope',(-44,20,-28),(38,40,38))
 # The straight colonnades rest on low connected podia, flush with the round
 # corner platform. Their existing 3-stud column-base elevation is retained.
 a.box('EastColonnadePodium',(24,1.6,-42.7),(104,3.2,9),'Stone',group='Foundation')
 a.box('ReturnColonnadePodium',(-70.6,1.6,24),(9,3.2,112),'Stone',group='Foundation')
 a.box('EastPodiumStep',(24,.95,-46.9),(104,1.9,2),'Stone',group='Foundation')
 a.box('ReturnPodiumStep',(-74.8,.95,24),(2,1.9,112),'Stone',group='Foundation')
 a.bands(104,48,[2,31.8,38.7],(24,0,-16))
 # Reusable tall white street colonnade and deeply shadowed windows.
 g=G();col(g,0,-3,3,28.5,1.0);window(g,0,6,-.23,5.6,20,True)
 g.box((0,32,-1),(10.5,2.5,6),'Ivory')
 a.template('StreetColumnBay',g)
 for i in range(9):a.inst('StreetColumnBay',f'EastColonnade_{i}',(-10+i*10,0,-40.02))
 for i in range(8):a.inst('StreetColumnBay',f'ReturnColonnade_{i}',(-68.02,0,-17+i*11),math.pi/2,'SideReturns')
 g=G()
 for i in range(9):
  t=-math.pi+i*math.pi/8
  col(g,23*math.cos(t),23*math.sin(t),3,28.5,1.05)
  q=G();window(q,0,6,-.22,5,20,True)
  g.merge(q.transformed((19.5*math.cos(t),0,19.5*math.sin(t)),-t-math.pi/2))
 g.lathe([(31,23.8),(32,24.5),(34,24.5),(35.3,22.3),(38.5,21.5),(40,19.8)],32,'Ivory')
 a.add('CurvedColonnade',g,'Facades',(-44,0,-28))
 # Drum has a continuous masonry body; windows cannot float below the dome.
 g=G();g.lathe([(39,18.2),(40,18.9),(41,17.8),(56,17.8),(57,18.8),(58,18.8)],32,'Ivory')
 a.add('DomeDrum',g,'Roofline',(-44,0,-28))
 g=G();window(g,0,43,-.1,3.7,10,True)
 for x in [-2.5,2.5]:g.box((x,48,-.12),(.4,13,.6),'White')
 a.template('DrumBay',g)
 for i in range(16):
  t=i*math.tau/16
  a.inst('DrumBay',f'DrumBay_{i}',(-44+17.8*math.cos(t),0,-28+17.8*math.sin(t)),-t-math.pi/2,'Roofline')
 profile=[(58,18),(60,17.9),(64,17.2),(68,15.7),(72,13.6),(76,10.4),(79,6.4),(81,2),(82,.85)]
 g=G();g.lathe(profile,32,'White');g.lathe([(82,.9),(83,1.4),(84,.65),(86,0)],12,'Ivory')
 # Sparse ribs support the tall dome's distinctive form.
 for i in range(12):
  t=i*math.tau/12
  for (y,r),(yy,rr) in zip(profile,profile[1:]):g.beam(((r+.08)*math.cos(t),y,(r+.08)*math.sin(t)),((rr+.08)*math.cos(t),yy,(rr+.08)*math.sin(t)),.075,'Ivory',4)
 a.add('TallRibbedDome',g,'Roofline',(-44,0,-28))
 g=G();g.box((0,38,0),(7,8,2.4),'Ivory');clock(g,0,39,-1.3,2.3)
 a.add('ProjectedClock',g,'Details',(-44,0,-52))
 g=G()
 for x in range(-15,75,9):
  g.box((x,36.4,-40.7),(6,1.6,.35),'Shadow')
  g.box((x,36.4,-40.93),(5.8,.23,.18),'Ivory')
 a.add('ClerestoryAndDentils',g,'Details')
 g=G()
 for y in [6,23]:window(g,0,y,-.23,4.2,8,False,shutters=True)
 a.template('RearWingWindow',g)
 for i in range(8):a.inst('RearWingWindow',f'EastRear_{i}',(-10+i*11,0,8.05),math.pi,'Rear')
 for i in range(3):a.inst('RearWingWindow',f'ReturnRear_{i}',(-58+i*13,0,80.05),math.pi,'Rear')
 a.finish();return a

def metropolitan():
 a=Asset('metropolitan_building','Metropolitan Building','MET')
 # Clipped corner makes the tower turn onto both street elevations.
 outline=[(-65,-44),(49,-44),(65,-28),(65,44),(-65,44)]
 g=G();g.polygon([(x,0,z) for x,z in outline],'Stone');g.polygon([(x,47,z) for x,z in reversed(outline)],'Ivory')
 for i,(x,z) in enumerate(outline):
  xx,zz=outline[(i+1)%len(outline)]
  g.polygon([(x,0,z),(x,47,z),(xx,47,zz),(xx,0,zz)],'Ivory')
 a.add('ClippedCornerEnvelope',g)
 a.collider('MainEnvelope',(-8,23.5,0),(114,47,88));a.collider('ReturnEnvelope',(56,23.5,9),(18,47,70))
 g=G()
 for y in [1.5,15.3,30,46.8]:
  outline_slab(g,outline,y,.5,expand=.2)
  outline_slab(g,outline,y+.6,.55,expand=.7)
  outline_slab(g,outline,y+1.15,.4,expand=1)
 a.add('ClippedCornerCornices',g,'Roofline')
 g=G();window(g,0,2,-.24,6.6,10.3,True,shutters=True)
 window(g,0,18,-.25,4.9,9.3,False,shutters=True)
 window(g,0,34,-.25,5.9,10,True)
 for x in [-4.55,4.55]:
  g.box((x,31.6,-.15),(.65,29,.55),'White')
  g.box((x,44.5,-.3),(1.3,.6,.95),'Gold')
 g.arch(7.8,6.5,.42,.6,(0,34,-1.5),'White',10)
 g.box((0,30.8,-1.1),(10,.7,3.6),'Ivory');balustrade(g,8.6,31.3,-2.8,height=2,spacing=2)
 a.template('BaroqueBay',g)
 for i in range(11):a.inst('BaroqueBay',f'ChowringheeBay_{i}',(-58+i*10,0,-44.04))
 for i in range(7):a.inst('BaroqueBay',f'ReturnBay_{i}',(65.04,0,-21+i*9.5),-math.pi/2,'SideReturns')
 for i,offset in enumerate([-5,5]):
  a.inst('BaroqueBay',f'ClockCornerBay_{i}',(57+offset/math.sqrt(2),0,-36+offset/math.sqrt(2)),-math.pi/4,'Facades')
 g=G();pediment(g,27,47,-1.7,6.8,'Ivory')
 for x in [-9.3,9.3]:
  g.box((x,8.7,-2.6),(3.45,16.8,6.4),'Ivory')
  g.box((x,16.85,-2.6),(3.9,.6,6.6),'Ivory')
  col(g,x,-3.8,17,28.8,1.1,gilt=True)
 g.box((0,16.7,-2.6),(27,.7,6.6),'Ivory')
 balustrade(g,23,31.2,-5.1,spacing=2.1)
 a.template('PedimentBalcony',g)
 a.inst('PedimentBalcony','FrontPediment',(-15,0,-44))
 a.inst('PedimentBalcony','SidePediment',(65,0,13),-math.pi/2,'SideReturns')
 # Three cupolas, with the prominent corner clock tower deliberately tallest.
 for n,(x,z,large) in enumerate([(56,-35,True),(-57,-37,False),(58,36,False)]):
  r=7 if large else 4.6;base=47;top=68 if large else 55
  g=G();g.lathe([(base,r*1.15),(base+1.2,r*1.2),(top-1,r),(top,r*1.2)],8,'Ivory')
  a.add(f'TowerBody_{n}',g,'Roofline',(x,0,z))
  g=G();window(g,0,51,-.2,4.6 if large else 2.7,9.4 if large else 3.5,True)
  if large:
   for xx in [-3.2,3.2]:col(g,xx,-.4,49,12,.5,gilt=True)
   clock(g,0,64.6,-.6,2.6)
  a.template(f'TowerFace_{n}',g)
  for j in range(8 if large else 4):
   t=j*math.tau/(8 if large else 4)
   a.inst(f'TowerFace_{n}',f'TowerFace_{n}_{j}',(x+r*math.cos(t),0,z+r*math.sin(t)),-t-math.pi/2,'Roofline')
  g=G();g.lathe([(top,r*1.15),(top+.8,r*1.2),(top+1.5,r),(top+4,r*.9),(top+6.3,r*.62),(top+7.5,r*.16),(top+8.5,0)],20,'Gold')
  g.lathe([(top+8,.3),(top+9,.65),(top+10.5,0)],8,'Gold')
  a.add(f'GoldCupola_{n}',g,'Roofline',(x,0,z))
 g=G()
 for x in range(-63,48,3):g.box((x,47.6,-44.8),(1.1,.9,1.5),'Ivory')
 balustrade(g,108,49,-44.2,height=2,spacing=2.7)
 for x in range(-60,49,10):g.lathe([(0,.5),(1,.6),(1.8,0)],8,'Gold',(x,51.2,-44.2))
 a.add('StreetRoofBalustrade',g,'Roofline')
 # Side parapet uses the same linked mesh, with a shorter authored section.
 g=G();balustrade(g,65,49,0,height=2,spacing=2.7)
 a.add('ReturnRoofBalustrade',g,'Roofline',(65.1,0,8),-math.pi/2)
 a.rear_windows(126,88,[4,20,36],14)
 a.finish();return a

def town_hall():
 a=Asset('town_hall','Kolkata Town Hall','TH')
 a.box('MainEnvelope',(0,20,2),(92,40,60),'White')
 a.box('PorticoLanding',(0,2.5,-36),(75,5,19),'Stone')
 for i in range(9):a.box(f'EntranceStep_{i}',(0,(i+1)*.25,-62+i*1.9),(75,(i+1)*.5,2.8),'Stone')
 a.bands(92,60,[4,19.5,37.5],(0,0,2),'White')
 g=G()
 for x in [-28,-16.8,-5.6,5.6,16.8,28]:col(g,x,-42,5,29,1.45,'White',True)
 for yy,ww,dd,hh in [(34.5,76,20,1.4),(36.6,77,21,3),(38.7,79,22,1.2),(40,80,23,.5)]:g.box((0,yy,-35),(ww,hh,dd),'White')
 for x in [-29,-17.4,-5.8,5.8,17.4,29]:
  # Frieze medallions are geometric reliefs, not dense carved motifs.
  points=[(x+1.05*math.cos(i*math.tau/16),36.5+1.05*math.sin(i*math.tau/16)) for i in range(16)]
  prism(g,points,.18,-45.65,'Ivory')
  points=[(x+.62*math.cos(i*math.tau/12),36.5+.62*math.sin(i*math.tau/12)) for i in range(12)]
  prism(g,points,.1,-45.8,'White')
 a.add('SixColumnPortico',g,'Facades')
 for x in [-28,-16.8,-5.6,5.6,16.8,28]:a.collider('PorticoColumn',(x,19,-42),(2.8,28,2.8))
 g=G();window(g,0,6,-.25,4.8,10.6,True,trim='White',shutters=True);window(g,0,23,-.25,4.8,10.8,False,trim='White',shutters=True)
 a.template('HallWindowBay',g)
 for i,x in enumerate([-34,-22,-11,0,11,22,34]):a.inst('HallWindowBay',f'FrontBay_{i}',(x,0,-28.04))
 for side in [-1,1]:
  for i in range(5):a.inst('HallWindowBay',f'SideBay_{side}_{i}',(side*46.04,0,-18+i*11),-side*math.pi/2,'SideReturns')
 g=G();balustrade(g,73,41,-44,height=2.8,spacing=2.7)
 for x in [-37,-19,0,19,37]:g.box((x,42.2,-44),(1.7,3.4,1.3),'White')
 flat_flag(g,0,44.5,-40)
 a.add('RoofBalustradeAndFlag',g,'Roofline')
 a.rear_windows(92,64,[6,23],13)
 a.finish();return a

def jorasanko():
 a=Asset('jorasanko_thakur_bari','Jorasanko Thakur Bari','JTB')
 # The front wing is split around a genuine 12-stud, ground-level passage.
 for side in [-1,1]:
  a.box('SideWing_'+str(side),(side*57,18,0),(18,36,112),'Red')
  a.box('EntranceWing_'+str(side),(side*30,18,-48),(48,36,16),'Red')
 a.box('RearWing',(0,18,48),(96,36,16),'Red')
 for side in [-1,1]:a.box('WhiteCourtLining_'+str(side),(side*47.85,18,0),(.2,35.6,80),'White',group='Courtyard',solid=False)
 a.box('WhiteRearLining',(0,18,39.85),(96,35.6,.2),'White',group='Courtyard',solid=False)
 a.box('CourtyardPaving',(0,.1,0),(96,.2,80),'Court',solid=True)
 a.box('CourtyardLawn',(0,.19,-13),(42,.16,29),'Grass',group='Courtyard',solid=False)
 # External red-and-green window kit, two storeys with readable shutter slats.
 g=G();window(g,0,3,-.2,5.6,10,True,shutters=True);window(g,0,21,-.2,5.6,10.5,False,shutters=True)
 for x in [-4.6,4.6]:g.box((x,18,-.26),(.5,32,.65),'Ivory')
 g.box((0,18,-.35),(9.5,.55,.8),'Ivory');g.box((0,33.2,-.25),(9.5,.8,.8),'Ivory')
 a.template('RedShutterBay',g)
 for side in [-1,1]:
  for i in range(5):a.inst('RedShutterBay',f'FrontBay_{side}_{i}',(side*(11+i*9),0,-56.03))
  for i in range(10):a.inst('RedShutterBay',f'OuterSide_{side}_{i}',(side*66.03,0,-44+i*9.5),-side*math.pi/2,'SideReturns')
 # Outer cornices follow the ring, without spanning/closing the courtyard.
 for side in [-1,1]:
  g=G()
  for y in [1,18,34.5,36]:g.box((0,y,0),(19.2,.65,113),'Ivory')
  a.add('SideCornice_'+str(side),g,'Roofline',(side*57,0,0))
 for z in [-48,48]:
  g=G()
  for y in [18,34.5,36]:g.box((0,y,0),(114,.65,17.5),'Ivory')
  a.add('CrossCornice_'+str(z),g,'Roofline',(0,0,z))
 # Inner white galleries surround an open-to-sky courtyard. The gallery floors
 # are shallow exterior slabs; no full interior room network is authored.
 for side in [-1,1]:
  a.box('GalleryFloor_'+str(side),(side*44.5,.6,0),(7,1.2,80),'Ivory',group='Courtyard')
  a.box('GalleryUpper_'+str(side),(side*44.5,18,0),(7,.75,80),'Ivory',group='Courtyard')
 a.box('RearGalleryFloor',(0,.6,36.5),(89,1.2,7),'Ivory',group='Courtyard')
 a.box('RearGalleryUpper',(0,18,36.5),(89,.75,7),'Ivory',group='Courtyard')
 g=G();g.arch(7.4,8.2,.45,.7,(0,1.2,0),'White',10)
 for x in [-4.15,4.15]:
  col(g,x,0,1.2,10.5,.43,'White',True)
  g.lathe([(0,.52),(12.6,.38),(13.5,.6)],8,'White',(x,18.35,0))
  g.box((x,32,0),(1.45,.5,1.45),'White')
 # Closed haunches connect the arcade crown to the upper gallery floor.
 for i in range(10):
  t0=i*math.pi/10;t1=(i+1)*math.pi/10
  x0,y0=4.15*math.cos(t0),9.4+4.15*math.sin(t0)
  x1,y1=4.15*math.cos(t1),9.4+4.15*math.sin(t1)
  prism(g,[(x1,y1),(x0,y0),(x0,18.3),(x1,18.3)],.7,0,'White')
 for x in [-4.45,4.45]:g.box((x,13.8,0),(.6,9,.7),'White')
 g.box((0,33.85,0),(9.5,3.3,1.2),'White')
 g.box((0,35.5,3.5),(9.5,.7,8),'White')
 # Modest medallion band instead of ornate plaster carving.
 for x in [-2.6,0,2.6]:
  points=[(x+.37*math.cos(i*math.tau/8),15.5+.37*math.sin(i*math.tau/8)) for i in range(8)]
  prism(g,points,.1,-.52,'Ivory')
 balustrade(g,7.5,18.7,-.18,height=2,spacing=1.9)
 window(g,0,3,6.6,4.6,9.3,True,shutters=True)
 window(g,0,21,6.6,5.2,10.5,False,shutters=True)
 a.template('InnerGalleryBay',g)
 for side in [-1,1]:
  for i in range(8):a.inst('InnerGalleryBay',f'CourtSide_{side}_{i}',(side*41,0,-33.25+i*9.5),side*math.pi/2,'Courtyard')
 for i in range(9):a.inst('InnerGalleryBay',f'RearCourt_{i}',(-38+i*9.5,0,33),0,'Courtyard')
 # Five-arched Thakur Dalan on the rear side, with an accessible raised stage.
 g=G()
 for x in [-16,-8,0,8,16]:
  g.arch(6.5,8.5,.5,1.0,(x,1.2,-.3),'White',10)
 for x in [-20,-12,-4,4,12,20]:col(g,x,-.5,1.2,11.5,.55,'White')
 g.box((0,14,0),(43,3.4,1.4),'White')
 a.add('ThakurDalanArcade',g,'Courtyard',(0,0,31))
 for i in range(3):a.box(f'DalanStep_{i}',(0,(i+1)*.2,26+i*1.3),(43,(i+1)*.4,1.5),'Ivory',group='Courtyard')
 g=G();g.arch(12,9.4,.65,16,(0,0,0),'Ivory',12)
 g.box((0,16.1,0),(13.4,2,16),'Red')
 g.box((0,26,0),(12,20,16),'Red')
 window(g,0,21,-8.2,7.5,10.3,True,shutters=True)
 a.add('OpenEntrancePassage',g,'Facades',(0,0,-48))
 a.collider('EntranceLintel',(0,14.7,-48),(12,7.5,16))
 a.box('EntranceThreshold',(0,.1,-48),(12,.2,16),'Court',group='Courtyard')
 # Roof parapet accents, not hundreds of tiny rail posts.
 g=G()
 for x in range(-60,61,12):g.box((x,37.1,-56),(1,2.2,1),'Ivory')
 g.box((0,38.1,-56),(126,.3,.55),'Ivory')
 a.add('StreetParapet',g,'Roofline')
 a.rear_windows(126,112,[3,21],14)
 a.finish();return a

BUILDERS={'writers_building':writers,'gpo':gpo,'metropolitan_building':metropolitan,'town_hall':town_hall,'jorasanko_thakur_bari':jorasanko}

def build_all():
 # Regeneration owns only scenes bearing this library's AssetId metadata.
 # Original startup/user scenes and other task assets remain untouched.
 owned=[s for s in bpy.data.scenes if str(s.get('AssetId','')).startswith('kolkata.tier2.')]
 if owned:
  safe=next((s for s in bpy.data.scenes if s not in owned),None)
  if safe is None:safe=bpy.data.scenes.new('AuthoringWorkspace')
  bpy.context.window.scene=safe
  for scene in owned:
   collections=list(scene.collection.children_recursive)
   for obj in list(scene.objects):bpy.data.objects.remove(obj,do_unlink=True)
   bpy.data.scenes.remove(scene)
   for c in reversed(collections):
    if c.name in bpy.data.collections:bpy.data.collections.remove(c)
  for mesh in list(bpy.data.meshes):
   if mesh.users==0 and mesh.name.startswith(('WB_','GPO_','MET_','TH_','JTB_')):bpy.data.meshes.remove(mesh)
 assets=[]
 for slug,fn in BUILDERS.items():
  assets.append(fn())
 (BASE/'library-summary.json').write_text(json.dumps([a.summary for a in assets],indent=2),encoding='utf8')
 # The clean catalogue contains just authored scenes; the user's original scene
 # is preserved in the current session and is never deleted or exported.
 bpy.data.libraries.write(str(BASE/'Kolkata_Tier2_Library.blend'),{a.scene for a in assets},fake_user=True,compress=True)
 return assets

if __name__=='__main__':
 TIER2_ASSETS=build_all()
 print('TIER2_BUILD_COMPLETE',flush=True)
