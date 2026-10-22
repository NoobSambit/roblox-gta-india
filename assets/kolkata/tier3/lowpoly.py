"""Original Tier 3 geometry. Stud-space, Y up, street front -Z.

Closed low-resolution components are grouped by material without welding separate
solids together. This avoids the shared-edge defects of globally welded boxes.
"""
import math

def rotate(p, a):
    c,s=math.cos(a),math.sin(a)
    return (c*p[0]+s*p[2],p[1],-s*p[0]+c*p[2])

def add(a,b):return tuple(x+y for x,y in zip(a,b))
def blender_point(p):return (p[0],-p[2],p[1])

class Geometry:
    def __init__(self):self.groups={}

    def solid(self, vertices, faces, role):
        v,f=self.groups.setdefault(role,([],[]));offset=len(v)
        v.extend(vertices);f.extend(tuple(i+offset for i in face) for face in faces)

    def box(self, pos, size, role='Body', angle=0):
        w,h,d=(s/2 for s in size)
        assert min(size)>0
        v=[(-w,-h,-d),(w,-h,-d),(w,h,-d),(-w,h,-d),(-w,-h,d),(w,-h,d),(w,h,d),(-w,h,d)]
        self.solid([add(rotate(p,angle),pos) for p in v],
            [(0,3,2,1),(4,5,6,7),(0,4,7,3),(1,2,6,5),(0,1,5,4),(3,7,6,2)],role)

    def prism(self, polygon, low, high, role='Body'):
        # Polygon is XZ footprint. Winding is corrected per closed solid in Blender.
        n=len(polygon)
        self.solid([(x,low,z) for x,z in polygon]+[(x,high,z) for x,z in polygon],
            [tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],role)

    def profile(self, polygon, depth, pos, role='Trim', angle=0):
        n=len(polygon)
        v=[add(rotate((x,y,z),angle),pos) for z in [-depth/2,depth/2] for x,y in polygon]
        self.solid(v,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],role)

    def cylinder(self, pos, radius, height, role='Dark', segments=8):
        p=[(pos[0]+radius*math.cos(i*math.tau/segments),pos[2]+radius*math.sin(i*math.tau/segments)) for i in range(segments)]
        self.prism(p,pos[1]-height/2,pos[1]+height/2,role)

    def facebox(self,x,y,z,size,role='Dark',angle=0,origin=(0,0,0)):
        self.box(add(rotate((x,y,z),angle),origin),size,role,angle)

    def window(self,x,y,w=4.1,h=6.5,style='modern',surface=0,angle=0,origin=(0,0,0),frame=True):
        def b(xx,yy,zz,size,role):self.facebox(xx,yy,zz,size,role,angle,origin)
        if frame:b(x,y,surface-.11,(w+.55,h+.55,.26),'Trim')
        panel='Accent' if style=='old' else 'Dark'
        b(x,y,surface-.28,(w,h,.18),panel)
        if style=='old':
            b(x,y,surface-.4,(.16,h,.14),'Dark')
            b(x,y-h*.1,surface-.4,(w,.18,.14),'Dark')

    def arched_panel(self,x,y,w,h,surface=0,angle=0,origin=(0,0,0)):
        # Six-segment silhouette, no dense moulded arch or carved ornament.
        for extra,role,z in [(.28,'Trim',-.12),(0,'Accent',-.3)]:
            r=w/2+extra;base=-h/2-extra;spring=h/2-w/2
            p=[(-r,base),(r,base)]+[(r*math.cos(i*math.pi/6),spring+r*math.sin(i*math.pi/6)) for i in range(7)]
            self.profile(p,.22,add(rotate((x,y,surface+z),angle),origin),role,angle)

    def balcony(self,x,level,w,depth,front,style='modern',angle=0,origin=(0,0,0),posts=False):
        def b(xx,yy,zz,size,role):self.facebox(xx,yy,zz,size,role,angle,origin)
        rear=front+.25;edge=front-depth
        b(x,level,front-depth/2,(w,.55,depth+.5),'Trim')
        if style=='modern':
            b(x,level+1.7,edge,(w,2.9,.38),'Body')
            for sign in [-1,1]:b(x+sign*(w/2-.19),level+1.7,(rear+edge)/2,(.38,2.9,rear-edge),'Body')
            b(x,level+3.22,edge,(w+.08,.16,.5),'Trim')
        else:
            for yy in [level+1.25,level+3.15]:
                b(x,yy,edge,(w,.22,.22),'Accent')
                for sign in [-1,1]:b(x+sign*(w/2-.14),yy,(rear+edge)/2,(.22,.22,rear-edge),'Accent')
            for xx in [x-w/2+.15,x+w/2-.15]:b(xx,level+1.7,edge,(.28,3.2,.28),'Accent')
            if posts:
                for xx in [x-w/2+.25,x+w/2-.25]:b(xx,level+6.08,edge+.12,(.48,12,.48),'Trim')

    def wrap_gallery(self,width,depth,level,canopy=False):
        # A single L-shaped slab closes the corner; separate intersecting slabs
        # would leave an uncovered corner and coplanar faces at the meeting point.
        x=width/2;front=-depth/2;back=depth/2;over=3.2
        plan=[(-x-.5,front+.2),(x-.2,front+.2),(x-.2,back+.4),
              (x+over,back+.4),(x+over,front-1.7),(x+1.7,front-over),(-x-.5,front-over)]
        self.prism(plan,level-.275,level+.275,'Trim')
        if canopy:return
        outer=[(-x-.4,front-over),(x+1.7,front-over),(x+over,front-1.7),(x+over,back+.3)]
        for height in [1.25,3.15]:
            for a,b in zip(outer,outer[1:]):
                dx,dz=b[0]-a[0],b[1]-a[1]
                self.box(((a[0]+b[0])/2,level+height,(a[1]+b[1])/2),
                         (math.hypot(dx,dz),.22,.22),'Accent',math.atan2(-dz,dx))
        for xx,zz in outer:
            self.box((xx,level+6.08,zz),(.48,12,.48),'Trim')
            self.box((xx,level+1.7,zz),(.28,3.2,.28),'Accent')

    def sheet_roof(self,x,z,w,d,y,role='Roof',ridges=7,slope=.035):
        # One integrated shallow corrugation profile extruded along the roof.
        top=[]
        for i in range(ridges*2+1):
            xx=x-w/2+w*i/(ridges*2)
            top.append((xx,y+(.1 if i%2 else 0)))
        n=len(top);v=[]
        for zz in [z-d/2,z+d/2]:
            v.extend((xx,yy+slope*(zz-z),zz) for xx,yy in top)
            v.extend((xx,yy-.18+slope*(zz-z),zz) for xx,yy in top)
        f=[];stride=2*n
        for i in range(n-1):
            f.extend([(i,i+1,stride+i+1,stride+i),(n+i,stride+n+i,stride+n+i+1,n+i+1),
                      (i,n+i,n+i+1,i+1),(stride+i,stride+i+1,stride+n+i+1,stride+n+i)])
        f.extend([(0,stride,stride+n,n),(n-1,2*n-1,2*stride-1,stride+n-1)])
        self.solid(v,f,role)
