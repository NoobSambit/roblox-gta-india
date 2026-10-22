"""Blender FBX round-trip checks; imports are temporary and removed in finally."""
import bpy
import json
from pathlib import Path
from mathutils import Vector

OUT=Path(r"C:\Users\Sambit Pradhan\Documents\Indian_Hood\assets\victoria-memorial")

def bounds(objects):
    coords=[obj.matrix_world@Vector(corner) for obj in objects for corner in obj.bound_box]
    return [[min(v[i] for v in coords) for i in range(3)],[max(v[i] for v in coords) for i in range(3)]]

def triangle_count(objects):
    total=0
    for obj in objects:
        obj.data.calc_loop_triangles();total+=len(obj.data.loop_triangles)
    return total

def validate(filename,collections):
    source=[obj for name in collections for obj in bpy.data.collections[name].objects if obj.type=="MESH"]
    source_bounds=bounds(source);source_triangles=triangle_count(source)
    before_objects=set(bpy.data.objects);before_meshes=set(bpy.data.meshes);before_materials=set(bpy.data.materials)
    try:
        bpy.ops.import_scene.fbx(filepath=str(OUT/filename),use_custom_normals=True)
        imported=[obj for obj in bpy.data.objects if obj not in before_objects and obj.type=="MESH"]
        imported_bounds=bounds(imported);triangles=triangle_count(imported)
        error=max(abs(a-b) for aa,bb in zip(source_bounds,imported_bounds) for a,b in zip(aa,bb))
        result=dict(file=filename,source_objects=len(source),imported_objects=len(imported),source_triangles=source_triangles,imported_triangles=triangles,max_bounds_error_blender_units=error,missing_material_objects=[obj.name for obj in imported if len(obj.data.materials)!=1 or obj.data.materials[0] is None],positive_scales=all(min(obj.scale)>0 for obj in imported))
        result["passed"]=len(imported)==len(source) and triangles==source_triangles and error<.002 and not result["missing_material_objects"] and result["positive_scales"]
        return result
    finally:
        for obj in list(bpy.data.objects):
            if obj not in before_objects:bpy.data.objects.remove(obj,do_unlink=True)
        for mesh in list(bpy.data.meshes):
            if mesh not in before_meshes and mesh.users==0:bpy.data.meshes.remove(mesh)
        for mat in list(bpy.data.materials):
            if mat not in before_materials and mat.users==0:bpy.data.materials.remove(mat)

rows=[validate("VictoriaMemorial_Architecture.fbx",["VM_Architecture","VM_Structure_Collision","VM_Interior"]),validate("VictoriaMemorial_MeshLibrary.fbx",["VM_Library_Export"]),validate("VictoriaMemorial_Grounds.fbx",["VM_Grounds"]),validate("VictoriaMemorial_Collision.fbx",["VM_CollisionOnly"])]
(OUT/"fbx-roundtrip.json").write_text(json.dumps(rows,indent=2),encoding="utf-8")
print(json.dumps(rows,indent=2))
