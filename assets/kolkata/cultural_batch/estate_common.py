"""Original reusable compound architecture; author coordinates are X/Y-up/Z studs."""
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Vector

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
sys.path.insert(0,str(BASE.parent/'tier1'))
sys.path.insert(0,str(BASE.parent/'heritage_batch2'))
import common as H
import pipeline
from pipeline import Asset,Geometry as G
from geometry import bv,rotate
from landmark_refinements import slab

pipeline.COLORS.update(EstateBrick='97563C',EstateBrickLight='B16E50',EstateRed='AF4133',
    EstateIvory='E5D8BC',EstateWhite='EDE8D8',EstateGreen='205B44',EstateBlind='356E50',
    EstateTaupe='95846A',EstateStone='9C9282',EstatePaving='B8A993',EstateLawn='557744',
    EstateMaroon='74313A',EstateGold='C2A25B',EstateFlower='BE538B',EstateGlow='F5D392',
    EstatePlaster='CABC96',EstateRoof='A3987C',EstateDome='B7A571')


def recolor(g,**mapping):
    g.mat=[mapping.get(m,m) for m in g.mat]
    return g


def window(w=6,h=12,arched=True,green=False):
    return recolor(H.window(w,h,arched,True,trim='EstateIvory'),
        HeritageShutter='EstateGreen' if green else 'EstateTaupe',HeritageGlass='HeritageDark')


def arch_wall(w,h,opening,spring,depth=1.2,role='EstateIvory'):
    """Solid concave spandrel/piers; the arch is an actual opening."""
    r=opening/2
    pts=[(-w/2,h),(w/2,h),(w/2,0),(r,0),(r,spring)]
    pts.extend((r*math.cos(i*math.pi/12),spring+r*math.sin(i*math.pi/12)) for i in range(1,13))
    pts.extend([(-r,0),(-w/2,0)])
    return H.prism(pts,depth,0,role)


def cornice(w,d,y,role='EstateIvory',dentils=False):
    # Project the skirt from plaster instead of drawing two identical side planes.
    return H.cornices(w+.36,d+.36,[y],role=role,dentils=dentils)


def brick_column(height=17.5,r=.8):
    g=G();g.box((0,.35,0),(r*3,.7,r*3),'EstateIvory')
    g.lathe([(0,r*1.15),(.4,r*1.15),(.7,r),(height-1.1,r*.88)],12,'EstateBrick',(0,.65,0))
    for y in [.9,height-1.1]:g.cylinder((0,y,0),r*1.2,.4,'EstateIvory',12)
    g.box((0,height-.18,0),(r*3.1,.5,r*3.1),'EstateIvory')
    # Sparse proud bands convey brick coursework without individual bricks.
    for i in range(1,9):g.cylinder((0,1+i*(height-2.5)/9,0),r*1.015,.10,'EstateBrickLight',12)
    return g


def paired_post(height=17.5,role='EstateRed'):
    g=G()
    for x in [-.65,.65]:
        g.box((x,.35,0),(1.05,.7,1.1),'EstateIvory')
        g.box((x,height/2,0),(.65,height-.6,.75),role)
        g.box((x,height-.3,0),(1.1,.6,1.1),'EstateIvory')
        g.box((x,height-1.1,0),(.85,.45,.9),'EstateIvory')
    return g


def grille(w,h=3):
    g=G()
    for y in [.15,h]:g.box((0,y,0),(w,.22,.3),'EstateWhite')
    n=round(w/1.7)
    for i in range(n+1):
        x=-w/2+w*i/n;g.box((x,h/2,0),(.10,h,.20),'EstateWhite')
        if i<n:
            cx=x+w/n/2
            for pts in [[(cx,h*.12,0),(x,h*.52,0),(cx,h*.9,0)],[(cx,h*.12,0),(x+w/n,h*.52,0),(cx,h*.9,0)]]:
                for a,b in zip(pts,pts[1:]):g.beam(a,b,.05,'EstateWhite',4)
    return g


def blind(w,h=6):
    g=G();g.box((0,h/2,0),(w,h,.20),'EstateBlind')
    for i in range(10):g.box((0,(i+.5)*h/10,-.15),(w+.04,.09,.14),'EstateGreen')
    for x in [-w*.35,w*.35]:g.box((x,h/2,-.25),(.10,h,.1),'EstateTaupe')
    return g


def urn(flowers=False):
    g=G();g.lathe([(0,.7),(.25,.85),(.6,.65),(1.9,1.0),(2.3,1.12),(2.5,1.05)],10,'EstateBrick')
    for i in range(7):
        t=i*math.tau/7;x=math.cos(t);z=math.sin(t)
        g.beam((0,2.2,0),(x*1.3,3.5,z*1.3),.08,'Leaf',4)
        g.ellipsoid((x*1.0,3.0,z*1.0),(.75,.55,.6),'LeafLight',7,3)
        if flowers:g.ellipsoid((x*1.2,3.5,z*1.2),(.38,.25,.38),'EstateFlower',7,3)
    return g


def lantern():
    g=G();g.box((0,.2,0),(1.8,.4,1.8),'EstateStone')
    g.lathe([(0,.25),(.5,.28),(6,.13),(6.4,.4)],8,'HeritageIron',(0,.4,0))
    g.box((0,7.3,0),(.9,1.5,.9),'EstateGlow')
    for x,z in [(-.53,-.53),(.53,-.53),(-.53,.53),(.53,.53)]:g.box((x,7.3,z),(.12,1.8,.12),'HeritageIron')
    g.box((0,8.2,0),(1.5,.25,1.5),'HeritageIron');g.lathe([(0,.8),(.65,0)],4,'HeritageIron',(0,8.3,0))
    return g


class Compound(Asset):
    def __init__(self,key,name):
        for scene in bpy.data.scenes:
            if scene.get('AssetId')=='KOL_T1_'+key.upper():scene.name='DRAFT_'+scene.name
        super().__init__(key,name,BASE/key,ROOT/'exports/kolkata_cultural')
        self.collisions=[];self.layout={};self.light_specs=[]

    def box(self,key,pos,size,role='EstateIvory',section='01_Shell',collision=True):
        g=G();g.box(pos,size,role);self.put(key,g,section=section,role='Shell')
        if collision:self.collisions.append(dict(name=key,positionStuds=list(pos),sizeStuds=list(size),yaw=0))

    def instance(self,key,geo,pos=(0,0,0),angle=0,section='03_Gallery'):
        return self.put(key,geo if key not in self.cache else None,pos,angle,section=section)

    def steps(self,key,w,z,top,base=.8,count=5,tread=1.2,x=0,angle=0):
        g=G()
        for i in range(count):
            y=base+(top-base)*(i+1)/count;zz=z-(count-i-.5)*tread
            p=rotate((0,(base+y)/2,zz-z),angle);p=(p[0]+x,p[1],p[2]+z)
            size=(w,y-base,tread+.03);g.box(p,size,'EstateStone',angle)
            self.collisions.append(dict(name=key+str(i),positionStuds=list(p),sizeStuds=list(size),yaw=angle))
        self.put(key,g,section='00_Grounds',role='WalkableSteps')

    def ground(self,w,d):
        self.box('Ground_foundation',(0,.05,0),(w,.9,d),'EstateStone','00_Grounds')
        self.box('Paved_ground',(0,.6,0),(w-1,.3,d-1),'EstatePaving','00_Grounds')

    def lawn(self,key,x,z,w,d):
        g=G();g.box((x,.92,z),(w,.34,d),'EstateLawn')
        for sign in [-1,1]:
            g.box((x+sign*(w/2+.35),.96,z),(.7,.42,d+1.4),'EstateStone')
            g.box((x,.96,z+sign*(d/2+.35)),(w,.42,.7),'EstateStone')
        self.put(key,g,section='00_Grounds')

    def wing(self,key,x,z,w,d,role='EstateBrick',section='01_Shell'):
        # Shallow room strip, only gallery floors/covers. No floor across a court.
        self.box(key+'_socle',(x,1.65,z),(w+1.6,1.8,d+1.6),'EstateStone',section)
        self.box(key+'_body',(x,20.62,z),(w,36.24,d),role,section)
        # Small authored steps at wing junctions prevent coincident top/bottom
        # caps where the moulded profiles return into another wing.
        joint=.06 if 'Side' in key or '_east' in key or '_west' in key else .12 if 'Rear' in key or '_rear' in key or '_north' in key else 0
        self.put(key+'_courses',cornice(w+joint*2,d+joint*2,3.0+joint,role='EstateIvory').transformed((x,0,z)),section=section)
        self.put(key+'_upper_belt',cornice(w+joint*2,d+joint*2,20.4+joint,role='EstateIvory').transformed((x,0,z)),section=section)
        self.put(key+'_cornice',cornice(w+joint*2,d+joint*2,38.7+joint,dentils=True).transformed((x,0,z)),section=section)
        self.box(key+'_roof',(x,40.3,z),(w-.2,.5,d-.2),'EstateBrickLight',section)

    def gallery(self,key,length,pos,angle=0,brick=False,white=False,section='03_Gallery',street=False):
        """Six-stud-deep usable two-level gallery with a solid room wall behind."""
        n=round(length/14);pitch=length/n;g=G()
        g.box((0,1.45,1.7),(length,1.4,6.4),'EstateStone')
        for y in [2.8,20.6,38.65]:g.box((0,y-.35,1.7),(length,.7,6.4),'EstateIvory')
        for y,h in [(1.45,1.4),(2.45,.7),(20.25,.7)]:
            p=rotate((0,y,1.7),angle);p=tuple(p[j]+pos[j] for j in range(3))
            self.collisions.append(dict(name=key+'_gallery_floor_'+str(y),positionStuds=list(p),sizeStuds=[length,h,6.4],yaw=angle))
        g.box((0,39.4,1.7),(length+1.3,.8,7.3),'EstateIvory')
        self.instance(key+'_floors',g,pos,angle,section)
        lower=arch_wall(pitch,17.5,pitch-1.6,10.6,1.4,'EstateRed' if street else 'EstateWhite' if white else 'EstateIvory')
        lower.arch(pitch-2.0,10.6,.25,1.7,(0,0,-.05),'EstateRed' if street else 'EstateIvory',12)
        # Upper posts and railing leave galleries open, as in the supplied photos.
        for i in range(n):
            local=(-length/2+(i+.5)*pitch,2.8,0);p=rotate(local,angle);p=tuple(p[j]+pos[j] for j in range(3))
            self.instance(key+'_lower_arch',lower,p,angle,section)
            rail=H.balustrade(pitch-2.3,2.7,2,'EstateIvory',False) if brick else grille(pitch-2.0,3)
            rp=rotate((local[0],20.65,-.2),angle);rp=tuple(rp[j]+pos[j] for j in range(3))
            self.instance(key+'_upper_rail',rail,rp,angle,section)
            if not brick:
                bp=rotate((local[0],31.8,-.1),angle);bp=tuple(bp[j]+pos[j] for j in range(3))
                self.instance(key+'_green_blind',blind(pitch-2.4,6.8),bp,angle,section)
        post=brick_column(17.5,.8) if brick else paired_post(17.5,'EstateWhite' if white else 'EstateRed')
        if street:
            post=G()
            for dx in [-.65,.65]:post.merge(recolor(brick_column(17.5,.45),EstateBrick='EstateRed',EstateBrickLight='EstateRed').transformed((dx,0,0)))
        for i in range(n+1):
            p=rotate((-length/2+i*pitch,20.6,0),angle);p=tuple(p[j]+pos[j] for j in range(3))
            self.instance(key+'_upper_column',post,p,angle,section)

    def night_light(self,name,pos,target,power=17000,range_=50):
        self.light_specs.append(dict(name=name,positionStuds=list(pos),targetStuds=list(target),
            rangeStuds=range_,brightness=1.7,angleDegrees=100,colorRGB=[255,218,170],blenderWatts=power,shadows=False))

    def parapet(self,key,length,pos,angle=0):
        """Reuse rail bays/pier masters while seating all ends into masonry."""
        n=max(1,round(length/16));pitch=length/n
        base=G();base.box((0,.17,0),(length+1.5,.34,1.7),'EstateIvory')
        self.instance(key+'_base',base,pos,angle,'04_Roofline')
        rail=H.balustrade(pitch-1.2,2.8,1.8,'EstateIvory',False)
        pier=G();pier.box((0,1.7,0),(1.6,3.4,1.8),'EstateIvory');pier.box((0,3.5,0),(2,.3,2.2),'EstateIvory')
        for i in range(n):
            p=rotate((-length/2+(i+.5)*pitch,.3,0),angle);p=tuple(p[j]+pos[j] for j in range(3))
            self.instance('Roof_rail_bay_'+str(round(pitch,4)),rail,p,angle,'04_Roofline')
        for i in range(n+1):
            p=rotate((-length/2+i*pitch,0,0),angle);p=tuple(p[j]+pos[j] for j in range(3))
            self.instance('Roof_rail_masonry_pier',pier,p,angle,'04_Roofline')

    def finish(self):
        rig=bpy.data.collections.new('NIGHT_LIGHTS__NOT_FBX');self.scene.collection.children.link(rig)
        fixture=G();fixture.box((0,.18,0),(1.6,.36,1.4),'EstateStone');fixture.box((0,.6,0),(1.1,.45,.8),'HeritageIron')
        fixture.box((0,.86,0),(.85,.12,.65),'EstateGlow')
        for spec in self.light_specs:
            if spec['positionStuds'][1]<5:self.instance('Ground_flood',fixture,(spec['positionStuds'][0],.75,spec['positionStuds'][2]),section='00_Grounds')
            data=bpy.data.lights.new(spec['name'],'SPOT');data.energy=spec['blenderWatts'];data.color=(1,.76,.49)
            data.spot_size=math.radians(100);data.spot_blend=.7;data.use_shadow=False
            data.use_custom_distance=True;data.cutoff_distance=spec['rangeStuds']
            obj=bpy.data.objects.new(spec['name'],data);rig.objects.link(obj);obj.location=bv(spec['positionStuds'])
            obj.rotation_euler=(Vector(bv(spec['targetStuds']))-obj.location).to_track_quat('-Z','Y').to_euler();obj['NightWatts']=spec['blenderWatts']
        mat=pipeline.material('EstateGlow');node=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        node.inputs['Emission Color'].default_value=(1,.7,.3,1);node.inputs['Emission Strength'].default_value=1.3
        row=super().finish();row.update(collisionBoxes=self.collisions,layout=self.layout,nightLights=self.light_specs,
            scope='Blender exterior/compound asset production. No Studio integration or gameplay.')
        (self.folder/'asset.json').write_text(json.dumps(row,indent=2),encoding='utf8')
        guides=bpy.data.collections.new('COLLISION_GUIDES__NOT_FBX');self.scene.collection.children.link(guides);guides.hide_viewport=True
        for entry in self.collisions:
            o=bpy.data.objects.new('COL_'+entry['name'],None);guides.objects.link(o);o.empty_display_type='CUBE'
            o.location=bv(entry['positionStuds']);s=entry['sizeStuds'];o.scale=(s[0]/2,s[2]/2,s[1]/2);o.rotation_euler.z=entry['yaw']
        H.frame(self);bpy.data.libraries.write(str(self.folder/row['source']),{self.scene},fake_user=True,compress=True)
        self.scene['ProductionStage']='Cultural compound exterior ready for review'
        bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Cultural_Batch_Live.blend'),compress=True)
        print('CULTURAL_READY '+self.key+' '+str(row['uniqueSourceTriangles'])+' unique / '+str(row['assembledTriangles'])+' placed',flush=True)
        return row
