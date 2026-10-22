"""Seven independent riverfront connection pieces and two minimal context shells."""
import math
from howrah_geometry import Geo
from pipeline import Asset,save_master

def wedge(g,width,length,y0,y1,mat='Asphalt',x=0,base=0):
 w=width/2;z=length/2
 v=[(x-w,base,-z),(x+w,base,-z),(x+w,base,z),(x-w,base,z),
    (x-w,y0,-z),(x+w,y0,-z),(x+w,y1,z),(x-w,y1,z)]
 g.solid(v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat)

def rail_run(asset,key,length,pos,angle=0,terminal=True):
 # Joined modules own their start post; a separate terminal avoids double posts.
 g=Geo();g.rail(16,0,mat='White',balusters=8,joinable=True);g.box((0,1.9,0),(15.2,.18,.2),'Blue')
 n=round(length/16)
 for i in range(n):
  local=(-length/2+8+i*16,0,0);c,s=math.cos(angle),math.sin(angle)
  p=(pos[0]+c*local[0],pos[1],pos[2]-s*local[0])
  asset.instance(key,g,pos=p,angle=angle,collision_role='Boundary')
 end=Geo();end.box((0,1.9,0),(.8,3.8,.9),'White');end.box((0,3.9,0),(1.15,.4,1.2),'White')
 p=(pos[0]+math.cos(angle)*length/2,pos[1],pos[2]-math.sin(angle)*length/2)
 if terminal:asset.instance('RailTerminal',end,pos=p,angle=angle)

def make(number,name,refs=None):
 return Asset('KOL_HBR_RF_'+number,'riverfront_structures',name,refs or ['ghat_open_2','ghat_open_4','props_11'],
  'Simple box/wedge walkable proxies; continuous boundary boxes; decorative rail balusters and trim noncollidable. Align water/road sockets before placement.')

def build():
 rows=[]
 a=make('01','Bridge approach ramp 128',['road_06','side_04'])
 g=Geo();wedge(g,62,128,32,13.5)
 for x in [-40,40]:wedge(g,10,128,33,14.5,'Concrete',x)
 for x in [-31.5,31.5]:wedge(g,1,128,32.7,14.2,'Concrete',x)
 for x in [-46,46]:
  for z in range(-64,65,8):
   y=32-(z+64)*18.5/128+1
   g.box((x,y+1.75,z),(.25,3.5,.3),'DarkSteel')
  for h in [1,2.3,3.5]:g.beam((x,33+h,-64),(x,14.5+h,64),.22,.25,'DarkSteel')
 for z in range(-56,65,16):
  y=32-(z+64)*18.5/128+.07
  for x in [-20,-10,10,20]:g.beam((x,y+.36,z-2.5),(x,y-.36,z+2.5),.22,.05,'White')
 for x in [-.35,.35]:g.beam((x,32.08,-64),(x,13.58,64),.25,.05,'Yellow')
 a.instance('Ramp',g,collision_role='RoadAndSidewalk')
 a.sockets={'HighRoad':dict(position=[0,32,-64]),'LowRoad':dict(position=[0,13.5,64]),'WaterLevel':dict(position=[0,0,0])}
 rows.append(a.finish())
 a=make('02','Straight embankment 64')
 g=Geo();g.box((0,5.35,1),(64,14.7,18),'Stone');g.box((0,13.1,1),(64,.8,18),'Concrete')
 for y in [1,5,9]:g.box((0,y,-8.12),(64,.25,.3),'Concrete')
 a.instance('WallAndWalk',g,collision_role='Embankment');rail_run(a,'Balustrade16',64,(0,13.5,-7.4))
 a.sockets={'WaterLevel':dict(position=[0,0,0]),'Left':dict(position=[-32,13.5,1]),'Right':dict(position=[32,13.5,1])};rows.append(a.finish())
 a=make('03','Embankment corner 48')
 g=Geo();g.plan([(-24,-24),(24,-24),(24,24),(8,24),(8,-8),(-24,-8)],-2,13.1,'Stone')
 g.plan([(-24,-24),(24,-24),(24,24),(8,24),(8,-8),(-24,-8)],13.1,13.5,'Concrete')
 a.instance('CornerFoundation',g,collision_role='Embankment')
 rail_run(a,'Balustrade16',48,(0,13.5,-24),terminal=False);rail_run(a,'Balustrade16',48,(24,13.5,0),-math.pi/2)
 a.sockets={'WaterLevel':dict(position=[0,0,0]),'In':dict(position=[-24,13.5,-16]),'Out':dict(position=[16,13.5,24])};rows.append(a.finish())
 a=make('04','Promenade connector 64')
 g=Geo();g.box((0,13.1,0),(64,.8,16),'Concrete');g.box((0,12.55,0),(64,.3,16),'Stone')
 a.instance('WalkSlab',g,collision_role='Promenade');rail_run(a,'Balustrade16',64,(0,13.5,-7.4))
 a.sockets={'Left':dict(position=[-32,13.5,0]),'Right':dict(position=[32,13.5,0])};rows.append(a.finish())
 a=make('05','Ghat road arrival apron 64')
 g=Geo();g.box((0,13.1,0),(64,.8,40),'Concrete')
 for x in [-27,27]:
  g.box((x,13.8,0),(10,.6,40),'Concrete')
  for z in [-12,0,12]:g.box((x,14.25,z),(7,.3,1.5),'White')
 a.instance('ApronAndLedges',g,collision_role='RoadApron')
 for x in [-31,31]:rail_run(a,'Balustrade16',16,(x,14.1,0),math.pi/2)
 a.sockets={'Road':dict(position=[0,13.5,20]),'Ghat':dict(position=[0,13.5,-20])};rows.append(a.finish())
 a=make('06','Retaining return 32')
 g=Geo();g.box((0,5.45,0),(32,14.9,6),'Stone');g.box((0,13.2,0),(33,.6,7),'Concrete')
 for y in [1,5,9]:g.box((0,y,-3.12),(32,.25,.3),'Concrete')
 a.instance('ReturnWall',g,collision_role='RetainingWall');rail_run(a,'Balustrade16',32,(0,13.5,0));rows.append(a.finish())
 a=make('07','Small river landing connector',['boat_1','ghat_open_4'])
 g=Geo();g.box((0,1.6,0),(32,1.2,16),'Concrete')
 for x in [-12,-4,4,12]:g.box((x,.5,0),(1,2.2,12),'DarkSteel')
 for z in [-6,-4,-2,0,2,4,6]:g.box((0,2.28,z),(31,.16,1.7),'Timber')
 for x in [-14,14]:
  g.lathe((x,2.4,-5),[(0,.5),(.2,.5),(1.4,.3),(1.6,.45)],'DarkSteel',8)
 a.instance('Landing',g,collision_role='Landing')
 a.sockets={'WaterLevel':dict(position=[0,0,0]),'DeckTop':dict(position=[0,2.36,0])};rows.append(a.finish())
 total=sum(r['assembledTriangles'] for r in rows);assert 5000<=total<=12000,total
 save_master();print('SUPPORT_TOTAL '+str(total));return rows

def context():
 rows=[]
 for number,name,w,d,h in [('01','Small river service shed',22,16,11),('02','Low river store shell',34,20,13)]:
  a=Asset('KOL_HBR_CTX_'+number,'context',name,['ghat_open_2','road_06'],'Closed background shell: one box collider or noncollidable if inaccessible; no interior.')
  g=Geo();g.box((0,.25,0),(w+.6,.5,d+.6),'Concrete');g.box((0,h/2,0),(w,h,d),'Concrete')
  g.extrude([(-w/2-1,0),(0,1.3),(w/2+1,0),(w/2+1,-.2),(0,1.1),(-w/2-1,-.2)],d+2,(0,h+.2,0),'Roof')
  g.extrude([(-w/2,0),(-w/2,.2),(0,1.4),(w/2,.2),(w/2,0)],d,(0,h,0),'Concrete')
  g.box((-w*.22,4,-d/2-.12),(5,7.5,.3),'Blue')
  for x in [w*.12,w*.33]:
   g.box((x,6.5,-d/2-.17),(3.3,3,.3),'White');g.box((x,6.5,-d/2-.37),(2.8,2.5,.15),'Window')
  g.box((0,h*.83,-d/2-.6),(w*.86,.3,1.6),'Concrete')
  a.instance('Shell',g);rows.append(a.finish((100,500)))
 save_master();return rows

if __name__=='__main__':build();context()
