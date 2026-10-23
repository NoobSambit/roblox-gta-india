"""Five original, open ground-floor commercial shells. Blender edit-time only."""
import bpy,bmesh,json,math,sys
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE.parent/'howrah_bridge'))
from howrah_geometry import Geo,bp

PALETTE={'Trim':'E8E4D7','Stone':'B9AA8B','Glass':'304E55','Blue':'5B8DA5','Metal':'53696F','Gold':'B49A60','Roof':'667773'}
DESIGNS=[
 ('KOL_T25_BANK','Bank',66,50,18,'DFD5BE','Civic portico, pediment, stepped cornices and roof balustrade'),
 ('KOL_T25_JEWELLERY','Jewellery showroom',52,44,16,'D5C6AD','Complete gold-framed arched windows and supported sign canopy'),
 ('KOL_T25_RETAIL','General retail store',58,42,16,'B9C6AC','Wrap awning, shaded veranda and traditional shutter rhythm'),
 ('KOL_T25_ELECTRONICS','Electronics showroom',64,46,18,'B6C5C7','Offset upper volume, vertical service fins and broad display glazing'),
 ('KOL_T25_FASHION','Fashion store',54,44,17,'C9AB99','Art Deco piers, curved entrance hood and stepped central parapet'),
]

def mat(role,body):
 h=body if role=='Body' else PALETTE[role];key='IH_T25_'+h
 if key in bpy.data.materials:return bpy.data.materials[key]
 rgb=[int(h[i:i+2],16)/255 for i in (0,2,4)]
 linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
 m=bpy.data.materials.new(key);m.use_nodes=True;m.diffuse_color=(*linear,1)
 n=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');n.inputs['Base Color'].default_value=(*linear,1);n.inputs['Roughness'].default_value=.82
 return m

def build(d):
 asset,label,w,depth,clear,body,features=d
 scene=bpy.data.scenes.new(asset);bpy.context.window.scene=scene
 scene['AssetId']=asset;scene['Task']='006';scene.unit_settings.system='NONE';scene.unit_settings.scale_length=1
 collection=bpy.data.collections.new(asset+'__Geometry');scene.collection.children.link(collection)
 g=Geo();collisions=[];front=-depth/2;top=clear+14
 def box(pos,size,role='Body',collider=False,name='Structure'):
  g.box(pos,size,role)
  if collider:collisions.append(dict(name=name,position=list(pos),size=list(size),yaw=0))
 def frame(x,y,z,width,height,role='Trim',side=False):
  f=Geo();f.box((0,0,0),(width,height,.22),'Glass')
  for sx in [-1,1]:f.box((sx*(width/2+.16),0,-.12),(.32,height+.6,.5),role)
  for sy in [-1,1]:f.box((0,sy*(height/2+.15),-.12),(width+.65,.3,.6),role)
  f.box((0,-height/2-.45,-.4),(width+1.1,.35,1.1),'Stone')
  g.merge(f,(x,y,z),math.pi/2 if side else 0)
 def arched_window(x,base,z,width,straight):
  radius=width/2
  polygon=[(-radius,0),(radius,0),(radius,straight)]
  polygon.extend((radius*math.cos(i*math.pi/12),straight+radius*math.sin(i*math.pi/12)) for i in range(1,13))
  g.extrude(polygon,.22,(x,base,z),'Glass')
  g.arch((x,base,z-.1),width,straight,.38,.55,'Gold',12)
  box((x,base-.2,z-.12),(width+1.25,.4,.85),'Gold')
 # Real open ground-floor shell. The upper storey is a closed exterior volume.
 box((0,.3,0),(w,.6,depth),'Stone',True,'WalkableFloor')
 box((-w/2+.6,clear/2+.6,0),(1.2,clear,depth),'Body',True,'WestWall')
 box((w/2-.6,clear/2+.6,0),(1.2,clear,depth),'Body',True,'EastWall')
 for sign in [-1,1]:
  width=w/2-6
  box((sign*(6+width/2),clear/2+.6,front+.6),(width,clear,1.2),'Body',True,'FrontDoorSide')
  width=w/2-4
  box((sign*(4+width/2),clear/2+.6,depth/2-.6),(width,clear,1.2),'Body',True,'RearDoorSide')
 box((0,clear-.9,front+.6),(12,3,1.2),'Body',True,'FrontLintel')
 box((0,clear-.9,depth/2-.6),(8,3,1.2),'Body',True,'RearLintel')
 box((0,clear+.9,0),(w,1,depth),'Trim',True,'Ceiling')
 box((0,clear+7.7,0),(w,12.6,depth),'Body',True,'ClosedUpperStorey')
 for y,extra,h in [(clear+.6,1.2,.5),(top+.5,1.7,.7),(top+1.2,2.4,.45)]:
  box((0,y,0),(w+extra,h,depth+extra),'Trim')
 box((0,top+1.65,0),(w-.8,.4,depth-.8),'Roof')
 # A narrow exposed plinth and one shallow entry step; no solid across either door.
 box((0,.15,front-1),(w+1,.3,2),'Stone')
 # Projecting columns and hoods bear on a continuous entrance landing.
 box((0,.3,front-3.9),(w+2,.6,7.8),'Stone',True,'EntranceLanding')
 box((0,.15,front-8.4),(w+3,.3,1.2),'Stone',True,'EntranceStep')
 for sx in [-1,1]:
  box((sx*(w/2-1),clear/2+.6,front-1.1),(1.8,clear,2.2),'Trim')
  box((sx*(w/2-1),clear+7.6,front-.6),(1.6,12.5,1.4),'Trim')
 centres=[-w*.34,w*.34] if asset.endswith('FASHION') else [-w*.34,-w*.18,w*.18,w*.34]
 for x in centres:frame(x,clear*.49+.8,front-.15,w*(.23 if asset.endswith('FASHION') else .115),clear*.62)
 if asset.endswith('JEWELLERY'):
  for x in [-17,0,17]:arched_window(x,clear+2.4,front-.1,12,3.5)
 else:
  for i in range(7):
   x=(i-3)*(w-13)/6;frame(x,clear+7.3,front-.2,4.6,7.4)
 for side in [-1,1]:
  for i in range(4):frame(side*(w/2+.14),clear+7.3,(i-1.5)*(depth-12)/3,4.6,7.4,side=True)
 for i in range(5):frame((i-2)*(w-14)/4,clear+7.3,depth/2+.15,4.4,7.2)
 # Interior remains an empty, usable shell with restrained ceiling/wall bands.
 for sx in [-1,1]:
  box((sx*(w/2-1.32),2,0),(.18,1,depth-3),'Trim')
  box((sx*w*.28,clear+.28,0),(.35,.18,depth-5),'Stone')
 box((0,clear-1.8,front-1.6),(w-7,2.6,1.1),'Metal')
 box((0,clear-1.8,front-2.2),(w-9,1.9,.2),'Blue') # intentionally blank signage
 if asset.endswith('BANK'):
  for x in [-27,-9,9,27]:
   g.column(x,front-5,.6,clear,1,'Trim',12)
   collisions.append(dict(name='PorticoColumn',position=[x,clear/2+.6,front-5],size=[2.1,clear,2.1],yaw=0))
  g.extrude([(-w/2-1,0),(0,7.2),(w/2+1,0)],1.6,(0,top+1.2,front-.6),'Trim')
  for x in [-18,0,18]:g.arch((x,.6,front-5),16,9,.55,.65,'Stone',12)
  box((0,clear+.55,front-3.7),(w+3,1.1,8.1),'Trim')
  rail=Geo();rail.rail(w-7,0,0,'Trim',10)
  g.merge(rail,(0,top+1.8,depth/2-.7))
 elif asset.endswith('JEWELLERY'):
  for x in [-21,-10,10,21]:g.column(x,front-2.7,.6,clear,.66,'Gold',10)
  box((0,clear+.4,front-3.6),(w+2,.6,7.6),'Gold')
  for x in [-w/2+3,w/2-3]:
   for z in [front+3,depth/2-3]:g.column(x,z,top+1.7,3,.6,'Trim',8)
 elif asset.endswith('RETAIL'):
  for x in [-24,-12,12,24]:g.column(x,front-4,.6,clear-1.35,.6,'Trim',8)
  for i in range(15):
   x=(i-7)*(w/15)
   g.plan([(x-w/30,front+1),(x+w/30,front+1),(x+w/30,front-6),(x-w/30,front-6)],clear-1,clear-.65,'Blue' if i%2 else 'Trim')
  for x in [-w/2+2,w/2-2]:g.column(x,depth/2-1,top+1.6,3,.6,'Trim',8)
 elif asset.endswith('ELECTRONICS'):
  box((w*.22,clear+8.2,-depth*.08),(w*.52,14,depth+4),'Metal')
  for x in [w*.04,w*.16,w*.28,w*.40]:
   frame(x,clear+8.6,front-2.4,5.5,9,'Trim')
  for i in range(8):
   x=-w*.46+i*2.4
   box((x,clear+7.5,front-1.5),(.5,13.2,2.5),'Blue')
  box((0,clear-.2,front-2.8),(w*.94,.6,6),'Metal')
  for x in [-w*.45,w*.45]:g.column(x,front-2.4,.6,clear-1,.65,'Trim',10)
 else:
  for i in range(8):
   x=(i-3.5)*(w-9)/7
   g.lathe((x,0,front-1),[(clear+1,.7),(top+2,.7),(top+2.7,.45)],'Trim',10)
  for x in [-8.4,8.4]:
   g.column(x,front-4.2,.6,clear-3-.6,.58,'Trim',12)
   collisions.append(dict(name='EntranceHoodColumn',position=[x,(clear-3+.6)/2,front-4.2],size=[1.2,clear-3-.6,1.2],yaw=0))
  g.vault((0,clear-3,front-2.6),8,4.5,.45,6,'Stone',14)
  for i in range(4):box((0,top+1.7+i*.9,front+.6),(w*.6-i*5,.9,2),'Trim')
 # Rear and side cornice relief gives readable returns without tiny ornament.
 for z in [-depth/2,depth/2]:
  for i in range(14):box(((i-6.5)*(w-5)/14,top-.1,z),(1.2,.65,.75),'Stone')
 for x in [-w/2,w/2]:
  for i in range(10):box((x,top-.1,(i-4.5)*(depth-5)/10),(.75,.65,1.2),'Stone')
 folder=BASE/asset;folder.mkdir(parents=True,exist_ok=True)
 objects=[]
 for role,(vertices,faces) in g.groups.items():
  mesh=bpy.data.meshes.new(asset+'__'+role);mesh.from_pydata([bp(v) for v in vertices],[],faces);mesh.update()
  bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update()
  assert all(p.area>1e-7 for p in mesh.polygons)
  mesh.materials.append(mat(role,body));o=bpy.data.objects.new(mesh.name,mesh);collection.objects.link(o);objects.append(o)
  o['AssetId']=asset;o['MeshKey']=o.name;o['PaletteRole']=role
 total=sum(len(o.data.polygons) for o in objects);assert total<=8000,(asset,total)
 points=[v for vs,fs in g.groups.values() for v in vs];low=[min(p[i] for p in points) for i in range(3)];high=[max(p[i] for p in points) for i in range(3)]
 row=dict(assetId=asset,name=label,features=features,triangles=total,meshGroups=len(objects),source=f'{asset}/{asset}.blend',export=f'{asset}/{asset}.fbx',boundsMinStuds=low,boundsMaxStuds=high,dimensionsStuds=dict(zip(['width','height','depth'],[high[i]-low[i] for i in range(3)])),front='-Z',pivot=[0,0,0],entrance=[0,.6,front-1],rearExit=[0,.6,depth/2+.1],clearDoorWidth=12,clearCeilingHeight=clear,objectiveAttachment=[0,2,depth*.2],collisionBoxes=collisions,textures=[],materials=[o.data.materials[0].name for o in objects])
 (folder/'asset.json').write_text(json.dumps(row,indent=2),encoding='utf8')
 bpy.data.libraries.write(str(folder/(asset+'.blend')),{scene},fake_user=True,compress=True)
 for o in scene.objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
 bpy.ops.export_scene.fbx(filepath=str(folder/(asset+'.fbx')),use_selection=True,object_types={'MESH'},global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',use_mesh_modifiers=False,bake_anim=False,path_mode='AUTO',mesh_smooth_type='FACE',use_custom_props=True)
 # Original preview, with the open ground-floor entrance visible.
 scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=True;scene.view_settings.view_transform='Standard'
 scene.render.resolution_x=900;scene.render.resolution_y=750;scene.render.resolution_percentage=100
 world=bpy.data.worlds.new(asset+'_Preview');world.use_nodes=True
 bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.34,.40,.43,1);bg.inputs['Strength'].default_value=.8;scene.world=world
 camera=bpy.data.objects.new('ReviewCamera',bpy.data.cameras.new('ReviewCamera'));scene.collection.objects.link(camera);scene.camera=camera
 target=Vector((0,0,(top+4)*.45));camera.location=target+Vector((1,1.7,.8)).normalized()*max(w,depth,top)*2
 camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=max(w,depth)*1.5
 sun=bpy.data.objects.new('ReviewSun',bpy.data.lights.new('ReviewSun','SUN'));sun.data.energy=1.6;sun.data.angle=.35;sun.rotation_euler=(.5,-.5,-.4);scene.collection.objects.link(sun)
 scene.render.image_settings.file_format='PNG';scene.render.filepath=str(folder/'preview.png');bpy.ops.render.render(write_still=True)
 bpy.data.objects.remove(camera,do_unlink=True);bpy.data.objects.remove(sun,do_unlink=True)
 print('SAVED '+asset+' '+str(total)+' triangles',flush=True);return row

def main():
 rows=[build(d) for d in DESIGNS]
 (BASE/'asset-manifest.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
 master=BASE/'Kolkata_Tier25_Library.blend'
 for s in list(bpy.data.scenes):
  if s.get('Task')!='006':bpy.data.scenes.remove(s)
 bpy.context.preferences.filepaths.save_version=0
 bpy.ops.wm.save_as_mainfile(filepath=str(master),check_existing=False,compress=True)
 for r in rows:
  path=BASE/r['source'];bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False)
  next(w for wm in bpy.data.window_managers for w in wm.windows).scene=bpy.data.scenes[r['assetId']]
  bpy.ops.wm.save_as_mainfile(filepath=str(path),check_existing=False,compress=True)
 bpy.ops.wm.open_mainfile(filepath=str(master),load_ui=False)
 print(json.dumps({'assetCount':len(rows),'triangles':{r['assetId']:r['triangles'] for r in rows}}),flush=True)

if __name__=='__main__':main()
