"""Export selected landmark sections at their authored local origin, not the grid offset.

Blender --background --python reexport.py -- KOL_T1_ASSET_ID
Canonical source files and the original completed exports are never overwritten.
"""
import bpy
import sys
from pathlib import Path

BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
from catalog import EXPORT,MASTER


def export_section(scene,pivot,objects,path):
    """Copy existing mesh data/UVs, strip only the staging transform, and export."""
    original_scene=bpy.context.window.scene
    temp=bpy.data.scenes.new('__LOCAL_EXPORT_ONLY')
    temp.unit_settings.system='NONE';temp.unit_settings.scale_length=1
    bpy.context.window.scene=temp
    inverse=pivot.matrix_world.inverted()
    copies=[]
    try:
        for obj in objects:
            clone=obj.copy();clone.data=obj.data.copy()
            clone.parent=None;temp.collection.objects.link(clone)
            clone.matrix_world=inverse@obj.matrix_world
            clone.hide_render=False;clone.hide_viewport=False;clone.hide_set(False)
            clone.select_set(True);copies.append(clone)
        bpy.context.view_layer.objects.active=copies[0]
        path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
        bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'MESH'},
            global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',
            axis_forward='-Z',axis_up='Y',bake_anim=False,use_mesh_modifiers=False,
            path_mode='COPY',embed_textures=True,mesh_smooth_type='FACE',use_custom_props=True)
    finally:
        bpy.context.window.scene=original_scene
        for obj in copies:
            mesh=obj.data;bpy.data.objects.remove(obj,do_unlink=True);bpy.data.meshes.remove(mesh)
        bpy.data.scenes.remove(temp)


if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    if not args:raise SystemExit('Supply one or more KOL_T1_* asset IDs; no whole-showcase export exists.')
    if Path(bpy.data.filepath)!=MASTER:bpy.ops.wm.open_mainfile(filepath=str(MASTER))
    scene=bpy.context.scene
    for aid in args:
        pivot=next(o for o in scene.objects if o.get('StagingPivot') and o.get('AssetId')==aid)
        meshes=[o for o in scene.objects if o.type=='MESH' and o.get('StagingAssetId')==aid and o.get('Section') is not None]
        sections=sorted({o['Section'] for o in meshes})
        for section in sections:
            path=EXPORT/aid.removeprefix('KOL_T1_').lower()/'reexported'/(aid+'__'+section+'.fbx')
            export_section(scene,pivot,[o for o in meshes if o['Section']==section],path)
        print('REEXPORTED '+aid+' '+str(len(sections))+' sections to its reexported/ folder',flush=True)
