"""Reusable banner with a broad original museum emblem; no texture upload required."""
import bpy,bmesh,math,json,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]
sys.path.insert(0,str(BASE.parent));import pipeline;pipeline.BASE=BASE
from pipeline import Geo,Asset
original=next(s for s in bpy.data.scenes if s.collection.children.get('VM009_TwoStoreyInterior'))
id='VIC_F02_MUSEUM_BANNER';assert id not in bpy.data.collections
g=Geo();g.box((0,3,0),(2.7,6,.06),'Teal')
for y in [.03,6.03]:g.box((0,y,0),(3.0,.09,.16),'Brass')
for x in [-1.22,1.22]:g.box((x,3,-.05),(.035,5.7,.025),'Brass')
for y in [.18,5.85]:g.box((0,y,-.05),(2.45,.035,.025),'Brass')
for x in [-.72,0,.72]:g.box((x,2.65,-.06),(.12,1.3,.03),'Brass')
g.box((0,1.92,-.06),(1.85,.15,.03),'Brass')
g.vault((0,3.25,-.06),.875,.875,.10,.035,'Brass',8)
g.extrude([(.28*math.cos(i*math.tau/10),.28*math.sin(i*math.tau/10)) for i in range(10)],.03,(0,4.63,-.06),'Brass')
a=Asset(id,'RoomExhibits','Teal museum banner, double border and original broad heritage emblem',260,g)
for o in a.objects:
 bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold for e in bm.edges);assert all(f.calc_area()>1e-9 for f in bm.faces);bm.free()
a.scene['Task']='009';a.row['geometrySource']='Original simplified museum insignia; no real heraldry or external texture';a.save()
m=json.loads((BASE/'two-storey-manifest.json').read_text());m['assets']=[r for r in m['assets'] if r['assetId']!=id]+[a.row];m['uniqueTriangles']=sum(r['triangles'] for r in m['assets'])
(BASE/'two-storey-manifest.json').write_text(json.dumps(m,indent=2)+'\n');(ROOT/'authoring/task009/two-storey.json').write_text(json.dumps(m,indent=2)+'\n')
bpy.context.window.scene=original;bpy.ops.wm.save_as_mainfile(filepath=str(BASE.parents[1]/'VictoriaMemorial.blend'),compress=True)
print(id,a.row['triangles'])
