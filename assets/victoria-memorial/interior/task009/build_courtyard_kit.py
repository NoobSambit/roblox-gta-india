"""Targeted courtyard doorway repair and two reusable heritage garden pieces."""
import bpy,bmesh,json,math,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]
sys.path.insert(0,str(BASE.parent));import pipeline;pipeline.BASE=BASE
from pipeline import Geo,Asset
original=next(s for s in bpy.data.scenes if s.collection.children.get('VM009_TwoStoreyInterior'))
assets=[]
def save(id,name,g,cap):
 assert id not in bpy.data.collections,id
 a=Asset(id,'Courtyard',name,cap,g,note='Original optimized correction/dressing; preserves the existing courtyard and routes')
 for o in a.objects:
  bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold and e.is_contiguous for e in bm.edges),id;assert all(f.calc_area()>1e-9 for f in bm.faces),id;bm.free()
 a.scene['Task']='009';a.save();assets.append(a)
# Existing arch: seven-stud inner width, ten-stud spring above Y6,
# 0.7-stud ribbon. Fill the original nine-by-eighteen rectangular slot
# OUTSIDE that arch, matching the original twelve-segment curve.
g=Geo()
for i in range(12):
 a=math.pi-i*math.pi/12;b=math.pi-(i+1)*math.pi/12
 x1,y1=4.2*math.cos(a),10+4.2*math.sin(a);x2,y2=4.2*math.cos(b),10+4.2*math.sin(b)
 g.extrude([(x1,y1),(x2,y2),(x2,18),(x1,18)],2,(0,0,0),'Ivory')
for x in [-4.35,4.35]:g.box((x,9,0),(.3,18,2),'Ivory')
save('VIC_B14_COURTYARD_SPANDREL','Solid masonry infill around the original courtyard arch',g,220)

g=Geo();g.box((0,.2,0),(12,.4,5),'Stone');g.box((0,1.0,0),(11.7,1.6,4.7),'Ivory');g.box((0,1.83,0),(11.2,.12,4.2),'Ink')
for x in [-5.85,5.85]:g.box((x,1.95,0),(.3,.3,5),'Stone')
for z in [-2.35,2.35]:g.box((0,1.95,z),(11.4,.3,.3),'Stone')
for x in [-3.8,0,3.8]:g.lathe((x,0,0),[(2.0,.7),(2.5,1.8),(3.4,1.3),(3.7,.4)],'Leaf',8)
save('VIC_G01_FORMAL_PLANTER','Broad stone courtyard planter with three faceted shrubs',g,360)
g=Geo()
for x in [-3.35,3.35]:g.box((x,.68,0),(.65,1.36,2.15),'Stone')
g.box((0,1.5,0),(9,.38,2.5),'Ivory');g.box((0,2.45,.98),(9,1.55,.3),'Ivory')
for x in [-3.9,3.9]:g.box((x,1.95,0),(.28,.65,2.4),'Stone')
save('VIC_G02_STONE_BENCH','Simple heritage stone courtyard bench',g,120)
m=json.loads((BASE/'two-storey-manifest.json').read_text());m['assets'] += [a.row for a in assets];m['uniqueTriangles']=sum(r['triangles'] for r in m['assets'])
(BASE/'two-storey-manifest.json').write_text(json.dumps(m,indent=2)+'\n');(ROOT/'authoring/task009/two-storey.json').write_text(json.dumps(m,indent=2)+'\n')
bpy.context.window.scene=original;bpy.ops.wm.save_as_mainfile(filepath=str(BASE.parents[1]/'VictoriaMemorial.blend'),compress=True)
print(json.dumps({a.id:a.row['triangles'] for a in assets}))
