"""Measured interior-only transition and portal infill; run in the original source."""
import bpy,sys,json,math,bmesh
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]
sys.path.insert(0,str(BASE.parent));import pipeline
pipeline.BASE=BASE
from pipeline import Geo,Asset
original=next(s for s in bpy.data.scenes if s.collection.children.get('VM009_TwoStoreyInterior'))
manifest=json.loads((BASE/'two-storey-manifest.json').read_text())
def save(id,name,g):
    a=Asset(id,'Corrections',name,800,g,note='Interior-only measured join; preserve original exterior meshes')
    a.scene['Task']='009'
    for o in a.objects:
        bm=bmesh.new();bm.from_mesh(o.data)
        assert all(e.is_manifold and e.is_contiguous for e in bm.edges),id
        assert all(f.calc_area()>1e-9 for f in bm.faces),id
        bm.free()
    a.save()
    old=next((i for i,r in enumerate(manifest['assets']) if r['assetId']==id),None)
    if old is None:manifest['assets'].append(a.row)
    else:manifest['assets'][old]=a.row
    return a
g=Geo()
# Heights/radii are derived from the actual original CentralDrum mesh:
# base R29.3 at64; recessed upper drum R28.4 from67.6 to89.
profile=[(63.5,30.4,30.9),(64,28.65,29),(67.6,27.75,28.1),(88.8,27.75,28.1),(89.15,28.15,28.5)]
cross=[(r,y) for y,r,_ in profile]+[(r,y) for y,_,r in reversed(profile)]
n=len(cross);segments=3
verts=[]
for j in range(segments+1):
    a=-math.pi/12+j*math.pi/6/segments
    verts.extend((r*math.sin(a),y,r*math.cos(a)) for r,y in cross)
faces=[tuple(reversed(range(n))),tuple(range(segments*n,(segments+1)*n))]
for j in range(segments):
    for k in range(n):faces.append((j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k))
g.solid(verts,faces,'Ivory')
save('VIC_B15_DRUM_TRANSITION','Fitted internal drum shoulder and clerestory backing',g)
g=Geo();r=6.1;spring=6;top=14.2
# Fill outside the existing upper arcade's outer arch, all the way back to
# the preserved internal connection wall. The 10.8-stud inner arch stays clear.
for side in [-1,1]:
    points=[(side*7.45,0),(side*r,0),(side*r,spring)]
    points += [(side*r*math.cos(i*math.pi/2/8),spring+r*math.sin(i*math.pi/2/8)) for i in range(1,9)]
    points += [(0,top),(side*7.45,top)]
    g.extrude(points,4.6,(0,0,0),'Ivory')
save('VIC_B16_PORTAL_SPANDREL','Deep upper hall arch spandrels and wall return',g)
manifest['uniqueTriangles']=sum(r['triangles'] for r in manifest['assets'])
(BASE/'two-storey-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(ROOT/'authoring/task009/two-storey.json').write_text(json.dumps(manifest,indent=2)+'\n')
bpy.context.window.scene=original
bpy.ops.wm.save_as_mainfile(filepath=str(BASE.parents[1]/'VictoriaMemorial.blend'),compress=True)
print('Saved two fitted structural correction modules; original facade untouched.',flush=True)
