"""Howrah's paired cantilever outline and laced steel, compressed for driving."""
import math
from howrah_geometry import Geo,add,sub,mul,norm,cross,dot
from pipeline import Asset,save_master

HALF=[18,36,55,75,94,112,104,96,88,81,75,70,67,65,64]
HEIGHTS=HALF+list(reversed(HALF[:-1]))
LENGTH=896;BAY=32;DECK=32

def laced(g,a,b,width=1.4):
 axis=norm(sub(b,a));perp=norm(cross((1,0,0),axis));length=math.sqrt(dot(sub(b,a),sub(b,a)))
 for sign in [-1,1]:
  offset=mul(perp,sign*width/2)
  g.beam(add(a,offset),add(b,offset),.7,.8,'Steel','I')
 n=max(1,round(length/12))
 for i in range(n):
  aa=add(add(a,mul(axis,length*i/n)),mul(perp,(-1 if i%2 else 1)*width/2))
  bb=add(add(a,mul(axis,length*(i+1)/n)),mul(perp,(1 if i%2 else -1)*width/2))
  g.beam(aa,bb,.2,.24,'Steel')

def side_chunk(index):
 g=Geo()
 for j in range(4):
  k=index*4+j;z=j*BAY;y0=DECK+HEIGHTS[k];y1=DECK+HEIGHTS[k+1]
  g.beam((0,34,z),(0,34,z+BAY),1.8,2.3,'Steel','I')
  g.beam((0,y0,z),(0,y1,z+BAY),2,2.7,'Steel','I')
  laced(g,(0,29.5,z),(0,y0,z),1.8)
  # Alternate the main compression diagonal; the slim counter member remains legible.
  if k%2:
   laced(g,(0,35,z),(0,y1-1,z+BAY),1.35)
   g.beam((0,y0-1,z),(0,35,z+BAY),.52,.65,'Steel')
  else:
   laced(g,(0,y0-1,z),(0,35,z+BAY),1.35)
   g.beam((0,35,z),(0,y1-1,z+BAY),.52,.65,'Steel')
  mid0=34+(y0-34)*.45;mid1=34+(y1-34)*.45
  g.beam((0,mid0,z),(0,mid1,z+BAY),.55,.6,'Steel')
  # Visible joint plates, without bolts or rivet geometry.
  for y in [34,mid0,y0]:g.box((0,y,z),(.95,1.6,2.4),'Steel')
 return g

def transverse_chunk(index):
 g=Geo()
 for j in range(4):
  k=index*4+j;z=j*32;top=DECK+HEIGHTS[k];next_top=DECK+HEIGHTS[k+1]
  g.beam((-46,30.5,z),(46,30.5,z),1.7,2,'Steel','I')
  # A raised portal and its knees leave at least 15 studs over the road.
  portal=min(52,top-2)
  g.beam((-33,portal,z),(33,portal,z),1.4,1.7,'Steel','I')
  for sign in [-1,1]:g.beam((sign*33,portal-7,z),(sign*25,portal,z),.8,1,'Steel','I')
  g.beam((-33,top,z),(33,top,z),1.1,1.3,'Steel','I')
  g.beam((-33,top,z),(33,next_top,z+32),.5,.6,'Steel')
  g.beam((33,top,z),(-33,next_top,z+32),.5,.6,'Steel')
  # Under-deck lateral bracing is visible from the river.
  g.beam((-31,28.6,z),(31,28.6,z+32),.6,.7,'Steel')
  g.beam((31,28.6,z),(-31,28.6,z+32),.6,.7,'Steel')
 return g

def build():
 a=Asset('KOL_HBR_HOWRAH','bridge','Howrah Bridge — assembled 28-bay cantilever',
  ['side_01','side_02','side_04','side_08','road_01','road_06','road_07'],
  'Native box deck and sidewalks; simple curb/outer-rail boxes; disable collision/touch on truss detail. Bank/approach bearings only, with no exposed river piers. No precise mesh collision.')
 deck=Geo();deck.box((0,30.5,64),(62,3,128),'Asphalt')
 deck.box((0,29.45,64),(92,1.1,128),'Steel')
 for sign in [-1,1]:deck.box((sign*31.5,32.1,64),(1,1.2,128),'Concrete')
 markings=Geo()
 for x in [-20,-10,10,20]:
  for z in [8,40,72,104]:markings.box((x,32.07,z),(.3,.06,14),'White')
 for x in [-.35,.35]:markings.box((x,32.07,64),(.25,.06,128),'Yellow')
 walk=Geo();walk.box((0,32.25,64),(10,1.5,128),'Concrete')
 rail=Geo();rail.steel_rail(128,base=0,mat='DarkSteel',spacing=8,joinable=True)
 for i in range(7):
  z=-448+i*128
  side=side_chunk(i);transverse=transverse_chunk(i)
  for x in [-33,33]:a.instance('TrussSection'+str(i+1),side,pos=(x,0,z))
  a.instance('Crossframes'+str(i+1),transverse,pos=(0,0,z))
  a.instance('RoadSection128',deck,pos=(0,0,z),collision_role='RoadDeck')
  a.instance('LaneMarkings128',markings,pos=(0,0,z))
  for x in [-40,40]:a.instance('Sidewalk128',walk,pos=(x,0,z),collision_role='PedestrianDeck')
  for x in [-46,46]:a.instance('OuterRail128',rail,pos=(x,33,z+64),angle=math.pi/2,collision_role='OuterBarrier')
 rail_end=Geo();rail_end.box((0,1.75,0),(.22,3.5,.28),'DarkSteel')
 for x in [-46,46]:a.instance('OuterRailTerminal',rail_end,pos=(x,33,-448))
 end=Geo();laced(end,(0,29.5,0),(0,50,0),1.8)
 for x in [-33,33]:a.instance('EndUpright',end,pos=(x,0,448))
 frame=Geo();frame.beam((-46,30.5,0),(46,30.5,0),1.7,2,'Steel','I');frame.beam((-33,48,0),(33,48,0),1.4,1.7,'Steel','I')
 a.instance('EndCrossframe',frame,pos=(0,0,448))
 # No freestanding supports in the visible river opening. The short bearing
 # shoes sit at the approach ends, ready to meet later bank/abutment geometry.
 bearing=Geo()
 for x in [-33,33]:bearing.box((x,28.7,0),(4,1.6,6),'DarkSteel')
 for z in [-448,448]:a.instance('BankBearingShoes',bearing,pos=(0,0,z))
 a.sockets={'WaterLevel':dict(position=[0,0,0]),'RoadNorth':dict(position=[0,32,-448],yaw=180),
  'RoadSouth':dict(position=[0,32,448],yaw=0),'SidewalkWidthStuds':10,'RoadWidthStuds':60,'MinimumOverheadStuds':15}
 row=a.finish((35000,55000));save_master();return row

if __name__=='__main__':build()
