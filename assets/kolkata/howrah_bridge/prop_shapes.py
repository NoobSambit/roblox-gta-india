"""Fifteen original compact riverfront prop designs; no third-party mesh assets."""
import math
from howrah_geometry import Geo

def torus(g,pos,r=.75,t=.15,mat='White',major=12,minor=4,vertical=True):
 v=[]
 for i in range(major):
  a=i*math.tau/major
  for j in range(minor):
   b=j*math.tau/minor;x=(r+t*math.cos(b))*math.cos(a);y=(r+t*math.cos(b))*math.sin(a);z=t*math.sin(b)
   v.append((pos[0]+x,pos[1]+(y if vertical else z),pos[2]+(z if vertical else y)))
 f=[]
 for i in range(major):
  for j in range(minor):f.append((i*minor+j,((i+1)%major)*minor+j,((i+1)%major)*minor+(j+1)%minor,i*minor+(j+1)%minor))
 g.solid(v,f,mat)

def lamp():
 g=Geo();g.lathe((0,0,0),[(0,.65),(.35,.65),(.65,.4),(1.1,.3)],'White',8)
 g.cylinder((0,9.15,0),.18,16.4,'Steel',8)
 for sign in [-1,1]:
  path=[(0,10,0),(sign*1.7,10.6,0),(sign*3.1,12,0),(sign*3.5,15.5,0)]
  for a,b in zip(path,path[1:]):g.beam(a,b,.17,.2,'Steel')
 for x,y in [(-3.5,16),(0,18),(3.5,16)]:
  g.lathe((x,y,0),[(-.65,.14),(-.45,.65),(.2,.6),(.65,.16)],'Lamp',10)
  g.lathe((x,y,0),[(.62,.2),(.85,.72),(1.05,.15)],'DarkSteel',8)
 return g

def road_light():
 g=Geo();g.lathe((0,0,0),[(0,.55),(.4,.55),(.7,.25)],'Concrete',8)
 g.cylinder((0,7.5,0),.2,14.5,'Steel',8)
 p=[(0,14.5,0),(1,15.2,0),(3.5,15.2,0)]
 for a,b in zip(p,p[1:]):g.beam(a,b,.22,.22,'Steel')
 g.box((3.5,14.95,0),(2.1,.45,.9),'DarkSteel');g.box((3.5,14.65,0),(1.7,.18,.7),'Lamp')
 return g

def pole():
 g=Geo();g.cylinder((0,10,0),.3,20,'Concrete',8)
 for y in [17.5,19]:g.box((0,y,0),(5,.2,.22),'DarkSteel')
 for x in [-1.7,1.7]:
  for y in [17.7,19.2]:g.lathe((x,y,0),[(0,.18),(.25,.28),(.55,.14)],'Cream',8)
 g.box((0,12,0),(1,.9,.65),'Roof')
 return g

def balustrade():
 g=Geo();g.rail(16,0,mat='White',balusters=8);g.box((0,1.9,0),(15.2,.18,.2),'Blue');return g

def steel_barrier():
 g=Geo();g.steel_rail(16,spacing=4,mat='DarkSteel')
 for x in [-8,-4,0,4,8]:g.box((x,.1,0),(.7,.2,.7),'DarkSteel')
 return g

def mooring():
 g=Geo();g.lathe((0,0,0),[(0,.6),(.25,.6),(.4,.38),(1.8,.35)],'DarkSteel',8)
 g.box((0,1.6,0),(2.3,.55,.65),'DarkSteel');return g

def stone_bollard():
 g=Geo();g.lathe((0,0,0),[(0,.7),(.25,.7),(2.7,.5),(3,.32)],'Concrete',8)
 g.lathe((0,0,0),[(1.8,.53),(2.1,.53)],'Blue',8);return g

def bench():
 g=Geo()
 for x in [-2.4,2.4]:
  for z in [-.6,.6]:g.box((x,.8,z),(.25,1.6,.25),'DarkSteel')
  g.beam((x,1.5,.65),(x,3.2,1),.2,.2,'DarkSteel')
  g.box((x,2.15,0),(.22,.2,1.7),'DarkSteel')
 for z in [-.6,-.2,.2,.6]:g.box((0,1.65,z),(6,.18,.32),'Timber')
 for y in [2.05,2.6,3.15]:g.box((0,y,.85),(6,.35,.2),'Timber')
 return g

def bin_shape():
 g=Geo();g.lathe((0,0,0),[(0,.7),(.2,.85),(2.6,.85),(2.8,.72)],'Green',10)
 g.lathe((0,0,0),[(2.8,.75),(3,.85),(3.2,.55)],'DarkSteel',10)
 g.box((0,2.65,-.82),(.8,.35,.12),'Window')
 for x in [-.95,.95]:g.box((x,1.4,0),(.15,1.8,.35),'DarkSteel')
 return g

def sign():
 g=Geo()
 for x in [-2.2,2.2]:
  g.cylinder((x,3.5,0),.13,7,'DarkSteel',6);g.box((x,.1,0),(.6,.2,.6),'Concrete')
 g.box((0,5.6,0),(5.3,2.9,.35),'Blue');g.box((0,5.6,-.22),(4.8,2.4,.1),'White')
 return g

def vendor():
 g=Geo()
 for x in [-4.5,4.5]:
  for z in [-3,3]:g.box((x,4,z),(.25,8,.25),'DarkSteel')
 g.extrude([(-5,0),(0,1.6),(5,0),(5,-.18),(0,1.4),(-5,-.18)],7,(0,8,0),'Canvas')
 for x in [-4.5,4.5]:g.box((x,3.2,0),(.3,.2,6.2),'DarkSteel')
 g.box((0,2.6,1.4),(9,1.8,2.2),'Blue');g.box((0,3.6,1.4),(9.5,.25,2.6),'Timber')
 g.box((0,7.4,-3.2),(8,1,.2),'White')
 for z in [-2,0,2]:g.box((0,1.3,z),(8,.2,.2),'DarkSteel')
 return g

def cabinet():
 g=Geo();g.box((0,.2,0),(2.5,.4,1.7),'Concrete');g.box((0,2,0),(2.2,3.4,1.5),'Roof')
 g.box((0,3.85,0),(2.45,.3,1.8),'DarkSteel');g.box((0,2,-.79),(1.8,2.6,.12),'Green')
 for y in [1.3,1.6,1.9,2.2]:g.box((0,y,-.88),(1.3,.1,.12),'DarkSteel')
 g.box((.5,2.9,-.9),(.12,.3,.12),'Cream');return g

def lifebuoy():
 g=Geo();g.box((0,.15,0),(1.7,.3,1.4),'Concrete');g.box((0,2.4,0),(.2,4.5,.2),'Blue')
 torus(g,(0,3.1,-.25),.85,.18,'White');g.box((0,1.3,0),(1.6,.65,.2),'White')
 g.box((0,1.3,-.16),(1.2,.4,.1),'Blue');return g

def boat(canopy=False):
 g=Geo();length=28 if canopy else 26;width=8;stations=9;crossn=7
 rows=[]
 crossx=[-1,-.85,-.5,0,.5,.85,1];crossy=[3,1.7,.45,0,.45,1.7,3]
 for inner in [False,True]:
  for j in range(stations):
   s=j/(stations-1);z=(s-.5)*length;shape=.16+.84*math.sin(s*math.pi)**.7
   hw=width*.5*shape-(.2 if inner else 0);lift=2.2*abs(2*s-1)**2.4
   rows.extend((crossx[k]*hw,crossy[k]+lift+(.25 if inner else 0),z) for k in range(crossn))
 f=[];stride=stations*crossn
 for inner in [0,1]:
  offset=inner*stride
  for j in range(stations-1):
   for k in range(crossn-1):
    a=offset+j*crossn+k;f.append((a,a+1,a+crossn+1,a+crossn))
 for j in range(stations-1):
  for k in [0,crossn-1]:
   a=j*crossn+k;f.append((a,a+crossn,a+crossn+stride,a+stride))
 for j in [0,stations-1]:
  for k in range(crossn-1):
   a=j*crossn+k;f.append((a,a+stride,a+stride+1,a+1))
 g.solid(rows,f,'DarkWood')
 for sign in [-1,1]:
  points=[]
  for j in range(stations):
   s=j/(stations-1);points.append((sign*(width*.5*(.16+.84*math.sin(s*math.pi)**.7)),3.15+2.2*abs(2*s-1)**2.4,(s-.5)*length))
  for a,b in zip(points,points[1:]):g.beam(a,b,.22,.25,'Timber')
 for z in [-6,0,6]:g.box((0,2.35,z),(6.2,.3,.75),'Timber')
 for x in [-1.2,-.4,.4,1.2]:g.box((x,.55,0),(.6,.25,13),'Timber')
 for station in [2,3,5,6]:
  s=station/(stations-1);z=(s-.5)*length;hw=width*.5*(.16+.84*math.sin(s*math.pi)**.7)-.2
  lift=2.2*abs(2*s-1)**2.4
  rib=[(crossx[k]*hw,crossy[k]+lift+.3,z) for k in range(crossn)]
  for a,b in zip(rib,rib[1:]):g.beam(a,b,.15,.18,'Timber')
 for sign in [-1,1]:
  g.beam((sign*2.5,3.2,-3),(sign*7,1.3,1),.15,.18,'Timber')
  g.box((sign*7,.95,1),(.8,1,.18),'Timber',sign*.4)
 torus(g,(0,4,-length*.45),.4,.09,'Canvas',8,4,False)
 if canopy:
  g.vault((0,4.2,2),3.2,2.3,.12,10,'Canvas',8)
  for z in [-3,7]:g.vault((0,4.2,z),3.2,2.3,.18,.2,'Timber',8)
  for x in [-3.2,3.2]:
   for z in [-3,7]:g.box((x,3.7,z),(.15,1.1,.15),'Timber')
 return g

PROPS=[
 ('01','Three-arm riverfront lamp',lamp,['props_02','props_11'],'Native cylinder/box pole proxy only; lamps decorative; add unshadowed light later.'),
 ('02','Single roadway lamp',road_light,['road_06'],'Simple pole box; decorative light head noncollidable.'),
 ('03','Simple electric pole',pole,['road_06'],'Single pole proxy; insulators decorative; no wires/scripts.'),
 ('04','Blue-white balustrade 16',balustrade,['props_11'],'Continuous thin box barrier; disable collision on individual balusters.'),
 ('05','Steel barrier 16',steel_barrier,['road_06'],'Continuous thin box barrier, not each small bar.'),
 ('06','Mooring bollard',mooring,['boat_1'],'One cylinder or box proxy.'),
 ('07','Stone bollard',stone_bollard,['props_02'],'One cylinder or box proxy.'),
 ('08','Riverfront bench',bench,['props_02'],'Simple seat/back boxes; omit individual slat collision.'),
 ('09','Litter bin',bin_shape,['props_02'],'One box/hull proxy.'),
 ('10','Blank wayfinding frame',sign,['ghat_open_1'],'Posts and board boxes; blank surface for future authored signage.'),
 ('11','Compact vendor canopy',vendor,['boat_1','ghat_open_2'],'Posts/counter boxes only; canopy is decorative.'),
 ('12','Utility cabinet',cabinet,['road_06'],'One box proxy.'),
 ('13','Lifebuoy stand',lifebuoy,['boat_1'],'Stand proxy only; no interaction implemented.'),
 ('14','Hooghly open rowboat',lambda:boat(False),['boat_1','boat_2'],'Static prop. Use a few hull boxes; no buoyancy or detailed mesh collision.'),
 ('15','Hooghly canopy rowboat',lambda:boat(True),['boat_2','boat_3'],'Static prop. Hull boxes only; no boat controller or buoyancy.')]

def build():
 from pipeline import Asset,save_master
 result=[]
 for number,name,fn,refs,collision in PROPS:
  asset=Asset('KOL_HBR_PROP_'+number,'props',name,refs,collision)
  asset.instance('Model',fn());result.append(asset.finish((30,1500 if int(number)>=14 else 900)))
 total=sum(r['assembledTriangles'] for r in result);assert 4000<=total<=8000,total
 save_master();print('PROP_LIBRARY_TOTAL '+str(total));return result

if __name__=='__main__':build()
