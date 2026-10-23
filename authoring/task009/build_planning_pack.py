"""Portable, clean Studio photos plus factual coordinate plans for heist planning."""
import base64,copy,csv,hashlib,json,math,shutil,textwrap
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle
from planning_views import ROOMS,EXTRA
ROOT=Path(__file__).resolve().parents[2]
DEST=ROOT/'artifacts/review/task009/heist-planning'
DEST.mkdir(parents=True,exist_ok=True)
plan=json.loads((ROOT/'authoring/task009/final-plan.json').read_text())
layout=plan['upperLayout'];ground=layout['groundFloorOriginal']
roomdata={r['roomId']:dict(r,floor=1) for r in ground['rooms']}
roomdata.update({r['roomId']:dict(r,floor=2) for r in layout['upperRooms']})
loot=copy.deepcopy(ground['loot']+layout['upperLoot'])
for r in loot:
    r['visuals']=[dict(instanceId=p['instanceId'],assetId=p['assetId'],role=p['role']) for p in plan['instances'] if p['sourceMarker']==r['lootId']]
security=[]
for floor,rows in [(1,ground['security']),(2,layout['upperSecurity'])]:
    for i,r in enumerate(rows,1):
        row=copy.deepcopy(r);row.update(floor=floor,mapLabel=('G' if floor==1 else 'U')+str(i).zfill(2),active=False)
        security.append(row)
def decode(src,dst):
    dst.parent.mkdir(parents=True,exist_ok=True)
    if src.exists():dst.write_bytes(base64.b64decode(src.read_text()))
    else:assert dst.exists(),f'Missing committed photograph: {dst}'
photos=[];rooms=[]
for folder,id,forward,eye,target in ROOMS:
    entry=dict(roomdata[id],folder=folder,lootIds=[r['lootId'] for r in loot if r['roomId']==id],securityIds=[r['securityId'] for r in security if r['roomId']==id],photos=[])
    if forward:
        dst=DEST/folder/'01_approach.png'
        decode(ROOT/'artifacts/recovery/task009-captures'/('final_'+forward+'.b64'),dst)
        entry['photos'].append(str(dst.relative_to(DEST)))
    name='02_reverse.png' if forward else '01_approach.png'
    src=ROOT/'artifacts/recovery/task009-planning-captures'/folder/name.replace('.png','.b64')
    decode(src,DEST/folder/name);entry['photos'].append(folder+'/'+name)
    entry['captureCamera']=dict(file=folder+'/'+name,localEye=eye,localTarget=target)
    entry['adjacentGraphNodes']=[b if a==id else a for a,b in layout['connections'] if id in [a,b]]
    rooms.append(entry);photos.extend(entry['photos'])
    (DEST/folder/'README.md').write_text('# '+entry['name']+'\n\nRoom ID: `'+id+'`. Floor '+str(entry['floor'])+'.\n\nLoot: '+(', '.join(entry['lootIds']) or 'None')+'.\n\nSecurity reservations: '+(', '.join(entry['securityIds']) or 'None assigned to this zone')+'.\n\nConnections: '+', '.join(entry['adjacentGraphNodes'])+'.\n\n'+''.join('- [View '+str(i+1)+']('+p.split('/')[-1]+')\n' for i,p in enumerate(entry['photos']))+'\nPhotos are clean views, not marker overlays. Use the coordinate plans and JSON for exact marker locations.\n')
for folder,forward,eye,target in EXTRA:
    dst=DEST/folder/'01_route.png';dst.parent.mkdir(parents=True,exist_ok=True)
    if forward:decode(ROOT/'artifacts/recovery/task009-captures'/('final_'+forward+'.b64'),dst)
    else:decode(ROOT/'artifacts/recovery/task009-planning-captures'/folder/'01_route.b64',dst)
    photos.append(str(dst.relative_to(DEST)))
index=dict(snapshot='Task009 approved architecture and final lighting, 2026-10-23',coordinateSystem=dict(units='Roblox studs',frame='Landmark-local X horizontal, Z down on plans; negative Z is front/main portal, NOT geographic north',worldFromLocal='(820+z,y,-x)',blenderFromLocal='(x,-z,y)',floorHeights=[6.8,34]),sharedEvent=layout['sharedEvent'],rooms=rooms,loot=loot,security=security,restricted=ground['restricted']+layout['restrictedUpper'],stairs=layout['stairs'],externalRoutes=ground['exits'],connections=layout['connections'],photoCount=len(photos),photos=photos,sourceFiles={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'authoring/task009/final-plan.json',ROOT/'assets/victoria-memorial/interior/layout-lock.json']},implementationStatus=dict(architectureApproved=True,lightingInstalled=True,lootCollection=False,functionalLasers=False,electricHazards=False,terminalHacking=False,policeAlerts=False,sharedTimerBagCooldown=False,cctvMotionDetection='Not planned; decorative only'))
(DEST/'planning-index.json').write_text(json.dumps(index,indent=2)+'\n')
with (DEST/'room-index.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['Floor','RoomId','Name','LootIds','SecurityIds','PhotoFolder'])
    for r in rooms:w.writerow([r['floor'],r['roomId'],r['name'],';'.join(r['lootIds']),';'.join(r['securityIds']),r['folder']])
for floor in [1,2]:
    fig,ax=plt.subplots(figsize=(16,12));fig.patch.set_facecolor('#eee9df');ax.set_facecolor('#eee9df')
    def box(cx,cz,w,d,face,edge='#746f66',lw=1.4,alpha=1):ax.add_patch(Rectangle((cx-w/2,cz-d/2),w,d,facecolor=face,edgecolor=edge,lw=lw,alpha=alpha))
    box(0,-61.5,60,53,'#d9dcda');box(0,61.5,60,53,'#d9dcda')
    for r in rooms:
        if r['floor']!=floor or r['roomId'].endswith(('HALL','NORTH','SOUTH')):continue
        x,z=r['centerXZ'];w,d=r.get('sizeXZ',[18,34]);box(x,z,w,d,'#d6c2aa' if 'SCREENING' in r['roomId'] else '#c6d7ce')
        title='\n'.join(textwrap.wrap(r['name'].split('  ')[-1],14));ax.text(x,z-d/2+2.3,title,ha='center',va='top',fontsize=8.5,color='#273d40',weight='bold')
    ax.add_patch(Circle((0,0),30.8,facecolor='#c8d3cc',edgecolor='#566c6b',lw=2))
    if floor==2:ax.add_patch(Circle((0,0),23,facecolor='#eee9df',edgecolor='#566c6b',lw=2));hall='OPEN VOID\nOverlook surrounds it'
    else:hall="QUEEN'S HALL\nNo loot"
    ax.text(0,0,hall,ha='center',va='center',fontsize=11,color='#273d40')
    for st in layout['stairs']:
        a,b,c,d=st['boundsXZ'];box((a+b)/2,(c+d)/2,b-a,d-c,'#abb7c5')
        ax.text((a+b)/2,(c+d)/2,st['id'].replace('VIC_STAIR_','')+'\nSTAIR\n8.5-wide',ha='center',va='center',fontsize=8)
    if floor==1:
        for x in [-66,69]:
            for z0,z1 in [(-93,-89),(-79,-71),(-61,-59)]:ax.plot([x,x],[z0,z1],color='#4b4b46',lw=3)
        for r in ground['exits']:
            x,_,z=r['position'];ax.scatter([x],[z],marker='s',c='#407969',s=80);ax.text(x,z+5,r['routeId'].replace('VIC_EXIT_',''),ha='center',fontsize=9,color='#235847')
    else:
        for d in layout['upperWingDoors']:ax.plot([d['x'],d['x']],[d['z']-6,d['z']+6],color='white',lw=6);ax.plot([d['x'],d['x']],[d['z']-6,d['z']+6],color='#367968',lw=1)
        for z in [-33,33]:ax.plot([-5.4,5.4],[z,z],color='#367968',lw=3)
    for r in security:
        if r['floor']!=floor:continue
        pos=r.get('position',r.get('padCenter'));x,y,z=pos;w,d=r.get('footprintXZ',[r.get('size',[3,3,3])[0],r.get('size',[3,3,3])[2]])
        box(x,z,w,d,'none',edge='#b14646',lw=1.7);ax.annotate(r['mapLabel'],(x,z),xytext=(4,-13),textcoords='offset points',color='#9b2e2e',fontsize=8,weight='bold')
    for r in loot:
        if (2 if int(r['lootId'][-3:])>=19 else 1)!=floor:continue
        x,y,z=r['rootPosition'];ax.scatter([x],[z],s=42,c='#b48b33',edgecolors='#715213',zorder=5);ax.annotate(r['lootId'][-3:],(x,z),xytext=(0,8),ha='center',textcoords='offset points',fontsize=9,color='#48380f',weight='bold')
    ax.set(xlim=(-145,145),ylim=(116,-116),xlabel='Landmark-local X (studs)',ylabel='Landmark-local Z (studs; front is negative)');ax.set_aspect('equal');ax.grid(alpha=.18)
    ax.set_title(('GROUND FLOOR' if floor==1 else 'UPPER FLOOR')+' — rooms, loot and inactive security reservations',fontsize=16,pad=20)
    fig.text(.5,.025,'Gold dots = VIC_LOOT suffix. Red boxes = security footprints (G/U labels resolve in JSON). Green = routes/openings.\nZone extents are orientation guides, not a collision survey. Keep the approved architecture; plan one shared heist.',ha='center',fontsize=10)
    fig.savefig(DEST/f'00_floor_{floor}_map.png',dpi=130,bbox_inches='tight');fig.savefig(DEST/f'00_floor_{floor}_map.svg',bbox_inches='tight');plt.close(fig)
    selected=[r for r in rooms if r['floor']==floor]
    sheet=Image.new('RGB',(1400,math.ceil(len(selected)/2)*430),(29,33,37));draw=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19)
    for i,r in enumerate(selected):
        im=Image.open(DEST/r['photos'][0]).convert('RGB');im.thumbnail((690,380));x=(i%2)*700;y=(i//2)*430;sheet.paste(im,(x,y));draw.text((x+8,y+383),r['name'],font=font,fill='white');draw.text((x+8,y+407),r['roomId'],fill='#c8c1ae')
    sheet.save(DEST/f'00_floor_{floor}_contact_sheet.png')
lines=['# Victoria heist — planning photo pack','', 'Start with the two coordinate maps, then the contact sheets. Open each numbered room folder for clean approach/reverse Studio views. All photos show the actual approved museum, not ImageGen concepts.','', '- [Ground coordinate map](00_floor_1_map.png) / [Upper coordinate map](00_floor_2_map.png)', '- [Ground room sheet](00_floor_1_contact_sheet.png) / [Upper room sheet](00_floor_2_contact_sheet.png)', '- [Machine-readable planning index](planning-index.json) / [Room index CSV](room-index.csv)','', '## Planning rules','', 'This is ONE future robbery across both floors: one event/timer, individual bags, shared loot availability, one police alert and one cooldown/reset. Alert on the first unauthorized restricted entry OR theft start. Public entry alone does not trigger it. Ground-floor loot can be taken without completing upstairs. Both stairs and all four bidirectional exterior routes remain available.','', 'CCTV and motion sensors are decorative only. Lasers, electrical hazards, terminal hacking, protected-case interactions, loot collection, bags, payouts, alerts and reset logic are NOT implemented. The 16 security reservations are inactive visual/planning locations. Provisional values/capacities are planning numbers, not a balanced economy.','', 'The architecture is approved. Plan security around its routes and clearances; do not redesign it from these photos. Exact IDs, coordinates, case bindings, room graph, restrictions and camera poses are available in the index and source files. Photos have no fake marker overlays.','', '## Coordinate and photograph notes','', 'Plans use landmark-local X/Z, with negative Z at the main portal; this is not geographic north. Ground Y is 6.8 (hall approximately 7), upper Y is 34. World = (820+z, y, -x). Upper hall arch visual clearance is 10.8 studs inside the 14-stud structural opening; balcony floor radii are 23–30.8, with rails/piers reducing usable clearance.','', 'Security 010 is associated with the north antechamber metadata but physically lies inside the screening branch. The map shows its actual location. Security labels G01–G09 and U01–U07 resolve to full stable IDs in planning-index.json.','', 'Studio views were captured at existing afternoon lighting with a temporary fixed medium editor quality (Level10), then Automatic was restored. They are not mobile/FPS evidence. Approach and reverse refer to camera views, not enforced one-way routes.','', '## Rooms','', '| Floor | Room | Loot | Security | Photos |','|---|---|---:|---:|---|']
for r in rooms:lines.append('| '+str(r['floor'])+' | '+r['name']+' | '+str(len(r['lootIds']))+' | '+str(len(r['securityIds']))+' | [Open]('+r['folder']+'/README.md) |')
lines += ['', '## Inter-floor / escape views','']+['- ['+f+']('+f+'/01_route.png)' for f,_,_,_ in EXTRA]
(DEST/'README.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(dict(rooms=len(rooms),photographs=len(photos),loot=len(loot),security=len(security),output=str(DEST))))
