"""One upgraded public ghat: broad Ganga terraces and open blue-white vaults.

Ahiritola/Bagbazar bathing steps and Baje Kadamtala's public terraces inform
the original interpretation. No residential upper storey, windows or rooms.
"""
import math
from howrah_geometry import Geo
from pipeline import Asset,save_master

def build():
 a=Asset('KOL_HBR_GHAT','ghat','Grand Kolkata Ganga Ghat — open public pavilion',
  ['ghat_open_1','ghat_open_2','ghat_open_4','ghat_major_1','ghat_major_2','ghat_major_5','props_02','props_11'],
  'Box platforms/shallow road apron, three wedge proxies over stairs, simple columns/walls. Disable collision on canopy/ribs/trim/balusters. Never hull across the open pavilion.')
 river=Geo();river.box((0,-.3,-56),(148,2.6,12),'Stone')
 # Full river-bank foundation stops before the road-facing apron.
 river.box((0,6,27.15),(148,14,41.7),'Stone')
 river.box((0,13.25,27.15),(149,.5,41.7),'Concrete')
 for sign in [-1,1]:
  for z,y,length in [(-42,5.2,16),(-22,9.4,16),(-1,13.6,17)]:
   river.box((sign*69,y/2-.3,z),(9,y+1,length),'Concrete')
   river.box((sign*69,y+.45,z),(10,.6,length+.6),'White')
   river.box((sign*69,y+.81,z),(9,.12,length),'Blue')
 a.instance('RiverBankFoundation',river,collision_role='BankFoundation')
 street=Geo()
 # This shallow apron embeds in the street bank at Y=13.5. Its exposed edge
 # is 0.8 studs deep, rather than a tall building-like road-facing basement.
 street.box((0,13.1,57),(149,.8,18),'Concrete')
 a.instance('StreetApronFoundation',street,collision_role='RoadApron')
 for i,(z,bottom) in enumerate([(-50,1),(-29.9,5.2),(-9.8,9.4)]):
  rise=.6 if i<2 else 4.1/7;g=Geo()
  g.stair(128,z,bottom,7,2.3,rise,'Stone',foundation=0)
  for j in range(7):g.box((0,bottom+(j+1)*rise+.025,z+(j+1)*2.3-.15),(128,.05,.3),'Concrete')
  a.instance('StairFlight'+str(i+1),g,collision_role='Stairs')
 land=Geo()
 for z,y in [(-31.9,5.2),(-11.8,9.4)]:land.box((0,y/2,z),(128,y,4),'Stone')
 land.box((0,14.1,33),(142,1.2,32),'Concrete')
 steps=Geo();steps.stair(116,14.4,13.5,2,1.3,.6,'Concrete',foundation=13.5);land.merge(steps)
 land.box((0,14.1,49.65),(116,1.2,1.3),'Concrete')
 land.box((0,13.8,50.95),(116,.6,1.3),'Concrete')
 a.instance('LandingsAndPublicFloor',land,collision_role='Platforms')
 col=Geo()
 for z in [18,46]:
  for x in [-54,-18,18,54]:
   col.column(x,z,14.7,13.8,.85,'White',10)
   col.lathe((x,14.7,z),[(.55,.94),(1.5,.94),(1.65,.85)],'Blue',10)
 a.instance('MainPavilionColumns',col,collision_role='Columns')
 roof=Geo()
 for x in [-36,0,36]:
  roof.vault((x,28.5,32),18,8.5,.35,30,'White',12)
  for z in [16.8,47.2]:roof.vault((x,28.5,z),18,8.5,.65,.5,'Blue',12)
  for z in [21,28,35,42]:roof.vault((x,28.5,z),17.6,8.1,.4,.38,'Cream',12)
  for z in [18,46]:roof.vault((x,14.7,z),17.45,8.05,.55,.85,'White',12,legs=13.8)
 for x in [-54,-18,18,54]:roof.box((x,28.5,32),(1.1,.65,30.5),'Blue')
 a.instance('TripleVaultShadePavilion',roof)
 side=Geo()
 for sign in [-1,1]:
  x=sign*62
  for dx in [-7,7]:
   for z in [23,47]:side.column(x+dx,z,14.7,8.3,.55,'White',8)
  side.vault((x,23,35),8,3.5,.32,27,'White',10)
  for z in [21.4,48.6]:side.vault((x,23,z),8,3.5,.5,.4,'Blue',10)
 a.instance('SideShadeCanopies',side)
 rail=Geo();rail.rail(16,0,mat='White',balusters=8);rail.box((0,1.9,0),(15.2,.18,.2),'Blue')
 joined=Geo();joined.rail(16,0,mat='White',balusters=8,joinable=True);joined.box((0,1.9,0),(15.2,.18,.2),'Blue')
 terminal=Geo();terminal.box((0,1.9,0),(.8,3.8,.9),'White');terminal.box((0,3.9,0),(1.15,.4,1.2),'White')
 for sign in [-1,1]:
  for z in [12,28,44]:a.instance('PromenadeRail16',joined,pos=(sign*73,13.5,z),angle=math.pi/2)
  a.instance('RailTerminal',terminal,pos=(sign*73,13.5,4))
  a.instance('BoundaryRail16',rail,pos=(sign*56,13.5,64.8))
  for z,y in [(-36,5.96),(-16,10.16)]:a.instance('BoundaryRail16',rail,pos=(sign*73.5,y,z),angle=math.pi/2)
 entry=Geo()
 # Broad horizontal public entrance, not a pair of isolated stick columns.
 # Footings terminate inside the street subbase, avoiding coplanar apron tops.
 for x in [-49.5,-16.5,16.5,49.5]:
  entry.box((x,12.3,60.5),(5.2,1.6,5.2),'Concrete')
  entry.box((x,13.9,60.5),(4.4,.8,4.8),'White')
  entry.box((x,18.85,60.5),(3.2,9.1,4.4),'White')
  entry.box((x,23.6,60.5),(4.7,.4,5),'White')
  entry.box((x,15.1,62.76),(3.22,.7,.15),'Blue')
 for x in [-33,0,33]:entry.vault((x,13.5,62.5),15,2.8,.55,.8,'Blue',12,legs=7.5)
 entry.box((0,24.5,60.5),(104,1.4,6),'White')
 entry.box((0,25.4,60.5),(106,.4,6.6),'White')
 entry.box((0,25.75,60.5),(106,.3,6.6),'Blue')
 for z in [57.4,63.6]:entry.box((0,24.5,z),(102,.55,.15),'Blue')
 entry.box((0,24.5,63.76),(24,.95,.2),'White')
 a.instance('RoadArrivalGateway',entry,collision_role='EntrancePosts')
 ledges=Geo()
 for sign in [-1,1]:
  for z in [10,53]:
   ledges.box((sign*61,14.1,z),(17,1.2,2),'Concrete')
   ledges.box((sign*61,14.8,z),(18,.3,2.5),'White')
 a.instance('IntegralSeatLedges',ledges)
 a.sockets={'WaterLevel':dict(position=[0,0,0]),'LowestLanding':dict(position=[0,1,-56]),
  'RoadEntrance':dict(position=[0,13.5,66],yaw=0),'StreetEmbedBottomY':12.7,'StreetSurfaceY':13.5,
  'UpperPromenade':dict(position=[0,13.5,9]),'PromenadeLeft':dict(position=[-74,13.5,12],yaw=-90),
  'PromenadeRight':dict(position=[74,13.5,12],yaw=90)}
 row=a.finish((8000,15000));save_master();return row

if __name__=='__main__':build()
