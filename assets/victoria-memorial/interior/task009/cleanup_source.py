"""Remove retired interior objects from the final source after recovery is saved."""
import bpy, json
from pathlib import Path
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[3]
source=BASE.parents[1]/'VictoriaMemorial.blend'
assert (ROOT/'artifacts/recovery/VictoriaMemorial-Task009-before-cleanup.blend').exists()
bpy.ops.wm.open_mainfile(filepath=str(source))
removed=[]
archive=bpy.data.collections.get('VM009_ArchivedInterior')
if archive:
    for obj in list(archive.objects):
        assert not any(c.name!='VM009_ArchivedInterior' for c in obj.users_collection),obj.name
        removed.append(obj.name)
        bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.collections.remove(archive)
# Purge orphan meshes only, retaining every scene, source master and material.
orphan_meshes=[m for m in bpy.data.meshes if m.users==0 and not m.use_fake_user]
for mesh in orphan_meshes:bpy.data.meshes.remove(mesh)
bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
report=dict(removedOriginalInteriorObjects=removed,removedObjectCount=len(removed),orphanMeshesRemoved=len(orphan_meshes),recovery='artifacts/recovery/VictoriaMemorial-Task009-before-cleanup.blend',finalSource=str(source.relative_to(ROOT)))
(ROOT/'docs/task009/cleanup-source.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(removedObjects=len(removed),orphanMeshesRemoved=len(orphan_meshes))))
