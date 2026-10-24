"""Sir Stuart Hogg Market: red gabled range, roof sheds and off-axis clock tower."""
from common import *


def market_bay(w=18,large=False):
    opening=22 if large else 12.5
    spring=11 if large else 10
    g=archwall(w,23.5,opening,spring,1.4,'B4_Brick')
    g.merge(profile_frame(opening,spring+opening/2,.85 if large else .45,1.1 if large else .7,False,'B4_Ivory',12,False).transformed((0,0,-.72)))
    g.merge(gable(w-1,23.5,12 if large else 7,1.6))
    if large:
        fan=prism(rounded(9.8,4.9,16),.24,0,'B4_Glass')
        fan.merge(profile_frame(9.8,4.9,.28,.55,False,'B4_Ivory',16).transformed((0,0,-.2)))
        fan.box((0,-.16,-.35),(10.6,.36,1),'B4_Ivory')
        for theta in [math.pi/4,math.pi/2,3*math.pi/4]:
            fan.beam((0,0,-.35),(4.75*math.cos(theta),4.75*math.sin(theta),-.35),.065,'B4_Ivory',4)
        g.merge(fan.transformed((0,27.6,-.95)))
    else:g.merge(window(7,4.5,False,'B4_Glass',1,trim='B4_Ivory').transformed((0,22.7,-.95)))
    for sign in [-1,1]:
        x=sign*(w/2-.5)
        g.box((x,11.8,-.1),(1,23.6,2),'B4_BrickLight')
        for y in [1,18.5,23.2]:g.box((x,y,-.65),(1.7,.5,2.2),'B4_Ivory')
    if large:
        for sign in [-1,1]:
            g.box((sign*12.1,10.7,-1.15),(1.9,21.4,1.5),'B4_Ivory')
            g.box((sign*12.1,.6,-1.25),(3.4,1.2,2.1),'B4_Stone')
            g.box((sign*12.1,11.2,-1.25),(2.8,.8,1.8),'B4_Trim')
        g.box((0,22.9,-1.2),(1.7,2.0,1.6),'B4_Trim')
        g.box((0,24.7,-.9),(w,.6,1.2),'B4_Ivory')
    else:g.box((0,18.4,-.9),(w,.5,.6),'B4_Ivory')
    return g


def clock_ring(r,t,depth,n,mat):
    """Closed continuous annulus; no hidden radial caps between segments."""
    g=G()
    for j in range(n):
        a=j*math.tau/n;b=(j+1)*math.tau/n
        for z in [-depth/2,depth/2]:
            g.polygon([(r*math.cos(a),r*math.sin(a),z),(r*math.cos(b),r*math.sin(b),z),
                ((r+t)*math.cos(b),(r+t)*math.sin(b),z),((r+t)*math.cos(a),(r+t)*math.sin(a),z)],mat)
        for rr in [r,r+t]:
            g.polygon([(rr*math.cos(a),rr*math.sin(a),-depth/2),(rr*math.cos(b),rr*math.sin(b),-depth/2),
                (rr*math.cos(b),rr*math.sin(b),depth/2),(rr*math.cos(a),rr*math.sin(a),depth/2)],mat)
    return g


def market_pinnacle():
    g=G();g.box((0,13,0),(1.5,25,2),'B4_BrickLight')
    g.box((0,25.5,0),(2.6,.6,2.8),'B4_Ivory')
    g.lathe([(0,1.45),(.6,1.3),(6,.18),(6.3,.12)],4,'B4_Ivory',(0,25.8,0))
    g.beam((0,32,0),(0,33.7,0),.09,'B4_Iron',4)
    return g


def clock_face():
    g=prism([(4.25*math.cos(i*math.tau/48),4.25*math.sin(i*math.tau/48)) for i in range(48)],.35,0,'B4_Ivory')
    for r,t,mat in [(3.85,.13,'B4_Iron'),(4.3,.32,'B4_Trim'),(4.68,.18,'B4_Iron')]:g.merge(clock_ring(r,t,.32,48,mat))
    for i in range(60):
        a=i*math.tau/60;r0=3.28 if i%5==0 else 3.55
        g.beam((r0*math.sin(a),r0*math.cos(a),-.24),(3.72*math.sin(a),3.72*math.cos(a),-.24),.07 if i%5 else .12,'B4_Dark',4)
    # Static readable hands, intentionally no runtime clock mechanism.
    for end,r in [((.28,2.45,-.4),.15),((-2.6,-.4,-.42),.10)]:g.beam((0,0,-.4),end,r,'B4_Iron',4)
    g.merge(prism([(0,.4),(.35,0),(0,-.35),(-.35,0)],.35,-.5,'B4_Brass'))
    return g


def tower_face():
    g=G();g.box((0,37.5,0),(21,70,1.2),'B4_Brick')
    for sign in [-1,1]:
        x=sign*9.65
        g.box((x,36,-.6),(1.5,68,1.7),'B4_Ivory')
        g.merge(prism([(x-1.3,28),(x+1.3,28),(x+.75,35),(x-.75,35)],2,-.6,'B4_Ivory'))
        for y in [30,49,54.5,59]:g.box((x,y,-.85),(2.1,.6,2),'B4_Trim')
    for y,w,h,d in [(3,22,1.4,2),(30,24,1.1,3.4),(31.4,25,.7,4),(50,21.8,.8,1.8),(54.5,21.8,.6,1.8)]:
        g.box((0,y,-.5),(w,h,d),'B4_Ivory')
    for x in [-6.2,0,6.2]:
        g.merge(window(3.5,11,True,'B4_Green',0,'B4_Ivory',8).transformed((x,34,-1)))
        for j in range(10):g.box((x,35+j*.66,-1.18),(3,.12,.25),'B4_Green')
    for x in [-5,-2.5,0,2.5,5]:
        g.box((x,52,-.85),(.9,.6,.7),'B4_Ivory')
        g.merge(prism([(x-.5,56),(x+.5,56),(x,57)],.5,-.9,'B4_Ivory'))
    g.merge(gable(21,69,10,1.2))
    g.merge(clock_face().transformed((0,66,-1.15)))
    # Entrance at the tower foot is a visible shallow vestibule.
    g.merge(window(7,15,False,'B4_Green',1).transformed((0,3,-.8)))
    g.box((0,24,-1),(10,1,3),'B4_Ivory')
    for j in range(10):g.box((-10.7+j*2.35,29.1,-1.6),(.7,1.5,1),'B4_Ivory')
    return g


def build():
    a=Landmark('new_market','New Market — Sir Stuart Hogg Market')
    a.scene['MainEntranceWidthStuds']=22
    a.scene['MainEntranceDepthStuds']=18
    a.ground(310,184)
    # Closed outer ranges, no complete market interior.
    a.box('Raised_market_plinth',(-1,1.1,8),(282,1.7,141),'B4_Stone','00_FoundationGrounds')
    for sign in [-1,1]:a.box('Side_range_'+str(sign),(sign*132,11.7,7),(9,20,123),'B4_Brick')
    a.box('Rear_range',(0,11.7,66),(272,20,8),'B4_Brick')
    a.box('Rear_cornice',(0,22.2,66),(275,1.2,10),'B4_Ivory','04_RoofsTower')
    # Repeated low gables across a genuinely long frontage, with major central entrance.
    for i,x in enumerate([-126,-108,-90,-72,-54,-36,-18,0,18,36,54,72,90,108]):
        if x in [-36,-18]:continue
        a.inst('Repeated_gabled_market_bay',market_bay(),(x,1.9,-59),section='02_Frontage')
    a.inst('Main_Hogg_entrance',market_bay(36,True),(-27,1.9,-59),section='02_Frontage')
    for x in [-135,-81,-45,-9,45,99,117]:a.inst('Front_pinnacle',market_pinnacle(),(x,1.9,-59.6),section='02_Frontage')
    # The inner surface lies behind the arcades, preserving six studs of covered depth.
    for x in [-126,-108,-90,-72,-54,0,18,36,54,72,90,108]:
        a.box('Shallow_shop_closure_'+str(x),(x,9.6,-50),(17.3,15.4,.7),'B4_Dark')
        shutters=G()
        for j in range(13):shutters.box((0,1.7+j*.84,-.22),(13,.06,.18),'B4_Iron')
        a.inst('Closed_shop_grille',shutters,(x,1.8,-50.5),section='03_ModularArchitecture')
    a.box('Entry_dark_return',(-27,13.45,-41),(31,23,.6),'B4_Dark')
    for sign in [-1,1]:a.box('Entry_reveal_'+str(sign),(-27+sign*12,12.7,-50),(1.6,21.5,18),'B4_Brick')
    a.box('Entry_vestibule_cover',(-27,24.8,-50),(25.6,.7,18),'B4_Ivory')
    a.put('Entrance_pavilion_roof',pitched_roof(35,18.5,25.1,12.1),(-27,0,-50),section='04_RoofsTower')
    a.put('Entrance_pavilion_rear_closure',prism([(-17.5,21.5),(17.5,21.5),(17.5,25.1),(0,37.15),(-17.5,25.1)],.6,0,'B4_Brick'),
        (-27,0,-41.1),section='04_RoofsTower')
    # Wide iron verandah and pitched entrance canopy copied in spirit from photo 10.
    porch=G()
    # The continuous lower verandah stops at the main entrance pavilion.
    for x,w in [(-91.25,90.5),(64.25,144.5)]:porch.box((x,15.1,-3),(w,.5,9),'B4_Slate')
    for x in range(-132,115,18):
        if -46<x<-8:continue
        porch.cylinder((x,8,-7),.20,12.3,'B4_Iron',8)
        porch.beam((x,13,-7),(x,15,-3.5),.10,'B4_Iron',6)
    for y in [3.4,4.2]:
        for x,w in [(-91.25,90.5),(64.25,144.5)]:porch.box((x,y,-7),(w,.12,.18),'B4_Iron')
    a.put('Continuous_covered_verandah',porch,(0,1.9,-59),section='02_Frontage')
    canopy=pitched_roof(38,20,16.9,6.4,'B4_BrickLight')
    for sign in [-1,1]:
        canopy.beam((sign*19,16.9,-10.2),(0,23.3,-10.2),.23,'B4_Iron',6)
        canopy.beam((sign*18.7,16.9,-10.2),(0,19.2,-10.2),.13,'B4_Iron',6)
        canopy.cylinder((sign*17,8.45,-9.2),.28,16.9,'B4_Iron',8)
        canopy.box((sign*17,.4,-9.2),(1.5,.8,1.5),'B4_Stone')
    canopy.beam((0,16.9,-10.2),(0,23.3,-10.2),.16,'B4_Iron',6)
    a.put('Main_entrance_canopy',canopy,(-27,1.8,-66),section='02_Frontage')
    a.box('Entrance_sign_back',(-27,17.25,-76.45),(25,2.9,.4),'B4_Green','05_FacadeDetails')
    a.text('S. S. HOGG MARKET',(-27,16.9,-76.75),1.8,24,'05_FacadeDetails')
    a.text('SIR STUART HOGG MARKET',(-27,27.2,-60.35),1.65,30,'05_FacadeDetails')
    # Multiple shallow pitched sheds make the aerial footprint read as a market.
    for i in range(5):
        x=-109+i*53.5
        # The former roof stopped seven studs behind the front gables and two
        # studs before the rear range. Carry it into both facade wall thicknesses.
        roof=pitched_roof(54,129.7,21.9,8.3)
        for z in range(-56,60,8):
            for sign in [-1,1]:roof.beam((sign*27,22.05,z),(0,30.35,z),.065,'B4_Iron',4)
        a.inst('Long_ridged_market_roof',roof,(x,0,6.15),section='04_RoofsTower')
        for z in [-58.65,70.15]:
            a.inst('Shed_roof_end_infill',prism([(-27,21.5),(27,21.5),(0,30.15)],.8,0,'B4_Brick'),(x,0,z),section='04_RoofsTower')
    a.box('Rear_eave_flashing',(0,22.1,70.45),(274,.6,1.6),'B4_Slate','04_RoofsTower')
    # True tower mass at the frontage's right end, not on the centreline.
    for side in range(4):
        p=rotate((0,0,-11),side*math.pi/2)
        a.inst('Clock_tower_elevation',tower_face(),(128+p[0],0,-49+p[2]),side*math.pi/2,'04_RoofsTower')
    a.box('Clock_tower_core',(128,39,-49),(19,73,19),'B4_Brick','04_RoofsTower')
    crown=G()
    # Green tapered louvred cap and restrained iron roof crest.
    low=[(-8,75,-8),(8,75,-8),(8,75,8),(-8,75,8)]
    high=[(-4.7,85,-4.7),(4.7,85,-4.7),(4.7,85,4.7),(-4.7,85,4.7)]
    crown.polygon(low,'B4_Green');crown.polygon(list(reversed(high)),'B4_Green')
    for i in range(4):j=(i+1)%4;crown.polygon([low[i],high[i],high[j],low[j]],'B4_Green')
    for side in range(4):
        l=G()
        for j in range(12):
            y=76+j*.65;half=8.05-(y-75)*.33
            l.box((0,y,-half-.12),(half*1.65,.16,.3),'B4_Iron')
        l.merge(railing(10.3,2.5,1.5,'B4_Iron',False).transformed((0,85.5,-5.15)))
        for j in range(8):
            t=j*math.tau/8;tt=(j+1)*math.tau/8
            l.beam((.75*math.cos(t),86.75+.75*math.sin(t),-5.35),(.75*math.cos(tt),86.75+.75*math.sin(tt),-5.35),.055,'B4_Iron',4)
        crown.merge(l.transformed(angle=side*math.pi/2))
    for x,z in [(-4.8,-4.8),(4.8,-4.8),(-4.8,4.8),(4.8,4.8)]:
        crown.lathe([(0,.18),(.65,.23),(3.3,0)],4,'B4_Iron',(x,87.5,z))
    crown.beam((0,86,0),(0,96,0),.09,'B4_Iron',5)
    for x,z in [(-10,-10),(10,-10),(-10,10),(10,10)]:
        crown.lathe([(0,.9),(.6,1),(4.9,.12)],4,'B4_Ivory',(x,74,z))
    a.put('Green_louvred_clock_crown',crown,(128,0,-49),section='04_RoofsTower')
    # Side and rear continuity, with far less detail than the main frontage.
    sidebay=window(8,12,False,'B4_Green',1)
    for sign in [-1,1]:
        for z in [-37,-15,7,29,51]:a.inst('Side_range_arch',sidebay,(sign*136.6,4,z),-sign*math.pi/2,'03_ModularArchitecture')
    for x in range(-120,121,24):a.inst('Rear_range_arch',sidebay,(x,4,70.2),math.pi,'03_ModularArchitecture')
    a.steps('Main_approach',-27,-60,34,1.95,4)
    a.box('Entry_approach_inlay',(-27,.36,-76),(30,.12,28),'B4_Stone','00_FoundationGrounds')
    # Low kerbs, paving joints, bollards and two compact planters; no bazaar.
    g=G()
    for x in range(-140,145,12):g.box((x,.29,-78),(.08,.04,24),'B4_Stone')
    for z in [-86,-78,-70]:g.box((0,.29,z),(290,.04,.08),'B4_Stone')
    for x in [-140,-115,-90,20,45,70,95,145]:
        g.cylinder((x,1.7,-85),.3,2.8,'B4_Iron',8)
        g.cylinder((x,2.8,-85),.36,.35,'B4_Brass',8)
    for sign in [-1,1]:
        g.box((sign*148,1.1,30),(4,1.6,43),'B4_Stone')
        g.box((sign*148,2,30),(3.5,.3,42),'B4_Lawn')
    a.put('Market_forecourt_details',g,section='00_FoundationGrounds')
    for x in [-113,-62,15,69]:
        a.light('Frontage_wash_'+str(x),(x,.5,-73),(x,15,-57),42,2,4200)
        a.light('Gabled_frontage_'+str(x),(x,17.7,-65),(x,30,-57),27,1.5,2200)
    a.light('Entrance_canopy',(-27,15,-67),(-27,7,-62),23,1.6,1100,fixture_=False)
    for dx,dz in [(0,-21),(21,0),(0,21),(-21,0)]:
        a.light('Clock_tower_'+str(dx)+'_'+str(dz),(128+dx,57,-49+dz),(128,75,-49),36,2.3,4400,fixture_=False)
    a.light('Crown_wash',(128,79,-67),(128,87,-49),25,1.3,1800,fixture_=False)
    for x in [-90,65]:a.light('Rear_range_'+str(x),(x,.5,80),(x,23,68),38,1.5,2800)
    for sign in [-1,1]:
        for z in [-28,35]:a.light('Side_range_'+str(sign)+'_'+str(z),(sign*144,.5,z),(sign*136,23,z),37,1.5,2800)
    a.light('Entrance_portal_wash',(-27,1,-79),(-27,23,-59),34,2,3000,fixture_=False)
    # Photo 10's entrance elevation has the clock at the viewer's right. Reflect
    # the original authoring layout with positive transforms and repaired winding;
    # keep the sign lettering readable instead of using negative object scale.
    text_meshes={o.data for o in a.root.all_objects if o.type=='MESH' and '__SIGN_' in o.get('MeshKey','')}
    for mesh in {o.data for o in a.root.all_objects if o.type=='MESH'}-text_meshes:
        for v in mesh.vertices:v.co.x=-v.co.x
        bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update()
    for o in a.root.all_objects:
        o.location.x=-o.location.x
        if o.type=='MESH' and o.data not in text_meshes:o.rotation_euler.z=-o.rotation_euler.z
    lamps={o['StationId']:o for o in a.root.all_objects if o.type=='LIGHT'}
    for spec in a.light_specs:
        o=lamps[spec['name']]
        spec['positionStuds'][0]*=-1;spec['targetStuds'][0]*=-1
        o.location=Vector(bv((spec['positionStuds'][0],spec['positionStuds'][1]+1.4,spec['positionStuds'][2])))
        o.rotation_euler=(Vector(bv(spec['targetStuds']))-o.location).to_track_quat('-Z','Y').to_euler()
    return a.finish()
