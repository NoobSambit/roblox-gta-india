"""One saved-scene inspection: linked dependencies, transforms and gross infra collisions."""
from pathlib import Path
import bpy, json
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'assets/kolkata/masterplan_task014'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Kolkata_Masterplan_Stage_A.blend'))
s=bpy.context.scene
D=json.loads((OUT/'masterplan-manifest.json').read_text())
errors=[]
missing=[bpy.path.abspath(l.filepath) for l in bpy.data.libraries if not Path(bpy.path.abspath(l.filepath)).exists()]
if missing:errors.append('Missing linked libraries: '+str(missing))
for r in D['placements']:
    ob=s.objects.get(r['id']+'__GroundOrigin')
    if not ob or ob.instance_type!='COLLECTION':errors.append('Missing asset instance '+r['id']);continue
    if any(abs(v-1)>.0001 for v in ob.scale):errors.append('Non-unit asset scale '+r['id'])
    meshes=[o for o in ob.instance_collection.objects if o.type=='MESH']
    if len(meshes)!=r['linked_mesh_objects']:errors.append('Lost source geometry '+r['id'])
    if any(o.library is None for o in meshes):errors.append('Asset source is not linked '+r['id'])
infra_objects=0
for col in ['Flyover Network','Elevated Metro','Metro Stations']:
    for o in bpy.data.collections[col].objects:
        if o.type!='MESH':continue
        infra_objects+=1
        pts=[o.matrix_world@Vector(v) for v in o.bound_box]
        pts=[(v.x,v.z,-v.y) for v in pts]
        lo=[min(v[i] for v in pts) for i in range(3)];hi=[max(v[i] for v in pts) for i in range(3)]
        for r in D['placements']:
            # Bridge sockets intentionally join the original deck/footways.
            if r['id']=='HOWRAH':continue
            a,b=r['world_bounds_roblox']
            if all(min(hi[i],b[i])-max(lo[i],a[i])>.1 for i in range(3)):
                errors.append('Gross infrastructure / landmark collision: '+o.name+' / '+r['id'])
markers=[m for m in s.timeline_markers if m.camera]
if len(markers)!=8:errors.append('Expected eight camera bookmarks')
result=dict(status='PASS' if not errors else 'NEEDS_CORRECTION',errors=errors,
            linked_library_count=len(bpy.data.libraries),missing_libraries=missing,
            landmark_instances=len(D['placements']),infrastructure_objects_checked=infra_objects,
            bookmarked_cameras=len(markers),scene=s.name,
            note='Actual saved-scene object bounding boxes only; not collision simulation or structural analysis.')
(OUT/'saved-scene-check.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
if errors:raise RuntimeError('Saved masterplan needs correction')
