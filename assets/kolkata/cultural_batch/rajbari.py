"""Reference-led compact zamindar estate with a dedicated ceremonial mandap."""
from estate_common import *


def dome():
    g=G()
    g.lathe([(0,11.3),(.7,11.8),(1.3,11),(8,11),(8.7,11.8),(9.3,12)],32,'EstateIvory')
    g.lathe([(9.3,12),(11,11.8),(14,10.8),(17,9),(20,5.8),(21.2,2.5),(21.8,0)],32,'EstateDome')
    g.lathe([(0,.9),(1.2,1.2),(2.2,.65),(3.4,0)],10,'EstateGold',(0,21.7,0))
    for i in range(12):
        t=i*math.tau/12
        pts=[(r*math.cos(t),y,r*math.sin(t)) for y,r in [(9.4,12.04),(11,11.86),(14,10.86),(17,9.06),(20,5.86),(21.25,2.6)]]
        for a,b in zip(pts,pts[1:]):g.beam(a,b,.10,'EstateIvory',5)
        p=(11.1*math.cos(t),1.7,11.1*math.sin(t));ang=-t-math.pi/2
        g.merge(window(2.8,5.5,True).transformed(p,ang))
    return g


def mandap(a):
    sec='05_Puja_Mandap';x,z=33,14
    a.box('Mandap_raised_socle',(x,1.65,z),(36,1.8,29),'EstateBrick',sec)
    a.box('Mandap_coping',(x,2.7,z),(37,.45,30),'EstateIvory',sec)
    a.steps('Mandap_broad_steps',23,z-14.8,2.925,count=4,tread=1.1,x=x)
    g=G()
    for dx in [-15,15]:
        for dz in [-10.5,10.5]:g.merge(brick_column(21,.9).transformed((dx,2.9,dz)))
    g.box((0,23.5,0),(34,1.2,25),'EstateIvory')
    # Curved Bengali chala silhouette, made as one solid roof cross-section.
    pts=[(-19,23.9),(-15,25.4),(-10,27),(-5,28),(0,28.5),(5,28),(10,27),(15,25.4),(19,23.9),
         (19,25.1),(15,26.6),(10,28.2),(5,29.2),(0,29.7),(-5,29.2),(-10,28.2),(-15,26.6),(-19,25.1)]
    g.merge(H.prism(pts,29,0,'EstateMaroon'))
    for side in [-1,1]:
        for p,q in zip(pts[:9],pts[1:9]):g.beam((p[0],p[1],side*14.6),(q[0],q[1],side*14.6),.16,'EstateGold',5)
    # Rear architectural screen and recessed arch are a finished installation space.
    g.box((0,12.7,11.1),(28,19.6,1.2),'EstateMaroon')
    g.arch(18,10,.45,1.1,(0,3,10.3),'EstateGold',16)
    g.box((0,3.35,6.7),(22,.8,7),'EstateBrickLight')
    g.merge(H.disk(0,24.6,-13,1.4,'EstateGold',12))
    for i in range(5):
        t=(i-2)*.45;cx=math.sin(t)*2.4;cy=25.4+math.cos(t)*1.3
        g.ellipsoid((cx,cy,-13),(1.1,1.8,.22),'EstateGold',8,4)
    # Open side rails leave the front stage accessible.
    for dx in [-15,15]:g.merge(H.balustrade(19,2.7,2,'EstateIvory',False).transformed((dx,3.0,0),math.pi/2))
    a.put('Finished_Bengali_Puja_mandap',g,(x,0,z),section=sec)
    for dx in [-19,19]:a.instance('Flower_urn',urn(True),(x+dx,2.9,z-10),section=sec)
    a.night_light('Mandap_stage',(x,22,z-10),(x,9,z+7),7000,32)
    a.layout['mandap']={'positionStuds':[x,2.925,z],'stageWidthStuds':34,'stageDepthStuds':26,
        'function':'Dedicated finished Puja mandap space, intentionally open for a later ceremonial installation'}


def build():
    a=Compound('rajbari','Bengali Rajbari Estate');a.ground(202,220)
    # Rear mansion and two shallow wings leave the entire court genuinely open.
    a.wing('Rear_mansion',0,64,174,26,'EstatePlaster',section='01_Rear_Mansion')
    for sign in [-1,1]:
        a.wing('Side_wing_'+str(sign),sign*77,-7,20,116,'EstatePlaster',section='02_Side_Wings')
        a.gallery('Brick_veranda',112,(sign*62.1,0,-6),sign*math.pi/2,brick=True,section='02_Side_Wings')
        for z in [-53,-34,-15,4,23,42]:
            for y in [5.3,23.4]:
                a.instance('Wing_outer_shutter',window(6.2,12,False),(sign*87.15,y,z),-sign*math.pi/2,'02_Side_Wings')
            a.instance('Wing_inner_shutter',window(6.2,12,False),(sign*67.15,23.4,z),sign*math.pi/2,'02_Side_Wings')
    # Tall central order and proper broad stair are the courtyard hero.
    a.box('Rear_portico_platform',(0,5.0,43),(82,8.5,18),'EstateBrick','01_Rear_Mansion')
    a.box('Rear_portico_floor',(0,9.25,43),(84,.55,19),'EstateIvory','01_Rear_Mansion')
    a.steps('Grand_courtyard_stair',72,33.5,9.525,count=11,tread=1.25)
    tall=brick_column(28.7,1.1)
    for x in [-35,-21,-7,7,21,35]:a.instance('Grand_brick_order',tall,(x,9.45,36),section='01_Rear_Mansion')
    a.put('Grand_portico_entablature',cornice(84,19,38.0,dentils=True),(0,0,43),section='01_Rear_Mansion')
    a.put('Rear_central_pediment',H.pediment(80,40.0,8.5,0,'EstateIvory','EstateWhite'),(0,0,34),section='01_Rear_Mansion')
    for x in [-35,-21,-7,7,21,35]:
        a.instance('Tall_Dalan_shutter',window(7.4,24.5,False),(x,11.3,50.8),section='01_Rear_Mansion')
    for x in [-73,-57,57,73]:
        for y in [5.1,23.2]:a.instance('Rear_inner_window',window(6.5,12,True),(x,y,50.8),section='01_Rear_Mansion')
    for x in [-76,-57,-38,-19,0,19,38,57,76]:
        for y in [5.1,23.2]:a.instance('Rear_external_window',window(6.3,12,False),(x,y,77.15),math.pi,'01_Rear_Mansion')
    for x in [-44,44]:a.instance('Flower_urn',urn(True),(x,9.55,35),section='01_Rear_Mansion')
    # Front gatehouse: separate side solids plus a true central walk-through.
    for sign in [-1,1]:a.wing('Front_wing_'+str(sign),sign*49,-78,76,26,'EstatePlaster','03_Street_Front')
    a.box('Gate_upper_hall',(0,29.6,-78),(22,18.6,26),'EstatePlaster','03_Street_Front')
    gate=arch_wall(22,18.1,14.4,10.6,2.2,'EstatePlaster');gate.arch(14,10.6,.65,2.8,(0,0,-.1),'EstateIvory',16)
    for z in [-91, -65]:a.instance('Central_open_gateway',gate,(0,2.8,z),section='03_Street_Front')
    for x in [-77,-59,-41,-23,23,41,59,77]:
        for y in [5,23.4]:a.instance('Street_shutter',window(7,12.5,True),(x,y,-91.15),section='03_Street_Front')
        for y in [5,23.4]:a.instance('Courtyard_gatehouse_shutter',window(6.4,12,True),(x,y,-64.85),math.pi,'03_Street_Front')
    pilaster=G();pilaster.box((0,17.8,0),(1.5,35.6,.9),'EstateIvory')
    for y in [.4,17.4,35]:pilaster.box((0,y,-.15),(2.8,.8,1.2),'EstateIvory')
    for x in [-86,-68,-50,-32,-14,14,32,50,68,86]:a.instance('Street_classical_pilaster',pilaster,(x,3,-91.25),section='03_Street_Front')
    a.put('Gatehouse_center_cornice',cornice(23,27,38.88,dentils=True),(0,0,-78),section='03_Street_Front')
    a.put('Gatehouse_pediment',H.pediment(38,40.2,7.2,0,'EstatePlaster','EstateIvory'),(0,0,-92),section='03_Street_Front')
    a.instance('Central_upper_window',window(9,12.5,True),(0,23,-91.2),section='03_Street_Front')
    a.put('Domed_street_pavilion',dome(),(0,40.5,-76),section='04_Roofline')
    # A projecting, grounded portico distinguishes the arrival from ordinary bays.
    a.box('Gateway_walkthrough_landing',(0,1.775,-78),(24,2.05,27),'EstateStone','03_Street_Front')
    a.box('Grand_arrival_portico_plinth',(0,1.775,-97.5),(43,2.05,13),'EstateStone','03_Street_Front')
    a.box('Arrival_portico_stone_coping',(0,2.8,-97.5),(44,.3,13.5),'EstateIvory','03_Street_Front')
    a.steps('Arrival_portico_steps',39,-104.25,2.95,count=4,tread=1.1)
    a.steps('Inner_gateway_steps',22,-64.5,2.8,count=4,tread=1.1,angle=math.pi)
    portico_column=recolor(H.column(21,.95,'EstateIvory',True),HeritageCream='EstateIvory')
    for x in [-17,-12,12,17]:a.instance('Arrival_Corinthian_column',portico_column,(x,2.9,-101),section='03_Street_Front')
    a.put('Arrival_portico_entablature',cornice(43,13,23.7,'EstateIvory',True),(0,0,-97.5),section='03_Street_Front')
    a.put('Arrival_portico_pediment',H.pediment(44,25.2,6.8,0,'EstatePlaster','EstateWhite'),(0,0,-104.1),section='03_Street_Front')
    crest=H.disk(0,0,0,1.45,'EstateGold',16)
    for sign in [-1,1]:
        for i in range(4):crest.ellipsoid((sign*(2.5+i*.65),-.4+i*.25,0),(.65,.3,.2),'EstateGold',7,3)
    a.put('Arrival_pediment_crest',crest,(0,27.5,-105),section='03_Street_Front')
    # Roofs use muted stone; brick is reserved for the courtyard's structural order.
    for obj in a.root.all_objects:
        if obj.type=='MESH' and '_roof__' in obj.name:
            obj.data.materials.clear();obj.data.materials.append(pipeline.material('EstateRoof'))
    # Continuous rail runs have masonry piers, a seated base and supported ends.
    for z in [-91,-65]:
        for sign in [-1,1]:a.parapet('Front_complete_parapet',64,(sign*54,40.5,z))
    a.parapet('Rear_complete_parapet',172,(0,40.5,77))
    for sign in [-1,1]:a.parapet('Side_complete_parapet',166,(sign*87,40.5,-7),math.pi/2)
    mandap(a)
    a.lawn('West_courtyard_lawn',-28,-12,40,68);a.lawn('Mandap_front_lawn',31,-37,37,20)
    # Inlaid path edges emphasize the clear entry-to-Dalan axis.
    g=G()
    for x in [-8,8]:g.box((x,.83,-13),(.4,.13,101),'EstateBrickLight')
    for x in [-48,48]:g.box((x,.83,-12),(.3,.13,70),'EstateBrickLight')
    a.put('Courtyard_path_inlays',g,section='00_Grounds')
    for x,z in [(-47,-49),(-47,24),(48,-50),(11,24)]:a.instance('Court_lantern',lantern(),(x,.8,z),section='00_Grounds')
    for x in [-94,94]:
        for z in [-90,76]:a.instance('Flower_urn',urn(True),(x,.8,z),section='00_Grounds')
    for x in [-65,-32,32,65]:a.night_light('Street_'+str(x),(x,2,-99),(x,26,-91),19000,48)
    a.night_light('Arrival_portico',(0,3,-107),(0,19,-100),12000,35)
    for x in [-64,0,64]:a.night_light('Rear_'+str(x),(x,2,87),(x,26,77),17000,48)
    for sign in [-1,1]:
        for z in [-42,17]:a.night_light('Outer_side_'+str(sign)+'_'+str(z),(sign*95,2,z),(sign*87,26,z))
        for z in [-36,15]:a.night_light('Court_wing_'+str(sign)+'_'+str(z),(sign*50,2,z),(sign*64,29,z),13000,45)
    a.night_light('Courtyard_Dalan',(0,3,19),(0,28,37),22000,55)
    a.night_light('Front_dome',(0,41,-94),(0,56,-76),9000,40)
    a.night_light('Rear_dome',(0,41,-58),(0,56,-76),9000,40)
    a.layout.update(compoundFootprintStuds=[202,220],mainCourt={'boundsXZ':[-55,-55,55,33]},
        centralEntrance={'positionStuds':[0,.8,-108],'minimumClearWidthStuds':14},
        style='Warm ivory/ochre plaster estate, terracotta courtyard columns, projecting Corinthian entrance and muted gold dome',
        openSkyChecksXZ=[[-28,-12],[0,-20]],entryRay={'origin':[0,7,-109],'direction':[0,0,1],'length':72})
    a.sockets['StreetEntry']={'positionStuds':[0,.8,-108],'clearWidthStuds':14}
    return a.finish()


if __name__=='__main__':build()
