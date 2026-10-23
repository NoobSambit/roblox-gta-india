"""Original reference-led Dakshineshwar kit, staged for live Blender authoring."""
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Vector

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'tier1'))
import pipeline
from pipeline import Asset,Geometry,ellipse,panel,palm_geometry
from geometry import rotate,bv
from landmark_refinements import skin,slab

pipeline.COLORS.update(TempleCream='E5D3A4',TempleRed='8E3839',TempleRoof='AF6861',
    TempleStone='AC927A',TemplePaving='BE9481',TempleJoint='9D7668',
    TempleGold='C6A354',TempleSilver='B7B7AD',TempleDark='211E29',
    KaliBlue='35466E',KaliRed='B3383E',KaliGold='D6AB45',KaliWhite='E5DDD1',
    TempleGlow='F4C777',GarlandGreen='4A7050')
A=None


def frame(target=(0,15,65),eye=(160,340,210)):
    bpy.context.view_layer.update()
    areas=bpy.context.screen.areas if bpy.context.screen else [a for s in bpy.data.screens for a in s.areas]
    for area in areas:
        if area.type!='VIEW_3D':continue
        sp=area.spaces.active;sp.clip_start=1;sp.clip_end=4000
        sp.shading.type='SOLID';sp.shading.color_type='MATERIAL'
        sp.overlay.show_floor=False;sp.overlay.show_axis_x=False;sp.overlay.show_axis_y=False
        sp.overlay.show_extras=False
        region=next((r for r in area.regions if r.type=='WINDOW'),None)
        sp.region_3d.view_rotation=(Vector(eye)-Vector(target)).to_track_quat('Z','Y')
        sp.region_3d.view_location=target;sp.region_3d.view_distance=(Vector(eye)-Vector(target)).length
        sp.region_3d.view_perspective='ORTHO'
        area.tag_redraw()


def save_stage(label):
    A.scene['ProductionStage']=label;frame()
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'KOL_T1_DAKSHINESHWAR.blend'),compress=True)
    print('LIVE STAGE: '+label,flush=True)


def prism(points,depth,role):
    g=Geometry();front=[(x,y,-depth/2) for x,y in points];back=[(x,y,depth/2) for x,y in points]
    g.polygon(front,role);g.polygon(list(reversed(back)),role)
    for i in range(len(points)):
        j=(i+1)%len(points);g.polygon([front[i],back[i],back[j],front[j]],role)
    return g


def disk(x,y,z,r,role,segments=10):
    return prism([(x+r*math.cos(i*math.tau/segments),y+r*math.sin(i*math.tau/segments)) for i in range(segments)],.24,role).transformed((0,0,z))


def stairs(g,width,top_z,top_y,base_y,count,tread,x=0,role='TempleStone'):
    for i in range(1,count+1):
        top=base_y+(top_y-base_y)*i/count
        g.box((x,(base_y+top)/2,top_z-(count-i+.5)*tread),(width,top-base_y,tread+.025),role)


def arch_bay(width=16,clear=10.4,spring=13.2,height=36):
    g=Geometry();radius=clear/2;post=(width-clear)/2
    for sign in [-1,1]:
        g.box((sign*(clear/2+post/2),height/2,0),(post,height,2.4),'TempleCream')
        g.cylinder((sign*(clear/2+.65),spring/2,-1.6),.53,spring,'TempleCream',8)
        for yy in [.4,spring-.3]:g.box((sign*(clear/2+.65),yy,-1.6),(1.65,.7,1.4),'TempleRed')
    arc=[(radius*math.cos(math.pi-i*math.pi/12),spring+radius*math.sin(math.pi-i*math.pi/12)) for i in range(13)]
    g.merge(prism(arc+[(radius,height),(-radius,height)],2.4,'TempleCream'))
    g.arch(clear,spring,.62,.65,pos=(0,0,-1.6),mat='TempleRed',segments=12)
    # A broad medallion and panel lines carry ornament without carved texture.
    g.merge(disk(0,min(height-2,spring+radius+3),-1.25,.9,'TempleRed'))
    for xx in [-width/2+.45,width/2-.45]:g.box((xx,height*.62,-1.35),(.22,height*.7,.22),'TempleRed')
    g.box((0,height-.8,-1.35),(width-.8,.24,.32),'TempleRed')
    return g


def roof_height(x,z,w,d,base,rise):
    return base+rise*(2-(2*x/w)**2-(2*z/d)**2)


def bengal_roof(w,d,base,rise,n=12,role='TempleCream'):
    grid=[[(x,roof_height(x,z,w,d,base,rise),z) for x in [-w/2+w*i/n for i in range(n+1)]] for z in [-d/2+d*j/n for j in range(n+1)]]
    return skin(grid,(0,-1.15,0),role)


def cornice(w,d,base,rise,detail=True):
    g=Geometry()
    for side in range(4):
        width=w if side%2==0 else d;depth=d if side%2==0 else w;angle=side*math.pi/2
        # Continuous masonry follows the roof curve and overlaps the flat
        # header below. Decorative blocks and trim now have solid backing.
        steps=24 if detail else 8
        curve=[(-width/2+width*j/steps,base+rise*(1-(2*(-width/2+width*j/steps)/width)**2)+.15) for j in range(steps+1)]
        band_bottom=base-(7.5 if detail else 3.5)
        band=prism([(-width/2,band_bottom),(width/2,band_bottom)]+list(reversed(curve)),3.6,'TempleCream')
        g.merge(band.transformed(rotate((0,0,-depth/2+1.5),angle),angle))
        segments=16 if detail else 8
        for j in range(segments):
            x=-width/2+width*j/segments;xx=-width/2+width*(j+1)/segments
            y=base+rise*(1-(2*x/width)**2);yy=base+rise*(1-(2*xx/width)**2)
            points=[(x,y,-depth/2),(xx,yy,-depth/2)]
            bands=[(0,.48,'TempleRed'),(-1,.35,'TempleCream'),(-2,.3,'TempleRed')] if detail else [(0,.32,'TempleCream')]
            for dy,r,role in bands:
                p=rotate((x,y+dy,-depth/2),angle);q=rotate((xx,yy+dy,-depth/2),angle);g.beam(p,q,r,role,4)
        if detail:
            for j in range(1,12):
                x=-width/2+width*j/12;y=base+rise*(1-(2*x/width)**2)
                for dy,h in [(-4,2.2),(-6.5,.85)]:
                    # Wall front is -depth/2-.3. Embed the back of each red
                    # panel and project its face .45, avoiding coplanar skins.
                    p=rotate((x,y+dy,-depth/2-.45),angle);g.box(p,(1.1,h,.6),'TempleRed',angle)
                    for dx in [-.75,.75]:
                        p=rotate((x+dx,y+dy,-depth/2-.7),angle);g.box(p,(.28,h+.65,.5),'TempleCream',angle)
                    for dh in [-h/2-.16,h/2+.16]:
                        p=rotate((x,y+dy+dh,-depth/2-.7),angle);g.box(p,(1.8,.3,.5),'TempleCream',angle)
    return g


def roof_balustrade(w,d,base,rise):
    """Follow the curved roof with seated posts and a continuous red rail."""
    g=Geometry()
    for side in range(4):
        width=w if side%2==0 else d;depth=d if side%2==0 else w;angle=side*math.pi/2
        n=16;edge=-depth/2+1.5
        for j in range(n):
            x=-width/2+1.5+(width-3)*j/n
            foot=roof_height(x,edge,width,depth,base,rise)
            p=rotate((x,foot+1,edge),angle);g.box(p,(.65,2.2,.65),'TempleCream',angle)
            if j<n:
                xx=-width/2+1.5+(width-3)*(j+1)/n
                yy=roof_height(xx,edge,width,depth,base,rise)
                for dy,r,role in [(2,.28,'TempleRed'),(.25,.18,'TempleCream')]:
                    g.beam(rotate((x,foot+dy,edge),angle),rotate((xx,yy+dy,edge),angle),r,role,5)
    return g


def squared_profile(rings,role):
    g=Geometry();loops=[]
    for y,rx,rz in rings:
        loops.append([(-rx,y,-.65*rz),(-.65*rx,y,-rz),(.65*rx,y,-rz),(rx,y,-.65*rz),(rx,y,.65*rz),(.65*rx,y,rz),(-.65*rx,y,rz),(-rx,y,.65*rz)])
    for a,b in zip(loops,loops[1:]):
        for i in range(8):
            j=(i+1)%8;g.polygon([a[i],b[i],b[j],a[j]],role)
    g.polygon(loops[0],role);g.polygon(list(reversed(loops[-1])),role)
    return g


def finial(height=5,r=.85):
    return _finial_geometry(height,r)


def _finial_geometry(height,r):
    g=Geometry();g.lathe([(0,r),(.12*height,r*1.1),(.26*height,r*.55),(.35*height,r*.95),(.49*height,r*.4),(.61*height,r*.7),(.76*height,r*.3),(height,.07)],8,'TempleRed')
    return g


def ratna(radius,stem,dome):
    g=squared_profile([(0,radius,radius),(1,radius*1.04,radius*1.04),(stem-.8,radius,radius),(stem,radius*1.08,radius*1.08)],'TempleCream')
    # Integrated stepped ribs maintain a single clean spire shell.
    rings=[]
    for i in range(10):
        t=i/10;r=radius*(1-t*t)*1.06
        rings.extend([(stem+dome*t,r,r),(stem+dome*(t+.045),r*1.025,r*1.025)])
    rings.append((stem+dome,radius*.08,radius*.08));g.merge(squared_profile(rings,'TempleRoof'))
    for y in [1,stem-1]:g.merge(squared_profile([(y-.25,radius*1.055,radius*1.055),(y+.25,radius*1.055,radius*1.055)],'TempleRed'))
    for side in range(4):
        angle=side*math.pi/2;mod=Geometry();width=radius*.48;spring=stem*.53
        mod.arch(width,spring,.28,.35,pos=(0,2,-radius-.18),mat='TempleRed',segments=7)
        panel(mod,0,2+spring*.48,-radius-.25,width*.62,spring*.9,'TempleDark')
        g.merge(mod.transformed(angle=angle))
    g.merge(finial(5 if radius<7 else 7,radius*.15).transformed((0,stem+dome,0)))
    return g


def begin():
    global A
    old=bpy.data.scenes.get('KOL_T1_DAKSHINESHWAR')
    if old:old.name='Dakshineshwar_previous_stage'
    A=Asset('dakshineshwar','Dakshineshwar Kali temple complex and attached ghat',folder=HERE,export_dir=ROOT/'exports/dakshineshwar')
    g=Geometry();g.box((0,-.175,0),(416,1.65,172),'TempleStone')
    g.box((0,.66,0),(414,.04,170),'TempleJoint')
    # True separated paving blocks expose recessed joints. No overlapping
    # coplanar cap or thin grid overlay is used anywhere on the courtyard.
    for ix in range(13):
        for iz in range(6):g.box((-192+ix*32,.72,-70+iz*28),(31.8,.16,27.8),'TemplePaving')
    A.put('Connected_courtyard',g,section='01_Campus',role='Ground')
    g=Geometry();g.box((0,3.25,22),(92,4.9,82),'TempleRed');g.box((0,5.85,22),(95,.4,85),'TempleCream')
    stairs(g,32,-20.4,6.05,.8,14,1.5)
    for x in [-47,47]:g.box((x,4.6,22),(1,2.3,84),'TempleCream')
    A.put('Main_raised_plinth_and_stairs',g,section='02_Main_Platform',role='Walkable')
    for sign in [-1,1]:
        g=Geometry();g.box((sign*121,2.025,30),(147,2.45,36),'TempleRed');g.box((sign*121,3.25,30),(149,.3,38),'TempleCream')
        stairs(g,145,11,3.4,.8,7,1.3,x=sign*121)
        A.put('Shiva_wing_plinth_'+str(sign),g,section='02_Main_Platform',role='Walkable')
    save_stage('Connected campus, main platform, two six-shrine wing platforms')
    return A


def main_temple():
    a=A;assert a
    g=Geometry()
    for x in [-40.5,40.5]:g.box((x,22.05,22),(2.5,32,72),'TempleCream')
    g.box((0,22.05,57),(81,32,2),'TempleCream')
    # Only the central entry reaches the real, limited shrine chamber.
    for x in [-26,26]:g.box((x,21,-7),(28,30,1.5),'TempleDark')
    g.box((0,37,21),(78,1,69),'TempleCream')
    a.put('Main_ground_shell',g,section='03_Main_Envelope',role='ShellWalls')
    bay=arch_bay(height=32)
    for x in [-32,-16,0,16,32]:a.put('Main_open_arch_bay',bay if 'Main_open_arch_bay' not in a.cache else None,(x,6.05,-14),section='04_Main_Arcades')
    # Side and rear bays are shallow architectural recesses, with opaque backs.
    for side in [1,2,3]:
        width=72 if side%2 else 80;depth=80 if side%2 else 72;angle=side*math.pi/2
        for i in range(4 if side%2 else 5):
            count=4 if side%2 else 5;x=-width/2+(i+.5)*width/count;p=rotate((x,6.05,-depth/2-1.4),angle)
            mod=arch_bay(width=width/count,clear=10.4,height=32)
            panel(mod,0,9,-.1,10.2,17.5,'TempleDark')
            key='Main_return_bay_'+str(side%2)
            a.put(key,mod if key not in a.cache else None,(p[0],p[1],p[2]+22),angle,section='04_Main_Arcades')
    # Two curved cornice/roof stages support the 4 + 4 + 1 ratna hierarchy.
    a.put('Lower_Bengali_roof',bengal_roof(86,76,41,9),pos=(0,0,22),section='05_Curved_Roofs')
    a.put('Lower_curved_cornice',cornice(86,76,41,9),pos=(0,0,22),section='05_Curved_Roofs')
    a.put('Lower_curved_balustrade',roof_balustrade(86,76,41,9),pos=(0,0,22),section='05_Curved_Roofs')
    g=Geometry();g.box((0,66,22),(48,30,42),'TempleCream')
    a.put('Upper_central_body',g,section='03_Main_Envelope',role='UpperEnvelope')
    upper=arch_bay(width=13,clear=6.5,spring=8,height=24)
    panel(upper,0,5.5,-.1,6.3,10.6,'TempleDark')
    for side in range(4):
        angle=side*math.pi/2;depth=42 if side%2==0 else 48
        for x in [-13,0,13]:
            p=rotate((x,54,-depth/2-1.4),angle)
            a.put('Upper_arched_bay',upper if 'Upper_arched_bay' not in a.cache else None,(p[0],p[1],p[2]+22),angle,section='04_Main_Arcades')
    a.put('Upper_Bengali_roof',bengal_roof(52,46,78,6),pos=(0,0,22),section='05_Curved_Roofs')
    a.put('Upper_curved_cornice',cornice(52,46,78,6),pos=(0,0,22),section='05_Curved_Roofs')
    a.put('Upper_curved_balustrade',roof_balustrade(52,46,78,6),pos=(0,0,22),section='05_Curved_Roofs')
    for x in [-34,34]:
        for z in [-7,51]:a.put('Ratna_lower_master',ratna(5.6,22,16) if 'Ratna_lower_master' not in a.cache else None,(x,43,z),section='06_Nine_Spires')
    for x in [-18,18]:
        for z in [6,38]:a.put('Ratna_upper_master',ratna(4.7,21,15) if 'Ratna_upper_master' not in a.cache else None,(x,82,z),section='06_Nine_Spires')
    a.put('Ratna_central',ratna(8,28,25),(0,89,22),section='06_Nine_Spires')
    a.scene['MainSpireCount']=9
    save_stage('Main temple: open entry, curved cornices and nine ribbed spires')


def kali_murti():
    """Respectful original four-arm silhouette and broad ceremonial details."""
    g=Geometry()
    # All positions are local to the altar: feet rest on the reclining Shiva.
    g.ellipsoid((0,8.8,.5),(3.5,5.4,1.7),'TempleDark',12,6)
    g.lathe([(2.1,4.5),(3,4.9),(7.3,3.2),(9.5,2.1)],12,'KaliBlue',center=(0,0,0))
    g.ellipsoid((0,11,.1),(2.5,3.1,1.25),'TempleDark',12,6)
    g.ellipsoid((0,14,-.2),(1.9,2.2,1.3),'TempleDark',12,7)
    # Broad blue side drapes and red/gold borders stand in for fabric patterns.
    for sign in [-1,1]:
        points=[(sign*1.4,10),(sign*3,9.2),(sign*5.4,2.1),(sign*2.1,3.1)]
        g.merge(prism(points,.45,'KaliBlue').transformed((0,0,-.1)))
        g.beam((sign*1.7,9.8,-.55),(sign*5.2,2.25,-.55),.16,'KaliGold',5)
        for y in [3.4,5.3,7.2]:g.merge(disk(sign*(4.7-(y-3.4)*.38),y,-.58,.24,'KaliRed',7))
    # Crown: layered base, five clear points and restrained cabochons.
    g.merge(prism([(-2,15.1),(-2.35,16.2),(-1.5,17.2),(-1.1,16.8),(0,19.7),(1.1,16.8),(1.5,17.2),(2.35,16.2),(2,15.1)],.8,'KaliGold').transformed((0,0,-.25)))
    g.merge(disk(0,17.8,-.75,.42,'KaliRed',8));g.merge(disk(0,16.2,-.75,.36,'KaliRed',8))
    for sign in [-1,1]:
        g.ellipsoid((sign*1.95,13.5,-.6),(.55,.8,.3),'KaliGold',8,4)
        g.ellipsoid((sign*.77,14,-1.41),(.67,.36,.18),'KaliWhite',10,4)
        g.ellipsoid((sign*.77,14,-1.58),(.22,.28,.11),'TempleDark',8,4)
        g.beam((sign*.18,14.55,-1.38),(sign*1.33,14.5,-1.22),.12,'KaliRed',5)
    g.ellipsoid((0,15,-1.27),(.25,.48,.13),'KaliWhite',8,4)
    g.ellipsoid((0,15,-1.4),(.1,.23,.08),'TempleDark',8,4)
    g.ellipsoid((0,13.1,-1.5),(.65,.29,.2),'KaliRed',10,4)
    g.merge(prism([(-.39,13.2),(.39,13.2),(.29,11.85),(0,11.55),(-.29,11.85)],.25,'KaliRed').transformed((0,0,-1.72)))
    # Four separate arms, with red palms, gold cuffs and conventional poses.
    arms=[((-2.1,11.7,.2),(-3.9,13,-.15),(-4.9,16.1,-.5)),
          ((2.1,11.7,.2),(3.6,13.2,-.1),(4.3,15.5,-.6)),
          ((-2,9.7,.25),(-3.9,10,-.2),(-4.8,8.7,-1)),
          ((2,9.7,.25),(3.7,9.4,-.5),(4.4,10,-1.4))]
    for shoulder,elbow,hand in arms:
        g.beam(shoulder,elbow,.55,'TempleDark',8);g.beam(elbow,hand,.43,'TempleDark',8)
        p=tuple(hand[i]*.85+elbow[i]*.15 for i in range(3));g.ellipsoid(p,(.65,.55,.6),'KaliGold',8,4)
        g.ellipsoid(hand,(.6,.85,.32),'KaliRed',8,5)
        for j in range(3):g.beam((hand[0]-.35+j*.34,hand[1]+.25,hand[2]-.22),(hand[0]-.35+j*.34,hand[1]+1,hand[2]-.25),.10,'KaliRed',5)
    # Curved ceremonial blade; a small non-graphic symbolic head below.
    blade=[(-5.1,16.6),(-5,19.6),(-4.1,20.4),(-3.8,19.7),(-4.4,19.3),(-4.5,16.6)]
    g.merge(prism(blade,.3,'KaliGold').transformed((0,0,-.65)))
    g.beam((-4.85,15.5,-.6),(-4.85,17.1,-.6),.18,'KaliGold',6)
    g.ellipsoid((-4.8,7.5,-1.05),(.75,.95,.65),'TempleDark',10,5)
    g.ellipsoid((-4.8,7.4,-1.55),(.53,.65,.18),'KaliGold',8,4)
    # Bib, necklaces and garland use a few readable shapes rather than jewels.
    g.merge(prism([(-1.85,12.2),(1.85,12.2),(2.1,10),(1.2,7.3),(0,6.5),(-1.2,7.3),(-2.1,10)],.38,'KaliGold').transformed((0,0,-1.35)))
    for y,r,role in [(11.2,.55,'KaliRed'),(9.3,.65,'KaliBlue'),(7.5,.35,'KaliRed')]:g.merge(disk(0,y,-1.68,r,role,10))
    for sign in [-1,1]:
        for j in range(8):
            y=12-j*.78;x=sign*(2.45-.08*j)
            g.ellipsoid((x,y,-1.45),(.36,.43,.29),'KaliGold' if j%2 else 'GarlandGreen',7,4)
        g.ellipsoid((sign*.8,2,-.8),(.52,.45,1.25),'TempleDark',8,4)
    # Reclining Shiva forms the physical support below Kali's feet.
    g.ellipsoid((0,1.2,-.2),(4.6,.9,1.55),'KaliWhite',12,5)
    g.ellipsoid((4.8,1.25,-.2),(1.5,1.05,1.45),'TempleDark',10,5)
    g.ellipsoid((4.7,1.5,-1.2),(1,.65,.35),'KaliWhite',10,5)
    for sign in [-1,1]:g.beam((-2,.95,sign*.65),(-5.3,.65,sign*.9),.5,'KaliWhite',8)
    g.ellipsoid((-1.8,1.5,-.4),(1.8,.5,1.3),'TempleCream',10,4)
    return g


def shrine():
    a=A;assert a;g=Geometry()
    # A single accessible chamber and short approach, no room network.
    for x in [-15.6,15.6]:g.box((x,21,24),(1.6,30,34),'TempleCream')
    g.box((0,21,40),(32,30,1.5),'TempleRed')
    g.box((0,36.5,24),(33,1,34),'TempleCream')
    g.box((0,6.35,21),(30,.5,37),'TempleStone')
    for x in [-14,14]:g.box((x,19,24),(.2,25,32),'TempleRed')
    g.box((0,7.3,29),(23,1.5,18),'TempleCream')
    g.box((0,8.25,29),(20,.45,16),'KaliGold')
    ellipse(g,(0,9.1,28),8,5.6,1.4,'TempleRed',24)
    ellipse(g,(0,9.85,28),8.5,6,.35,'KaliGold',24)
    for i in range(12):
        t=i*math.tau/12;g.ellipsoid((7.9*math.cos(t),9.2,28+5.4*math.sin(t)),(.75,.65,.55),'TempleCream',6,3)
    a.put('Limited_shrine_chamber_and_altar',g,section='07_Shrine_Chamber',role='ShrineShell')
    a.put('Kali_four_armed_murti',kali_murti(),(0,9.8,28),section='08_Kali_Murti',role='SacredFocalSculpture')
    # Silver ceremonial frame and burgundy arched backdrop.
    g=Geometry();arch=Geometry();arch.arch(19,16,.9,.8,mat='TempleSilver',segments=16)
    g.merge(arch.transformed((0,8.4,30)))
    shape=[(-9.5,0),(-9.5,16)]+[(9.5*math.cos(math.pi-i*math.pi/16),16+9.5*math.sin(math.pi-i*math.pi/16)) for i in range(17)]+[(9.5,0)]
    g.merge(prism(shape,.7,'TempleRed').transformed((0,8.4,31)))
    for x in [-9.8,9.8]:
        g.lathe([(0,.95),(.8,.95),(1.1,.6),(18,.6),(18.7,1),(19.3,1)],10,'TempleSilver',center=(x,8.4,26.9))
        g.box((x,8.8,26.9),(2.5,.8,2.5),'TempleCream')
    for sign in [-1,1]:
        g.ellipsoid((sign*8.2,17,29.6),(3.4,7.4,.5),'KaliBlue',12,6)
        for y in [12,16,20]:g.merge(disk(sign*8.2,y,28.96,.5,'KaliGold',8))
    for x in [-12,12]:
        g.lathe([(0,.9),(.5,1.1),(.8,.4),(3.2,.35),(3.5,1.3),(3.9,1.3)],10,'KaliGold',center=(x,6.6,19))
        g.ellipsoid((x,11.1,19),(.35,.7,.35),'TempleGlow',8,4)
    a.put('Shrine_silver_arch_drapery_lamps',g,section='09_Shrine_Frame')
    a.sockets['MainShrineEntry']={'positionStuds':[0,6.05,-14],'clearWidthStuds':10.4,'clearHeightStuds':18.4}
    a.sockets['ShrineViewingFloor']={'positionStuds':[0,6.6,12],'clearWidthStuds':26,'clearDepthStuds':14}
    save_stage('Accessible Kali chamber, original four-arm murti, silver frame and altar')


def shiva_master():
    g=Geometry()
    for x in [-8.6,8.6]:g.box((x,7,0),(1.2,14,23),'TempleCream')
    g.box((0,7,10.8),(18,14,1.2),'TempleCream')
    bay=arch_bay(width=18,clear=6.5,spring=8,height=14)
    g.merge(bay.transformed((0,0,-11.5)))
    g.merge(bengal_roof(20,25,14,3.5,n=6,role='TempleRoof'))
    g.merge(cornice(20,25,14,3.5,detail=False))
    g.merge(bengal_roof(11,13,20,2.2,n=4,role='TempleRoof'))
    g.merge(finial(4,.65).transformed((0,24.4,0)))
    g.box((0,.25,0),(19,.5,25),'TempleCream')
    # Simple recognizable lingam/yoni shrine form inside each open doorway.
    ellipse(g,(0,1.3,3),2.6,2,1.5,'TempleDark',12)
    g.lathe([(0,1.2),(1.7,1.2),(2.3,.9),(2.5,.1)],10,'TempleDark',center=(0,1.7,3))
    g.box((0,1.8,.9),(1.3,.5,3.2),'TempleDark')
    return g


def shiva_rows():
    a=A;assert a;master=shiva_master()
    for sign in [-1,1]:
        for index in range(6):
            x=sign*(61+24*index)
            objects=a.put('Shiva_temple_shared_master',master if 'Shiva_temple_shared_master' not in a.cache else None,(x,3.4,30),section='10_Shiva_Temples')
            for obj in objects:obj['ShrineIndex']=(index+1 if sign<0 else index+7)
    a.scene['ShivaTempleCount']=12
    save_stage('Twelve linked Shiva temples, six per side, on shared accessible platforms')


def ghat():
    a=A;assert a;g=Geometry();bottom=-8.5;z=-87;level=1.0
    # One raised threshold seats into the courtyard. Its visible top is .2
    # above the paving, replacing the two overlapping coplanar landing caps.
    g.box((0,.85,-84.5),(278,.3,5),'TemplePaving')
    profile=[(z,level)]
    for index in range(16):
        level-=.5;depth=2.3+(5 if index in [5,10] else 0)
        for x,width in [(0,106),(-95,80),(95,80)]:
            g.box((x,(bottom+level)/2,z-depth/2),(width,level-bottom,depth+.02),'TempleStone')
            g.box((x,level+.03,z-.16),(width,.18,.32),'TempleCream')
        z-=depth;profile.append((z,level))
    # Low solid separators follow the stair pitch; their caps are deliberately
    # above the steps rather than coplanar with them.
    for x in [-136,-54,54,136]:
        for (z0,y0),(z1,y1) in zip(profile,profile[1:]):
            verts=[(x-1.2,bottom,z0),(x+1.2,bottom,z0),(x+1.2,y0+1.5,z0),(x-1.2,y0+1.5,z0),
                   (x-1.2,bottom,z1),(x+1.2,bottom,z1),(x+1.2,y1+1.5,z1),(x-1.2,y1+1.5,z1)]
            piece=Geometry()
            for ids in [(0,3,2,1),(4,5,6,7),(0,4,7,3),(1,2,6,5),(0,1,5,4),(3,7,6,2)]:piece.polygon([verts[i] for i in ids],'TempleRed')
            g.merge(piece);g.beam((x,y0+1.6,z0),(x,y1+1.6,z1),.25,'TempleCream',4)
    for sign in [-1,1]:
        g.box((sign*173,-4.9,-84),(66,11.4,4),'TempleRed')
        g.box((sign*173,.85,-84),(68,.4,5),'TempleCream')
        for x in range(145,204,12):g.box((sign*x,-2,-86.15),(8,3,.4),'TempleCream')
    a.put('Attached_ghat_steps_landings_retaining_edges',g,section='11_Ghat',role='RiverStairs')
    # A low open gateway frames the river/main-shrine axis without sealing it.
    bay=arch_bay(width=15,clear=10.5,spring=10.5,height=19)
    for x in [-15,0,15]:a.put('River_gate_shared_bay',bay if 'River_gate_shared_bay' not in a.cache else None,(x,.8,-77),section='12_River_Gateway')
    g=Geometry();g.box((0,20.4,-77),(47,1.2,7),'TempleRed');g.box((0,21.2,-77),(49,.6,8),'TempleCream')
    for x in [-20,20]:g.merge(finial(3,.7).transformed((x,21.6,-77)))
    a.put('River_gateway_entablature',g,section='12_River_Gateway')
    datum=bpy.data.objects.new('WATER_DATUM__native_Roblox_water_at_Y_minus_5',None)
    a.section('AUTHORING_GUIDES__NOT_EXPORTED').objects.link(datum);datum.empty_display_type='PLAIN_AXES';datum.empty_display_size=14
    datum.location=bv((0,-5,-129));datum['WaterLevelStuds']=-5;datum['FinalWaterMesh']=False
    a.sockets['WaterDatum']={'heightStuds':-5,'bankFrontZ':-87,'lowestStepHeightStuds':level,'ghatFrontZ':round(z,3),'nativeRobloxTerrainWaterLater':True}
    a.sockets['GhatMainLanding']={'positionStuds':[0,1,-84.5],'clearWidthStuds':104}
    save_stage('Attached broad ghat with three flights, intermediate landings and native-water datum')


def supports():
    a=A;assert a;g=Geometry()
    for sign in [-1,1]:
        g.box((sign*114,4,83),(188,6.4,2.5),'TempleCream')
        g.box((sign*114,7.1,83),(190,.6,3.6),'TempleRed')
        g.box((sign*206,3,0),(2.2,4.4,166),'TempleCream')
        g.box((sign*206,5.3,0),(3,.5,168),'TempleRed')
        for x in range(30,201,20):g.box((sign*x,4,81.6),(12,3,.3),'TempleRed')
    a.put('Boundary_walls_and_gate_returns',g,section='13_Boundary_Support')
    gate=arch_bay(width=34,clear=18,spring=12,height=23)
    a.put('Rear_open_campus_gate',gate,(0,.8,83),section='13_Boundary_Support')
    g=Geometry();g.box((0,24.3,83),(37,.6,5),'TempleRed')
    a.put('Rear_gate_cap',g,section='13_Boundary_Support')
    # Reused restrained planting; no dense garden campus.
    planter=Geometry();planter.box((0,1.3,0),(12,1,10),'TempleRed');planter.box((0,1.95,0),(12.8,.3,10.8),'TempleCream')
    planter.box((0,2.15,0),(10.8,.35,8.8),'Leaf')
    for i,(x,z) in enumerate([(-193,-55),(193,-55),(-193,65),(193,65)]):
        a.put('Courtyard_planter_master',planter if i==0 else None,(x,0,z),section='14_Landscape_Fixtures')
        a.put('Temple_palm_master',palm_geometry() if i==0 else None,(x,2.25,z),section='14_Landscape_Fixtures')
    lamp=Geometry();lamp.box((0,1.2,0),(2.5,.8,2.5),'TempleStone')
    lamp.cylinder((0,5.2,0),.26,8.4,'TempleGold',8)
    lamp.box((0,10,0),(1.8,2,1.8),'TempleGlow');lamp.box((0,11.3,0),(2.4,.6,2.4),'TempleRed')
    for i,(x,z) in enumerate([(-151,-66),(-51,-66),(51,-66),(151,-66),(-48,70),(48,70)]):a.put('Courtyard_lamp_master',lamp if i==0 else None,(x,0,z),section='14_Landscape_Fixtures')
    for x in [-95,95]:a.put('Courtyard_lamp_master',None,(x,-2.8,-102),section='14_Landscape_Fixtures')
    # Small physical housings keep architectural washes visibly installed.
    g=Geometry()
    for x,y,z in [(-28,12,-28),(28,12,-28),(-23,57,-3),(23,57,-3),(-12,93,17),(12,93,17)]:
        foot=6.05 if y<20 else roof_height(x,z-22,86,76,41,9) if y<80 else roof_height(x,z-22,52,46,78,6)
        g.cylinder((x,(foot+y-.3)/2,z),.2,y-.3-foot+.1,'TempleGold',6)
        g.box((x,y-.3,z),(1.1,.6,1.2),'TempleGold')
        g.box((x,y+.04,z),(.8,.12,.9),'TempleGlow')
    a.put('Architectural_light_housings',g,section='14_Landscape_Fixtures')
    g=Geometry()
    for x in [-157,-85,85,157]:
        g.box((x,15.4,16.6),(1.5,.5,1.1),'TempleGold')
        g.box((x,15.12,16.4),(1,.16,.7),'TempleGlow')
    a.put('Shiva_porch_light_fixtures',g,section='14_Landscape_Fixtures')
    save_stage('Boundaries, shared planting, eight lanterns and architectural light fixtures')


def lighting_plan():
    lights=[]
    def add(name,pos,range_,brightness,power,kind='POINT',target=None,shadows=False):
        lights.append(dict(name=name,positionStuds=list(pos),rangeStuds=range_,brightness=brightness,
            blenderWatts=power,type=kind,targetStuds=list(target) if target else None,
            colorRGB=[255,209,147],angleDegrees=75,shadows=shadows))
    for i,(x,z) in enumerate([(-151,-66),(-51,-66),(51,-66),(151,-66),(-48,70),(48,70)]):
        add('Courtyard_%02d'%(i+1),(x,10,z),22,1.2,1500)
    for i,x in enumerate([-95,95]):add('Ghat_%02d'%(i+1),(x,7.2,-102),38,1.5,2400)
    add('Kali_face',(0,24,18),26,2.2,950,shadows=True)
    add('Shrine_fill',(0,16,23),18,1.1,350)
    for i,x in enumerate([-157,-85,85,157]):add('Shiva_row_%02d'%(i+1),(x,14.7,15),36,1.1,2000)
    for i,(pos,target) in enumerate([
        ((-28,12,-28),(-20,42,-10)),((28,12,-28),(20,42,-10)),
        ((-23,57,-3),(-18,101,10)),((23,57,-3),(18,101,10)),
        ((-12,93,17),(0,137,22)),((12,93,17),(0,137,22))]):
        add('Temple_wash_%02d'%(i+1),pos,60,2.4,42000,'SPOT',target)
    return lights


def night_lights():
    a=A;assert a
    rig=bpy.data.collections.new('NIGHT_LIGHTS__native_Roblox_install_plan');a.scene.collection.children.link(rig)
    for spec in lighting_plan():
        data=bpy.data.lights.new(spec['name'],spec['type']);data.energy=spec['blenderWatts']
        data.color=(1,.72,.4);data.use_shadow=spec['shadows']
        data.use_custom_distance=True;data.cutoff_distance=spec['rangeStuds']
        if spec['type']=='SPOT':data.spot_size=math.radians(spec['angleDegrees']);data.spot_blend=.65
        else:data.shadow_soft_size=.75
        obj=bpy.data.objects.new(spec['name'],data);rig.objects.link(obj);obj.location=bv(spec['positionStuds'])
        if spec['targetStuds']:obj.rotation_euler=(Vector(bv(spec['targetStuds']))-obj.location).to_track_quat('-Z','Y').to_euler()
        obj['NightWatts']=spec['blenderWatts'];obj['RobloxRangeStuds']=spec['rangeStuds']
    mat=pipeline.material('TempleGlow');node=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    node.inputs['Emission Color'].default_value=(1,.65,.23,1);node.inputs['Emission Strength'].default_value=2
    plan=dict(origin='Ground center; Roblox X/Y/Z studs',lights=lighting_plan(),shadowCastingLights=1)
    (HERE/'night-lights.json').write_text(json.dumps(plan,indent=2),encoding='utf8')
    a.sockets['NightLightingZones']={'installedBlenderLights':len(plan['lights']),'nativeRobloxPlan':'night-lights.json',
        'nativeInstaller':'exports/dakshineshwar/InstallNightLights.luau','shadowCastingLights':1}
    save_stage('Working warm temple, shrine, courtyard and ghat night lights installed')


def finish():
    a=A;assert a
    # Export the Shiva module once. The editable scene retains all twelve
    # linked placements; Studio clones must reuse the imported mesh IDs.
    source_col=a.sections.pop('10_Shiva_Temples')
    master_col=bpy.data.collections.new('__SHIVA_MASTER_EXPORT');a.scene.collection.children.link(master_col)
    clones=[]
    for obj in source_col.objects:
        if obj.get('ShrineIndex')!=1:continue
        copy=obj.copy();copy.location=(0,0,0);copy['Section']='10_Shiva_Temple_Master'
        master_col.objects.link(copy);clones.append(copy)
    a.sections['10_Shiva_Temple_Master']=master_col
    try:row=a.finish()
    finally:
        a.sections.pop('10_Shiva_Temple_Master');a.sections['10_Shiva_Temples']=source_col
        for obj in clones:bpy.data.objects.remove(obj,do_unlink=True)
        bpy.data.collections.remove(master_col)
    obsolete=a.export_dir/(a.scene.name+'__10_Shiva_Temples.fbx')
    if obsolete.is_file():obsolete.unlink()
    placements=[dict(index=i+1 if sign<0 else i+7,positionStuds=[sign*(61+24*i),3.4,30],yawDegrees=0)
        for sign in [-1,1] for i in range(6)]
    row['reusedModules']={'ShivaTemple':dict(masterFile=a.scene.name+'__10_Shiva_Temple_Master.fbx',placements=placements)}
    (a.export_dir/'shiva-placements.json').write_text(json.dumps(row['reusedModules']['ShivaTemple'],indent=2),encoding='utf8')
    row['waterLevelStuds']=-5;row['mainSpireCount']=9;row['shivaTempleCount']=12
    row['scope']='Blender landmark asset only; limited shrine, no gameplay or final water mesh'
    row['concepts']=['concepts/01-campus.png','concepts/02-ghat.png','concepts/03-courtyard.png','concepts/04-shrine.png']
    row['triangleBudget']={'uniqueTarget':[40000,55000],'placedTarget':[65000,95000],'placedSoftReview':110000,'targetsAreAllowances':True}
    (HERE/'asset.json').write_text(json.dumps(row,indent=2),encoding='utf8')
    save_stage('Complete complex exported; ready for minimal final review')
    return row


if __name__=='__main__':
    begin();main_temple();shrine();shiva_rows();ghat();supports();night_lights();finish()
