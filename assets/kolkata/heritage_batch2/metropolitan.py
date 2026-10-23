"""Metropolitan's two street elevations and rounded clock-tower corner."""
from common import *


def commercial_bay():
    g=G()
    for y,w,h,arched in [(3.2,7.4,12,True),(22,5.8,12,False),(41,6.3,12,True)]:
        g.merge(window(w,h,arched,False,'HeritageWhite',balcony=y>3.2).transformed((0,y,0)))
    for x in [-5.2,5.2]:
        g.box((x,31,0),(1,54,1.1),'HeritageWhite')
        for y in [18.5,37.3,55.5]:g.box((x,y,-.5),(1.8,.8,1.9),'HeritageCream')
        for y in [17,35.8,54]:
            g.merge(prism([(x-.8,y),(x+.8,y),(x+1.1,y+1.2),(x,y+2),(x-1.1,y+1.2)],.7,-.6,'HeritageCream'))
    for y in [18.5,37.3,56]:g.box((0,y,-.2),(11,.6,1.1),'HeritageCream')
    # Scrolled arch crest and simplified carved spandrel medallion.
    for sign in [-1,1]:
        g.merge(disk(sign*2.4,54.4,-.75,.55,'HeritageCream',10))
    hood=arch_fill(9.1,14.3,.05,'HeritageDark',.24)
    # A wider shadowed upper arcade, visible around the inset glazed opening.
    g.merge(hood.transformed((0,40,0)))
    g.arch(9.1,9.75,.36,.7,(0,40,-.5),'HeritageCream',14)
    g.box((0,54.8,-.7),(1,1.5,.9),'HeritageCream')
    return g


def cupola(r=7,base=58,large=True):
    g=G();stem=18 if large else 9
    g.lathe([(base,r*1.15),(base+1,r*1.18),(base+2,r),(base+stem-1,r),(base+stem,r*1.2)],24,'HeritageWhite')
    profile=[(base+stem,r*1.2),(base+stem+.7,r*1.22),(base+stem+1.4,r*1.08),
        (base+stem+4,r*.95),(base+stem+7,r*.63),(base+stem+9,r*.12)]
    g.lathe(profile,32,'HeritageOchre')
    for i in range(8):
        t=i*math.tau/8
        for (y,rr),(yy,rrr) in zip(profile[2:],profile[3:]):
            g.beam(((rr+.08)*math.cos(t),y,(rr+.08)*math.sin(t)),((rrr+.08)*math.cos(t),yy,(rrr+.08)*math.sin(t)),.12,'HeritageCream',5)
    finial=[(0,.5),(.8,1.1),(1.7,1.5),(2.8,1.4),(3.8,.8),(4.6,.25),(5.4,0)] if large else [(0,.4),(.8,.8),(2,.6),(3.4,0)]
    g.lathe(finial,12,'HeritageGold',(0,base+stem+9,0))
    return g


def build():
    a=HeritageAsset('metropolitan','Metropolitan Building')
    outline=[(-74,-47),(56,-47),(74,-29),(74,47),(-74,47)]
    a.foundation(150,96,10)
    a.put('Clipped_corner_shell',slab(outline,58,56.8,'HeritageWhite'),section='01_Shell',role='ExteriorShell')
    a.collisions.extend([dict(name='Main_shell',positionStuds=[-9,29.6,0],sizeStuds=[130,56.8,94],yaw=0),
        dict(name='Return_shell',positionStuds=[65,29.6,9],sizeStuds=[18,56.8,76],yaw=0)])
    a.box('Continuous_street_plinth',(0,1.5,0),(150,1.4,96),'HeritageStone','00_Foundation')
    # Clipped cornices wrap the corner rather than protruding into the junction.
    g=G()
    for y in [2.3,19,38,57.3]:
        for dy,expand,h in [(0,.2,.6),(.65,.8,.6),(1.2,1.5,.45)]:
            expanded=[(x+math.copysign(expand,x),z+math.copysign(expand,z)) for x,z in outline]
            g.merge(slab(expanded,y+dy,h,'HeritageCream'))
    a.put('Wrapped_clipped_cornices',g,section='02_Cornices')
    for i in range(11):a.instance('Heritage_commercial_bay',commercial_bay(),(-66+11*i,0,-47.12))
    for i in range(6):a.instance('Heritage_commercial_bay',commercial_bay(),(74.12,0,-20+11*i),-math.pi/2,'04_Returns')
    # The corner tower grows from the facade for its full height, with curved
    # balconies at both upper floors, not a disconnected roof prop.
    center=(61,-34);g=G();g.cylinder((0,30,0),11,57.6,'HeritageWhite',32)
    for y in [2.2,19,38,57.3]:g.lathe([(y,11),(y+.5,11.8),(y+1.2,12.1),(y+1.7,11.7)],32,'HeritageCream')
    a.put('Rounded_corner_tower_base',g,(center[0],0,center[1]),section='05_Clock_Corner')
    for j in range(5):
        angle=-j*math.pi/8
        pos=rotate((0,0,-11.1),angle)
        bay=G()
        for y in [4,22,41]:bay.merge(window(4,11,False,False,'HeritageWhite').transformed((0,y,0)))
        for x in [-2.5,2.5]:bay.box((x,39,0),(.65,34,.7),'HeritageCream')
        a.instance('Rounded_corner_window_bay',bay,(center[0]+pos[0],0,center[1]+pos[2]),angle,'05_Clock_Corner')
    g=G()
    for y in [0]:
        # Open curved balustrade, supported by the projecting cornice below.
        for j in range(25):
            t=-math.pi/2+j*math.pi/24
            g.lathe([(0,.22),(.7,.14),(1.3,.25),(2.4,.2)],6,'HeritageWhite',(12.25*math.cos(t),y,12.25*math.sin(t)))
        g.merge(arc_band(11.9,12.5,y+2.3,.35))
    for y in [21.5,40.5,59]:a.instance('Corner_curved_balcony',g,(center[0],y,center[1]),section='05_Clock_Corner')
    # Roof clock pavilion, lower satellite cupolas, clocks visible on both roads.
    a.put('Principal_clock_cupola',cupola(8,59,True),(61,0,-34),section='06_Cupolas')
    for i in range(8):
        angle=i*math.pi/4;p=rotate((0,0,-8.1),angle)
        face=G();face.merge(arch_fill(4.2,12.6,-.2,'HeritageDark').transformed((0,61,0)))
        face.arch(4.2,10.5,.45,.85,(0,61,-.6),'HeritageCream',12)
        for sign in [-1,1]:face.merge(column(14,.5,'HeritageCream').transformed((sign*2.9,60.2,-.4)))
        face.merge(pediment(6.8,74.7,1.6,-.65,'HeritageWhite'))
        face.lathe([(0,.45),(.35,.7),(1.1,.6),(1.6,.25),(2,.18)],10,'HeritageGold',(0,61.3,-.5))
        face.merge(balustrade(5.8,1.8,1.3,'HeritageWhite').transformed((0,60.5,-.9)))
        a.instance('Clock_pavilion_face',face,(61+p[0],0,-34+p[2]),angle,'06_Cupolas')
    for angle in [0,-math.pi/2]:
        p=rotate((0,81,-10.2),angle)
        outline=[(-3.3,-3),(3.3,-3),(3.8,-1),(3.5,2),(2.4,3.8),(0,5),(-2.4,3.8),(-3.5,2),(-3.8,-1)]
        face=prism(outline,.65,.45,'HeritageWhite');face.merge(clock(2.6))
        for edge_p,edge_q in zip(outline,outline[1:]+outline[:1]):face.beam((*edge_p,-.05),(*edge_q,-.05),.16,'HeritageCream',5)
        for sign in [-1,1]:
            face.merge(disk(sign*.65,4.2,-.15,.45,'HeritageCream',12))
        a.instance('Metropolitan_clock',face,(61+p[0],p[1],-34+p[2]),angle,'06_Cupolas')
    for x,z in [(-65,-38),(65,38)]:
        a.instance('Satellite_cupola',cupola(4.2,59,False),(x,0,z),section='06_Cupolas')
        for angle in [0,math.pi/2,math.pi,math.pi*1.5]:
            p=rotate((0,0,-4.3),angle)
            a.instance('Satellite_niche',window(2.3,5.4,True,False),(x+p[0],60,z+p[2]),angle,'06_Cupolas')
    # Two street pediments and balconies anchor the elevations.
    hero=G();hero.merge(pediment(31,58.4,7,0,'HeritageWhite'))
    for x in [-11,11]:hero.merge(column(33,1,'HeritageWhite').transformed((x,21,-3.1)))
    hero.box((0,20.4,-2),(31,1.2,7),'HeritageCream');hero.box((0,54.7,-2),(31,1.8,7),'HeritageCream')
    hero.merge(balustrade(27,2.6,1.6,'HeritageWhite').transformed((0,39,-5.3)))
    a.instance('Street_pediment_balcony',hero,(-14,0,-47),section='07_Street_Crowns')
    a.instance('Street_pediment_balcony',hero,(74,0,13),-math.pi/2,'07_Street_Crowns')
    rail=balustrade(10.5,3,1.9,'HeritageWhite',end_posts=False)
    for i in range(12):a.instance('Roof_balustrade_module',rail,(-66.75+i*10.5,59.1,-47.3),section='07_Street_Crowns')
    for i in range(6):a.instance('Roof_balustrade_module',rail,(74.3,59.1,-20.75+i*10.5),-math.pi/2,'07_Street_Crowns')
    g=G()
    for x in range(-70,52,11):g.lathe([(0,.6),(.7,.75),(1.7,.4),(2.1,.2)],8,'HeritageCream',(x,62.3,-47.3))
    a.put('Roof_balustrades_and_urns',g,section='07_Street_Crowns')
    rear=G()
    for y in [5,24,43]:rear.merge(window(4.5,9,False,False).transformed((0,y,0)))
    for x in range(-62,64,18):a.instance('Rear_sober_bay',rear,(x,0,47.15),math.pi,'04_Returns')
    for z in [-33,-11,11,33]:a.instance('Rear_sober_bay',rear,(-74.15,0,z),math.pi/2,'04_Returns')
    a.steps('Front_commercial_threshold',29,-47.8,2.2,count=4,x=-14)
    a.night=['Clock faces and upper cupola ribs','Rounded corner balconies','Two street pediments and ground entrances; avoid lighting every bay']
    a.save_live('Metropolitan Building — wrapped commercial facades and clock corner')
    return a,a.finish()
