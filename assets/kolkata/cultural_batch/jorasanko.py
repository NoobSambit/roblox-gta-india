"""Two-main-building Jorasanko adaptation, retaining the supplied plan's court order."""
from estate_common import *


def portal(a,key,z,section,role='EstateRed',width=18,x=0):
    a.box(key+'_landing',(x,1.775,z),(width,2.05,16),'EstateStone',section)
    a.steps(key+'_outer_steps',width-2,z-8,2.8,count=4,tread=1.1,x=x)
    a.steps(key+'_inner_steps',width-2,z+8,2.8,count=4,tread=1.1,x=x,angle=math.pi)
    a.box(key+'_upper',(x,29.6,z),(width,18.6,16),role,section)
    g=arch_wall(width,17.8,12.4,10.4,1.4,role)
    g.arch(12,10.4,.35,1.8,(0,0,-.05),'EstateIvory',12)
    for face in [-8,8]:a.instance(key+'_opening',g,(x,2.8,z+face),section=section)
    a.put(key+'_crown',cornice(width,16,38.7),(x,0,z),section=section)
    surround=G()
    for sign in [-1,1]:
        surround.box((sign*(width/2-.55),8.7,0),(1.2,17.4,.65),'EstateIvory')
        surround.box((sign*(width/2-.55),.35,-.12),(2.0,.7,.95),'EstateIvory')
        surround.box((sign*(width/2-.55),17.1,-.12),(2.0,.7,.95),'EstateIvory')
    surround.box((0,17.7,-.05),(width+1.2,.65,.9),'EstateIvory')
    surround.box((0,18.3,-.15),(width+2.0,.5,1.2),'EstateIvory')
    a.instance(key+'_entrance_surround',surround,(x,2.8,z-8.9),section=section)


def facade_bay():
    g=G();g.merge(window(6.8,12,True,True).transformed((0,4.8,0)))
    g.merge(window(6.8,12,False,True).transformed((0,23.4,0)))
    for y in [3.6,20.0,38.5]:g.box((0,y,.25),(13.8,.4,.7),'EstateIvory')
    return g


def roof_parapet(w):
    g=G();g.box((0,1.55,0),(w,3.1,1.0),'EstateRed')
    g.box((0,3.1,0),(w+.6,.35,1.6),'EstateIvory')
    n=max(1,round(w/14))
    for i in range(n):
        x=-w/2+(i+.5)*w/n
        g.box((x,1.55,-.56),(w/n-1.7,1.9,.15),'EstateBrickLight')
        for yy in [.6,2.5]:g.box((x,yy,-.71),(w/n-1.5,.15,.2),'EstateIvory')
        for dx in [-(w/n-1.5)/2,(w/n-1.5)/2]:g.box((x+dx,1.55,-.71),(.15,1.9,.2),'EstateIvory')
    return g


def building_shell(a,which,front_z,back_z,split_west=False,white=False):
    sec='01_Bahir_Mahal' if which=='Bahir' else '02_Andar_Mahal'
    # Explicit room strips, not one solid bounding box. Courts remain open sky.
    for sign in [-1,1]:
        a.wing(which+'_front_'+str(sign),sign*45.5,front_z,73,16,'EstateRed',sec)
    portal(a,which+'_front_portal',front_z,sec,'EstateWhite' if white else 'EstateRed')
    if which=='Bahir':
        # West return starts exactly after the entry header; the old 6-stud
        # overlap produced the broad flickering red strip in the user's close-up.
        a.wing('Bahir_rear_return_west',-72,-1,20,10,'EstateRed',sec)
        a.wing('Bahir_rear_return_east',72,back_z,20,16,'EstateRed',sec)
    else:
        a.wing('Andar_north_west',-13,back_z,138,16,'EstateRed',sec)
        a.wing('Andar_north_east',78,back_z,8,16,'EstateRed',sec)
        portal(a,'Andar_northeast_rear_passage',back_z,sec,width=18,x=65)
    length=back_z-front_z-16;center=(front_z+back_z)/2
    a.wing(which+'_east',74,center,16,length,'EstateRed',sec)
    if split_west:
        # Actual west side entrance at the upper end of the private court.
        low_start=front_z+8;low_end=-22
        a.wing(which+'_west_long',-74,(low_start+low_end)/2,16,low_end-low_start,'EstateRed',sec)
        if back_z-8>-6:a.wing(which+'_west_short',-74,(-6+back_z-8)/2,16,back_z-8+6,'EstateRed',sec)
        a.box('West_entry_upper_gallery',(-74,29.6,-14),(16,18.6,16),'EstateRed',sec)
        a.box('West_entry_landing',(-74,1.775,-14),(16,2.05,16),'EstateStone',sec)
        a.steps('West_entry_street_steps',14,-14,2.8,count=4,tread=1.1,x=-82,angle=math.pi/2)
        a.steps('West_entry_court_steps',14,-14,2.8,count=4,tread=1.1,x=-66,angle=-math.pi/2)
        g=arch_wall(16,17.8,12.4,10.4,1.5,'EstateRed')
        g.arch(12,10.4,.4,2.1,(0,0,-.1),'EstateIvory',14)
        for side in [-1,1]:g.box((side*7.3,8.7,-.45),(1.2,17.4,.9),'EstateIvory')
        g.box((0,17.6,-.5),(17,.55,1.1),'EstateIvory')
        for x in [-82,-66]:a.instance('West_side_entry_arch',g,(x,2.8,-14),math.pi/2,sec)
        a.put('West_entry_header',cornice(16,16,38.7),(-74,0,-14),section=sec)
        a.put('West_entry_belt',cornice(16,16,20.58),(-74,0,-14),section=sec)
        for x,ang in [(-82.2,math.pi/2),(-65.8,-math.pi/2)]:a.instance('West_entry_upper_shutter',window(6.4,12,False,True),(x,23.4,-14),ang,sec)
    else:a.wing(which+'_west',-74,center,16,length,'EstateRed',sec)
    # Outer elevations are red; inner public galleries use the supplied white finish.
    bay=facade_bay()
    for sign in [-1,1]:
        for z in [front_z+17+i*(length-2)/max(1,round(length/17)-1) for i in range(round(length/17))]:
            if split_west and sign==-1 and -23<z<-5:continue
            if split_west and sign==-1 and z>=-6:z=-1.5
            a.instance('Jora_external_shutter_bay',bay,(sign*82.12,0,z),-sign*math.pi/2,sec)
    for x in [-73,-55,-37,-19,19,37,55,73]:
        if which=='Bahir' and abs(x)<64:continue
        if which=='Andar' and abs(x-65)<14:continue
        a.instance('Jora_external_shutter_bay',bay,(x,0,back_z+8.12),math.pi,sec)
    # Court galleries: right/left face inward; floor depth meets the room strip.
    court_len=back_z-front_z-30
    for sign in [-1,1]:
        if split_west and sign==-1:
            a.gallery(which+'_west_court',court_len-18,(-61.1,0,center-9),-math.pi/2,white=white,section=sec)
        else:a.gallery(which+'_court_gallery',court_len,(sign*61.1,0,center),sign*math.pi/2,white=white,section=sec)
    # Rear gallery spans 110 studs, eight bays; it is not an axial entrance.
    if which=='Andar':a.gallery(which+'_rear_court',120,(0,0,back_z-12.9),white=white,section=sec)
    # Court-facing shutter backing completes shallow verandas.
    for sign in [-1,1]:
        for z in [front_z+24,center,back_z-22]:
            if split_west and sign==-1 and -23<z<-5:continue
            for y in [5,23.4]:a.instance('Jora_court_green_shutter',window(6.6,12,False,True),(sign*65.9,y,z),sign*math.pi/2,sec)
    for x in [-48,-24,0,24,48]:
        if which=='Bahir':continue
        for y in [5,23.4]:a.instance('Jora_court_green_shutter',window(6.8,12,False,True),(x,y,back_z-8.12),section=sec)
    # Panelled parapets are built atop each actual wing roof.
    for z in [front_z-8,back_z+8]:
        if which=='Bahir' and z==front_z-8:continue
        if which=='Bahir' and z==back_z+8:
            a.instance('Bahir_rear_Dalan_parapet',roof_parapet(120),(0,40.5,z),section=sec)
            for sign in [-1,1]:a.instance('Bahir_return_parapet',roof_parapet(20),(sign*72,40.5,z),section=sec)
        else:a.instance(which+'_long_parapet',roof_parapet(164),(0,40.5,z),section=sec)
    for sign in [-1,1]:a.instance(which+'_side_parapet',roof_parapet(back_z-front_z-16),(sign*82,40.5,center),sign*math.pi/2,sec)
    return sec


def dalan(a):
    sec='03_Thakur_Dalan_Link';g=G()
    # The five-bay white dalan bridges the main buildings without filling either court.
    a.box('Dalan_platform',(0,1.8,8),(118,2.0,24),'EstateStone',sec)
    a.box('Dalan_floor',(0,2.95,8),(120,.35,25),'EstateWhite',sec)
    a.steps('Thakur_Dalan_broad_stair',104,-4.5,3.125,count=4,tread=1.2)
    pitch=23.6
    for i in range(5):
        x=(i-2)*pitch
        arch=arch_wall(pitch,17.5,13.9,9,1.4,'EstateWhite')
        arch.arch(13.5,9,.35,1.9,(0,0,-.1),'EstateIvory',14)
        a.instance('White_Dalan_arch',arch,(x,3.05,-2),section=sec)
        a.instance('Dalan_gallery_railing',grille(pitch-3,2.8),(x,20.65,-2),section=sec)
        # Dark floral/frieze inset panels from the supplied white-court reference.
        panel=G();panel.box((0,0,0),(pitch-4,1.9,.25),'HeritageIron')
        for j in range(5):panel.merge(H.disk((j-2)*3.3,0,-.2,.45,'EstateIvory',8))
        a.instance('Dalan_ornamental_frieze',panel,(x,38,-2.6),section=sec)
    for i in range(6):
        x=-59+i*pitch
        a.instance('White_Dalan_upper_paired_column',paired_post(17.5,'EstateWhite'),(x,20.6,-2),section=sec)
    for y in [20.6,38.7]:a.box('Dalan_gallery_slab_'+str(y),(0,y-.35,8),(120,.7,25),'EstateWhite',sec)
    a.put('Dalan_entablature',cornice(120,25,38.7,'EstateWhite',True),(0,0,8),section=sec)
    a.box('Dalan_roof_finish',(0,40.3,8),(120,.5,25),'EstateBrickLight',sec)
    # Upper storey back is a shallow wall; below, central circulation remains clear.
    a.box('Dalan_upper_backing',(0,29.4,18.7),(118,17.4,1.6),'EstateWhite',sec)
    for x in [-47,-23.6,0,23.6,47]:a.instance('Dalan_upper_green_shutter',window(7,12,False,True),(x,23.2,17.75),section=sec)
    a.instance('Dalan_parapet',roof_parapet(120),(0,40.5,-4.5),section=sec)
    # Finish the two short links into the room wings, with real floors,
    # supported gallery ends and roof returns instead of exposed cut-off strips.
    for sign in [-1,1]:
        for y in [2.8,20.6,38.7]:a.box('Dalan_link_slab_'+str(sign)+'_'+str(y),(sign*71,y-.35,13),(22,.7,18),'EstateIvory',sec)
        a.box('Dalan_link_plinth_'+str(sign),(sign*71,1.45,13),(22,1.4,18),'EstateStone',sec)
        a.box('Dalan_link_roof_'+str(sign),(sign*71,40.3,13),(22,.5,18),'EstateBrickLight',sec)
        for outside in [True,False]:
            x=sign*(82 if outside else 60);ang=-sign*math.pi/2 if outside else sign*math.pi/2
            wall=arch_wall(18,17.5,12.4,10.4,1.3,'EstateRed' if outside else 'EstateWhite')
            wall.arch(12,10.4,.4,1.9,(0,0,-.05),'EstateIvory',14)
            a.instance('Dalan_link_outer_arch' if outside else 'Dalan_link_inner_arch',wall,(x,2.8,13),ang,sec)
            for dz in [-8,8]:a.instance('Dalan_link_upper_post',paired_post(17.5,'EstateWhite'),(x,20.6,13+dz),ang,sec)
            a.instance('Dalan_link_balcony',grille(15,2.8),(x,20.6,13),ang,sec)
        a.put('Dalan_link_cornice_'+str(sign),cornice(22,18,38.92),(sign*71,0,13),section=sec)


def front_identity(a,sec):
    # Door/shutter backing is essential: an open arcade against a blank wall
    # loses the facade rhythm visible in the supplied street photograph.
    for x in range(-70,71,14):
        if x!=0:a.instance('Street_ground_green_door',window(7.0,13.5,True,True),(x,3.8,-117.12),section=sec)
        a.instance('Street_upper_green_door',window(7.4,13.8,False,True),(x,22.1,-117.12),section=sec)
    a.box('Front_red_floral_frieze',(0,39.7,-123.6),(156,3.0,1.3),'EstateRed',sec)
    flower=G();flower.ellipsoid((0,0,0),(1.45,.62,.18),'EstateIvory',10,4)
    for i in range(8):
        t=i*math.tau/8;flower.ellipsoid((1.25*math.cos(t),.55*math.sin(t),-.03),(.55,.30,.16),'EstateIvory',7,3)
    for x in range(-70,71,14):a.instance('Front_white_floral_medallion',flower,(x,39.7,-124.4),section=sec)
    # A shallow open third gallery with slender green supports/eaves is a major
    # silhouette cue in the supplied front photo, not another enclosed floor.
    a.box('Front_roof_loggia_floor',(0,40.8,-118.8),(157,.7,8),'EstateIvory',sec)
    post=G();post.box((0,1.5,0),(1.35,3,1.5),'EstateRed');post.box((0,3.1,0),(1.7,.3,1.8),'EstateIvory')
    post.cylinder((0,4.6,0),.15,9.2,'EstateGreen',8)
    for x in range(-77,78,14):a.instance('Front_roof_loggia_pier',post,(x,41.15,-122.3),section=sec)
    rail=G()
    rail.box((0,.1,0),(12.7,.2,.3),'EstateIvory');rail.box((0,2.8,0),(12.7,.25,.4),'EstateGreen')
    for j in range(15):rail.box((-6.2+j*12.4/14,1.4,0),(.09,2.6,.18),'EstateWhite')
    for x in range(-70,71,14):a.instance('Front_roof_loggia_white_rail',rail,(x,41.15,-122.3),section=sec)
    roof=G();points=[(-80,50.0,-124.6),(80,50.0,-124.6),(80,50.8,-114.2),(-80,50.8,-114.2),
        (-80,50.7,-124.6),(80,50.7,-124.6),(80,51.5,-114.2),(-80,51.5,-114.2)]
    for ids in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:roof.polygon([points[i] for i in ids],'EstateGreen')
    roof.box((0,50.05,-124.6),(160,.45,.4),'EstateIvory')
    a.put('Front_green_sloped_eaves',roof,section=sec)
    # Distinctive white curved ironwork around a green-supported entry canopy.
    brace=G();curve=[]
    for i in range(17):
        t=i*math.pi/16;curve.append((11*math.cos(t),15.2+3.4*math.sin(t),0))
    for p,q in zip(curve,curve[1:]):brace.beam(p,q,.10,'EstateWhite',5)
    brace.box((0,19.3,0),(24,.2,.25),'EstateWhite')
    for x in range(-10,11,2):
        low=15.2+3.4*math.sqrt(max(0,1-(x/11)**2))
        brace.beam((x,low+.05,0),(x,19.3,0),.065,'EstateWhite',4)
        if 19.3-low>.65:
            mid=(low+19.3)/2
            for side in [-1,1]:brace.beam((x,low+.2,0),(x+side*.55,mid,0),.055,'EstateWhite',4)
    a.put('Entrance_white_curved_ironwork',brace,(0,0,-136.45),section=sec)
    iron=G();iron.box((0,.3,0),(1,.6,1),'EstateIvory');iron.cylinder((0,8.3,0),.22,16.6,'EstateGreen',10)
    iron.box((0,16.5,0),(.9,.4,.9),'EstateIvory')
    for x in [-11.8,11.8]:a.instance('Entrance_green_iron_column',iron,(x,2.8,-134),section=sec)
    a.instance('Entrance_upper_white_balcony',grille(26,2.9),(0,20.6,-136.4),section=sec)
    for x in [-13.7,13.7]:
        pier=G();pier.box((0,1.5,0),(1.6,3,1.6),'EstateRed');pier.box((0,3.1,0),(2,.3,2),'EstateIvory')
        a.instance('Entrance_upper_balcony_pier',pier,(x,20.6,-136.1),section=sec)
    for x in [-56,56]:a.night_light('Front_roof_gallery_'+str(x),(x,43,-124),(x,49,-119),3000,25)


def build():
    a=Compound('jorasanko','Jorasanko Thakurbari Two-Building Complex');a.ground(196,282)
    # South/private Bahir Mahal and north/public Andar Mahal follow image 1.
    # The shared Dalan occupies the crosspiece, leaving the two primary masses legible.
    sec=building_shell(a,'Bahir',-109,-4,True,False)
    building_shell(a,'Andar',30,112,False,True)
    # Andar's front strip also has a real central passage via portal().
    # South front double-height galleries and raised entry portico, as in refs 2/5/8.
    a.gallery('Bahir_street_gallery',154,(0,0,-121.9),section=sec,street=True)
    a.gallery('Bahir_south_inner_gallery',126,(0,0,-96.1),math.pi,section=sec)
    for x in [-48,-24,24,48]:
        for y in [5,23.4]:a.instance('Bahir_inner_front_green_shutter',window(6.6,12,False,True),(x,y,-100.9),math.pi,sec)
    a.box('Front_portico_plinth',(0,1.6,-129),(29,1.6,13),'EstateStone',sec)
    a.box('Front_portico_landing',(0,2.65,-129),(30,.5,14),'EstateIvory',sec)
    a.steps('South_portico_entry_steps',25,-136,2.9,count=4,tread=1.1)
    pp=recolor(brick_column(16.6,.62),EstateBrick='EstateRed',EstateBrickLight='EstateRed')
    for x in [-12.8,-10.8,10.8,12.8]:a.instance('Front_portico_paired_column',pp,(x,2.8,-123.8),section=sec)
    a.box('Front_portico_canopy',(0,19.55,-129.7),(31,.9,12.6),'EstateIvory',sec)
    a.box('Portico_red_fascia',(0,20.0,-129.7),(30,.5,12.6),'EstateRed',sec)
    a.put('Portico_moulded_fascia',cornice(31,12.6,19.1,'EstateIvory',True),(0,0,-129.7),section=sec)
    a.box('Entrance_balcony_deck',(0,20.45,-129.7),(30,.3,12.6),'EstateStone',sec)
    # The source photos show a paired-column canopy and deep green entry.
    # Open timber leaves enrich the reveal while keeping the axial route clear.
    door=G()
    for sign in [-1,1]:
        door.box((sign*6.5,8.9,-113.5),(.35,12,5.5),'EstateGreen')
        for z in [-115.5,-111.5]:door.box((sign*6.7,8.9,z),(.16,11.4,.18),'EstateIvory')
        for y in [3.5,8.9,14.3]:door.box((sign*6.7,y,-113.5),(.16,.18,4.2),'EstateIvory')
    a.put('Open_green_entrance_door_leaves',door,section=sec)
    medallion=H.disk(0,0,0,.9,'EstateIvory',12)
    for i in range(6):
        t=i*math.tau/6;medallion.ellipsoid((1.0*math.cos(t),1.0*math.sin(t),0),(.55,.45,.16),'EstateIvory',7,3)
    a.put('Portico_floral_roundel',medallion,(0,19.65,-136.6),section=sec)
    for x in [-17.5,17.5]:a.instance('Portico_flower_urn',urn(True),(x,.8,-132),section=sec)
    front_identity(a,sec)
    # Small roof pavilion is characteristic of the photographed red garden front.
    a.box('Bahir_roof_pavilion',(0,44.8,-107),(38,8.4,15),'EstateRed',sec)
    for x in [-12,0,12]:a.instance('Roof_pavilion_green_window',window(5.2,5.6,False,True),(x,41.8,-114.6),section=sec)
    a.put('Roof_pavilion_cornice',cornice(38,15,49.0),(0,0,-107),section=sec)
    a.box('Pavilion_roof',(0,50.7,-107),(38,.6,15),'EstateBrickLight',sec)
    # Public court's southern gallery is white and has an odd bay count, clearing the axis.
    a.gallery('Andar_south_white_gallery',98,(0,0,42.9),math.pi,white=True,section='02_Andar_Mahal')
    for x in [-36,-18,18,36]:
        for y in [5,23.4]:a.instance('Andar_south_court_window',window(6.6,12,False,True),(x,y,38.1),math.pi,'02_Andar_Mahal')
    dalan(a)
    # Rear NE entrance opens through the actual split Andar north room strip.
    gate=G()
    for x in [-8,8]:
        gate.box((x,5,0),(2.5,10,2.5),'EstateRed');gate.box((x,10.2,0),(3.5,.6,3.5),'EstateIvory')
    a.instance('Northeast_rear_gate',gate,(65,.75,130),section='00_Grounds')
    a.instance('West_main_gate',gate,(-93,.75,-14),math.pi/2,'00_Grounds')
    # Circulation court is paved; only the private garden court carries a compact lawn.
    a.lawn('Private_courtyard_garden',0,-62,88,48)
    g=G()
    for z in [-91,-33]:g.box((0,.84,z),(111,.16,.45),'EstateRed')
    for x in [-55,55]:g.box((x,.84,-62),(.45,.16,58),'EstateRed')
    # Inlaid public court tiles are separate thin strips, never coincident floor planes.
    for x in [-40,-20,0,20,40]:g.box((x,.82,70),(.18,.12,47),'EstateStone')
    for z in [48,64,80,96]:g.box((0,.83,z),(100,.14,.18),'EstateStone')
    a.put('Court_paving_borders_and_joints',g,section='00_Grounds')
    # Main private garden path crosses the lawn at its upper end, matching the west entry.
    for x,z in [(-49,-87),(49,-87),(-49,-35),(49,-35),(-49,45),(49,45),(-49,95),(49,95)]:
        a.instance('Jora_flower_urn',urn(True),(x,.8,z),section='00_Grounds')
    for x,z in [(-87,-101),(87,-101),(-50,40),(50,95)]:a.instance('Compound_lantern',lantern(),(x,.8,z),section='00_Grounds')
    # Low compound wall/pier rhythm; leave the west and northeast gates clear.
    wall=G()
    for z0,z1 in [(-125,-23),(-5,122)]:
        wall.box((-94,2.5,(z0+z1)/2),(1.5,3.5,z1-z0),'EstateRed')
        wall.box((-94,4.4,(z0+z1)/2),(2,.35,z1-z0),'EstateIvory')
    wall.box((94,2.5,0),(1.5,3.5,246),'EstateRed');wall.box((94,4.4,0),(2,.35,246),'EstateIvory')
    a.put('Compound_boundary',wall,section='00_Grounds')
    for x in [-60,-25,25,60]:a.night_light('South_front_'+str(x),(x,2,-137),(x,28,-122),18000,50)
    for x in [-55,0,55]:a.night_light('North_rear_'+str(x),(x,2,126),(x,27,120),17000,48)
    for sign in [-1,1]:
        for z in [-75,-28,48,97]:a.night_light('Outer_side_'+str(sign)+'_'+str(z),(sign*90,3,z),(sign*82,27,z),14000,45)
        for z in [-67,69]:a.night_light('Inner_gallery_'+str(sign)+'_'+str(z),(sign*49,2,z),(sign*61,28,z),14000,48)
    a.night_light('White_Dalan_front',(0,3,-25),(0,29,-2),20000,55)
    a.night_light('Bahir_inner_south',(0,3,-82),(0,28,-96),14000,45)
    a.night_light('Andar_inner_south',(0,3,62),(0,28,43),14000,45)
    a.night_light('Andar_inner_north',(0,3,85),(0,28,99),14000,45)
    a.night_light('Bahir_roof_pavilion',(0,41,-122),(0,47,-108),7000,30)
    a.night_light('South_entry_canopy',(0,16,-130),(0,3,-132),3000,25)
    a.night_light('West_main_entry',(-88,14,-14),(-78,5,-14),5000,28)
    a.night_light('Northeast_rear_entry',(65,17,126),(65,5,117),5000,28)
    a.layout={'mainBuildingCount':2,'buildings':[
        {'name':'Bahir Mahal','collection':'01_Bahir_Mahal','position':'South; private garden court','boundsXZ':[-82,-117,82,4]},
        {'name':'Andar Mahal','collection':'02_Andar_Mahal','position':'North; public paved court','boundsXZ':[-82,22,82,120]}],
        'ThakurDalan':'Central white five-bay crosspiece between the courts',
        'sourcePlan':'references/photos/image-1.png; street west, portico south, rear access northeast',
        'privateCourt':{'centerXZ':[0,-62],'openBoundsXZ':[-54,-91,54,-33]},
        'publicCourt':{'centerXZ':[0,70],'openBoundsXZ':[-54,45,54,96]},
        'westMainEntry':{'positionStuds':[-94,.8,-14],'clearWidthStuds':12},
        'northeastRearEntry':{'positionStuds':[65,.8,130],'clearWidthStuds':12,'route':'Open passage through Andar north wing'},
        'southPorticoEntry':{'positionStuds':[0,.8,-138],'clearWidthStuds':12},
        'openSkyChecksXZ':[[0,-62],[0,70]],
        'entryRay':{'origin':[-97,7,-14],'direction':[1,0,0],'length':75}}
    a.scene['MainBuildingCount']=2;a.sockets['MainEntry']=a.layout['westMainEntry'];a.sockets['RearEntry']=a.layout['northeastRearEntry']
    return a.finish()


if __name__=='__main__':build()
