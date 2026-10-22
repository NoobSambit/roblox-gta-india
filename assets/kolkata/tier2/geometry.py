"""Original reusable architecture primitives, shared by the Tier 2 library."""
import math
from mathutils import Vector
def bv(p): return (p[0],-p[2],p[1])

def rotate(p, angle):
    c, s = math.cos(angle), math.sin(angle)
    return (c*p[0] + s*p[2], p[1], -s*p[0] + c*p[2])

class Geometry:
    def __init__(self):
        self.v, self.f, self.mat, self.smooth = [], [], [], []

    def polygon(self, vertices, mat="Marble", smooth=False):
        offset = len(self.v)
        self.v.extend(vertices)
        self.f.append(tuple(range(offset, offset+len(vertices))))
        self.mat.append(mat)
        self.smooth.append(smooth)

    def box(self, pos, size, mat="Marble", angle=0):
        x,y,z=pos; w,h,d=(s/2 for s in size)
        points=[(-w,-h,-d),(w,-h,-d),(w,h,-d),(-w,h,-d),(-w,-h,d),(w,-h,d),(w,h,d),(-w,h,d)]
        points=[tuple(a+b for a,b in zip(rotate(p,angle),pos)) for p in points]
        for face in [(0,3,2,1),(4,5,6,7),(0,4,7,3),(1,2,6,5),(0,1,5,4),(3,7,6,2)]:
            self.polygon([points[i] for i in face],mat)

    def lathe(self, profile, segments=24, mat="Marble", center=(0,0,0), smooth=True, cap=True, start=0, sweep=2*math.pi):
        rings=[]
        closed=abs(sweep-2*math.pi)<0.001
        for y,r in profile:
            rings.append([(center[0]+r*math.cos(start+i*sweep/segments),center[1]+y,center[2]+r*math.sin(start+i*sweep/segments)) for i in range(segments+(0 if closed else 1))])
        for lower,upper in zip(rings,rings[1:]):
            for i in range(segments):
                j=(i+1)%len(lower)
                self.polygon([lower[i],upper[i],upper[j],lower[j]],mat,smooth)
        if cap:
            self.polygon(rings[0],mat)
            self.polygon(list(reversed(rings[-1])),mat)

    def cylinder(self,pos,r,h,mat="Marble",segments=12,r2=None):
        self.lathe([(-h/2,r),(h/2,r if r2 is None else r2)],segments,mat,pos)

    def ellipsoid(self,pos,size,mat="Marble",segments=12,rings=6):
        rows=[]
        for j in range(rings+1):
            phi=-math.pi/2+j*math.pi/rings
            rows.append([(pos[0]+size[0]*math.cos(phi)*math.cos(i*math.tau/segments),pos[1]+size[1]*math.sin(phi),pos[2]+size[2]*math.cos(phi)*math.sin(i*math.tau/segments)) for i in range(segments)])
        for a,b in zip(rows,rows[1:]):
            for i in range(segments):
                j=(i+1)%segments
                self.polygon([a[i],b[i],b[j],a[j]],mat,True)

    def beam(self,a,b,r,mat="Marble",segments=8):
        direction=Vector(b)-Vector(a)
        axis=direction.normalized()
        u=axis.cross(Vector((0,1,0)))
        if u.length<0.1: u=axis.cross(Vector((1,0,0)))
        u.normalize(); v=axis.cross(u)
        rings=[]
        for p in [Vector(a),Vector(b)]:
            rings.append([tuple(p+r*(math.cos(i*math.tau/segments)*u+math.sin(i*math.tau/segments)*v)) for i in range(segments)])
        for i in range(segments):
            j=(i+1)%segments
            self.polygon([rings[0][i],rings[0][j],rings[1][j],rings[1][i]],mat,True)
        self.polygon(list(reversed(rings[0])),mat)
        self.polygon(rings[1],mat)

    def arch(self, width, spring, thickness, depth, pos=(0,0,0), mat="Trim", segments=16, angle=0):
        r=width/2
        def pt(radius,t,z):
            p=(radius*math.cos(t),spring+radius*math.sin(t),z)
            return tuple(a+b for a,b in zip(rotate(p,angle),pos))
        for i in range(segments):
            t0,t1=i*math.pi/segments,(i+1)*math.pi/segments
            coords=[pt(r,t0,-depth/2),pt(r,t1,-depth/2),pt(r+thickness,t1,-depth/2),pt(r+thickness,t0,-depth/2),pt(r,t0,depth/2),pt(r,t1,depth/2),pt(r+thickness,t1,depth/2),pt(r+thickness,t0,depth/2)]
            for ids in [(0,1,2,3),(7,6,5,4),(4,5,1,0),(3,2,6,7)]:
                self.polygon([coords[j] for j in ids],mat)
            if i==0: self.polygon([coords[j] for j in (0,3,7,4)],mat)
            if i==segments-1: self.polygon([coords[j] for j in (1,5,6,2)],mat)
        for side in [-1,1]:
            p=rotate((side*(r+thickness/2),spring/2,0),angle)
            self.box(tuple(a+b for a,b in zip(p,pos)),(thickness,spring,depth),mat,angle)

    def column(self,x,z,bottom,height,r=0.7,mat="Trim"):
        self.box((x,bottom+0.25,z),(r*3,0.5,r*3),mat)
        self.lathe([(0,r*1.35),(.55,r),(height-1.7,r*.87),(height-.65,r*1.5)],8,mat,(x,bottom+.5,z))
        self.box((x,bottom+height,z),(r*3.5,.8,r*3.5),mat)
        # Readable capital silhouette, no tiny carved leaves.
        self.box((x,bottom+height-.8,z),(r*2.7,.55,r*2.7),mat,math.pi/4)

    def transformed(self,pos=(0,0,0),angle=0):
        result=Geometry()
        result.v=[tuple(a+b for a,b in zip(rotate(v,angle),pos)) for v in self.v]
        result.f=list(self.f); result.mat=list(self.mat); result.smooth=list(self.smooth)
        return result

    def merge(self,other):
        offset=len(self.v)
        self.v.extend(other.v)
        self.f.extend(tuple(i+offset for i in face) for face in other.f)
        self.mat.extend(other.mat);self.smooth.extend(other.smooth)

