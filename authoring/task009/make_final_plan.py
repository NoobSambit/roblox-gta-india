"""Final art/native structure plan shared by Blender review and Studio assembly."""
import json,math,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];KIT=ROOT/'assets/victoria-memorial/interior';BASE=KIT/'task009'
old=json.loads((ROOT/'authoring/task009/placements.json').read_text())
layout=json.loads((ROOT/'docs/task009/two-floor-plan.json').read_text())
architecture=json.loads((BASE/'two-storey-manifest.json').read_text())
catalog={r['assetId']:r for r in json.loads((KIT/'asset-manifest.json').read_text())['assets']+architecture['assets']}
art=[];blocks=[];lights=[];legacy=[]
def add(asset,id,pos,yaw=0,scale=1,role='Dressing',room='',owner=''):
 p=dict(assetId=asset,instanceId=id,position=list(pos),yaw=yaw,scale=scale,role=role,roomId=room,sourceMarker=owner,triangles=catalog[asset]['triangles']);art.append(p);return p
scale_by_loot={f'VIC_LOOT_{i:03}':(1.8 if i in [2,8,9,10,12,14] else 1.25 if i in [5,6,7] else 1.2 if i==17 else 1.35 if i in [15,16] else 1.5) for i in range(1,19)}
for p in old['instances']:
 # New source wing modules already supply continuous wall bands; avoid duplicate trims.
 if p['assetId'] in ['VIC_A04_DADO_8','VIC_A05_CORNICE_8','VIC_A12_FLOOR_RUNNER_8','VIC_E07_ARCHIVE_CABINET'] or p['sourceMarker'].startswith('VIC_LOOT_'):continue
 p=copy.deepcopy(p);s=scale_by_loot.get(p['sourceMarker'],1);p['scale']=s
 if s!=1:
  b=next(b for b in old['lootBindings'] if b['lootId']==p['sourceMarker']);root=b['sourceRootPosition'];p['position']=[a+(v-a)*s for v,a in zip(p['position'],root)]
 p['triangles']=catalog[p['assetId']]['triangles'];art.append(p)
for p in architecture['instances']:
 p=copy.deepcopy(p);p['scale']=1
 if p['assetId']=='VIC_B04_UPPER_LINING':
  h=15.5/21;p['stretch']=[1,h,1];p['position']=[0,48-48*h,0]
 if p['assetId']=='VIC_B10_UPPER_DOORS':p['yaw']=0 if p['position'][2]<0 else math.pi
 p['roomId']='Architecture';p['sourceMarker']='';art.append(p)
# Close the outer edge of the upper ring; leave only the two real hall connections.
# Reuse the same lining mesh, stretched vertically to precisely Y34..48.
for i in range(12):
 if i in [0,6]:continue
 p=add('VIC_B04_UPPER_LINING',f'VIC_UPPER_GALLERY_BACKING_{i:02}',[0,2,0],yaw=i*math.tau/12,role='UpperGalleryBacking',room='VIC_ROOM_UPPER_HALL');p['stretch']=[1,2/3,1]
artwork_bindings=copy.deepcopy(old['artworkBindings'])
ground_bindings=copy.deepcopy(old['lootBindings'])
def exhibit(id,pos,room,support,obj,scale,support_id,object_id,yaw=0,object_scale=None):
 add(support,support_id,pos,yaw=yaw,scale=scale,role='ExhibitSupport',room=room,owner=id)
 mount=catalog[support]['sockets']['ExhibitMount'][1]*scale
 if object_scale is None:
  c,d=catalog[support]['dimensionsStuds'],catalog[obj]['dimensionsStuds']
  object_scale=min((c['width']*scale-.5)*.82/d['width'],(c['depth']*scale-.5)*.8/d['depth'])
  if support.startswith('VIC_E0'):object_scale=min(object_scale,(c['height']*scale-mount-.4)*.85/d['height'])
 add(obj,object_id,[pos[0],pos[1]+mount,pos[2]],yaw=yaw,scale=object_scale,role='LootVisual',room=room,owner=id)
def painting(b,room,scale):
 id=b['lootId'];pos=b['sourceRootPosition'];stand,frame=b['instances'];yaw=math.pi if pos[2]<76 else 0
 add('VIC_F01_PAINTING_MONOLITH',stand,pos,yaw=yaw,scale=scale,role='ExhibitSupport',room=room,owner=id)
 fs=2.2*scale
 add('VIC_E04_FRAME_LANDSCAPE',frame,[pos[0]+math.sin(yaw)*(-.38*scale),pos[1]+3.5*scale,pos[2]+math.cos(yaw)*(-.38*scale)],yaw=yaw,scale=fs,role='Frame',room=room,owner=id)
 lights.append(dict(id='VIC_LIGHT_PAINTING_'+id[-3:],fixtureId=stand,position=[pos[0],pos[1]+10.56*scale,pos[2]-.42*scale*math.cos(yaw)],floor=1,range=12,brightness=.8,kind='Point'))
 b['supportAsset']='VIC_F01_PAINTING_MONOLITH';b['lootAsset']=None

# Per-room curation: preserve each marker and binding identity; change its presentation.
choices={1:('VIC_E02_CASE_MEDIUM','VIC_H05_OPEN_CHARTER',1.45),3:('VIC_E06_DOCUMENT_DESK','VIC_L01_FOLIO',1.7),4:('VIC_E01_CASE_SMALL','VIC_L12_MINIATURE',1.8),5:('VIC_E02_CASE_MEDIUM','VIC_L05_TRADE_COLLECTION',1.1),6:('VIC_E01_CASE_SMALL','VIC_L09_KEEPSAKE',1.15),7:('VIC_E02_CASE_MEDIUM','VIC_H06_CEREMONIAL_SET',1.1),12:('VIC_A07_PLINTH_OCTAGON','VIC_L06_ABSTRACT_BRONZE',2.2),13:('VIC_E02_CASE_MEDIUM','VIC_H01_CEREMONIAL_URN',1.85),14:('VIC_A06_PLINTH_SQUARE','VIC_H04_GILDED_KNOT',2.2),15:('VIC_E03_CASE_PREMIUM','VIC_H02_CEREMONIAL_CROWN',1.35),16:('VIC_E03_CASE_PREMIUM','VIC_H01_CEREMONIAL_URN',1.35),17:('VIC_E03_CASE_PREMIUM','VIC_H05_OPEN_CHARTER',1.2),18:('VIC_E02_CASE_MEDIUM','VIC_H06_CEREMONIAL_SET',1.5)}
for b in ground_bindings:
 id=b['lootId'];i=int(id[-3:]);room=next(r['roomId'] for r in layout['groundFloorOriginal']['loot'] if r['lootId']==id)
 if i in [2,8,9,10,11]:
  painting(b,room,.95 if i==2 else 1)
  if i==11:
   b['artworkId']='ART_01_RIVER_DAWN'
   artwork_bindings.append(dict(lootId=id,artworkId='ART_01_RIVER_DAWN',frameInstance=b['instances'][1],targetComponent='Canvas',aspectRatio=1.5,implementation='Framed river portfolio, original image reused; original marker metadata preserved'))
 else:
  support,obj,s=choices[i];s=.95 if i==17 else s
  exhibit(id,b['sourceRootPosition'],room,support,obj,s,*b['instances'],yaw=math.pi/2 if i in [17,18] else math.pi if i in [1,12,14,15,16] else 0)
  b['supportAsset'],b['lootAsset']=support,obj

upper_objects={19:'VIC_H05_OPEN_CHARTER',20:'VIC_H06_CEREMONIAL_SET',21:'VIC_H02_CEREMONIAL_CROWN',22:'VIC_H01_CEREMONIAL_URN',23:'VIC_H06_CEREMONIAL_SET',24:'VIC_H02_CEREMONIAL_CROWN',25:'VIC_H05_OPEN_CHARTER',26:'VIC_H03_RIVER_TRADE_MODEL',27:'VIC_H04_GILDED_KNOT',28:'VIC_H01_CEREMONIAL_URN'}
for e in layout['upperLoot']:
 id=e['lootId'];i=int(id[-3:]);e['lootAsset']=upper_objects[i]
 e['scale']=1.5 if i in [21,24] else 1.8
 exhibit(id,e['rootPosition'],e['roomId'],e['supportAsset'],e['lootAsset'],e['scale'],id+'_CASE',id+'_OBJECT',yaw=-math.pi/2 if e['rootPosition'][0]<0 else math.pi/2)
for sx in [-1,1]:
 for x in [sx*47,sx*62,sx*77]:add('VIC_A11_MUSEUM_BANNER',f'VIC_UPPER_PREMIUM_BANNER_{x}',[x,36.0,-92.84],yaw=math.pi,scale=1.1,role='PremiumBanner',room='VIC_ROOM_UPPER_TREASURY' if sx<0 else 'VIC_ROOM_UPPER_ROYAL')
 # South wings have their own banner family; only river/navigation receives paintings.
 for x in ([47,77] if sx>0 else [-80]):add('VIC_A11_MUSEUM_BANNER',f'VIC_CRAFT_BANNER_{x}',[x,36,92.82],scale=1.1,role='MuseumBanner',room='VIC_ROOM_UPPER_CRAFT' if sx>0 else 'VIC_ROOM_UPPER_RIVER')
# Allocate each wall bay once: paintings in bays34..51 and51..72; one
# banner in bay72..88. Frames never straddle the pilasters or other dressing.
for i,x in enumerate([-42.5,-61.5]):
 p=add('VIC_E04_FRAME_LANDSCAPE',f'VIC_RIVER_WALL_PAINTING_{i}',[x,37.5,92.78],scale=2.1,role='WallArtwork',room='VIC_ROOM_UPPER_RIVER')
 p['artworkId']='ART_01_RIVER_DAWN' if i==0 else 'ART_04_HERITAGE_SKYLINE'
p=add('VIC_E04_FRAME_LANDSCAPE','VIC_PAINTING_GALLERY_END_WALL',[-88.0,12.0,76],yaw=-math.pi/2,scale=3.2,role='WallArtwork',room='VIC_ROOM_GALLERY_A');p['artworkId']='ART_04_HERITAGE_SKYLINE'
for x in [76,83.5]:add('VIC_E07_ARCHIVE_CABINET',f'VIC_ARCHIVE_FLATFILES_{x}',[x,6.8,-91.75],yaw=math.pi,scale=1.5,role='SecureArchiveDressing',room='VIC_ROOM_ARCHIVE')
for pos,yaw,room in [([-88.0,12,-76],-math.pi/2,'VIC_ROOM_GALLERY_C'),([88.0,12,76],math.pi/2,'VIC_ROOM_GALLERY_B')]:add('VIC_A11_MUSEUM_BANNER','VIC_ROOM_THEME_'+room,pos,yaw=yaw,scale=1.5,role='MuseumBanner',room=room)
for s in layout['upperSecurity']:
 id=s['securityId'];x,y,z=s['position'];r=s['roomId'];kind=s['securityType']
 if kind=='StaticLaser':
  for off in [-5,5]:add('VIC_S01_STATIC_EMITTER',id+('_A' if off<0 else '_B'),[x,y,z+off],role='Emitter',room=r,owner=id)
 elif kind=='MovingLaser':add('VIC_S02_MOVING_HOUSING',id+'_HOUSING',[x,y,z-6],role='Housing',room=r,owner=id)
 elif kind=='ElectricFloor':add('VIC_S03_ELECTRIC_FLOOR',id+'_FLOOR',[x,y+.02,z],role='FloorInlay',room=r,owner=id)
 elif kind=='Terminal':add('VIC_S04_TERMINAL',id+'_TERMINAL',[x,y,z],role='Terminal',room=r,owner=id)
def block(name,pos,size,role='Ivory',solid=True,yaw=0,purpose='InteriorStructure'):
 blocks.append(dict(name=name,position=pos,size=size,material=role,solid=solid,yaw=yaw,purpose=purpose))
def carpet(name,x,z,w,d,floor,role='Teal'):
 # Continuous fabric field with separately raised double brass borders. Intentional
 # under-display carpet is retained; it never changes collision or marker positions.
 block(name,[x,floor+.04,z],[w,.08,d],role,False,purpose='Carpet')
 for inset,thickness in [(.18,.075),(.38,.05)]:
  for sign in [-1,1]:
   block(name+'_BorderX',[x+sign*(w/2-inset),floor+.11,z],[thickness,.05,d-2*inset],'Brass',False,purpose='CarpetBorder')
   block(name+'_BorderZ',[x,floor+.11,z+sign*(d/2-inset)],[w-2*inset-thickness,.05,thickness],'Brass',False,purpose='CarpetBorder')
for row in [('PaintingAxialRunner',-60.5,76,47,12,6.8),('SculptureAxialRunner',60.5,76,47,12,6.8),('PublicAxialRunner',-48.5,-76,26,11,6.8),('CollectionsDisplayCarpet',-78,-76,19,13,6.8),('ArchiveDisplayCarpet',79.5,-76,17,14,6.8),('HighSecurityDisplayCarpet',55.5,-87,17.5,10,6.8,'Oxblood'),('UpperTreasuryCarpet',-62,-76,46,15,34,'Oxblood'),('UpperCeremonialCarpet',62,-76,46,15,34,'Oxblood'),('UpperRiverCarpet',-62,76,46,15,34),('UpperCraftCarpet',62,76,46,15,34)]:carpet(*row)
# Finished shallow dado panels follow actual walls and stop at the courtyard door.
for sx in [-1,1]:
 for sz in [-1,1]:
  add('VIC_B14_COURTYARD_SPANDREL',f'VIC_COURTYARD_ARCH_INFILL_{sx}_{sz}',[sx*60,6,sz*58],role='CourtyardRepair',room='Courtyard')
  block('CourtyardThresholdLower',[sx*60,6.2,sz*55.8],[9,.4,1.4])
  block('CourtyardThresholdUpper',[sx*60,6.6,sz*57.6],[9,.4,2.2])
  block('CourtyardDoorHeaderProxy',[sx*60,22,sz*58],[9,4,2],purpose='InvisibleCollision')
  for dx in [-4,4]:block('CourtyardDoorJambProxy',[sx*60+dx,11,sz*58],[.9,10,2],purpose='InvisibleCollision')
  for floor in [6.8,34]:
   # The approved tower's stepped base projects inward at ground level. Finish
   # around that real base without editing its shared exterior mesh or clipping cases.
   end_x=87.9 if floor==6.8 else 88.05
   block('WingEndDado',[sx*end_x,floor+2.1,sz*76],[.12,4.2,33.4],'Mushroom',False,purpose='WallFinish')
   if floor==6.8:block('TowerBaseDadoCap',[sx*88.02,11.05,sz*76],[.38,.1,33.4],'Ivory',False,purpose='WallFinish')
   block('WingOuterDado',[sx*60.5,floor+2.1,sz*92.91],[56.8,4.2,.12],'Mushroom',False,purpose='WallFinish')
   if floor==6.8:
    for x in [43.75,77.25]:block('CourtyardDado',[sx*x,floor+2.1,sz*59.09],[23.2,4.2,.12],'Mushroom',False,purpose='WallFinish')
   else:block('UpperCourtDado',[sx*60.5,floor+2.1,sz*59.09],[56.8,4.2,.12],'Mushroom',False,purpose='WallFinish')
# Retain the recognizable open checkerboard quadrangles. Peripheral seating and
# interpretation clusters leave the entire Z[-19,19] escape/interception axis clear.
for side in [-1,1]:
 for z in [-28,28]:
  add('VIC_G01_FORMAL_PLANTER',f'VIC_COURT_PLANTER_{side}_{z}',[side*69,6.04,z],role='CourtyardFurniture',room='EastQuadrangle' if side>0 else 'WestQuadrangle')
  for dz in [-7,7]:add('VIC_G02_STONE_BENCH',f'VIC_COURT_BENCH_{side}_{z}_{dz}',[side*69,6.04,z+dz],yaw=math.pi if dz<0 else 0,role='CourtyardFurniture',room='Courtyard')
 for z in [-20,20]:add('VIC_E08_INFO_STAND',f'VIC_COURT_INTERPRETATION_{side}_{z}',[side*46,6.04,z],yaw=-side*math.pi/2,scale=1.3,role='CourtyardInterpretation',room='Courtyard')
tree_positions=[]
for x in [-220,220]:
 for z in [-238,-175,-100,100,175,238]:tree_positions.append([x,-.05,z])
for x,z in [(145,193),(62,143),(148,85)]:
 for sx in [-1,1]:
  for sz in [-1,1]:tree_positions.append([sx*x,-.05,sz*z])
for i,pos in enumerate(tree_positions):legacy.append(dict(instanceId=f'VIC_GARDEN_TREE_{i+1:02}',templateId='GardenTree',position=pos,yaw=(i%7)*.41,scale=[.9,1.05,1.0,1.1][i%4],triangles=224,role='GardenLandscaping'))
for p in legacy:
 s=p['scale'];x,y,z=p['position'];block('GardenTreeTrunkProxy',[x,y+4.5*s,z],[1.2*s,9*s,1.2*s],purpose='InvisibleCollision')
for side in [-1,1]:
 for a,b in [(-248,-32),(32,248)]:block('RaisedBoundaryProxy',[(a+b)/2,3.57,side*262],[b-a,7.14,.5],purpose='InvisibleCollision')
 for a,b in [(-262,-17),(17,262)]:block('RaisedBoundarySideProxy',[side*248,3.57,(a+b)/2],[.5,7.14,b-a],purpose='InvisibleCollision')
for x in [-66,69]:block('PartitionUpperInfill',[x,30.1,-76],[1,5.8,34])
for lo,hi in [(-88,-85),(-75,-69),(-59,-54)]:block('ScreeningWall',[-12,44,(lo+hi)/2],[1,20,hi-lo])
for z in [-80,-64]:
 block('ScreeningHeader',[-12,51.4,z],[1,5.2,10])
 for x,yaw in [(-11.4,-math.pi/2),(-12.6,math.pi/2)]:add('VIC_A03_ARCH_10',f'VIC_SCREENING_ARCH_{x}_{z}',[x,34,z],yaw=yaw,role='ChamberArch',room='VIC_ROOM_UPPER_SCREENING')
for sx in [-1,1]:block('WingEndWall_'+str(sx),[sx*88.65,26.8,-76],[1,40,34.6]);block('WingEndWallRear_'+str(sx),[sx*88.65,26.8,76],[1,40,34.6])
for sign in [-1,1]:
 for x in [-10.5,10.5]:block('UpperHallJambFoot',[x,36,sign*33],[7,4,4])
 block('VestibuleVaultEnd_'+str(sign),[0,51,sign*88],[59,10,.5])
 block('UpperEntranceGuard_'+str(sign),[0,35.9,sign*87.8],[31,3.8,.65])
 # Collision for visual wall groups must not use their combined bounding box across doors.
 for x in [-21,21]:block('HallUpperJambProxy',[x,52,sign*33],[28,28,4],solid=True,purpose='InvisibleCollision')
 block('HallUpperHeaderProxy',[0,57,sign*33],[14,18,4],purpose='InvisibleCollision')
 block('HallLowerBeamProxy',[0,32.5,sign*33],[28,1,4],purpose='InvisibleCollision')
 for sx in [-1,1]:
  block('WingBeamProxy',[sx*31,31.6,sign*76],[2,3.2,34],purpose='InvisibleCollision')
  for z,l in [(90.5,5),(73.5,5),(58.5,1)]:block('WingJambProxy',[sx*31,40.5,sign*z],[3.2,13,l],purpose='InvisibleCollision')
  block('WingHeaderProxy',[sx*31,45.75,sign*76],[3.2,2.5,36],purpose='InvisibleCollision')
 # Guard the actual stair opening at upper-floor level, leaving the top flight open.
 handed=-sign
 for x in [1.5,21.5]:
  block('StairVoidParapet',[handed*x,34.5,sign*66],[.5,1,37],'Ivory')
  block('StairVoidHandrail',[handed*x,37.9,sign*66],[.4,.3,37],'Brass')
  for z in [49,55,61,67,73,79,84]:block('StairVoidPost',[handed*x,36.2,sign*z],[.3,3.6,.3],'Charcoal')
 for x,w,z in [(11.5,20,84.5),(16,11,47.5)]:
  block('StairVoidEndGuard',[handed*x,35.9,sign*z],[w,3.8,.5],'Ivory')
 block('StairArrivalLip',[handed*6.25,33.5,sign*47.75],[8.5,1,1.5])
 block('StairApproachApron',[handed*11.5,6.4,sign*45],[19,.8,6])
 block('StairApproachStep',[handed*11.5,6.2,sign*41],[19,.4,2])
 for x in [2.8,20.2]:block('StairLandingSupport',[handed*x,13.2,sign*79.5],[1.4,14.4,1.4])
 # Fill the short end of the upper floor ring behind the preserved wall piers.
 for x in [-24,24]:block('HallRingCornerFinish',[x,35.5,sign*24],[4,3,4],solid=False)
# Thin safety proxies follow the curved balcony without filling its central void.
for i in range(48):
 a=i*math.tau/48;b=(i+1)*math.tau/48;m=(a+b)/2;r=23.5
 block('BalconyGuardProxy',[r*math.sin(m),36,r*math.cos(m)],[2*r*math.sin((b-a)/2),4,.35],solid=True,yaw=m,purpose='InvisibleCollision')
# A fitted interior transition follows the measured narrowing of the original
# drum. Never extend the 31-stud lower lining through the 28.4-stud upper drum.
for i in range(12):
 add('VIC_B15_DRUM_TRANSITION',f'VIC_DRUM_TRANSITION_{i:02}',[0,0,0],yaw=i*math.tau/12,role='UpperGalleryBacking',room='VIC_ROOM_UPPER_HALL')
for sign in [-1,1]:
 add('VIC_B16_PORTAL_SPANDREL',f'VIC_HALL_PORTAL_FINISH_{sign}',[0,34,sign*28.9],yaw=0 if sign>0 else math.pi,role='UpperGalleryBacking',room='VIC_ROOM_UPPER_HALL')
 for side in [-1,1]:block('WingStairCornerPier',[side*30.9,26.8,sign*58.1],[3.8,40,1.8],'Ivory',True,purpose='InteriorStructure')
 # Upper landing terminates behind the approved portal facade, above the
 # ground-floor escape opening. The old vault end only began at Y46.
 block('UpperVestibuleEndWall',[0,40.6,sign*88.1],[59.4,13.2,.4],'Ivory',True,purpose='InteriorStructure')
 block('UpperVestibuleEndDado',[0,36.1,sign*87.85],[59.4,4.2,.12],'Mushroom',False,purpose='WallFinish')
 block('UpperVestibuleEndCap',[0,38.25,sign*87.8],[59.4,.16,.2],'Ivory',False,purpose='WallFinish')
# Ground-floor fixture positions split compact archive/public rooms appropriately.
for sx in [-1,1]:
 for sz in [-1,1]:
  for x in [46,79]:
   lights.append(dict(id=f'VIC_LIGHT_G_{sx}_{sz}_{x}',position=[sx*x,32.7,sz*76],floor=1,range=29,brightness=1.45,kind='Spot',angle=100))
   lights.append(dict(id=f'VIC_LIGHT_U_{sx}_{sz}_{x}',position=[sx*x,46.1,sz*76],floor=2,range=19,brightness=1.3,kind='Spot',angle=110))
for sign in [-1,1]:
 lights.append(dict(id='VIC_LIGHT_STAIR_LOWER_'+str(sign),position=[sign*17,32.7,sign*62],floor=1,range=29,brightness=1.3,kind='Spot',angle=110))
 lights.append(dict(id='VIC_LIGHT_STAIR_UPPER_'+str(sign),position=[0,53.7,sign*66],floor=2,range=25,brightness=1.5,kind='Spot',angle=110))
 lights.append(dict(id='VIC_LIGHT_BALCONY_'+str(sign),position=[0,46.35,sign*28.9],floor=2,range=23,brightness=.8,kind='Point'))
for i in range(3):
 a=i*math.tau/3
 lights.append(dict(id='VIC_LIGHT_HALL_'+str(i),position=[26.9*math.sin(a),32.4,26.9*math.cos(a)],floor=1,range=42,brightness=1.4,blenderPower=7000,kind='Point'))
lights.append(dict(id='VIC_LIGHT_SCREENING',position=[-21,51.2,-70],floor=2,range=20,brightness=1.2,kind='Spot',angle=110))
for sign in [-1,1]:lights.append(dict(id='VIC_LIGHT_BALCONY_SIDE_'+str(sign),position=[sign*28.9,46.35,0],floor=2,range=23,brightness=.8,kind='Point',zone='Upper hall arcade'))
for l in lights:
 if l['id'].startswith('VIC_LIGHT_BALCONY'):
  l.update(range=28,brightness=1.0,blenderPower=4500)
# Fill the tall arcade band independently of the windows above it.
for i in range(6):
 a=(i+.5)*math.tau/6;x,z=29.1*math.sin(a),29.1*math.cos(a)
 lights.append(dict(id=f'VIC_LIGHT_HIGH_ARCADE_{i:02}',position=[x,47.1,z],target=[29.2*math.sin(a),64,29.2*math.cos(a)],floor=2,range=23,brightness=1.1,kind='Spot',angle=110,fixtureYaw=a,fixturePitch=math.pi,blenderPower=7000,zone='Tall upper arcade between balcony and clerestory'))
 block('HighArcadeLightBracket',[29.7*math.sin(a),46.85,29.7*math.cos(a)],[2,.2,1],'Charcoal',False,yaw=a,purpose='LightMount')
# Separate architectural light bands: lower lamps cannot reach the clerestory
# and112-stud dome crown. Aim restrained upward floods from real cornice mounts.
for i in range(6):
 a=i*math.tau/6;x,z=26.6*math.sin(a),26.6*math.cos(a)
 lights.append(dict(id=f'VIC_LIGHT_CLERESTORY_{i:02}',position=[x,68.5,z],target=[27.5*math.sin(a),84,27.5*math.cos(a)],floor=2,range=24,brightness=1.15,kind='Spot',angle=110,fixtureYaw=a,fixturePitch=math.pi,blenderPower=8500,zone='Clerestory and high arches'))
 block('ClerestoryLightBracket',[27.15*math.sin(a),68.2,27.15*math.cos(a)],[2,.2,1],'Charcoal',False,yaw=a,purpose='LightMount')
for i in range(3):
 a=(i+.5)*math.tau/3;x,z=26.65*math.sin(a),26.65*math.cos(a)
 lights.append(dict(id=f'VIC_LIGHT_DOME_WASH_{i:02}',position=[x,88.3,z],target=[0,108,0],floor=2,range=36,brightness=1.25,kind='Spot',angle=95,fixtureYaw=a,fixturePitch=math.pi,blenderPower=12000,zone='Upper dome and crown'))
 block('DomeLightBracket',[27.2*math.sin(a),88.05,27.2*math.cos(a)],[2,.2,1],'Charcoal',False,yaw=a,purpose='LightMount')
for side in [-1,1]:
 for z in [-36,36]:lights.append(dict(id=f'VIC_LIGHT_QUADRANGLE_{side}_{z}',position=[side*(91+32*math.sqrt(1-(z/77)**2)),25.05,z],floor=1,range=24,brightness=1,kind='Spot',angle=110,zone='Covered courtyard colonnade'))
for l in lights:
 l['shadows']=l['id'] in ['VIC_LIGHT_G_-1_-1_46','VIC_LIGHT_G_1_1_46']
 # Roblox's authored outdoor ambient differs from the deliberately low-ambient
 # Blender lighting review. Tune local brightness without altering city Lighting.
 if l['id'].startswith('VIC_LIGHT_HALL_'):l['brightness']=.45
 elif l['id'].startswith('VIC_LIGHT_BALCONY'):l['brightness']=.4
 elif l['id'].startswith('VIC_LIGHT_HIGH_ARCADE'):l['brightness']=.45
 elif l['id'].startswith('VIC_LIGHT_CLERESTORY'):l['brightness']=.6
 elif l['id'].startswith('VIC_LIGHT_DOME_WASH'):l.update(brightness=2.1,range=50,angle=120)
# Final lighting-only polish. Fixture geometry and the approved plan stay fixed.
for l in lights:
 l['color']=[255,247,233]
 l['shadows']=l['id'] in ['VIC_LIGHT_HALL_0','VIC_LIGHT_G_-1_1_46']
 id=l['id']
 if id.startswith('VIC_LIGHT_G_'):l.update(brightness=.95 if '_1_-1_' in id else 1.05,angle=105)
 elif id.startswith('VIC_LIGHT_U_'):
  x,y,z=l['position'];s=1 if x>0 else -1
  l['position']=[s*(40 if abs(x)<60 else 84),y,z]
  l.update(target=[s*(47 if abs(x)<60 else 77),39,z],brightness=1.15,range=25,angle=110,zone='Upper exhibit face and aisle')
 elif id.startswith('VIC_LIGHT_HALL_'):
  i=int(id[-1]);l.update(kind='Spot',target=([0,14,0] if i==0 else [-12 if i==1 else 12,17,0]),range=40 if i==0 else 42,angle=75 if i==0 else 90,brightness=1.3 if i==0 else 1.0,blenderPower=7000 if i==0 else 5000,zone='Memorial key' if i==0 else 'Cross-hall architectural fill')
  if i==0:l['position']=[0,32.4,-26]
 elif id.startswith('VIC_LIGHT_BALCONY'):l.update(brightness=.45,range=24)
 elif id.startswith('VIC_LIGHT_HIGH_ARCADE'):l.update(brightness=.4,angle=100)
 elif id.startswith('VIC_LIGHT_CLERESTORY'):l.update(brightness=.65,angle=115)
 elif id.startswith('VIC_LIGHT_DOME_WASH'):l.update(brightness=1.5,range=50,angle=125)
 elif id.startswith('VIC_LIGHT_STAIR_LOWER'):l.update(brightness=1,range=29)
 elif id.startswith('VIC_LIGHT_STAIR_UPPER'):l.update(brightness=1.1,range=25)
 elif id.startswith('VIC_LIGHT_PAINTING'):l.update(brightness=.65,range=10)
for l in lights:
 if not l.get('fixtureId'):
  p=add('VIC_B12_LIGHT',l['id'],l['position'],yaw=l.get('fixtureYaw',0),role='LightFixture',room='Lighting');p['pitch']=l.get('fixturePitch',0)
for p in art:
 if p['assetId']=='VIC_A11_MUSEUM_BANNER':p['assetId']='VIC_F02_MUSEUM_BANNER';p['triangles']=catalog[p['assetId']]['triangles']
 if p['assetId']=='VIC_H01_CEREMONIAL_URN' and p['sourceMarker'] in ['VIC_LOOT_013','VIC_LOOT_028']:p['materialOverrides']={'Bronze':'Teal'}
def bounds(p):
 d=catalog[p['assetId']]['dimensionsStuds'];w,depth=d['width']*p['scale'],d['depth']*p['scale']
 if abs(math.sin(p['yaw']))>.7:w,depth=depth,w
 x,_,z=p['position'];return [x-w/2,x+w/2,z-depth/2,z+depth/2]
supports=[bounds(p) for p in art if p['role']=='ExhibitSupport' or (p['role']=='PermanentCollection' and not p['assetId'].startswith(('VIC_L','VIC_H')))]
removed=[]
for p in list(art):
 if p['assetId']!='VIC_A12_FLOOR_RUNNER_8':continue
 a=bounds(p)
 if any(min(a[1],b[1])-max(a[0],b[0])>.05 and min(a[3],b[3])-max(a[2],b[2])>.05 for b in supports):art.remove(p);removed.append(p['instanceId'])
# Check the specific repeated failure: independent wall dressing must not share
# a bay with another card or cross a structural pilaster. This is a placement
# check, separate from watertight mesh validation; intentional wall mounts are fine.
cards=[]
for p in art:
 if p['role']!='WallArtwork' and p['assetId']!='VIC_F02_MUSEUM_BANNER':continue
 row=catalog[p['assetId']];d=row['dimensionsStuds'];x,y,z=p['position'];f=2 if y>=34 else 1
 xwall=abs(math.sin(p['yaw']))>.7
 axis='X' if xwall else 'Z';wall=x if xwall else z;t=z if xwall else x
 half=d['width']*p['scale']/2;low=t-half;high=t+half
 columns=[-92.75,-59.25,59.25,92.75] if xwall else [-88,-72,-51,-34,34,51,72,88]
 for col in columns:
  radius=.65 if f==2 else 1.225
  assert min(high,col+radius)-max(low,col-radius)<0,p['instanceId']+' crosses column '+str(col)
 key=(f,axis,round(wall),1 if (x if not xwall else z)>0 else -1)
 bottom=y+row['boundsMinStuds'][1]*p['scale'];top=y+row['boundsMaxStuds'][1]*p['scale']
 for c in cards:
  if c['wall']==key:assert min(high,c['high'])-max(low,c['low'])<=0 or min(top,c['top'])-max(bottom,c['bottom'])<=0,p['instanceId']+' overlaps '+c['id']
 cards.append(dict(id=p['instanceId'],wall=key,low=low,high=high,bottom=bottom,top=top))
final=dict(task='009',status='Two-floor final integration specification',units=old['units'],instances=art,legacyInstances=legacy,nativeStructure=blocks,lights=lights,lootBindings=ground_bindings,securityBindings=old['securityBindings'],artworkBindings=artwork_bindings,upperLayout=layout,wallDressingInspection=cards,groundsRevision=dict(authorizedBy='Latest user feedback: dress quadrangles, improve grounds materials/trees and increase property-boundary height',boundaryHeightScale=dict(base=1.35,rail=1.7,picket=1.7),maximumFenceHeight=7.14,keepExistingGateGaps=True,reference='https://victoriamemorial-cal.org/gardens/'),statistics=dict(importedArtInstances=len(art),importedPlacedTriangles=sum(p['triangles'] for p in art),legacyTreeInstances=len(legacy),legacyPlacedTriangles=sum(p['triangles'] for p in legacy),nativeVisualTriangles=sum(12 for p in blocks if p['purpose']!='InvisibleCollision'),nativeCollisionTriangles=sum(12 for p in blocks if p['purpose']=='InvisibleCollision'),lights=len(lights),groundLoot=18,upperLoot=len(layout['upperLoot']),securityReservations=9+len(layout['upperSecurity'])))
final['removedOverlappingRunners']=removed
(ROOT/'authoring/task009/final-plan.json').write_text(json.dumps(final,indent=2)+'\n');(BASE/'placement-manifest.json').write_text(json.dumps(final,indent=2)+'\n')
print(json.dumps(final['statistics']))
