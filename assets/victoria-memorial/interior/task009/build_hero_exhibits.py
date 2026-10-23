"""Three original reference-led, reusable exhibits. Live Blender MCP authoring."""
import bpy,bmesh,math,json,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]
sys.path.insert(0,str(BASE.parent));import pipeline;pipeline.BASE=BASE
from pipeline import Asset,Geo
original=next(s for s in bpy.data.scenes if s.collection.children.get('VM009_TwoStoreyInterior'))
assets=[]
def save(id,name,g,cap=700):
 old=bpy.data.collections.get(id)
 if old:
  assert not any(o.instance_type=='COLLECTION' and o.instance_collection==old for o in original.objects),'Already placed; inspect before replacing'
  for o in list(old.objects):bpy.data.objects.remove(o,do_unlink=True)
  bpy.data.collections.remove(old)
 if id in bpy.data.scenes:bpy.data.scenes.remove(bpy.data.scenes[id])
 a=Asset(id,'HeroExhibits',name,cap,g,note='Original fictional museum exhibit; shared mesh, no gameplay, no texture dependency')
 for o in a.objects:
  bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold and e.is_contiguous for e in bm.edges);assert all(f.calc_area()>1e-9 for f in bm.faces);bm.free()
 a.scene['Task']='009';a.row['geometrySource']='Original optimized hero exhibit, guided by selected museum concepts';a.save();assets.append(a)
def torus(g,center,rx,ry,depth,segments,role):
 # Ring in XY, square section. Broad handles/arches, no high-density rounded mesh.
 verts=[]
 for i in range(segments):
  a=i*math.tau/segments
  for r,z in [(-.07,-depth/2),(.07,-depth/2),(.07,depth/2),(-.07,depth/2)]:verts.append((center[0]+(rx+r)*math.cos(a),center[1]+(ry+r)*math.sin(a),center[2]+z))
 faces=[]
 for i in range(segments):
  for j in range(4):faces.append((i*4+j,((i+1)%segments)*4+j,((i+1)%segments)*4+(j+1)%4,i*4+(j+1)%4))
 g.solid(verts,faces,role)
g=Geo();g.lathe((0,0,0),[(0,.62),(.16,.68),(.32,.39),(.55,.43),(.8,.72),(1.25,.8),(1.7,.65),(1.92,.41),(2.12,.43),(2.22,.57)],'Bronze',12)
g.lathe((0,0,0),[(2.18,.58),(2.3,.61),(2.36,.48),(2.48,.12)],'Brass',12)
g.lathe((0,0,0),[(.76,.735),(.85,.755)],'Brass',12)
for sign in [-1,1]:torus(g,(sign*.82,1.45,0),.34,.52,.14,8,'Brass')
save('VIC_H01_CEREMONIAL_URN','Handled ceremonial urn with lid and shaped foot',g,700)
g=Geo();g.lathe((0,0,0),[(0,1.05),(.16,1.15),(.42,1.07),(.58,1.10)],'Brass',12)
for i in range(6):
 a=i*math.tau/6;x,z=1.02*math.sin(a),1.02*math.cos(a)
 p=[(x-.18,.42,z-.18),(x+.18,.42,z-.18),(x+.18,.42,z+.18),(x-.18,.42,z+.18),(x,1.16,z)]
 g.solid(p,[(0,3,2,1),(0,1,4),(1,2,4),(2,3,4),(3,0,4)],'Brass')
 # A faceted cabochon on each broad crown point.
 g.lathe((x,1.14,z),[(0,.13),(.14,.19),(.28,.08)],'Gem',6)
# Two economical crossing arches; closed rectangular ribbons, eight segments each.
for yaw in [0,math.pi/2]:
 a=Geo();a.vault((0,.5,0),.95,1.25,.12,.13,'Brass',8);g.merge(a,angle=yaw)
g.lathe((0,1.8,0),[(0,.11),(.2,.26),(.46,.09)],'Gem',8)
save('VIC_H02_CEREMONIAL_CROWN','Fictional jewelled ceremonial crown',g,700)
g=Geo();top=[(-1.5,0),(-1.1,-.55),(.9,-.55),(1.5,0),(.9,.55),(-1.1,.55)];n=len(top)
verts=[(x*.76,.08,z*.7) for x,z in top]+[(x,.52,z) for x,z in top]
g.solid(verts,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],'Bronze')
g.plan([(x*.92,z*.9) for x,z in top],.51,.58,'Paper')
g.box((-.4,.85,0),(.95,.55,.65),'Teal')
roof=Geo();roof.vault((0,1.12,0),.45,.18,.07,1.05,'Ivory',6);g.merge(roof,pos=(-.4,0,0),angle=math.pi/2)
for x in [-.85,.05]:
 for z in [-.33,.33]:g.box((x,.93,z),(.06,.7,.06),'Brass')
g.cylinder((.55,1.3,0),.045,1.6,'Brass',6)
# One low-detail sail; no cloth simulation, no texture and no dense rigging.
g.extrude([(.58,1.95),(.58,1.02),(1.22,1.05)],.035,(0,0,0),'Ivory')
g.beam((.55,1.95,0),(-1.1,.62,0),.035,.035,'Brass')
for x,z in [(-1.05,0),(.9,.28)]:g.box((x,.7,z),(.32,.25,.32),'Charcoal')
save('VIC_H03_RIVER_TRADE_MODEL','Faceted river-trade boat with cabin, sail and cargo',g,600)
m=json.loads((BASE/'two-storey-manifest.json').read_text());ids={a.id for a in assets};m['assets']=[r for r in m['assets'] if r['assetId'] not in ids]+[a.row for a in assets];m['uniqueTriangles']=sum(r['triangles'] for r in m['assets']);m['heroExhibitTriangles']={a.id:a.row['triangles'] for a in assets}
(BASE/'two-storey-manifest.json').write_text(json.dumps(m,indent=2)+'\n');(ROOT/'authoring/task009/two-storey.json').write_text(json.dumps(m,indent=2)+'\n')
bpy.context.window.scene=original;bpy.ops.wm.save_as_mainfile(filepath=str(BASE.parents[1]/'VictoriaMemorial.blend'),compress=True)
print(json.dumps(m['heroExhibitTriangles']),flush=True)
