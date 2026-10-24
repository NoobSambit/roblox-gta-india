"""Monumental neoclassical museum around a compact, genuinely open quadrangle."""
from common import *


def entablature(w,d,y):
    g=G()
    for yy,h,ex in [(y,.55,.3),(y+.6,.65,.8),(y+1.25,.45,1.6)]:g.box((0,yy,0),(w+ex,h,d+ex),'B4_Trim')
    return g


def museum_bay(w=12):
    g=G()
    for y,h in [(4,12),(23,14)]:g.merge(window(6.3,h,False,'B4_Glass',1,n=6).transformed((0,y,-.1)))
    for sign in [-1,1]:
        g.box((sign*(w/2-.8),20,-.2),(1.35,35,1.1),'B4_Plaster')
        for y in [3,20,39]:g.box((sign*(w/2-.8),y,-.5),(2.2,.6,1.7),'B4_Trim')
    # A shallow recessed panel and continuous string-courses keep the wings restrained.
    for y in [2.8,20,39]:g.box((0,y,-.25),(w,.55,1.2),'B4_Trim')
    g.box((0,17.7,-.4),(7.7,.7,.75),'B4_Ivory')
    return g


def court_bay(pitch=12):
    g=G()
    for y in [2.1,21.9]:
        g.merge(archwall(pitch,18.5,9.3,11.8,1.2,n=8).transformed((0,y,0)))
        g.merge(profile_frame(9.3,16.45,.36,.5,False,'B4_Trim',6,False).transformed((0,y,-.72)))
        # One engaged shaft on the shared left pier; the next bay provides the right.
        shaft=G();shaft.box((0,.3,0),(1.9,.6,1.6),'B4_Trim')
        shaft.lathe([(.6,.65),(1.1,.55),(16.8,.48),(17.4,.7)],6,'B4_Trim')
        shaft.box((0,17.65,0),(1.9,.5,1.8),'B4_Trim')
        g.merge(shaft.transformed((-pitch/2+.25,y,-.52)))
        g.box((0,y+16.5,-.85),(1.1,1.3,.6),'B4_Trim')
    for y in [2,21.3,40.8]:g.box((0,y,-.5),(pitch,.7,2.2),'B4_Trim')
    g.merge(railing(pitch,2.5,2.5).transformed((0,41.2,-.25)))
    return g


def secondary_bay(w=16):
    g=G()
    for y in [4,24]:
        g.merge(prism(rounded(6.3,12,6),.25,-.15,'B4_Glass').transformed((0,y,0)))
        g.merge(profile_frame(6.3,12,.26,.45,False,'B4_Trim',6).transformed((0,y,-.35)))
        g.box((0,y-.3,-.4),(7.5,.4,1),'B4_Trim')
    for y in [2.8,20,39]:g.box((0,y,-.25),(w,.5,1),'B4_Trim')
    return g


def entrance():
    g=G()
    # Three true arches: the centre remains open to the courtyard passage.
    for x in [-12,0,12]:
        g.merge(archwall(12,23,9.8,13,5.3).transformed((x,2.4,0)))
        g.merge(profile_frame(9.8,17.9,.55,.8,False,'B4_Trim',14,False).transformed((x,2.4,-2.8)))
        g.box((x,22.5,-2.9),(1.4,2.2,.8),'B4_Ivory')
    for x in [-18,-6,6,18]:
        g.merge(column(21.6,1.05,capital='ionic',segments=16).transformed((x,2.5,-3.6)))
        g.merge(column(23.5,1.1,capital='ionic',segments=16).transformed((x,27,-3.1)))
    for x in [-12,0,12]:g.merge(window(8.0,18,False,'B4_Glass',1).transformed((x,28,1.4)))
    g.box((0,26,0),(42,2.2,9.6),'B4_Trim')
    g.box((0,50.9,0),(44,1.4,10.5),'B4_Trim')
    for y,w,d in [(25,41,9),(50,43,10),(53,45,11)]:g.merge(entablature(w,d,y))
    # Rectangular attic/parapet, deliberately without a Victoria-style dome or pediment.
    g.box((0,58,1.5),(42,7.3,6),'B4_Plaster')
    for x in [-12,0,12]:
        g.box((x,58,-1.65),(5.4,3,.5),'B4_Glass')
        for dx in [-3.05,3.05]:g.box((x+dx,58,-2),(.45,3.8,.6),'B4_Trim')
        for y in [56,60]:g.box((x,y,-2),(6.6,.4,.6),'B4_Trim')
    for sign in [-1,1]:g.box((sign*20.5,58,-.7),(1.6,8,6),'B4_Ivory')
    g.merge(entablature(46,11,62))
    for x in range(-18,19,3):g.box((x,51,-4.95),(.5,.7,.7),'B4_Trim')
    return g


def build():
    a=Landmark('indian_museum','Indian Museum, Kolkata')
    a.ground(282,218)
    # Outer envelope 248×168; inner court 180×106. Wide galleries are exterior structure.
    for x in [-110,110]:
        a.box('Side_plinth_'+str(x),(x,1.5,16),(29,2.4,142),'B4_Stone','00_FoundationGrounds')
        a.box('Side_volume_'+str(x),(x,21.1,12),(27,37.6,148),'B4_Plaster')
        a.put('Side_entablature_'+str(x),entablature(28,142.5,40),(x,0,15.75),section='04_RoofsCrown')
        a.box('Side_low_roof_'+str(x),(x,42.3,15),(28,.6,140),'B4_Slate','04_RoofsCrown')
    for x in [-72,72]:
        a.box('Street_wing_'+str(x),(x,21,-73),(103,37.8,22),'B4_Plaster')
        a.box('Street_wing_base_'+str(x),(x,1.5,-70),(105,2.4,30),'B4_Stone','00_FoundationGrounds')
        a.put('Street_entablature_'+str(x),entablature(104,29,40),(x,0,-70),section='04_RoofsCrown')
    a.box('Continuous_street_roof',(0,42.3,-70),(248,.6,30),'B4_Slate','04_RoofsCrown')
    a.box('Rear_volume',(0,21.1,72),(193,37.6,28),'B4_Plaster')
    a.box('Rear_plinth',(0,1.5,72),(195,2.4,30),'B4_Stone','00_FoundationGrounds')
    a.put('Rear_entablature',entablature(195,29,40),(0,0,72),section='04_RoofsCrown')
    a.box('Rear_low_roof',(0,42.3,72),(192,.6,26),'B4_Slate','04_RoofsCrown')
    # The centre entry is a genuine covered exterior passage, not a white block.
    a.box('Entrance_floor',(0,1.7,-74),(42,2,35),'B4_Stone','00_FoundationGrounds')
    for sign in [-1,1]:a.box('Central_reveal_'+str(sign),(sign*19.6,27,-72),(2.4,48,31),'B4_Plaster')
    a.box('Centre_upper_envelope',(0,40,-69),(38,26,28),'B4_Plaster')
    a.box('Central_passage_ceiling',(0,25,-72),(39,1.3,32),'B4_Trim')
    a.put('Monumental_triple_arch_portico',entrance(),(0,0,-87),section='02_EntrancePortico')
    a.steps('Main_entrance_steps',0,-90.5,42,2.5,5)
    # Street rhythm and end pavilions; decorative rustication is deliberately sparse.
    for x in list(range(-114,-24,12))+list(range(30,121,12)):
        a.inst('Street_two_register_bay',museum_bay(),(x,0,-84.2),section='05_FacadeDetails')
    for x in [-111,111]:
        pavilion=G();pavilion.box((0,21.2,0),(25,38,3),'B4_Plaster')
        for xx in [-6,6]:pavilion.merge(window(7.4,14,False,'B4_Glass',1).transformed((xx,22,-1.8)))
        for yy in [4,7,10,13,16,19,22,25,28,31,34,37]:
            for sign in [-1,1]:pavilion.box((sign*11.5,yy,-1.8),(2,.35,.8),'B4_Ivory')
        pavilion.merge(railing(24,3.2,1.8).transformed((0,42,-.5)))
        a.inst('Street_corner_pavilion',pavilion,(x,0,-85.3),section='05_FacadeDetails')
    for sign in [-1,1]:
        for z in range(-58,75,16):a.inst('Outer_side_bay',secondary_bay(16),(sign*123.7,0,z),-sign*math.pi/2,'05_FacadeDetails')
    for x in range(-84,85,14):a.inst('Rear_bay',secondary_bay(14),(x,0,86.2),math.pi,'05_FacadeDetails')
    # Two-level open arcades line all four quadrangle elevations. Room closures behind
    # the six-stud passages are intentionally featureless (no galleries/exhibits).
    for side in range(4):
        width=180 if side%2==0 else 106
        depth=106 if side%2==0 else 180
        n=13 if side%2==0 else 7;pitch=width/n;angle=side*math.pi/2
        for i in range(n):
            p=rotate((-width/2+(i+.5)*pitch,0,-depth/2),angle)
            a.inst('Court_arcade_'+str(n),court_bay(pitch),p,angle+math.pi,'03_ModularArchitecture')
        floor=G()
        for y in [2.0,21.45,40.6]:floor.box((0,y,3.2),(width,.65,7.5),'B4_Trim')
        p=rotate((0,0,-depth/2),angle)
        a.put('Gallery_floor_'+str(side),floor,p,angle+math.pi,section='03_ModularArchitecture')
    # Muted backing and dark openings make the covered galleries read as depth,
    # rather than white arch outlines against equally white room closures.
    for x in [-55,55]:a.box('Front_court_backing_'+str(x),(x,21.1,-61.75),(70,37.6,.3),'B4_MuseumRecess')
    a.box('Rear_court_backing',(0,21.1,57.8),(180,37.6,.3),'B4_MuseumRecess')
    for sign in [-1,1]:a.box('Side_court_backing_'+str(sign),(sign*96.25,21.1,0),(.3,37.6,106),'B4_MuseumRecess')
    for side in range(4):
        width=180 if side%2==0 else 106;depth=106 if side%2==0 else 180
        n=13 if side%2==0 else 7;angle=side*math.pi/2
        offset=8.45 if side==0 else 4.5 if side==2 else 5.95
        for i in range(n):
            xx=-width/2+(i+.5)*width/n
            if side==0 and abs(xx)<20:continue
            for y in [3.0,23.0]:
                panel=G();panel.box((0,6.25,0),(5.8,12.5,.25),'B4_Green')
                if y<10:panel.box((0,6.25,-.17),(.14,12.5,.18),'B4_MuseumBand')
                p=rotate((xx,y,-depth/2-offset),angle)
                a.inst('Court_door' if y<10 else 'Court_upper_inset',panel,p,angle+math.pi,'03_ModularArchitecture')
    # Upper parapet and repeated small attic lights from the court photo.
    for side in range(4):
        width=196 if side%2==0 else 122;depth=122 if side%2==0 else 196
        g=G()
        for i in range(round(width/6)):
            x=-width/2+(i+.5)*width/round(width/6)
            g.box((x,44.8,0),(4.2,5,1.5),'B4_Plaster')
            g.box((x,45,-.8),(1.9,2.6,.15),'B4_Dark')
        g.box((0,47.5,0),(width+1,.65,2.5),'B4_Trim')
        for i in range(round(width/20)+1):
            x=-width/2+i*width/round(width/20)
            g.lathe([(0,.65),(.4,.8),(1.1,.4),(1.8,0)],8,'B4_Trim',(x,48,0))
        p=rotate((0,0,-depth/2),side*math.pi/2)
        a.put('Court_attic_'+str(side),g,p,side*math.pi/2,section='04_RoofsCrown')
    # Garden court: central octagonal pool, cross paths and four compact lawns.
    for x in [-46,46]:
        for z in [-26,26]:a.lawn('Court_lawn_'+str(x)+'_'+str(z),x,z,76,38)
    pool=G();pool.lathe([(0,10.5),(.6,11),(.9,10.5)],8,'B4_Stone',(0,.3,0))
    pool.cylinder((0,1.25,0),9.4,.16,'B4_Water',8)
    pool.lathe([(0,1.5),(.5,1.8),(2.2,.6),(3.2,.8)],10,'B4_Trim',(0,1.3,0))
    a.put('Courtyard_pool',pool,section='00_FoundationGrounds')
    a.boundary(273,209,48)
    for sign in [-1,1]:
        a.lawn('Entrance_lawn_'+str(sign),sign*86,-96,63,13)
        for z in [-31,36]:a.inst('Compact_compound_tree',tree(),(sign*132,0,z),section='00_FoundationGrounds')
    # Sparse bollards mark the museum forecourt, without giant estate landscaping.
    g=G()
    for x in [-30,30]:
        g.box((x,1.65,-100),(1,3,1),'B4_Iron');g.box((x,2.9,-100),(1.1,.2,1.1),'B4_Brass')
    a.put('Entrance_bollards',g,section='00_FoundationGrounds')
    for x in [-108,-68,-32,32,68,108]:a.light('Street_uplight_'+str(x),(x,.4,-96),(x,34,-83),48,2,5500)
    for sign in [-1,1]:
        a.light('Portico_giant_column_'+str(sign),(sign*15,25,-95),(sign*12,49,-87),32,1.8,1800,fixture_=False)
        a.light('Side_wash_'+str(sign),(sign*132,.4,5),(sign*124,35,5),46,1.6,4800)
    for x,z in [(-68,-44),(68,-44),(-68,44),(68,44)]:
        a.light('Court_arcade_'+str(x)+'_'+str(z),(x,.45,z),(x,30,math.copysign(53,z)),40,1.5,2500)
    a.light('Entrance_vault',(0,22,-77),(0,4,-85),25,1.5,1200,fixture_=False)
    for x in [-75,0,75]:a.light('Rear_institution_wash_'+str(x),(x,.4,100),(x,35,86),44,1.6,3400)
    palette={'B4_Plaster':'B4_MuseumWall','B4_Trim':'B4_MuseumTrim','B4_Stone':'B4_MuseumStone','B4_Ivory':'B4_MuseumBand','B4_Slate':'B4_MuseumRoof'}
    for mesh in {o.data for o in a.root.all_objects if o.type=='MESH'}:
        for i,mat in enumerate(mesh.materials):
            role=mat.name.replace('KOL_T1_','')
            if role in palette:mesh.materials[i]=pipeline.material(palette[role])
    return a.finish()
