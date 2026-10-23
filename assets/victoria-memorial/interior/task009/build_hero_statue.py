"""Selective low/mid-poly replacement for the crude interior-only hall figure.

Run via live Blender MCP after opening VictoriaMemorial.blend. Keeps its plinth.
"""
import bpy,bmesh,math,json,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]
sys.path.insert(0,str(BASE.parent));import pipeline;pipeline.BASE=BASE
from pipeline import Asset,Geo,bp
original=next(s for s in bpy.data.scenes if s.collection.children.get('VM009_TwoStoreyInterior'))
g=Geo()
g.lathe((0,0,0),[(0,1.6),(.3,1.7),(1.2,1.6),(3.7,1.3),(5.6,.9),(6.1,1.05)],'Ivory',12)
g.lathe((0,0,0),[(5.5,.8),(6.4,1.15),(7.2,1.05),(7.6,.55)],'Ivory',10)
g.lathe((0,7.4,0),[(0,.36),(.5,.36)],'Ivory',8)
# Controlled broad head/jaw planes, a readable nose and crown silhouette.
g.lathe((0,0,-.04),[(7.75,.35),(7.95,.52),(8.35,.64),(8.9,.59),(9.15,.43),(9.25,.24)],'Ivory',10)
g.extrude([(-.15,8.6),(.15,8.6),(.1,8.05),(-.1,8.05)],.22,(0,0,-.61),'Ivory')
g.lathe((0,0,-.02),[(9.0,.57),(9.2,.65),(9.35,.61)],'Brass',12)
for i in range(6):
 a=i*math.tau/6
 g.box((.48*math.sin(a),9.52,.48*math.cos(a)),(.18,.4,.18),'Brass')
# A broad, closed mantle gives the shoulders an intentional monumental silhouette.
g.solid([(-1.05,7.3,.35),(1.05,7.3,.35),(-1.5,5.3,.95),(1.5,5.3,.95),(-1.55,.45,1.15),(1.55,.45,1.15),(-.8,7.3,.65),(.8,7.3,.65),(-1.25,.45,1.4),(1.25,.45,1.4)],[(0,1,3,2),(2,3,5,4),(0,6,7,1),(6,8,9,7),(4,5,9,8),(0,2,4,8,6),(1,7,9,5,3)],'Stone')
for a,b,c in [((-1,7,0),(-1.6,5.9,-.15),(-1.2,5.2,-.5)),((1,7,0),(1.65,5.9,0),(2.0,6.4,-.4))]:
 g.beam(a,b,.52,.56,'Ivory');g.beam(b,c,.45,.46,'Ivory');g.lathe(c,[(0,.24),(.4,.23)],'Ivory',6)
g.cylinder((2.0,4,-.4),.085,6.3,'Brass',6)
g.lathe((2.0,7.2,-.4),[(0,.12),(.2,.24),(.45,.12)],'Brass',8)
for x in [-.7,0,.7]:g.extrude([(x-.12,.5),(x+.12,.5),(x+.06,4.5),(x-.06,4.5)],.09,(0,0,-1.26),'Ivory')
a=Asset('VIC_B13_HALL_FIGURE','TwoStorey','Crowned museum memorial figure with mantle and sceptre',1100,g,note='Permanent non-loot hero; replaces original interior figure only, original plinth retained')
for o in a.objects:
 bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold and e.is_contiguous for e in bm.edges),o.name;bm.free()
a.scene['Task']='009';a.row['geometrySource']='Original optimized Victoria hall memorial reconstruction';a.save()
bpy.context.window.scene=original
archive=bpy.data.collections.get('VM009_ArchivedInterior');old=[]
for o in list(bpy.data.collections['VM_Interior'].objects):
 if o.name.startswith('QueensHallFigure'):
  bpy.data.collections['VM_Interior'].objects.unlink(o);archive.objects.link(o);old.append(o.name)
assembly=bpy.data.collections['VM009_TwoStoreyInterior'];o=bpy.data.objects.new('VIC_HALL_HERO_STATUE',None);o.instance_type='COLLECTION';o.instance_collection=a.collection;o.location=bp((0,8.4,0));assembly.objects.link(o)
p=BASE/'two-storey-manifest.json';m=json.loads(p.read_text());m['assets']=[r for r in m['assets'] if r['assetId']!=a.id]+[a.row];m['instances']=[r for r in m['instances'] if r['assetId']!=a.id]+[dict(assetId=a.id,instanceId='VIC_HALL_HERO_STATUE',position=[0,8.4,0],yaw=0,triangles=a.row['triangles'],role='TwoStoreyArchitecture')];m['uniqueTriangles']=sum(r['triangles'] for r in m['assets']);m['placedTriangles']=sum(r['triangles'] for r in m['instances']);m['originalInteriorArchived']+=old
p.write_text(json.dumps(m,indent=2)+'\n');(ROOT/'authoring/task009/two-storey.json').write_text(p.read_text())
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(BASE.parents[1]/'VictoriaMemorial.blend'),compress=True)
print(json.dumps(dict(statueTriangles=a.row['triangles'],originalFigureReplaced=old,plinthPreserved=True)),flush=True)
