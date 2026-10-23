"""Reference-led room-specific exhibits and painting support, authored in live Blender."""
import bpy,bmesh,json,math,sys
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]
sys.path.insert(0,str(BASE.parent));import pipeline;pipeline.BASE=BASE
from pipeline import Geo,Asset,bp,material,triangles
win=bpy.context.window;original=next(s for s in bpy.data.scenes if s.collection.children.get('VM009_TwoStoreyInterior'))
assets=[]
def save(id,name,g,cap,sockets=None):
 assert id not in bpy.data.collections,'Inspect existing authored asset before replacing: '+id
 a=Asset(id,'RoomExhibits',name,cap,g,sockets=sockets,note='Original fictional exhibit; concept-led broad forms, reusable shared geometry, no gameplay')
 for o in a.objects:
  bm=bmesh.new();bm.from_mesh(o.data)
  assert all(e.is_manifold for e in bm.edges),id
  assert all(f.calc_area()>1e-9 for f in bm.faces),id
  bm.free()
 a.scene['Task']='009';a.row['geometrySource']='Original room-specific reference-led Task009 geometry';a.save();assets.append(a)

g=Geo()
g.box((0,.12,0),(9.25,.24,2.55),'Brass')
g.box((0,.67,0),(9.05,.86,2.35),'Charcoal')
g.box((0,1.14,0),(9.1,.08,2.4),'Brass')
g.box((0,6.32,.15),(8.8,10.3,.45),'Charcoal')
g.box((0,2.45,-.105),(1.2,.48,.055),'Brass')
g.box((0,10.75,-.23),(2.6,.28,1.0),'Brass')
g.box((0,10.585,-.42),(2.28,.05,.45),'Diffuser:Paper')
save('VIC_F01_PAINTING_MONOLITH','Tall charcoal painting monolith with brass foot and integrated picture light',g,140,{'FrameMount':[0,3.5,-.38],'LightMount':[0,10.56,-.42]})

g=Geo();n=48;k=6;v=[]
def center(t):return Vector(((2+math.cos(3*t))*.53*math.cos(2*t),1.38+.6*math.sin(3*t),(2+math.cos(3*t))*.53*math.sin(2*t)))
for i in range(n):
 t=i*math.tau/n;c=center(t);tan=(center(t+.001)-center(t-.001)).normalized();u=tan.cross(Vector((0,1,0))).normalized();w=tan.cross(u).normalized()
 for j in range(k):v.append(tuple(c+.24*(u*math.cos(j*math.tau/k)+w*math.sin(j*math.tau/k))))
f=[(i*k+j,((i+1)%n)*k+j,((i+1)%n)*k+(j+1)%k,i*k+(j+1)%k) for i in range(n) for j in range(k)]
g.solid(v,f,'Brass');g.box((0,.27,0),(1.2,.54,1.2),'Bronze')
save('VIC_H04_GILDED_KNOT','Broad faceted interwoven-loop sculpture',g,650)

# Two closed page blocks and covers; open book is inclined toward the viewer.
book=Geo()
for sign in [-1,1]:
 poly=[(0,0),(sign*1.85,.11),(sign*1.85,.24),(0,.14)]
 book.extrude(poly,2.5,(0,0,0),'Paper')
 book.extrude([(0,-.08),(sign*1.94,.03),(sign*1.94,.12),(0,.04)],2.66,(0,0,0),'Oxblood')
book.box((0,.07,0),(.12,.18,2.64),'Brass')
# Five broad printed bands per leaf suggest a manuscript without tiny modeled text.
for sign in [-1,1]:
 for z in [-.8,-.4,0,.4,.8]:book.box((sign*.95,.27,z),(1.28,.015,.055),'Ink')
g=Geo();a=math.radians(52)
for role,(verts,faces) in book.groups.items():g.solid([(x,y*math.cos(a)+z*math.sin(a)+1.15,z*math.cos(a)-y*math.sin(a)) for x,y,z in verts],faces,role)
g.extrude([(-.6,0),(.75,0),(.75,1.95)],2.8,(0,0,0),'Charcoal',-math.pi/2)
g.box((0,.06,0),(3.7,.12,2.3),'Brass')
save('VIC_H05_OPEN_CHARTER','Large inclined open charter folio and reading cradle',g,400)

g=Geo();g.box((0,.07,0),(3.3,.14,2.4),'Charcoal');g.box((0,.16,0),(3.4,.06,2.5),'Brass')
for x,z,s in [(-.9,-.3,.55),(.8,-.4,.6),(0,.55,1.0)]:
 g.lathe((x,.2,z),[(0,.35*s),(.15*s,.4*s),(.3*s,.22*s),(.8*s,.36*s),(1.1*s,.28*s),(1.2*s,.38*s)],'Bronze',8)
 g.lathe((x,.2,z),[(1.19*s,.4*s),(1.3*s,.39*s),(1.45*s,.08*s)],'Brass',8)
g.cylinder((-.3,.3,-.9),.11,.22,'Gem',5)
save('VIC_H06_CEREMONIAL_SET','Curated ceremonial vessels on one presentation tray',g,450)

m=json.loads((BASE/'two-storey-manifest.json').read_text());m['assets'] += [a.row for a in assets]
m['uniqueTriangles']=sum(r['triangles'] for r in m['assets'])
(BASE/'two-storey-manifest.json').write_text(json.dumps(m,indent=2)+'\n');(ROOT/'authoring/task009/two-storey.json').write_text(json.dumps(m,indent=2)+'\n')
win.scene=original;bpy.ops.wm.save_as_mainfile(filepath=str(BASE.parents[1]/'VictoriaMemorial.blend'),compress=True)
print(json.dumps({a.id:a.row['triangles'] for a in assets}))
