"""Kolkata St. Paul's: long Indo-Gothic nave, transepts, square pinnacled crossing."""
from common import *


def pinnacle(h=10,r=.8):
    g=G();g.box((0,.3,0),(r*2.5,.6,r*2.5),'B4_Trim')
    g.lathe([(.4,r),(.9,r*1.15),(h*.38,r*.85),(h*.45,r*1.1),(h*.5,r*.7),(h-.3,.08)],4,'B4_Stone')
    for sign in [-1,1]:
        g.beam((sign*r*.7,h*.55,0),(sign*r*1.15,h*.6,0),.09,'B4_Trim',4)
        g.beam((0,h*.55,sign*r*.7),(0,h*.6,sign*r*1.15),.09,'B4_Trim',4)
    g.beam((0,h-.4,0),(0,h+.6,0),.07,'B4_Iron',4)
    return g


def tracery_window(w=7.2,h=22,lights=2,detail=True):
    g=window(w,h,True,'B4_Glass',0,n=8 if detail else 4)
    spring=h-math.sqrt(3)*w/2
    for i in range(lights):
        x=-w/2+(i+.5)*w/lights
        ww=w/lights-.32;hh=spring+ww*.5
        if detail:g.merge(profile_frame(ww,hh,.12,.25,True,'B4_Trim',5).transformed((x,.35,-.42)))
        else:
            g.box((x-ww/2,spring*.5,-.4),(.13,spring,.2),'B4_Trim')
            g.beam((x-ww/2,spring,-.4),(x,hh,-.4),.065,'B4_Trim',4)
            g.beam((x+ww/2,spring,-.4),(x,hh,-.4),.065,'B4_Trim',4)
        for yy in [2.5,5.5,8.5,11.5]:
            if yy<spring:g.box((x,yy,-.38),(ww,.07,.15),'B4_Trim')
    # Small circular/quatrefoil-like rose in the pointed head, with actual trim depth.
    rr=w*.145;cy=spring+w*.40
    g.merge(ring(rr,.10,.24,12 if detail else 6,'B4_Trim').transformed((0,cy,-.42)))
    for sign in [-1,1]:g.beam((0,cy-rr,-.4),(sign*rr*.7,cy+rr*.7,-.4),.07,'B4_Trim',4)
    # Hood mould and stops give the visible stone arch a second order.
    if detail:g.merge(profile_frame(w+.9,h+.7,.17,.32,True,'B4_Stone',8,False).transformed((0,0,-.25)))
    return g


def buttress(h=44):
    g=G()
    # Three stepped stages and sloped weatherings, more faithful than a flat pilaster.
    for y,hh,w,d in [(7.5,12,2.4,3.6),(22,17,2,2.8),(36,12,1.55,1.9)]:
        g.box((0,y,0),(w,hh,d),'B4_Stone')
        g.box((0,y+hh/2-.1,-.1),(w+.4,.55,d+.3),'B4_Trim')
    for y,d in [(14,3.6),(30.5,2.8),(42.3,1.9)]:
        g.merge(prism([(-1.4,y),(1.4,y),(1,y+1.4),(-1,y+1.4)],d,-.1,'B4_Trim'))
    g.merge(prism(pointed(.8,4,3),.16,-1.12,'B4_GothicRecess').transformed((0,33.5,0)))
    g.box((0,34.8,-1.25),(.11,2.6,.18),'B4_Trim')
    g.merge(pinnacle(9,.7).transformed((0,43.7,0)))
    return g


def nave_bay(w=15):
    g=G();g.merge(tracery_window(7.2,22,detail=False).transformed((0,13,-.4)))
    # The original has a low repeated blind panel register beneath the Gothic windows.
    for x in [-3.3,0,3.3]:
        g.box((x,6.4,-.15),(2.7,7.2,.2),'B4_Plaster')
        for dx in [-1.4,1.4]:g.box((x+dx,6.4,-.38),(.18,7.5,.35),'B4_Trim')
    for y in [2.3,10.8,39.7,43.5]:g.box((0,y,-.2),(w,.45,.8),'B4_Trim')
    # Crenellated parapet, recessed tiny pointed blindwork and repeated finials.
    for x in [-5.7,-2.85,0,2.85,5.7]:
        g.box((x,45.8,0),(1.75,2,.95),'B4_Stone')
    g.box((0,44.3,0),(w,.65,1.1),'B4_Trim')
    return g


def large_gable(w=47,base=44,rise=15):
    g=gable(w,base,rise,2,'B4_Stone','B4_Trim')
    for sign in [-1,1]:
        for j in range(1,9):
            t=j/9;x=sign*w/2*(1-t);y=base+rise*t
            g.box((x,y+.65,-.8),(1.15,1.7,1.4),'B4_Stone')
    g.merge(pinnacle(8,.65).transformed((0,base+rise,0)))
    return g


def tower_face():
    g=G();g.box((0,71,0),(25,46,1.4),'B4_Stone')
    # Paired tall belfry louvres, clock dial, panelled lower tower and tiered bands.
    for x in [-5.3,5.3]:
        g.merge(window(6.2,25,True,'B4_Slate',1,n=5).transformed((x,61,-.9)))
        for j in range(16):g.box((x,62+j*1.05,-1.22),(5.4,.27,.25),'B4_Slate')
        g.merge(profile_frame(4.8,8.5,.18,.4,True,'B4_Trim',7).transformed((x,49,-.85)))
    g.merge(prism([(2.6*math.cos(i*math.tau/32),2.6*math.sin(i*math.tau/32)) for i in range(32)],.2,-1.15,'B4_Ivory').transformed((0,87,0)))
    g.merge(ring(2.6,.18,.3,32,'B4_Iron').transformed((0,87,-1.32)))
    for i in range(12):
        t=i*math.tau/12
        g.beam((1.9*math.sin(t),87+1.9*math.cos(t),-1.5),(2.3*math.sin(t),87+2.3*math.cos(t),-1.5),.075,'B4_Iron',4)
    g.beam((0,87,-1.5),(.2,88.7,-1.5),.10,'B4_Iron',5);g.beam((0,87,-1.5),(-1.4,86.4,-1.5),.08,'B4_Iron',4)
    for y in [48,59,91.5,94]:g.box((0,y,-.25),(26,.6,2.1),'B4_Trim')
    for x in [-10.3,-7.3,-4.3,-1.3,1.7,4.7,7.7,10.7]:g.box((x,96,-.1),(1.7,3,1.5),'B4_Stone')
    for sign in [-1,1]:
        for x in [sign*11.7,sign*9.9]:
            g.box((x,71,-.8),(1.1,45,1.8),'B4_Trim')
            for y in [59,74,88]:g.box((x,y,-1),(1.5,.65,2),'B4_Stone')
    return g


def build():
    a=Landmark('st_pauls',"St. Paul's Cathedral, Kolkata")
    a.ground(156,252)
    a.box('Nave_plinth',(0,1.4,0),(54,2.4,194),'B4_Stone','00_FoundationGrounds')
    # Opaque exterior shell without furnishings; separate nave roof preserves future access.
    for sign in [-1,1]:a.box('Nave_wall_'+str(sign),(sign*25,23,0),(2,42,190),'B4_Stone')
    a.box('West_wall',(0,23,-95),(48,42,2),'B4_Stone')
    a.box('East_wall',(0,23,95),(48,42,2),'B4_Stone')
    a.put('Nave_pitched_roof',pitched_roof(50,191,43.5,10.5),section='04_RoofsTower')
    for sign in [-1,1]:
        for z in range(-87,94,15):
            if 23<z<58:continue
            a.inst('Nave_pointed_tracery_bay',nave_bay(),(sign*26.1,0,z),-sign*math.pi/2,'03_ModularArchitecture')
        for z in range(-95,96,15):
            if 23<z<58:continue
            a.inst('Stepped_nave_buttress',buttress(),(sign*27,0,z),-sign*math.pi/2,'03_ModularArchitecture')
    # The pronounced transept and off-centre crossing tower are essential to the side silhouette.
    a.box('Transept_plinth',(0,1.4,40),(99,2.4,42),'B4_Stone','00_FoundationGrounds')
    for sign in [-1,1]:
        a.box('Transept_outer_end_'+str(sign),(sign*48,23,40),(2,42,40),'B4_Stone')
        for z in [20.6,59.4]:a.box('Transept_side_'+str(sign)+'_'+str(z),(sign*35,23,z),(25,42,1.5),'B4_Stone')
        # Rotated roof runs across the nave, rather than parallel to it.
        a.put('Transept_roof_'+str(sign),pitched_roof(40,24,43.5,13),(sign*36,0,40),math.pi/2,section='04_RoofsTower')
        # The tall transept ridge ends above the sloping nave roof. Close that
        # exposed triangular end instead of leaving a view into an empty shell.
        a.inst('Transept_inner_gable',prism([(-20,43.2),(20,43.2),(0,56.55)],.6,0,'B4_Stone'),
            (sign*24,0,40),math.pi/2,'04_RoofsTower')
        end=G();end.merge(large_gable(40,44,13))
        end.merge(tracery_window(12,25,3).transformed((0,12,-1.1)))
        for x in [-13.5,13.5]:end.merge(tracery_window(6,21,2,False).transformed((x,12,-1.1)))
        end.merge(ring(3.1,.32,.55,32,'B4_Trim').transformed((0,47,-1.3)))
        end.merge(prism([(2.9*math.cos(i*math.tau/24),2.9*math.sin(i*math.tau/24)) for i in range(24)],.2,-1.1,'B4_Glass').transformed((0,47,0)))
        for x in [-19,19]:end.merge(buttress().transformed((x,0,0)))
        a.put('Transept_Gothic_elevation_'+str(sign),end,(sign*49,0,40),-sign*math.pi/2,section='05_FacadeDetails')
    # Large west and east end windows; north porch remains the main shallow entry.
    for z,angle in [(-96.2,0),(96.2,math.pi)]:
        end=G();end.merge(large_gable())
        end.merge(tracery_window(17.5,29,3).transformed((0,11,-1)))
        for x in [-17,17]:end.merge(tracery_window(6,21,2,False).transformed((x,12,-1)))
        for x in [-23,23]:end.merge(buttress().transformed((x,0,0)))
        a.put('Nave_end_'+str(z),end,(0,0,z),angle,section='05_FacadeDetails')
    # Main side porch: real pointed portal, two returned walls and covered depth.
    porch=G()
    # Concave pointed doorway wall.
    opening=pointed(7.6,11,10)
    outline=[(-7,15),(7,15),(7,0)]+list(reversed(opening[1:]))+[(-7,0)]
    porch.merge(prism(outline,1,0,'B4_Stone'))
    porch.merge(profile_frame(7.6,11,.55,.8,True,'B4_Trim',10,False).transformed((0,0,-.6)))
    porch.merge(large_gable(15,15,4))
    for sign in [-1,1]:porch.box((sign*6.5,7.5,5),(1,15,10),'B4_Stone')
    porch.merge(pitched_roof(15,11,15,4).transformed((0,0,4)))
    porch.box((0,7.5,9),(11,15,.4),'B4_Dark')
    for x in [-6.5,6.5]:porch.merge(pinnacle(5,.35).transformed((x,15,0)))
    a.put('North_entrance_porch',porch,(36,2,-59),-math.pi/2,section='02_EntrancePorches')
    steps=G()
    for i in range(4):steps.box((0,(i+1)*.25,-(4-i)*1.2),(12,(i+1)*.5,1.23),'B4_Stone')
    a.put('North_porch_steps',steps,(37,0,-59),-math.pi/2,section='00_FoundationGrounds')
    # Square tower with pinnacles (photo-led present-day silhouette, no invented needle spire).
    a.box('Crossing_tower_core',(0,70,40),(23,44,23),'B4_Stone','04_RoofsTower')
    for side in range(4):
        p=rotate((0,0,-12.1),side*math.pi/2)
        a.inst('Crossing_tower_elevation',tower_face(),(p[0],0,40+p[2]),side*math.pi/2,'04_RoofsTower')
    a.box('Tower_roof',(0,94.4,40),(24,.6,24),'B4_Slate','04_RoofsTower')
    p=G()
    p.box((0,70,0),(2.7,46,2.7),'B4_Stone')
    for y in [59,74,89,96]:p.box((0,y,0),(3.3,.7,3.3),'B4_Trim')
    p.merge(pinnacle(16,1.25).transformed((0,96.5,0)))
    for height,radius in [(104.5,.95),(108.5,.55)]:
        for side in range(4):
            leaf=prism([(-.32,height),(.32,height),(0,height+1.15)],.35,-radius-.25,'B4_Trim')
            p.merge(leaf.transformed(angle=side*math.pi/2))
    for x in [-12,12]:
        for z in [28,52]:a.inst('Tower_corner_pinnacle',p,(x,0,z),section='04_RoofsTower')
    # Calm, finished compound: a direct west path and side connection to the porch.
    for sign in [-1,1]:
        a.lawn('West_lawn_'+str(sign),sign*42,-108,53,20)
        a.lawn('Side_lawn_'+str(sign),sign*57,-20,25,119)
        a.lawn('East_lawn_'+str(sign),sign*42,109,53,19)
        for z in [-101,90]:a.inst('Compound_tree',tree(),(sign*64,0,z),section='00_FoundationGrounds')
    # Ensure the entrance path cuts the right-hand lawn instead of dead-ending in grass.
    a.box('Side_porch_path',(52,.55,-59),(43,.2,10),'B4_Paving','00_FoundationGrounds')
    a.box('West_forecourt_cross_path',(0,.55,-111),(91,.2,8),'B4_Paving','00_FoundationGrounds')
    a.boundary(148,244,18)
    bench=G()
    for x in [-2.1,2.1]:bench.box((x,1.1,0),(.6,1.8,1.8),'B4_Stone')
    bench.box((0,2.1,0),(6,.4,2.2),'B4_Wood');bench.box((0,3,1),(6,1.5,.3),'B4_Wood')
    for sign in [-1,1]:a.inst('Garden_bench',bench,(sign*49,0,-107),section='00_FoundationGrounds')
    for sign in [-1,1]:
        for z in [-79,-24,79]:a.light('Nave_wash_'+str(sign)+'_'+str(z),(sign*36,.4,z),(sign*26,35,z),42,1.7,3400)
        a.light('Transept_wash_'+str(sign),(sign*61,.4,40),(sign*49,49,40),58,2.1,5300)
    a.light('West_window',(0,.4,-110),(0,42,-96),54,2.1,4800)
    a.light('East_window',(0,.4,110),(0,40,96),54,1.8,4000)
    for sign in [-1,1]:a.light('Tower_pinnacle_'+str(sign),(sign*28,54,40),(sign*8,103,40),60,2,4200,fixture_=False)
    a.light('Tower_front',(0,53,17),(0,90,28),48,1.8,3200,fixture_=False)
    a.light('Porch_entry',(43,13,-59),(37,3,-59),18,1.2,800,fixture_=False)
    return a.finish()
