"""GPO: monumental white corner rotunda, ribbed dome and two colonnades."""
from common import *


def build():
    a=HeritageAsset('gpo','General Post Office')
    outline=[(-76,-70),(84,-70),(84,9),(-10,9),(-10,79),(-76,79)]
    a.put('L_shaped_compact_foundation',slab(outline,.8,.8,'HeritageStone'),section='00_Foundation',role='Walkable')
    a.collisions.extend([dict(name='East_base',positionStuds=[4,.4,-30.5],sizeStuds=[160,.8,79],yaw=0),
        dict(name='Return_base',positionStuds=[-43,.4,44],sizeStuds=[66,.8,70],yaw=0)])
    a.box('East_wing',(25,23,-24),(108,44.4,54),'HeritageWhite')
    a.box('Return_wing',(-39,23,24),(44,44.4,100),'HeritageWhite')
    a.box('East_colonnade_stylobate',(20,1.9,-55.5),(118,2.2,14),'HeritageStone','00_Foundation')
    a.box('Return_colonnade_stylobate',(-65,1.9,24),(14,2.2,100),'HeritageStone','00_Foundation')
    g=G();g.cylinder((0,1.9,0),31,2.2,'HeritageStone',48)
    g.cylinder((0,23,0),22,44.4,'HeritageWhite',48)
    a.put('Rotunda_body_and_seated_podium',g,(-39,0,-30),section='01_Shell')
    # One continuous L-shaped roof cap covers the coplanar top intersections
    # of the two wings and rotunda; no overlapping exposed roof planes remain.
    outline=[(-39+32*math.cos(math.pi+i*math.pi/32),-30+32*math.sin(math.pi+i*math.pi/32)) for i in range(17)]
    outline.extend([(80,-62),(80,4),(-16,4),(-16,75),(-71,75)])
    a.put('Continuous_L_roof_cap',slab(outline,45.6,.5,'HeritageWhite'),section='01_Shell')
    for i in range(10):
        x=-27+11*i
        a.instance('Street_Corinthian_column',column(37,1.15,'HeritageWhite'),(x,3,-60),section='03_Colonnades')
        a.collisions.append(dict(name='East_column',positionStuds=[x,21.5,-60],sizeStuds=[2.4,37,2.4],yaw=0))
    for i in range(9):
        z=-18+11*i
        a.instance('Street_Corinthian_column',column(37,1.15,'HeritageWhite'),(-69,3,z),section='03_Colonnades')
        a.collisions.append(dict(name='Return_column',positionStuds=[-69,21.5,z],sizeStuds=[2.4,37,2.4],yaw=0))
    for i in range(7):
        t=math.pi+i*math.pi/12
        x=-39+30*math.cos(t);z=-30+30*math.sin(t)
        a.instance('Street_Corinthian_column',column(37,1.15,'HeritageWhite'),(x,3,z),section='03_Colonnades')
    g=G();g.box((20,41.1,-55.5),(119,3.2,15),'HeritageWhite')
    g.box((-65,41.1,24),(15,3.2,101),'HeritageWhite')
    g.merge(cornices(119,15,[42.5],(20,0,-55.5),'HeritageCream'))
    g.merge(cornices(15,101,[42.5],(-65,0,24),'HeritageCream'))
    a.put('Supported_street_entablatures',g,section='02_Entablature')
    g=G();g.lathe([(39.5,30),(40.5,31),(42.6,31),(43,31.8),(44.5,31.8),(45.3,30.5)],48,'HeritageWhite')
    for i in range(25):
        t=math.pi+i*math.pi/48
        g.box((31*math.cos(t),42.2,31*math.sin(t)),(.7,.8,1),'HeritageCream',-t-math.pi/2)
    a.put('Rotunda_frieze_and_dentils',g,(-39,0,-30),section='02_Entablature')
    for i in range(9):a.instance('Colonnade_tall_recess',window(5.8,26,True,False,'HeritageCream'),(-25+12*i,7,-51.15),section='04_Recesses')
    for i in range(8):a.instance('Colonnade_tall_recess',window(5.8,26,True,False,'HeritageCream'),(-61.15,7,-16+12*i),math.pi/2,'04_Recesses')
    for i in range(5):
        angle=math.pi/2-i*math.pi/8;p=rotate((0,0,-22.15),angle)
        a.instance('Rotunda_tall_recess',window(5.4,26,True,False,'HeritageCream'),(-39+p[0],7,-30+p[2]),angle,'04_Recesses')
    # Drum windows and double pilasters preserve the dome's tall, airy identity.
    g=G();g.lathe([(45,20.6),(46,21.2),(47,20),(64,20),(65,21.1),(66,21.1)],48,'HeritageWhite')
    a.put('Tall_windowed_drum',g,(-39,0,-30),section='05_Dome_Drum')
    bay=window(3.6,11.5,True,False,'HeritageCream')
    for x in [-2.8,2.8]:
        bay.box((x,6.2,.1),(.65,15.1,.8),'HeritageCream')
        bay.box((x,13.8,-.1),(1.35,.8,1.2),'HeritageWhite')
    for i in range(16):
        angle=i*math.tau/16;p=rotate((0,0,-20.1),angle)
        a.instance('Drum_repeated_window',bay,(-39+p[0],48,-30+p[2]),angle,'05_Dome_Drum')
    profile=[(66,20.5),(68,20.3),(72,19.6),(77,18.1),(82,15.7),(87,12.5),(91,8.6),(94,3.5),(95,.7)]
    g=G();g.lathe(profile,48,'HeritageWhite')
    for j in range(16):
        t=j*math.tau/16
        for (y,r),(yy,rr) in zip(profile,profile[1:]):
            g.beam(((r+.1)*math.cos(t),y,(r+.1)*math.sin(t)),((rr+.1)*math.cos(t),yy,(rr+.1)*math.sin(t)),.14,'HeritageCream',5)
    g.lathe([(0,.85),(.8,1.1),(1.7,.7),(2.4,.8),(3.4,.25),(4.2,0)],12,'HeritageCream',(0,95,0))
    a.put('Ribbed_monumental_dome',g,(-39,0,-30),section='06_Dome')
    # Clock is a projecting street-facing plaque below the drum.
    g=G();g.box((0,0,.5),(8.4,8.4,1.5),'HeritageWhite');g.merge(clock(3.05))
    a.put('GPO_street_clock',g,(-39,46,-62.3),section='07_Civic_Details')
    g=G()
    for side in range(2):
        for i in range(9):
            p=(-27+12*i,47.5,-55.5) if side==0 else (-65,47.5,-18+11*i)
            g.box(p,(8.4,4,1.2) if side==0 else (1.2,4,8.4),'HeritageWhite')
            if side==0:g.box((p[0],p[1],p[2]-.7),(6.2,2,.3),'HeritageDark')
            else:g.box((p[0]-.7,p[1],p[2]),(.3,2,6.2),'HeritageDark')
    a.put('Attic_ventilation_rhythm',g,section='07_Civic_Details')
    # Low corner piers and pierced roof rail, no giant empty campus around it.
    for i in range(10):a.instance('GPO_front_parapet_module',balustrade(11.8,2.7,2.2,'HeritageWhite',False),(-33.1+11.8*i,50,-55.5),section='07_Civic_Details')
    for i in range(10):a.instance('GPO_return_parapet_module',balustrade(10,2.7,2.2,'HeritageWhite',False),(-65,50,-21+10*i),math.pi/2,'07_Civic_Details')
    g=G()
    for x,z in [(-61,-52),(76,-56),(-65,71)]:
        g.box((x,46.2,z),(4.8,4.8,4.8),'HeritageWhite');g.box((x,48.8,z),(5.4,.5,5.4),'HeritageCream')
        g.lathe([(0,.65),(.6,.45),(1.5,.8),(2.2,.55),(2.6,.2)],10,'HeritageCream',(x,49.1,z))
    a.put('Street_parapet_and_corner_piers',g,section='07_Civic_Details')
    a.steps('East_colonnade_steps',115,-62.6,3,count=5,x=20)
    rear=G()
    for y in [7,26]:rear.merge(window(5.4,12,False,False).transformed((0,y,0)))
    for x in [-19,-1,17,35,53,71]:a.instance('Secondary_wing_window',rear,(x,0,3.15),math.pi,'08_Secondary')
    for x in [-52,-38,-24]:a.instance('Secondary_wing_window',rear,(x,0,74.15),math.pi,'08_Secondary')
    a.night=['Dome ribs and finial','Drum openings with restrained warm highlights','Rotunda columns, clock and two colonnade entrances']
    a.save_live('GPO — connected colonnades, tall drum and ribbed dome')
    return a,a.finish()
