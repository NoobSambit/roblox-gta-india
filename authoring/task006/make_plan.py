"""Edit-time Kolkata placement data. Does not generate or alter source assets."""
import json, math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'authoring/task006/world-plan.json'
assets=json.loads((ROOT/'authoring/task006/asset-catalog.json').read_text())
catalog={a['assetId']:a for a in assets}
plan={'version':1,'streetY':0,'waterY':-13.5,'roads':[], 'placements':[], 'commercialPlots':[], 'roadSurfaces':[]}

def road(key,x0,z0,x1,z1,width=40,footpath=12):
    assert x0==x1 or z0==z1
    rect=[min(x0,x1),min(z0,z1),max(x0,x1),max(z0,z1)]
    rect=[rect[0]-width/2,rect[1]-width/2,rect[2]+width/2,rect[3]+width/2]
    plan['roads'].append(dict(id='KOL_RD_'+key,rect=rect,ends=[[x0,z0],[x1,z1]],width=width,footpath=footpath))

road('MAIN',-500,0,400,0)
road('RIVER',-500,-760,-500,650,32)
road('EAST',400,-760,400,650,24)
road('CENTRAL',80,-760,80,650,24)
for key,z in [('NORTH',-400),('CIVIC',-180),('SOUTH',400)]:road(key,-500,z,400,z)
road('OUTER_N',-500,-760,400,-760,20)
road('OUTER_S',-500,650,400,650,20)
road('NORTH_GULLY',-500,-550,80,-550,16,8)
road('MODERN_LOCAL',80,-580,400,-580,24,10)
road('COMMERCIAL_CROSS',-240,200,400,200,20)
road('WEST_SERVICE',-240,200,-240,650,20)
road('INFORMAL_LOOP',-500,580,-240,580,16,8)
road('SOUTH_LOCAL',-240,550,400,550,20,10)
road('JORA_WEST_GULLY',-310,-760,-310,-550,14,2)
road('JORA_EAST_GULLY',-133,-760,-133,-550,14,2)

def place(asset,district,x,z,yaw=0,kind='residential',y=0):
    row=dict(assetId=asset,district=district,position=[x,y,z],yaw=yaw,kind=kind)
    row['id']=f'KOL_{district.upper()}_{len(plan["placements"])+1:03d}'
    plan['placements'].append(row)
    return row

for asset,dist,x,z,yaw in [
 ('writers_building','Civic',-130,-280,180),('town_hall','Civic',270,-285,180),
 ('gpo','Civic',-340,150,90),('metropolitan_building','Civic',240,290,0),
 ('jorasanko_thakur_bari','NorthKolkata',-230,-650,180)]:
 place('kolkata.tier2.'+asset,dist,x,z,yaw,'landmark')

n=0
def residential(prefix,count,district,rows):
 global n
 for xs,z,yaw in rows:
  for x in xs:
   n+=1;place(f'KOL_T3_{prefix}_{(n-1)%count+1:02d}',district,x,z,yaw)

residential('OLD',10,'NorthKolkata',[(list(range(-440,1,48)),-450,180),(list(range(-440,1,48)),-510,0),
 ([-440,-386,-338,-100,-46,8],-600,180),([-440,-386,-338,-100,-46,8],-720,0)])
n=0
residential('MOD',9,'ModernResidential',[(list(range(120,361,60)),z,yaw) for z,yaw in [(-450,180),(-540,0),(-630,180),(-720,0)]])
n=0
residential('MIX',5,'Civic',[([-410,-345,-280,-205,-135,-65],-70,180)])
n=0
residential('MOD',9,'Civic',[([-430,-370,-310,-30,40,130],-350,0)])
n=0
residential('MIX',5,'Commercial',[([-230,-75,140,350],70,0),([-300,-75,140,350],340,180),([-170,15],460,0)])
n=0
residential('INF',3,'InformalResidential',[([-430,-395,-360],555,180),([-430,-395,-360],610,0)])

for kind,x,z,yaw in [('BANK',-150,105,0),('JEWELLERY',10,105,0),('FASHION',200,105,0),('RETAIL',-150,300,180),('ELECTRONICS',10,300,180)]:
 row=place('KOL_T25_'+kind,'Commercial',x,z,yaw,'commercial')
 meta=json.loads((ROOT/f'assets/kolkata/tier25/KOL_T25_{kind}/asset.json').read_text())
 plot=dict(id='KOL_PLOT_'+kind+'_001',buildingId=row['id'],assetId=row['assetId'],origin=[x,0,z],yaw=yaw,
    footprint=[meta['dimensionsStuds']['width']+12,meta['dimensionsStuds']['depth']+14],entrance=meta['entrance'],rearExit=meta['rearExit'],
    objectiveAttachment=meta['objectiveAttachment'],front='-Z',groundElevation=0,road='KOL_RD_MAIN' if z==105 else 'KOL_RD_SOUTH')
 plan['commercialPlots'].append(plot);row['plotId']=plot['id']

# Second street walls and southern residential transition close the empty blocks
# visible in the first assembly. Each remains a clone of an existing master.
for asset,x,z,yaw in [('02',-338,-629,-90),('04',-338,-662,-90),('01',-338,-695,-90),('03',-100,-629,90),('08',-100,-662,90),('04',-100,-695,90)]:
 place('KOL_T3_OLD_'+asset,'NorthKolkata',x,z,yaw)
n=0
residential('MOD',9,'ModernResidential',[([125,180,235,290,345],480,0),([125,180,235,290,345],610,0)])
n=0
residential('MIX',5,'Commercial',[([-175,-115,-55,5],500,180),([-175,-115,-55,5],610,0)])
n=0
residential('MIX',5,'Civic',[([-430,-370,-310],-260,180)])
n=0
residential('MOD',9,'Civic',[([125,180,240,310,355],-70,180)])

# Generate a disjoint rectangular road/pavement union; no overlapping asphalt or
# pavements across junctions. Original boulevard asphalt is retained separately.
rects=[]
for r in plan['roads']:
 a,b,c,d=r['rect'];f=r['footpath'];rects.extend([(a,b,c,d),(a-f,b-f,c+f,d+f)])
rects.append((-320,-20,320,20))
xs=sorted(set(v for r in rects for v in [r[0],r[2]]))
zs=sorted(set(v for r in rects for v in [r[1],r[3]]))
def inside(x,z,r):return r[0]<x<r[2] and r[1]<z<r[3]
def classify(x,z):
 if inside(x,z,(-320,-20,320,20)):return None
 if any(inside(x,z,r['rect']) for r in plan['roads']):return 'Road'
 if any(inside(x,z,(r['rect'][0]-r['footpath'],r['rect'][1]-r['footpath'],r['rect'][2]+r['footpath'],r['rect'][3]+r['footpath'])) for r in plan['roads']):return 'Pavement'
 return None
# Merge equal row runs vertically. Limit long strips to ~128 later in Luau.
active={};final=[]
for j in range(len(zs)-1):
 runs=[];start=None;last=None
 for i in range(len(xs)):
  k=classify((xs[i]+xs[i+1])/2,(zs[j]+zs[j+1])/2) if i<len(xs)-1 else None
  if k!=last:
   if last:runs.append((last,xs[start],xs[i]))
   start=i;last=k
 keys=set(runs)
 for key in list(active):
  if key not in keys:final.append(active.pop(key))
 for k,x0,x1 in runs:
  key=(k,x0,x1)
  if key in active:active[key]['rect'][3]=zs[j+1]
  else:active[key]=dict(kind=k,rect=[x0,zs[j],x1,zs[j+1]])
final.extend(active.values());plan['roadSurfaces']=final
plan['expansionConnections']=[
 dict(id='KOL_EXP_NORTH',position=[80,0,-760],direction=[0,0,-1]),
 dict(id='KOL_EXP_SOUTH',position=[80,0,650],direction=[0,0,1]),
 dict(id='KOL_EXP_EAST',position=[400,0,650],direction=[1,0,0]),
 dict(id='KOL_EXP_HOWRAH',position=[-1720,0,-180],direction=[-1,0,0])]
plan['riverfront']={'bridge':[-1092,-13.5,-180],'bridgeYaw':90,'ghat':[-620,-13.5,380],'ghatYaw':90,'waterBounds':[-1560,-830,-628,750]}
OUT.write_text(json.dumps(plan,indent=2)+'\n')
print(json.dumps({'placements':len(plan['placements']),'tier3':sum(r['kind']=='residential' for r in plan['placements']),'roadRectangles':len(final),'uniqueTier3':len({r['assetId'] for r in plan['placements'] if r['kind']=='residential'})}))
