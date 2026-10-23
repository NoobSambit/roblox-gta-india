"""Precise two-floor layout; generated concepts cannot change these coordinates."""
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2];KIT=ROOT/'assets/victoria-memorial/interior'
lock=json.loads((KIT/'layout-lock.json').read_text());lock=lock.get('groundFloorOriginal',lock)
rooms=[dict(roomId='VIC_ROOM_UPPER_HALL',name='Hall overlook',role='Decorative orientation, no loot',centerXZ=[0,0],annulusRadii=[23,30.8]),dict(roomId='VIC_ROOM_UPPER_NORTH',name='North stair / security antechamber',role='Security-only transition, no loot',centerXZ=[0,-64],sizeXZ=[60,53]),dict(roomId='VIC_ROOM_UPPER_SOUTH',name='South stair / landing',role='Stair transition, no loot',centerXZ=[0,64],sizeXZ=[60,53])]
for id,name,x,z in [('TREASURY','Heritage treasury',-60.5,-76),('ROYAL','Ceremonial collection',60.5,-76),('RIVER','River / navigation',-60.5,76),('CRAFT','Sculpture / craft',60.5,76)]:
 rooms.append(dict(roomId='VIC_ROOM_UPPER_'+id,name=name,role='Premium branch' if z<0 else 'Valuable exhibition',centerXZ=[x,z],sizeXZ=[57,34]))
rooms.append(dict(roomId='VIC_ROOM_UPPER_SCREENING',name='Security screening chamber',role='Security-only chamber, no loot',centerXZ=[-21,-71],sizeXZ=[18,34]))
upper=[]
items=[(-48,-76,'TREASURY','Rare','River charter','VIC_L11_RARE_ARCHIVE_FOLIO'),(-65,-76,'TREASURY','Rare','Presentation set','VIC_L07_PRESENTATION_SET'),(-81,-76,'TREASURY','Premium','Heritage insignia','VIC_L10_PREMIUM_INSIGNIA'),(52,-76,'ROYAL','Rare','Ceremonial vessel','VIC_L08_CEREMONIAL_VESSEL'),(68,-76,'ROYAL','Rare','Jewel casket','VIC_L09_KEEPSAKE'),(82,-76,'ROYAL','Premium','Royal insignia','VIC_L10_PREMIUM_INSIGNIA'),(-51,76,'RIVER','Valuable','Navigation portfolio','VIC_L14_RIVER_PORTFOLIO'),(-78,76,'RIVER','Rare','Trading collection','VIC_L05_TRADE_COLLECTION'),(51,76,'CRAFT','Valuable','Abstract bronze','VIC_L06_ABSTRACT_BRONZE'),(78,76,'CRAFT','Rare','Craft vessel','VIC_L08_CEREMONIAL_VESSEL')]
for i,(x,z,r,c,n,a) in enumerate(items,19):
 x={19:-47,20:-62,21:-77,22:47,23:62,24:77,26:-77,28:77}.get(i,x)
 upper.append(dict(lootId=f'VIC_LOOT_{i:03}',roomId='VIC_ROOM_UPPER_'+r,rootPosition=[x,34,z],placeholderCenter=[x,38,z],footprintXZ=[8,8],category=c,name='Fictional '+n,lootAsset=a,supportAsset='VIC_E03_CASE_PREMIUM' if c=='Premium' else 'VIC_E02_CASE_MEDIUM',scale=1.3 if c=='Premium' else 1.65,provisionalValue={'Valuable':1400,'Rare':2200,'Premium':3400}[c],capacityCost={'Valuable':3,'Rare':4,'Premium':5}[c],collectionSeconds={'Valuable':4,'Rare':6,'Premium':8}[c],floor=2))
security=[]
for i,(kind,pos,size,r) in enumerate([('StaticLaser',[-21,34,-68],[8,8,8],'NORTH'),('MovingLaser',[-39,34,-76],[10,8,12],'TREASURY'),('StaticLaser',[40,34,-76],[8,8,12],'ROYAL'),('ElectricFloor',[66,34,-65],[8,.2,8],'ROYAL'),('Terminal',[46,34,-88],[3,5,3],'ROYAL'),('ProtectedCase',[82,34,-76],[8,8,8],'ROYAL')],10):security.append(dict(securityId=f'VIC_SECURITY_{i:03}',securityType=kind,position=pos,size=size,roomId='VIC_ROOM_UPPER_'+r,difficultyTier=3,floor=2,active=False))
security.append(dict(securityId='VIC_SECURITY_016',securityType='Terminal',position=[-16,34,-56],size=[3,5,3],roomId='VIC_ROOM_UPPER_SCREENING',difficultyTier=2,floor=2,active=False))
next(s for s in security if s['securityType']=='ProtectedCase')['position'][0]=77
stairs=[dict(id='VIC_STAIR_'+name,role='Prominent museum' if s<0 else 'Secondary return',floorFrom=6.8,floorTo=34,risers=36,rise=27.2/36,tread=1.5,flightWidth=8.5,midLandingSize=[19,9],boundsXZ=[2,21,-84,-48] if s<0 else [-21,-2,48,84],voidBoundsXZ=[1.5,21.5,-84.5,-47.5] if s<0 else [-21.5,-1.5,47.5,84.5],upperArrival=[-s*6.25,34,s*47.5],minimumHeadroom=9) for name,s in [('NORTH',-1),('SOUTH',1)]]
edges=[['MAIN','NORTH_GROUND'],['REAR','SOUTH_GROUND'],['NORTH_GROUND','VIC_ROOM_MAIN_HALL'],['SOUTH_GROUND','VIC_ROOM_MAIN_HALL'],['NORTH_GROUND','VIC_ROOM_PUBLIC'],['NORTH_GROUND','VIC_ROOM_HIGH_SECURITY'],['SOUTH_GROUND','VIC_ROOM_GALLERY_A'],['SOUTH_GROUND','VIC_ROOM_GALLERY_B'],['VIC_ROOM_PUBLIC','VIC_ROOM_GALLERY_C'],['VIC_ROOM_HIGH_SECURITY','VIC_ROOM_ARCHIVE'],['VIC_ROOM_MAIN_HALL','SIDE_A'],['VIC_ROOM_MAIN_HALL','SIDE_B'],['NORTH_GROUND','VIC_ROOM_UPPER_NORTH'],['SOUTH_GROUND','VIC_ROOM_UPPER_SOUTH'],['VIC_ROOM_UPPER_NORTH','VIC_ROOM_UPPER_HALL'],['VIC_ROOM_UPPER_SOUTH','VIC_ROOM_UPPER_HALL'],['VIC_ROOM_UPPER_NORTH','VIC_ROOM_UPPER_TREASURY'],['VIC_ROOM_UPPER_NORTH','VIC_ROOM_UPPER_ROYAL'],['VIC_ROOM_UPPER_SOUTH','VIC_ROOM_UPPER_RIVER'],['VIC_ROOM_UPPER_SOUTH','VIC_ROOM_UPPER_CRAFT']]
event=dict(heistId='VIC_HEIST_007',floorsShareEvent=True,alert='First unauthorized restricted entry OR theft start, once per shared robbery',timer='One shared future timer',economy='One shared individual bag / loot economy',cooldown='One shared cooldown/reset',gameplayImplemented=False)
edges.remove(['VIC_ROOM_UPPER_NORTH','VIC_ROOM_UPPER_TREASURY']);edges.extend([['VIC_ROOM_UPPER_NORTH','VIC_ROOM_UPPER_SCREENING'],['VIC_ROOM_UPPER_SCREENING','VIC_ROOM_UPPER_TREASURY']])
plan=dict(task='009 revised',coordinateSystem='Local studs Y-up; Blender (x,-z,y)',groundFloorOriginal=lock,upperFloorY=34,wingRoofUndersideY=47,centralVoidRadius=23,balconyOuterRadius=30.8,upperRooms=rooms,upperLoot=upper,upperSecurity=security,stairs=stairs,connections=edges,upperWingDoors=[dict(x=x,z=z,clearWidth=12,baseY=34,height=10.5) for x in [-31,31] for z in [-82,-65,65,82]],hallUpperDoors=[dict(x=0,z=z,clearWidth=14,baseY=34,height=14) for z in [-33,33]],restrictedUpper=[dict(id='VIC_RESTRICTED_003',roomId='VIC_ROOM_UPPER_TREASURY',center=[-60.5,40.5,-76],size=[57,13,34]),dict(id='VIC_RESTRICTED_004',roomId='VIC_ROOM_UPPER_ROYAL',center=[60.5,40.5,-76],size=[57,13,34])],sharedEvent=event,clearance=dict(noNewFacadeOpenings=True,groundPartitions='Paired ten-stud openings retained',upperGallery='12-stud paired doors, 10+ stud exhibit lanes',balcony='7.8-stud annular walk, 46-stud open void'))
plan['restrictedUpper'].append(dict(id='VIC_RESTRICTED_005',roomId='VIC_ROOM_UPPER_SCREENING',center=[-21,44,-71],size=[18,20,34]))
(ROOT/'docs/task009/two-floor-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
(KIT/'layout-lock.json').write_text(json.dumps(dict(lock,task009Revision='One interconnected two-floor robbery',groundFloorOriginal=lock,upperRooms=rooms,upperLoot=upper,upperSecurity=security,upperRestricted=plan['restrictedUpper'],stairs=stairs,connections=edges,sharedEvent=event),indent=2)+'\n')
folder=ROOT/'artifacts/review/task009/planning';folder.mkdir(exist_ok=True,parents=True)
for floor in [1,2]:
 im=Image.new('RGB',(1400,1160),'#e7e1d6');d=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
 def pt(x,z):return(700+x*4.5,580+z*4.5)
 def rect(b,fill):d.rectangle([pt(b[0],b[2]),pt(b[1],b[3])],fill,'#786f61',3)
 rect([-35,35,-35,35],'#c9c6b6');rect([-31,31,-92,-35],'#dad4c6');rect([-31,31,35,92],'#dad4c6')
 for x in [-1,1]:
  for z in [-1,1]:rect([min(x*32,x*90),max(x*32,x*90),min(z*59,z*93),max(z*59,z*93)],'#c8d4ce' if z>0 else '#d8c59f')
 for st in stairs:
  b=st['boundsXZ'];rect(b,'#9aa9a9');d.text(pt(b[0]+2,(b[2]+b[3])/2),'STAIR',fill='#173e43',font=small)
 if floor==2:
  d.ellipse([pt(-23,-23),pt(23,23)],fill='#f6f1e6',outline='#576e70',width=4);d.text(pt(-13,-4),'OPEN HALL\nNO FLOOR',fill='#304f52',font=font);loot=upper
  for r in rooms[3:]:d.text(pt(r['centerXZ'][0]-24,r['centerXZ'][1]-13),r['name'],fill='#253c40',font=small)
 else:
  for x in [-66,69]:
   for za,zb in [(-93,-89),(-79,-71),(-61,-59)]:rect([x-.6,x+.6,za,zb],'#786f61')
  d.text(pt(-18,-4),"QUEEN'S HALL\nDOUBLE HEIGHT",fill='#304f52',font=font);loot=lock['loot']
 for item in loot:
  x,y,z=item['rootPosition'];d.ellipse([pt(x-1.4,z-1.4),pt(x+1.4,z+1.4)],fill='#925748');d.text(pt(x-2,z+2),item['lootId'][-3:],fill='#572b25',font=small)
 d.text((40,30),f'VICTORIA TASK009 | FLOOR {floor} | PRECISE FOOTPRINT REFERENCE',fill='#304f52',font=font);d.text((40,65),'Local X horizontal / Z down. Concept imagery cannot change these coordinates.',fill='#304f52',font=small)
 for t,x,z in [('FRONT',-8,-104),('REAR',-8,99),('SIDE A',-132,0),('SIDE B',110,0)]:d.text(pt(x,z),t,fill='#304f52',font=small)
 im.save(folder/f'precise_floor_{floor}.png')
print('Plan: 7 ground rooms, 8 upper spaces, 28 loot, 16 security, 2 stairs.')
