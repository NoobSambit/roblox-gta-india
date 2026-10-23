"""Reference-led exterior refinements; all forms are original mesh geometry."""
import bpy
import math
from mathutils import Vector
from pipeline import Asset,Geometry,panel,ellipse,foundation,floor_band


def slab(outline,height,thickness,role='Pearl'):
    g=Geometry()
    top=[(x,height(x,z) if callable(height) else height,z) for x,z in outline]
    bottom=[(x,y-thickness,z) for x,y,z in top]
    g.polygon(top,role);g.polygon(list(reversed(bottom)),role)
    for i in range(len(top)):
        j=(i+1)%len(top);g.polygon([top[i],bottom[i],bottom[j],top[j]],role)
    return g


def skin(grid,offset,role,smooth=True):
    """A closed, thick grid surface, including every boundary return."""
    g=Geometry();rows=len(grid);cols=len(grid[0])
    back=[[tuple(p[i]+offset[i] for i in range(3)) for p in row] for row in grid]
    for j in range(rows-1):
        for i in range(cols-1):
            g.polygon([grid[j][i],grid[j+1][i],grid[j+1][i+1],grid[j][i+1]],role,smooth)
            g.polygon([back[j][i+1],back[j+1][i+1],back[j+1][i],back[j][i]],role,smooth)
    boundary=[(0,i) for i in range(cols)]+[(j,cols-1) for j in range(1,rows)]+[(rows-1,i) for i in range(cols-2,-1,-1)]+[(j,0) for j in range(rows-2,0,-1)]
    for a,b in zip(boundary,boundary[1:]+boundary[:1]):
        j,i=a;k,l=b;g.polygon([grid[j][i],grid[k][l],back[k][l],back[j][i]],role)
    return g


def oval(cx,cz,rx,rz,n=48):
    return [(cx+rx*math.cos(i*math.tau/n),cz+rz*math.sin(i*math.tau/n)) for i in range(n)]


def marriott_towers(a):
    step=8.2
    for index,(x,z,w,d,levels) in enumerate([(55,42,142,48,23),(-94,57,69,54,25)]):
        section='Hotel_Tower' if index==0 else 'Companion_Tower';h=levels*step;base=35
        core=Geometry();core.box((0,base+h/2,0),(w,h,d),'Graphite')
        for xx in [-w/2,w/2]:
            for zz in [-d/2,d/2]:core.box((xx,base+h/2,zz),(2.1,h,2.3),'Stone')
        for xx in [-w*.29,w*.29]:core.box((xx,base+h/2,-d/2-.4),(.65,h,1),'Silver')
        a.put('JW_tower_core_'+str(index),core,(x,0,z),section=section,role='TowerEnvelope')
        for level in range(levels):
            key=f'JW_room_floor_{index}_{level%2}'
            g=floor_band(w,d,step,level%2,'Silver',glazing=.97,glazing_height=.86)
            # A broad opaque service spine divides the main glazed wings.
            for side in [-1,1]:
                cx=0 if index==0 else w*.26
                spine=w*.2 if index==0 else w*.13
                g.box((cx,step/2,side*(d/2+1.05)),(spine,step,.65),'Graphite')
                for j in range(round(spine/2)+1):
                    xx=cx-spine/2+j*2;g.box((xx,step/2,side*(d/2+1.45)),(.3,step,.45),'Silver')
                g.box((cx+spine/2+.6,step/2,side*(d/2+1.35)),(.6,step,.7),'Stone')
            if index==0:panel(g,0,step/2,-d/2-1.8,1.5,5.7,'WarmWindow' if level%2 else 'Glass')
            else:
                g.box((-w*.12,step/2,-d/2-1.35),(w*.45,step,.6),'Graphite')
                g.box((-w*.12,.15,-d/2-3),(w*.46,.45,5.5),'Stone')
                panel(g,-w*.12,1.45,-d/2-5.85,w*.44,2.1,'GlassBlue')
                g.box((-w*.12,2.6,-d/2-5.9),(w*.46,.2,.3),'Silver')
                for xx in [-w*.35,w*.11]:g.box((xx,step/2,-d/2-3),(1.05,step,5.5),'Stone')
            a.put(key,g if key not in a.cache else None,(x,base+level*step,z),section=section)
        top=base+h;g=Geometry()
        g.box((0,top,0),(w+3,1.3,d+3),'Stone')
        g.box((0,top+5.8,0),(w+1,11.3,d+1),'Graphite')
        for side in range(4):
            from geometry import rotate
            width=w if side%2==0 else d;depth=d if side%2==0 else w;angle=side*math.pi/2
            count=round(width/4.5)
            for j in range(count):
                left=-width/2+j*width/count;right=left+width/count
                for lo,hi in [(left,right),(right,left)]:
                    p=rotate((lo,top+.8,-depth/2-1.05),angle);q=rotate((hi,top+11.6,-depth/2-1.05),angle)
                    g.beam(p,q,.24,'Pearl',4)
            for y in [top+.6,top+11.7]:
                p=rotate((0,y,-depth/2-1.15),angle)
                g.box(p,(width+3,.4,.65),'Accent' if y>top+1 else 'Pearl',angle)
        if index==0:
            g.box((0,top-7,-d/2-3),(92,15,6),'GlassBlue')
            for xx in range(-45,46,9):g.box((xx,top-7,-d/2-6.15),(.35,15,.45),'Silver')
            for y in [top-14.7,top-7,top+.6]:g.box((0,y,-d/2-6.3),(92,.35,.7),'Silver')
            g.box((0,top-14.8,-d/2-6.6),(93,.3,.45),'Accent')
        a.put('JW_lattice_crown_'+str(index),g,(x,0,z),section=section)
        if index==0:a.text('JW MARRIOTT',(x+34,top+3.1,z-d/2-1.7),4.2,65,section=section)


def marriott():
    a=Asset('jw','JW Marriott Kolkata / swept diagrid arrival')
    foundation(a,316,236)
    # A raised rear podium physically bears both towers. The curved front
    # volume steps down to a planted terrace, as in the supplied aerial views.
    g=Geometry();g.box((0,18.05,42),(284,33.6,110),'Stone')
    g.box((0,34.85,42),(286,.4,112),'Pearl')
    for x in [-142,142]:
        for z in [-8,10,28,46,64,82]:g.box((x,18,z),(1.6,33.5,1.1),'Stone')
    for x in range(-132,133,12):panel(g,x,14,-14.1,9,19,'Glass')
    g.box((0,26,-14),(284,1.1,1.6),'Louvre')
    a.put('JW_bearing_podium',g,section='Podium_Base',role='PodiumEnvelope')
    marriott_towers(a)
    def curve(t):
        u=2*t-1
        return (135*math.sin(u*math.pi/2),-50-18*math.sin(math.pi*u)**2+16*math.exp(-(u/.23)**2)+45*abs(u)**8+5*u)
    def plan(t,offset=0):
        x,z=curve(t);p=curve(max(0,t-.0001));q=curve(min(1,t+.0001));dx=q[0]-p[0];dz=q[1]-p[1];length=math.hypot(dx,dz)
        return x-dz/length*offset,z+dx/length*offset
    def front(t,s=0):
        x,z=plan(t,-5*math.sin(s*math.pi)+3*(1-s))
        bottom=2.1+18*math.sqrt(max(0,1-(curve(t)[0]/35)**2))
        return x,bottom+(34.1-bottom)*s,z
    n=56;rows=4
    grid=[[front(i/n,j/rows) for i in range(n+1)] for j in range(rows+1)]
    a.put('JW_bowed_S_glass',skin(grid,(0,0,.45),'GlassLight'),section='Hero_Diagrid')
    g=Geometry()
    for j in range(rows):
        for i in range(n):
            for i0,i1 in [(i,i+1),(i+1,i)]:
                p=front(i0/n,j/rows);q=front(i1/n,(j+1)/rows)
                g.beam((p[0],p[1],p[2]-.7),(q[0],q[1],q[2]-.7),.28,'Bronze',4)
    for j in [0,2,4]:
        for i in range(n):
            p=front(i/n,j/rows);q=front((i+1)/n,j/rows)
            g.beam((p[0],p[1],p[2]-.75),(q[0],q[1],q[2]-.75),.32,'Stone',4)
    for t in [0,1]:
        x,y,z=front(t)
        g.box((x,18,(z+22)/2),(1.3,32,22-z),'Stone')
    a.put('JW_structural_diamond_lattice',g,section='Hero_Diagrid')
    # Solid terrace roof and sweeping continuous coping; no paper-thin roof.
    outline=[plan(i/n) for i in range(n+1)]+[(135,22),(-135,22)]
    roof=slab(outline,34.7,1,'Stone');edge=Geometry();water=Geometry()
    for i in range(n):
        p=front(i/n,1);q=front((i+1)/n,1)
        edge.beam((p[0],35,p[2]),(q[0],35,q[2]),.5,'Pearl',6)
        edge.beam((p[0],34.2,p[2]-.3),(q[0],34.2,q[2]-.3),.18,'Accent',4)
    pool_grid=[[(plan(i/n,offset)[0],35,plan(i/n,offset)[1]) for i in range(n+1)] for offset in [2.2,7.2]]
    water.merge(skin(pool_grid,(0,-.25,0),'Water'))
    for i in range(n):
        for offset in [1.8,7.6]:
            p=plan(i/n,offset);q=plan((i+1)/n,offset);edge.beam((p[0],35.15,p[1]),(q[0],35.15,q[1]),.2,'Pearl',4)
    for t in [.12,.22,.32,.42,.58,.68,.78,.88]:
        x,z=plan(t,18)
        roof.box((x,35.3,z),(7,1.2,7),'Stone');roof.box((x,36,z),(6.4,.4,6.4),'Leaf')
        a.put('palm',None,(x,36.1,z),section='Roof_Terrace')
    for t in [.18,.28,.38,.62,.72,.82]:
        x,z=plan(t,11)
        roof.box((x,35.4,z),(3.4,1.3,6),'Louvre');roof.box((x,36.1,z-.2),(3,.3,4.5),'Pearl')
    a.put('JW_terrace_roof_planters',roof,section='Roof_Terrace')
    a.put('JW_pool_ribbon',water,section='Roof_Terrace')
    a.put('JW_continuous_coping',edge,section='Roof_Terrace')
    # Open vaulted arrival recess under the pinched part of the diagrid.
    def vault(x,z):return 12+10*math.cos(x*math.pi/60)+.025*(z+35)
    grid=[[(x,vault(x,z),z) for x in range(-30,31,3)] for z in [-54,-44,-34,-24,-14]]
    g=skin(grid,(0,-.6,0),'GlassLight')
    for j in range(4):
        for i in range(20):
            for i0,i1 in [(i,i+1),(i+1,i)]:
                p=grid[j][i0];q=grid[j+1][i1];g.beam((p[0],p[1]-.8,p[2]),(q[0],q[1]-.8,q[2]),.24,'Bronze',4)
    for x in [-30,30]:
        g.box((x,6.8,-39),(1.4,11.1,28),'Stone')
    panel(g,0,9,-14.2,32,14,'Glass')
    for x in [-12,-6,6,12]:g.box((x,9,-14.5),(.35,14,.6),'Bronze')
    g.box((0,1.65,-34),(66,.8,41),'Stone')
    ellipse(g,(0,1.8,-91),28,13,.8,'Stone',48)
    ellipse(g,(0,2.25,-91),25,10.5,.25,'Water',48)
    ellipse(g,(0,3,-91),6,3,1.4,'Pearl',24)
    for x in [-112,112]:
        g.box((x,2,-80),(20,1.5,9),'Stone');g.box((x,2.9,-80),(18,.5,7),'Leaf')
    a.put('JW_vaulted_arrival_fountain',g,section='Arrival',role='GroundAndPortico')
    a.sockets['MainEntrance']={'positionStuds':[0,2,-14.2],'clearWidthStuds':28,'clearHeightStuds':14,'exteriorOnly':True}
    return a.finish()


def sonar():
    a=Asset('sonar','ITC Sonar / terracotta water gardens and flaring canopy')
    foundation(a,258,228)
    blocks=[(0,63,104,30,80),(-82,40,30,80,48),(82,40,30,80,48)]
    for index,(x,z,w,d,h) in enumerate(blocks):
        section=f'Guest_Wing_{index+1}';g=Geometry()
        for xx in [-w/2,w/2]:g.box((xx,h/2+1.25,0),(1.2,h,d),'Terra')
        for zz in [-d/2,d/2]:g.box((0,h/2+1.25,zz),(w,h,1.2),'Terra')
        for yy,thick in [(h+1.25,1.3),(h-5,.45)]:g.box((0,yy,0),(w+2,thick,d+2),'Louvre')
        for side in [-1,1]:
            for xx in range(int(-w/2+3),int(w/2),9):g.box((xx,h/2+1.25,side*(d/2+.85)),(.65,h,1.3),'Terra')
        a.put('Sonar_brick_wing_'+str(index),g,(x,0,z),section=section,role='ShellWalls')
        for level in range(int((h-10)/10)):
            key=f'Sonar_glazing_{index}_{level%2}'
            g=floor_band(w+1.3,d+1.3,10,level%2,'Stone',slab=False,glazing=.49,glazing_height=.6)
            a.put(key,g if key not in a.cache else None,(x,3+level*10,z),section=section)
        floor=Geometry();floor.box((0,0,0),(w-1.2,.7,d-1.2),'Stone')
        for level in range(int(h/10)):
            a.put('Sonar_shell_floor_'+str(index),floor if level==0 else None,(x,1.6+level*10,z),section='Internal_Shell',role='StructuralFloor')
    g=Geometry();g.box((0,1.55,9),(126,.6,98),'Graphite');g.box((0,1.92,9),(122,.18,94),'PondWater')
    for x in [-63,63]:g.box((x,2,9),(1.4,.6,100),'Stone')
    for z in [-40,58]:g.box((0,2,z),(127,.6,1.4),'Stone')
    for i in range(180):
        x=-58+(i*37%116);z=-36+(i*29%90)
        ellipse(g,(x,2.1,z),1.6+(i%3)*.4,1.3,.1,'LeafLight' if i%5==0 else 'Leaf',8)
        if i%19==0:ellipse(g,(x,2.24,z),.4,.32,.12,'Pearl',6)
    for x,z in [(-64,-43),(64,-43),(-30,45),(30,45)]:
        ellipse(g,(x,2,z),8,6,.8,'Stone',24);ellipse(g,(x,2.55,z),7.3,5.3,.3,'Leaf',24)
        a.put('palm',None,(x,2.7,z),section='Water_Gardens')
    for z in [-6,40]:g.box((0,2.5,z),(104,.8,5),'Stone')
    a.put('Sonar_lily_courtyard_edges_walks',g,section='Water_Gardens')
    # One complete tea pavilion module, repeated around the lily court.
    g=Geometry();g.box((0,2,0),(28,1.5,29),'Stone')
    g.box((0,7,0),(25,9,26),'Glass')
    g.box((0,11.5,0),(28.5,1.2,29.5),'Louvre')
    g.box((0,15.7,0),(27,7.6,28),'Louvre')
    g.box((0,20.1,0),(29,1.1,30),'Louvre')
    for side in range(4):
        from geometry import rotate
        for j in range(-12,13,2):
            p=rotate((j,15.8,-14.3),side*math.pi/2);g.box(p,(.5,8.4,.7),'Terra',side*math.pi/2)
        for j in range(-11,12,3):
            p=rotate((j,6.8,-13.5),side*math.pi/2);g.box(p,(.45,8,.65),'Louvre',side*math.pi/2)
            for yy in [3.5,6.7,9.8]:
                p=rotate((j+.9,yy,-13.6),side*math.pi/2);g.box(p,(2.1,.45,.65),'Louvre',side*math.pi/2)
    for i,(x,z) in enumerate([(-48,-26),(48,-26),(-48,21),(48,21)]):
        a.put('Sonar_screened_tea_pavilion',g if i==0 else None,(x,0,z),section='Tea_Pavilions')
    g=Geometry();g.box((86,11.3,-67),(76,20.1,19),'Terra')
    g.box((86,21.6,-67),(78,.9,21),'Stone');panel(g,78,8.3,-77.4,24,13,'GlassLight')
    for xx in [67,73,83,89]:g.box((xx,8.3,-77.7),(.4,13,.8),'Louvre')
    for x in [66,90,114]:
        canopy=[]
        for j in range(9):
            z=-84-15+30*j/8;row=[]
            for i in range(9):
                xx=-12+24*i/8;zz=z+84
                yy=22-8*(1-(xx/12)**2)**2*(1-(zz/15)**2)**2
                row.append((x+xx,yy,z))
            canopy.append(row)
        g.merge(skin(canopy,(0,-.65,0),'Pearl'))
        g.box((x,7.35,-84),(1.7,12.2,1.7),'Pearl')
        g.box((x,1.65,-84),(3,.8,3),'Stone')
    for z in [-99,-69]:g.box((90,22.05,z),(72,.45,.6),'Pearl')
    g.box((90,22.05,-99.4),(72,.2,.3),'Accent')
    for i in range(3):g.box((78,1.55+i*.35,-83+i*2),(29,.4,10-i*2),'Stone')
    a.put('Sonar_white_flaring_arrival',g,section='Arrival',role='GroundAndPortico')
    a.text('ITC SONAR',(49,12,-77.6),2.4,22,section='Arrival')
    a.sockets['MainEntrance']={'positionStuds':[78,2,-77.6],'clearWidthStuds':20,'clearHeightStuds':13,'exteriorOnly':True}
    return a.finish()


def urbana():
    a=Asset('urbana','Urbana / seven towers with folded facade wings')
    foundation(a,416,304)
    positions=[(-146,-52,37),(-70,-22,35),(9,3,33),(143,-56,37),(140,63,34),(56,79,32),(-85,81,35)]
    front=[(-24,-12),(-18,-18),(-10,-13),(-2,-19),(6,-13),(15,-17),(24,-11)]
    outline=front+[(x,-z) for x,z in reversed(front)]
    # The zigzag is a real folded footprint with recessed glazing between
    # projecting white fins, visible in silhouette and oblique views.
    floor=Geometry();glazing=[]
    for p,q in zip(outline,outline[1:]+outline[:1]):
        dx=q[0]-p[0];dz=q[1]-p[1];length=math.hypot(dx,dz);angle=math.atan2(-dz,dx)
        normal=(dz/length,-dx/length);cx=(p[0]+q[0])/2;cz=(p[1]+q[1])/2
        floor.box((cx+normal[0],.2,cz+normal[1]),(length+.2,2.5,.8),'Pearl',angle)
        bays=max(1,round(length/4))
        for j in range(bays):
            t=(j+.5)/bays
            glazing.append((p[0]+dx*t,p[1]+dz*t,normal,angle,length/bays))
    for index,(x,z,levels) in enumerate(positions):
        section=f'Tower_{index+1:02}';height=levels*10;key='Urbana_folded_core_'+str(levels)
        g=slab(outline,height+1.25,height,'Pearl')
        for xx,zz in outline:g.box((xx,1.25+height/2,zz),(1.2,height+1,1.6),'Pearl')
        # Continuous glazing/mullions sit behind repeated opaque spandrels.
        # This preserves the same window grid without thousands of redundant
        # closed glass boxes and per-floor vertical dividers.
        for xx,zz,normal,angle,bay_width in glazing:
            panel(g,xx+normal[0]*.85,1.25+height/2,zz+normal[1]*.85,bay_width*.68,height-1,'Glass',angle)
            g.box((xx+normal[0]*.95,1.25+height/2,zz+normal[1]*.95),(.22,height,.35),'Pearl',angle)
        g.box((0,height/2+1.25,0),(3,height+4,39),'Stone')
        a.put(key,g if key not in a.cache else None,(x,0,z),section=section,role='TowerEnvelope')
        for level in range(levels):
            a.put('Urbana_folded_floor',floor if 'Urbana_folded_floor' not in a.cache else None,(x,1.25+level*10,z),section=section)
        roof=slab(outline,1.3,1.35,'Pearl')
        for p,q in zip(outline,outline[1:]+outline[:1]):
            roof.beam((p[0],5.8,p[1]),(q[0],5.8,q[1]),.35,'Pearl',4)
        for xx,zz in outline:roof.box((xx,3.5,zz),(.55,4.6,.55),'Pearl')
        roof.box((1,4,1),(9,6,11),'Stone')
        a.put('Urbana_folded_roof_frame',roof if index==0 else None,(x,1.25+height,z),section=section)
        entry=Geometry();entry.box((0,9.6,-22),(12,1.1,10),'Pearl')
        for xx in [-4.5,4.5]:entry.box((xx,5.3,-25),(.7,8.2,.7),'Stone')
        entry.box((0,1.6,-22),(16,.7,13),'Stone');panel(entry,0,5.4,-20,8,8,'Glass')
        a.put('Urbana_tower_entry',entry if index==0 else None,(x,0,z),section=section)
    # Complete kidney-shaped clubhouse: foundation, glazed drum, roof fascia
    # and a separate outdoor pool with coping and terrace, rather than disks.
    perimeter=[]
    for i in range(64):
        t=i*math.tau/64;r=1+.1*math.cos(3*t)
        perimeter.append((-10+59*r*math.cos(t),-70+25*r*math.sin(t)))
    g=slab(perimeter,2.5,1.25,'Stone')
    roof_height=lambda x,z:18.2+2.4*math.cos((x+10)/24)+.03*(z+70)
    wall=Geometry()
    for i in range(len(perimeter)):
        p=perimeter[i];q=perimeter[(i+1)%len(perimeter)]
        lower=[];upper=[]
        for factor in [.94,.93]:
            for x,z in [p,q]:
                xx=(x+10)*factor-10;zz=(z+70)*.9*factor/.94-70
                lower.append((xx,2.5,zz));upper.append((xx,roof_height(xx,zz)-1,zz))
        for points in [[lower[0],upper[0],upper[1],lower[1]],
                       [lower[3],upper[3],upper[2],lower[2]],
                       [upper[0],upper[2],upper[3],upper[1]],
                       [lower[1],lower[3],lower[2],lower[0]]]:wall.polygon(points,'GlassLight',True)
    g.merge(slab(perimeter,roof_height,1.1,'Pearl'))
    for i in range(0,len(perimeter),4):
        x,z=perimeter[i];xx=(x+10)*.94-10;zz=(z+70)*.9-70;top=roof_height(xx,zz)-1
        g.box((xx,(top+2.45)/2,zz),(.65,top-2.45,.65),'Pearl')
    for i,p in enumerate(perimeter):
        q=perimeter[(i+1)%len(perimeter)]
        g.beam((p[0],roof_height(*p)+.12,p[1]),(q[0],roof_height(*q)+.12,q[1]),.35,'Silver',4)
    a.put('Urbana_complete_curved_clubhouse',g,section='Clubhouse',role='PodiumEnvelope')
    a.put('Urbana_clubhouse_glazing',wall,section='Clubhouse')
    g=Geometry();ellipse(g,(80,2.3,-60),29,17,1.2,'Pearl',48)
    ellipse(g,(80,3,-60),26.5,14.5,.3,'Water',48)
    ellipse(g,(70,3.5,-61),7,5,1,'Stone',24)
    ellipse(g,(70,4.15,-61),6.4,4.4,.35,'Leaf',24)
    for x in [58,72,86,100]:
        g.box((x,2,-80),(3.2,1.5,6),'Louvre');g.box((x,2.9,-80),(3,.35,5),'Pearl')
    ellipse(g,(0,1.65,-113),29,20,.6,'Asphalt',48)
    ellipse(g,(0,2.05,-113),16,11,.8,'Stone',40)
    ellipse(g,(0,2.6,-113),14,9,.35,'Leaf',40)
    ellipse(g,(0,3.4,-113),4,3,1.4,'Stone',24)
    g.box((0,2,-92),(38,1.5,8),'Stone')
    for x in [-180,180]:g.box((x,1.7,42),(12,.5,170),'Leaf')
    a.put('Urbana_pool_roundabout_landscape',g,section='Clubhouse')
    a.text('URBANA',(0,3,-96.3),3.2,32,section='Clubhouse')
    return a.finish()
