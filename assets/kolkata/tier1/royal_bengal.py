"""Royal Bengal hero exterior, staged for visible MCP authoring."""
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Vector

BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
from pipeline import Asset,Geometry,panel,ellipse,foundation,material
from geometry import rotate

ASSET=None
TIERS=[(172,94,2,32),(154,86,34,42),(130,76,76,88),(112,70,164,86),(116,72,250,25)]


def ochre_palette():
    mapping={'PaleStone':'RoyalOchre','Pearl':'RoyalTrim','Stone':'RoyalStone'}
    for mesh in {o.data for o in ASSET.root.all_objects if o.type=='MESH'}:
        for index,mat in enumerate(mesh.materials):
            if mat:
                role=mat.name.removeprefix('KOL_T1_').split('.')[0]
                if role in mapping:mesh.materials[index]=material(mapping[role])


def frame(target=(0,0,143),eye=(265,530,235)):
    for area in bpy.context.screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;sp.clip_start=1;sp.clip_end=5000;sp.shading.type='MATERIAL'
            sp.overlay.show_floor=False;sp.overlay.show_axis_x=False;sp.overlay.show_axis_y=False
            t=Vector(target);e=Vector(eye);sp.region_3d.view_rotation=(t-e).to_track_quat('-Z','Y')
            sp.region_3d.view_location=t;sp.region_3d.view_distance=(e-t).length
            region=next((r for r in area.regions if r.type=='WINDOW'),None)
            if region:
                with bpy.context.temp_override(area=area,region=region):bpy.ops.view3d.view_all(center=False)
                sp.region_3d.view_distance*=1.06


def begin():
    global ASSET
    old=bpy.data.scenes.get('KOL_T1_ROYAL')
    if old:old.name='Royal_Bengal_before_hero_rebuild'
    a=Asset('royal','ITC Royal Bengal / hero exterior');ASSET=a
    a.scene['ReviewStatus']='Hero exterior rebuild in progress'
    foundation(a,240,210)
    mass=Geometry()
    for i,(w,d,y,h) in enumerate(TIERS):
        if i==0:
            # True shallow arrival recess, open to the exterior, with a back
            # door plane. No room network or furnished lobby is constructed.
            for x in [-55,55]:mass.box((x,y+h/2,22),(62,h,d),'PaleStone')
            mass.box((0,y+h/2,32),(48,h,74),'PaleStone')
            mass.box((0,y+h-.7,22),(w,1.4,d),'PaleStone')
        else:mass.box((0,y+h/2,22),(w,h,d),'PaleStone')
        if i in [2,3]:
            front=22-d/2
            mass.box((0,y+h/2,front-2.7),(36,h,5.4),'Stone')
        for yy,extra,thick,mat in [(y+h-2,1.5,1,'Stone'),(y+h,4,1.3,'Pearl'),(y+h+1.2,7,.8,'PaleStone')]:
            mass.box((0,yy,22),(w+extra,thick,d+extra),mat)
        mass.box((0,y+h+.6,22),(w+5,.22,d+5),'Accent')
    a.put('RB_hero_massing',mass,section='01_Massing',role='BuildingEnvelope')
    # Central crown rises above the flanking pavilions.
    crown=Geometry();crown.box((0,278,19),(62,9,70),'PaleStone')
    crown.box((0,283,19),(66,1.1,73),'Pearl')
    for x in [-49,49]:
        crown.box((x,280,22),(19,12,74),'PaleStone')
        crown.box((x,286.5,22),(23,1.2,78),'Pearl')
    a.put('RB_crown_masses',crown,section='01_Massing',role='BuildingEnvelope')
    frame()
    print('ROYAL STAGE 1: wider stepped silhouette, central projection, recessed arrival and crown masses visible.',flush=True)
    return a


def window_module():
    g=Geometry();panel(g,0,4.6,-.15,4.6,6.8,'Glass')
    for x in [-2.65,2.65]:g.box((x,4.6,-.46),(.55,7.8,.65),'Pearl')
    g.box((0,8.8,-.45),(6.4,.65,.95),'PaleStone')
    g.box((0,9.2,-.55),(7,.35,1.25),'Pearl')
    g.box((0,1,-.7),(7,.55,1.8),'PaleStone')
    g.box((0,4.6,-.52),(.15,6.8,.22),'Graphite')
    g.box((0,5.6,-.52),(4.6,.14,.22),'Graphite')
    return g


def arch_module(width=10,spring=14):
    g=Geometry();r=width/2
    pts=[(-r,0,.25),(-r,spring,.25)]
    pts += [(r*math.cos(math.pi-i*math.pi/16),spring+r*math.sin(math.pi-i*math.pi/16),.25) for i in range(17)]
    pts += [(r,0,.25)]
    g.polygon(pts,'Glass')
    g.arch(width,spring,.85,1.1,mat='Pearl',segments=12)
    g.box((0,0,-.2),(width+2,.8,2),'PaleStone')
    for x in [-width*.26,0,width*.26]:g.box((x,spring*.65,-.4),(.2,spring*1.25,.35),'Graphite')
    g.box((0,spring*.65,-.4),(width,.25,.35),'Graphite')
    g.box((0,spring+.6,-.65),(1.1,2,1.1),'PaleStone')
    return g


def facades():
    a=ASSET;assert a
    window=window_module()
    for tier,(w,d,bottom,height) in enumerate(TIERS[1:4],start=1):
        for side in range(4):
            width=w if side%2==0 else d;depth=d if side%2==0 else w;angle=side*math.pi/2
            count=round(width/10)
            for floor in range(round(height/10)):
                yy=bottom+2+floor*10
                for j in range(count):
                    xx=-width/2+(j+.5)*width/count
                    projection=5.4 if tier in [2,3] and side==0 and abs(xx)<18 else 0
                    p=rotate((xx,yy,-depth/2-.9-projection),angle)
                    pos=(p[0],p[1],p[2]+22)
                    key='RB_standard_window'
                    a.put(key,window if key not in a.cache else None,pos,angle,section='02_Window_Bays')
    # Large ground arches establish a legible hotel frontage and approach scale.
    arch=arch_module(10,15)
    for side in range(4):
        width=172 if side%2==0 else 94;depth=94 if side%2==0 else 172;angle=side*math.pi/2
        count=round(width/15)
        for j in range(count):
            xx=-width/2+(j+.5)*width/count
            if side==0 and abs(xx)<25:continue
            p=rotate((xx,5,-depth/2-1),angle)
            a.put('RB_ground_arch',arch if 'RB_ground_arch' not in a.cache else None,(p[0],p[1],p[2]+22),angle,section='03_Arcades')
    upper=arch_module(6.3,6)
    for side in [0,2]:
        angle=side*math.pi/2
        for x in range(-45,46,9):
            p=rotate((x,254,-37.5),angle)
            a.put('RB_crown_arch',upper if 'RB_crown_arch' not in a.cache else None,(p[0],p[1],p[2]+22),angle,section='03_Arcades')
    # Restrained masonry joints are concentrated around player-level stonework.
    g=Geometry()
    for y in range(4,33,2):
        for x,w in [(-56,59),(56,59)]:g.box((x,y,-25.55),(w,.12,.16),'Stone')
        for side in [-1,1]:g.box((side*86.55,y,22),(.16,.12,94),'Stone')
    for row,y in enumerate(range(5,32,2)):
        for x in range(-84+row%2*4,85,8):
            if abs(x)<25:continue
            g.box((x,y,-25.55),(.12,1.8,.16),'Stone')
    a.put('RB_ground_rustication',g,section='03_Arcades')
    print('ROYAL STAGE 2: framed recessed bays, cross mullions, crown arches and player-height masonry joints added.',flush=True)


def column_module(height,radius=1):
    g=Geometry();g.box((0,.4,0),(radius*3.5,.8,radius*3.5),'PaleStone')
    g.lathe([(.8,radius*1.5),(1.3,radius*1.12),(height-2.3,radius*.92),(height-1.3,radius*1.4)],10,'Pearl')
    g.box((0,height-.95,0),(radius*3,.8,radius*3),'Pearl')
    g.box((0,height-.3,0),(radius*3.6,.6,radius*3.6),'PaleStone')
    return g


def signature():
    a=ASSET;assert a
    # Strong giant-order lower colonnade, with visible depth in front of bays.
    # Base cornice top = 35.6, beam underside = 68.95. Both ends embed
    # 0.05 stud, so column heights derive from their actual bearing surfaces.
    col=column_module(33.45,1)
    for x in [-68,-56,-44,-32,32,44,56,68]:a.put('RB_column_33_45',col if 'RB_column_33_45' not in a.cache else None,(x,35.55,-24),section='04_Columns_Loggias')
    g=Geometry();g.box((0,70,-23),(151,2.1,8),'PaleStone')
    for x in [-68,-56,-44,-32,32,44,56,68]:g.box((x,72,-24),(5,1.3,6),'Pearl')
    for width,depth,bottom,height in TIERS[1:4]:
        y=bottom+height+1.6
        for z in [22-depth/2-2,22+depth/2+2]:
            g.box((0,y+3,z),(width+4,.65,1.2),'Pearl')
            for x in range(int(-width/2+2),int(width/2),4):
                g.box((x,y+1.35,z),(.65,2.8,.65),'PaleStone')
        for x in [-width/2-2,width/2+2]:
            g.box((x,y+3,22),(1.2,.65,depth+4),'Pearl')
            for z in range(int(22-depth/2+2),int(22+depth/2),4):g.box((x,y+1.35,z),(.65,2.8,.65),'PaleStone')
        # Dentils sit below the major cornices, where their shadows can read.
        for x in range(int(-width/2+1),int(width/2),4):g.box((x,bottom+height-1.2,22-depth/2-1.3),(.9,1.1,1.5),'Pearl')
    for sign in [-1,1]:
        for y,height,outer in [(82,25,67),(124,26,67),(171,27,58),(213,28,58)]:
            x=sign*outer
            g.box((x,y-.8,22),(12,1.2,80 if outer==67 else 74),'PaleStone')
            g.box((x,y+height,22),(13,1.4,81 if outer==67 else 75),'Pearl')
            for z in ([-16,3,41,60] if outer==67 else [-13.2,3,41,57.2]):
                key='RB_loggia_column_'+str(height)
                a.put(key,column_module(height-.4,.85) if key not in a.cache else None,(x,y-.25,z),section='04_Columns_Loggias')
    # Recessed upper-pavilion openings and substantial corner piers.
    for x in [-49,49]:
        for z,angle in [(-15.7,0),(59.7,math.pi)]:
            panel(g,x,280,z,13,7,'Graphite',angle)
            for dx in [-7,0,7]:g.box((x+dx,280,z-1 if z<0 else z+1),(1,9,1.4),'Pearl')
    # Pediment is a deep prism with a moulded outline, not a pasted triangle.
    w=67;y=283;z=-18;h=14;d=5
    pts=[(-w/2,y,z-d/2),(w/2,y,z-d/2),(0,y+h,z-d/2),(-w/2,y,z+d/2),(w/2,y,z+d/2),(0,y+h,z+d/2)]
    for ids in [(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)]:g.polygon([pts[i] for i in ids],'PaleStone')
    for start,end in [((-w/2,y,z-3),(0,y+h,z-3)),((0,y+h,z-3),(w/2,y,z-3))]:g.beam(start,end,.65,'Pearl',4)
    g.box((0,y,z-3),(w+2,1.2,1.3),'Pearl')
    g.box((0,280.4,-18.8),(66,.25,.5),'Accent')
    a.put('RB_cornices_balustrades_pediment',g,section='05_Crown_Cornices')
    a.text('ITC ROYAL BENGAL',(0,276,-20.4),4.6,61,section='05_Crown_Cornices')
    print('ROYAL STAGE 3: giant columns, open corner loggias, dentils, balustrades, upper pavilions and moulded pediment added.',flush=True)


def arrival():
    a=ASSET;assert a
    g=Geometry()
    # The vehicle lane passes under a 17-stud-clear portico. Central bays are
    # kept free; the shallow recess behind it is an exterior arrival alcove.
    for x in [-25,-19,19,25]:
        a.put('RB_arrival_column',column_module(18,1.15) if 'RB_arrival_column' not in a.cache else None,(x,2.15,-47),section='06_Arrival')
    g.box((0,1.7,-39),(64,1,31),'PaleStone')
    g.box((0,21,-39),(60,2,27),'PaleStone');g.box((0,22.4,-39),(63,.9,30),'Pearl')
    g.box((0,23.1,-39),(65,.55,31),'PaleStone')
    for x in range(-28,29,4):g.box((x,20,-53),(.9,1.3,1.3),'Pearl')
    g.box((0,22,-53.8),(62,.24,.45),'Accent')
    panel(g,0,10,-5.9,20,15,'GlassLight')
    for x in [-6,0,6]:g.box((x,10,-6.2),(.3,15,.4),'Bronze')
    for i in range(4):g.box((0,1.5+i*.35,-56+i*2),(54,.35,13-i*2),'Pearl')
    # Solid exterior pavements leave usable side/rear approach space.
    for x in [-101,101]:g.box((x,1.5,23),(20,.35,139),'Asphalt')
    g.box((0,1.5,90),(222,.35,20),'Asphalt')
    ellipse(g,(0,2,-78),30,12,1.2,'Stone',48)
    ellipse(g,(0,2.75,-78),27.5,9.5,.3,'Water',48)
    ellipse(g,(0,3.6,-78),7,4,1.4,'PaleStone',24)
    for x in [-78,78]:
        g.box((x,2.2,-51),(22,1.5,24),'Stone');g.box((x,3.3,-51),(20,.7,22),'Leaf')
    # A legible service door is reserved on the right return for future heist
    # routing; it is a closed exterior door and carries no gameplay script.
    panel(g,87.3,9,43,13,13,'Graphite',-math.pi/2)
    g.box((88,16,43),(2,1.3,17),'Pearl')
    a.put('RB_portico_fountain_and_approaches',g,section='06_Arrival',role='GroundAndPortico')
    a.sockets.update(MainEntrance={'positionStuds':[0,2.7,-6],'clearWidthStuds':20,'clearHeightStuds':15},
        PorticoLane={'positionStuds':[0,2.2,-46],'clearWidthStuds':36,'clearHeightStuds':17},
        FutureServiceDoor={'positionStuds':[87.3,2.7,43],'clearWidthStuds':13,'clearHeightStuds':13,'activeGameplay':False})
    a.scene['ReviewStatus']='Hero exterior ready for focused visual review; gameplay and full interiors not built'
    frame()
    print('ROYAL STAGE 4: portico, arrival recess, fountain, compact grounds and future service-door metadata added.',flush=True)


def finish():
    a=ASSET;ochre_palette();row=a.finish()
    path=BASE/'batch-manifest.json';rows=json.loads(path.read_text(encoding='utf8')) if path.exists() else []
    rows=[r for r in rows if r['assetId']!='KOL_T1_ROYAL']+[row]
    path.write_text(json.dumps(rows,indent=2),encoding='utf8')
    return row


if __name__=='__main__':begin();facades();signature();arrival();finish()
