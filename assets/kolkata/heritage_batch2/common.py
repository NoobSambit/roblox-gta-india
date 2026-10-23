"""Original reference-led heritage modules. Coordinates: stud X/Y(up)/Z."""
import bpy
import math
import json
import sys
from pathlib import Path
from mathutils import Vector

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
sys.path.insert(0,str(BASE.parent/'tier1'))
import pipeline
from pipeline import Asset,Geometry as G
from geometry import bv,rotate
from landmark_refinements import slab

pipeline.COLORS.update(HeritageRed='A23E32',HeritageRedLight='B6503F',HeritageCream='DED2B5',
    HeritageWhite='EBE5D4',HeritageOchre='CDB98B',HeritageSlate='485459',HeritageGlass='2D4546',
    HeritageShutter='B8C4B3',HeritageIron='3C5550',HeritageStone='9E9585',HeritagePaving='B2A799',
    HeritageGold='B99A50',HeritageDark='343532')


def prism(points,depth,z,role='HeritageCream'):
    g=G();front=[(x,y,z-depth/2) for x,y in points];back=[(x,y,z+depth/2) for x,y in points]
    g.polygon(front,role);g.polygon(list(reversed(back)),role)
    for i in range(len(points)):
        j=(i+1)%len(points);g.polygon([front[i],back[i],back[j],front[j]],role)
    return g


def disk(x,y,z,r,role='HeritageCream',n=16):
    return prism([(x+r*math.cos(i*math.tau/n),y+r*math.sin(i*math.tau/n)) for i in range(n)],.22,z,role)


def arch_fill(w,h,z=0,role='HeritageGlass',depth=.25,n=12):
    r=w/2;s=h-r
    points=[(-r,0),(r,0)]+[(r*math.cos(i*math.pi/n),s+r*math.sin(i*math.pi/n)) for i in range(n+1)]
    return prism(points,depth,z,role)


def window(w=5.4,h=11,arched=True,shutters=True,trim='HeritageCream',balcony=False):
    g=G()
    if arched:
        g.merge(arch_fill(w,h,-.2));g.arch(w,h-w/2,.32,.6,(0,0,-.4),trim,12)
        # Fanlight spokes terminate in the actual arch, with a central transom.
        spring=h-w/2;g.box((0,spring,-.55),(w,.18,.24),trim)
        for t in [math.pi/4,math.pi/2,math.pi*3/4]:
            g.beam((0,spring,-.56),(w*.47*math.cos(t),spring+w*.47*math.sin(t),-.56),.065,trim,4)
    else:
        g.box((0,h/2,-.2),(w,h,.25),'HeritageGlass')
        for x in [-w/2-.16,w/2+.16]:g.box((x,h/2,-.4),(.32,h+.5,.6),trim)
        g.box((0,h+.15,-.4),(w+.65,.3,.6),trim)
    g.box((0,-.22,-.55),(w+1.2,.5,1.4),trim)
    g.box((0,h*.42,-.5),(.14,h*.8,.3),trim)
    for y in [h*.22,h*.43,h*.65]:g.box((0,y,-.51),(w,.12,.26),trim)
    if shutters:
        sh=h-w/2-.35 if arched else h-.35
        for sign in [-1,1]:
            x=sign*w*.285;g.box((x,sh/2,-.67),(w*.4,sh,.22),'HeritageShutter')
            for j in range(7):g.box((x,(j+.7)*sh/8,-.82),(w*.36,.14,.16),trim)
            for dx in [-w*.2,w*.2]:g.box((x+dx,sh/2,-.85),(.14,sh+.1,.2),trim)
    if balcony:
        g.box((0,-.48,-1.2),(w+2,.5,3.1),trim)
        g.merge(balustrade(w+1.5,2.3,spacing=1.6,role=trim).transformed((0,-.2,-2.5)))
        for x in [-w*.4,w*.4]:g.merge(prism([(x-.3,-.7),(x+.3,-.7),(x+.3,-2),(x-.3,-1.4)],1.6,-.5,trim))
    return g


def balustrade(w,height=2.5,spacing=1.8,role='HeritageCream',end_posts=True):
    g=G();g.box((0,.15,0),(w,.3,.65),role);g.box((0,height,0),(w+.25,.35,.85),role)
    n=max(2,round(w/spacing))
    for i in range(n+1 if end_posts else n):
        x=-w/2+w*i/n
        g.lathe([(0,.22),(.25,.22),(.65,.15),(height*.55,.25),(height-.2,.15),(height,.22)],6,role,(x,.25,0))
    return g


def column(height=34,r=1.2,role='HeritageCream',corinthian=True):
    g=G();g.box((0,.3,0),(r*3,.6,r*3),role)
    g.lathe([(0,r*1.23),(.3,r*1.23),(.6,r*1.05),(1,r),(height-2.6,r*.85),
             (height-2.3,r*1.03),(height-1.9,r*1.12)],16,role,(0,.6,0))
    g.box((0,height-.2,0),(r*3.2,.5,r*3.2),role)
    if corinthian:
        for side in range(4):
            angle=side*math.pi/2
            for sign in [-1,1]:
                q=prism([(sign*.1,height-2.2),(sign*r*.95,height-2.1),(sign*r*1.1,height-1.15),(sign*r*.5,height-.5)],r*.35,-r*.85,role)
                g.merge(q.transformed(angle=angle))
                p=rotate((sign*r*.95,height-.9,-r*.9),angle)
                g.ellipsoid(p,(r*.38,r*.36,r*.3),role,8,4)
    else:
        g.lathe([(height-1.9,r*1.12),(height-1.4,r*1.25),(height-.7,r*1.3)],16,role)
    return g


def pediment(w,base,rise,z,field='HeritageRed',trim='HeritageCream'):
    g=prism([(-w/2,base),(w/2,base),(0,base+rise)],1.4,z,field)
    g.box((0,base-.1,z-.25),(w+1.5,.9,3),trim)
    for sign in [-1,1]:
        x=sign*w/2;v=Vector((-x,rise,0));length=v.length
        nx=-v.y/length*.45;ny=v.x/length*.45
        g.merge(prism([(x+nx,base+ny),(nx,base+rise+ny),(-nx,base+rise-ny),(x-nx,base-ny)],2.4,z-.6,trim))
        for i in range(1,12):
            t=i/12;g.box((x*(1-t),base+rise*t-.85,z-.85),(.55,.65,2),trim)
    return g


def cornices(w,d,ys,center=(0,0,0),role='HeritageCream',dentils=True):
    g=G();cx,_,cz=center
    for y in ys:
        for dy,extra,h in [(0,0,.5),(.6,.8,.55),(1.2,1.9,.45)]:g.box((cx,y+dy,cz),(w+extra,h,d+extra),role)
        if dentils:
            for side in [0,1,3]:
                width=w if side%2==0 else d;depth=d if side%2==0 else w;angle=side*math.pi/2
                n=round(width/4.5)
                for i in range(n):
                    p=rotate((-width/2+(i+.5)*width/n,y-.5,-depth/2-.25),angle)
                    g.box((p[0]+cx,p[1],p[2]+cz),(.8,.6,1),role,angle)
    return g


def mansard(w,d,bottom,rise):
    g=G();lo=[(-w/2,bottom,-d/2),(w/2,bottom,-d/2),(w/2,bottom,d/2),(-w/2,bottom,d/2)]
    hi=[(-w/2+4,bottom+rise,-d/2+6),(w/2-4,bottom+rise,-d/2+6),(w/2-4,bottom+rise,d/2-6),(-w/2+4,bottom+rise,d/2-6)]
    g.polygon(list(reversed(lo)),'HeritageSlate');g.polygon(hi,'HeritageSlate')
    for i in range(4):j=(i+1)%4;g.polygon([lo[i],hi[i],hi[j],lo[j]],'HeritageSlate')
    return g


def roof_iron(w,height=3):
    g=G();g.box((0,.2,0),(w,.25,.3),'HeritageIron');g.box((0,height-.4,0),(w,.18,.25),'HeritageIron')
    n=round(w/3)
    for j in range(n+1):
        x=-w/2+j*w/n;g.cylinder((x,height/2+.3,0),.09,height+.6,'HeritageIron',5)
        g.lathe([(0,.15),(.45,0)],5,'HeritageIron',(x,height+.6,0))
        if j<n:
            cx=x+w/n/2;r=min(1.1,w/n*.4)
            for i in range(8):
                t=i*math.tau/8;tt=(i+1)*math.tau/8
                g.beam((cx+r*math.cos(t),height*.5+r*math.sin(t),0),
                    (cx+r*math.cos(tt),height*.5+r*math.sin(tt),0),.065,'HeritageIron',4)
    return g


def figure(height=5,pose=0):
    g=G();g.box((0,.15,0),(1.8,.3,1.6),'HeritageCream')
    g.lathe([(0,.7),(height*.2,.65),(height*.48,.38),(height*.65,.6)],8,'HeritageCream',(0,.3,0))
    torso_top=.3+height*.65;head_bottom=height*.84-.48
    g.cylinder((0,(torso_top+head_bottom)/2,0),.15,max(.15,head_bottom-torso_top+.15),'HeritageCream',6)
    g.ellipsoid((0,height*.84,0),(.38,.48,.38),'HeritageCream',10,5)
    for sign in [-1,1]:
        p=(sign*.5,height*.63,0);q=(sign*.9,height*(.82 if pose==0 else .48),.1)
        g.beam(p,q,.19,'HeritageCream',6);g.ellipsoid(q,(.22,.23,.22),'HeritageCream',6,3)
    return g


def clock(r=2.5):
    g=disk(0,0,0,r,'HeritageWhite',32)
    for i in range(32):
        t=i*math.tau/32;tt=(i+1)*math.tau/32
        g.beam((r*math.cos(t),r*math.sin(t),-.2),(r*math.cos(tt),r*math.sin(tt),-.2),.13,'HeritageDark',5)
    for i in range(12):
        t=i*math.tau/12;g.beam((r*.74*math.sin(t),r*.74*math.cos(t),-.21),(r*.88*math.sin(t),r*.88*math.cos(t),-.21),.10,'HeritageDark',4)
    g.beam((0,0,-.28),(r*.15,r*.62,-.28),.12,'HeritageDark',5)
    g.beam((0,0,-.3),(-r*.55,r*.14,-.3),.1,'HeritageDark',5)
    return g


def arc_band(inner,outer,y,height,start=-math.pi/2,sweep=math.pi,steps=24,role='HeritageCream'):
    g=G()
    for i in range(steps):
        t=start+sweep*i/steps;tt=start+sweep*(i+1)/steps
        pts=[(r*math.cos(a),yy,r*math.sin(a)) for yy in [y,y+height] for r,a in [(inner,t),(outer,t),(outer,tt),(inner,tt)]]
        for ids in [(0,3,2,1),(4,5,6,7),(0,4,7,3),(1,2,6,5)]:g.polygon([pts[j] for j in ids],role)
        if i==0:g.polygon([pts[j] for j in [0,1,5,4]],role)
        if i==steps-1:g.polygon([pts[j] for j in [3,7,6,2]],role)
    return g


def frame(asset):
    bpy.context.view_layer.update()
    pts=[o.matrix_world@Vector(p) for o in asset.root.all_objects if o.type=='MESH' for p in o.bound_box]
    lo=Vector(tuple(min(p[i] for p in pts) for i in range(3)));hi=Vector(tuple(max(p[i] for p in pts) for i in range(3)))
    target=(lo+hi)/2;extent=max(hi-lo)
    for s in bpy.data.screens:
        for area in s.areas:
            if area.type!='VIEW_3D':continue
            sp=area.spaces.active;sp.clip_start=.5;sp.clip_end=4000;sp.shading.type='SOLID';sp.shading.color_type='MATERIAL'
            sp.overlay.show_floor=False;sp.overlay.show_extras=False;sp.overlay.show_axis_x=False;sp.overlay.show_axis_y=False
            sp.region_3d.view_location=target;sp.region_3d.view_distance=extent*1.25
            sp.region_3d.view_rotation=Vector((1,2,.95)).to_track_quat('Z','Y');sp.region_3d.view_perspective='ORTHO'


class HeritageAsset(Asset):
    def __init__(self,key,name):
        for previous in list(bpy.data.scenes):
            if previous.get('AssetId')=='KOL_T1_'+key.upper():previous.name='DRAFT_'+previous.name
        super().__init__(key,name,folder=BASE/key,export_dir=ROOT/'exports/kolkata_heritage_batch2')
        self.collisions=[];self.night=[]
    def box(self,key,pos,size,role='HeritageCream',section='01_Shell',collision=True):
        g=G();g.box(pos,size,role);self.put(key,g,section=section,role='Shell')
        if collision:self.collisions.append(dict(name=key,positionStuds=list(pos),sizeStuds=list(size),yaw=0))
    def foundation(self,w,d,front_extra=12):
        self.box('Foundation',(0,.2,-front_extra/2),(w+10,.8,d+front_extra+10),'HeritageStone','00_Foundation')
        g=G();g.box((0,.7,-front_extra/2),(w+9,.2,d+front_extra+9),'HeritagePaving')
        for sign in [-1,1]:g.box((sign*(w/2+4.2),.9,-front_extra/2),(.6,.4,d+front_extra+9),'HeritageCream')
        self.put('Forecourt_finish',g,section='00_Foundation')
    def steps(self,key,w,z,top,base=.8,count=7,tread=1.2,x=0):
        g=G()
        for i in range(count):
            y=base+(top-base)*(i+1)/count;zz=z-(count-i-.5)*tread
            g.box((x,(base+y)/2,zz),(w,y-base,tread+.02),'HeritageStone')
            self.collisions.append(dict(name=key+str(i),positionStuds=[x,(base+y)/2,zz],sizeStuds=[w,y-base,tread+.02],yaw=0))
        self.put(key,g,section='00_Foundation',role='WalkableSteps')
    def instance(self,key,geo,pos=(0,0,0),angle=0,section='03_Facades'):
        return self.put(key,geo if key not in self.cache else None,pos,angle,section=section)
    def save_live(self,label):
        self.scene['ProductionStage']=label;frame(self)
        bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Heritage_Batch2_Live.blend'),compress=True)
        print('LIVE_HERITAGE '+label,flush=True)
    def finish(self):
        from refinements import apply
        apply(self)
        row=super().finish();row['collisionBoxes']=self.collisions;row['nightLightingZones']=self.night
        row['nightLights']=self.light_specs
        row['scope']='Exterior landmark only; no Studio integration, full interiors or gameplay'
        (self.folder/'asset.json').write_text(json.dumps(row,indent=2),encoding='utf8')
        guides=bpy.data.collections.new('COLLISION_GUIDES__NOT_EXPORTED');self.scene.collection.children.link(guides);guides.hide_viewport=True
        for entry in self.collisions:
            obj=bpy.data.objects.new('COL_'+entry['name'],None);guides.objects.link(obj);obj.empty_display_type='CUBE'
            obj.location=bv(entry['positionStuds']);size=entry['sizeStuds'];obj.scale=(size[0]/2,size[2]/2,size[1]/2)
            obj['CollisionBoxStuds']=size
        bpy.data.libraries.write(str(self.folder/row['source']),{self.scene},fake_user=True,compress=True)
        self.save_live(self.name+' — exterior and modular exports ready for review')
        return row
