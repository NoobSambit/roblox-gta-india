"""Original indexed, closed low-resolution geometry in Roblox stud coordinates."""
import math

def add(a,b):return tuple(x+y for x,y in zip(a,b))
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def mul(a,s):return tuple(x*s for x in a)
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def norm(a):return mul(a,1/math.sqrt(dot(a,a)))
def rotate(p,a):
 c,s=math.cos(a),math.sin(a)
 return (c*p[0]+s*p[2],p[1],-s*p[0]+c*p[2])
def bp(p):return (p[0],-p[2],p[1])

class Geo:
 def __init__(self):self.groups={}
 def solid(self,v,f,mat):
  vertices,faces=self.groups.setdefault(mat,([],[]));offset=len(vertices)
  vertices.extend(v);faces.extend(tuple(i+offset for i in face) for face in f)
 def box(self,pos,size,mat='Steel',angle=0):
  w,h,d=(s/2 for s in size)
  assert min(size)>0
  v=[(-w,-h,-d),(w,-h,-d),(w,h,-d),(-w,h,-d),(-w,-h,d),(w,-h,d),(w,h,d),(-w,h,d)]
  self.solid([add(rotate(p,angle),pos) for p in v],[(0,3,2,1),(4,5,6,7),(0,4,7,3),(1,2,6,5),(0,1,5,4),(3,7,6,2)],mat)
 def extrude(self,polygon,depth,pos=(0,0,0),mat='Cream',angle=0):
  n=len(polygon)
  self.solid([add(rotate((x,y,z),angle),pos) for z in [-depth/2,depth/2] for x,y in polygon],
   [tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],mat)
 def plan(self,polygon,low,high,mat='Stone'):
  n=len(polygon)
  self.solid([(x,low,z) for x,z in polygon]+[(x,high,z) for x,z in polygon],
   [tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],mat)
 def beam(self,a,b,w=.5,d=None,mat='Steel',profile='box'):
  d=w if d is None else d;axis=norm(sub(b,a))
  u=cross(axis,(0,1,0))
  if dot(u,u)<.01:u=cross(axis,(0,0,1))
  u=norm(u);v=norm(cross(axis,u))
  if profile=='I':
   t=min(w,d)*.2
   p=[(-w/2,-d/2),(w/2,-d/2),(w/2,-d/2+t),(t/2,-d/2+t),(t/2,d/2-t),(w/2,d/2-t),(w/2,d/2),(-w/2,d/2),(-w/2,d/2-t),(-t/2,d/2-t),(-t/2,-d/2+t),(-w/2,-d/2+t)]
  else:p=[(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]
  n=len(p);vertices=[add(point,add(mul(u,x),mul(v,y))) for point in [a,b] for x,y in p]
  self.solid(vertices,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],mat)
 def lathe(self,pos,profile,mat='Cream',segments=8):
  assert all(r>0 for y,r in profile)
  n=segments;rows=len(profile)
  v=[(pos[0]+r*math.cos(i*math.tau/n),pos[1]+y,pos[2]+r*math.sin(i*math.tau/n)) for y,r in profile for i in range(n)]
  f=[tuple(reversed(range(n))),tuple(range((rows-1)*n,rows*n))]
  for j in range(rows-1):
   for i in range(n):
    k=(i+1)%n;f.append((j*n+i,j*n+k,(j+1)*n+k,(j+1)*n+i))
  self.solid(v,f,mat)
 def cylinder(self,pos,r,h,mat='Steel',segments=8):self.lathe(pos,[(-h/2,r),(h/2,r)],mat,segments)
 def arch(self,pos,width,spring,thickness,depth,mat='Cream',segments=8):
  # One closed extruded ribbon with two straight legs; no solid face across the opening.
  r=width/2;t=thickness
  p=[(-r-t,0),(-r,0),(-r,spring)]
  p.extend((r*math.cos(math.pi-i*math.pi/segments),spring+r*math.sin(math.pi-i*math.pi/segments)) for i in range(1,segments+1))
  p.extend([(r,0),(r+t,0),(r+t,spring)])
  p.extend(((r+t)*math.cos(i*math.pi/segments),spring+(r+t)*math.sin(i*math.pi/segments)) for i in range(1,segments+1))
  self.extrude(p,depth,pos,mat)
 def column(self,x,z,base,height,r=.65,mat='Cream',segments=8):
  self.box((x,base+.28,z),(r*3.3,.56,r*3.3),mat)
  self.lathe((x,base,z),[(.45,r*1.28),(1.15,r),(height-1.5,r*.87),(height-.9,r*1.3)],mat,segments)
  self.box((x,base+height-.5,z),(r*3.6,1,r*3.6),mat)
 def vault(self,pos,rx,ry,thickness,depth,mat='White',segments=12,legs=0):
  p=[(-rx-thickness,0),(-rx,0)] if legs else []
  p.extend((rx*math.cos(math.pi-i*math.pi/segments),legs+ry*math.sin(math.pi-i*math.pi/segments)) for i in range(segments+1))
  if legs:p.extend([(rx,0),(rx+thickness,0)])
  p.extend(((rx+thickness)*math.cos(i*math.pi/segments),legs+(ry+thickness)*math.sin(i*math.pi/segments)) for i in range(segments+1))
  self.extrude(p,depth,pos,mat)
 def rail(self,length=16,base=0,z=0,mat='Cream',balusters=8,joinable=False):
  for x in ([-length/2] if joinable else [-length/2,length/2]):
   self.box((x,base+1.9,z),(.8,3.8,.9),mat)
   self.box((x,base+3.9,z),(1.15,.4,1.2),mat)
  self.box((0,base+.25,z),(length,.5,.65),mat)
  self.box((0,base+3.5,z),(length if joinable else length+.4,.4,.85),mat)
  for i in range(balusters):
   x=-length/2+(i+1)*length/(balusters+1)
   self.lathe((x,base,z),[(.5,.2),(1.2,.35),(2.1,.25),(3.3,.18)],mat,6)
 def steel_rail(self,length=128,base=0,z=0,spacing=8,mat='Steel',joinable=False):
  for i in range(round(length/spacing)+(0 if joinable else 1)):
   x=-length/2+i*length/round(length/spacing)
   self.box((x,base+1.75,z),(.22,3.5,.28),mat)
  for y in [base+.8,base+2,base+3.5]:self.box((0,y,z),(length,.16,.25),mat)
 def stair(self,width,start_z,bottom,steps=7,tread=2.3,rise=.6,mat='Stone',foundation=None):
  # Extruded complete stepped profile: a flight is one mesh group, never one Part/tread.
  p=[]
  for i in range(steps):p.extend([(start_z+i*tread,bottom+(i+1)*rise),(start_z+(i+1)*tread,bottom+(i+1)*rise)])
  base=bottom-1 if foundation is None else foundation
  p.append((start_z+steps*tread,base));p.append((start_z,base))
  # Profile axes are Z/Y, extruded along X.
  n=len(p);v=[(x,y,z) for x in [-width/2,width/2] for z,y in p]
  self.solid(v,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],mat)
 def merge(self,other,pos=(0,0,0),angle=0):
  for mat,(v,f) in other.groups.items():self.solid([add(rotate(p,angle),pos) for p in v],f,mat)
 def triangles(self):return sum(len(face)-2 for v,f in self.groups.values() for face in f)
