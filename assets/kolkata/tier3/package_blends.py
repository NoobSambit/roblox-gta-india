"""Turn dependency-isolated Blender libraries into normally opening source files.

Run only after build/export/review. The live file must be the Tier 3 master;
the earlier landmark session is preserved separately before this is called.
"""
import bpy,json
from pathlib import Path
from mathutils import Vector

BASE=Path(r'C:\Users\Sambit Pradhan\Documents\Indian_Hood\assets\kolkata\tier3')

def frame(row):
    scene=bpy.data.scenes[row['id']]
    # open_mainfile clears the current operator context until the next UI tick;
    # use the new window datablock directly within this packaging loop.
    window=next(w for wm in bpy.data.window_managers for w in wm.windows)
    window.scene=scene
    dims=row['dimensionsStuds'];height=dims['height']
    for obj in scene.objects:obj.select_set(False,view_layer=scene.view_layers[0])
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type!='VIEW_3D':continue
            space=area.spaces.active
            if 'MATERIAL' in [e.identifier for e in space.shading.bl_rna.properties['color_type'].enum_items]:space.shading.color_type='MATERIAL'
            space.overlay.show_floor=False;space.overlay.show_axis_x=False;space.overlay.show_axis_y=False
            region=space.region_3d
            region.view_location=Vector((0,0,height*.46))
            region.view_rotation=Vector((.95,1.6,.73)).to_track_quat('Z','Y')
            region.view_distance=max(dims.values())*1.55
            region.view_perspective='ORTHO'

def package():
    rows=json.loads((BASE/'asset-manifest.json').read_text(encoding='utf8'))
    master=BASE/'Kolkata_Tier3_Library.blend'
    assert Path(bpy.data.filepath).resolve()==master.resolve()
    assert len(bpy.data.scenes)==27 and all(s.get('AssetId','').startswith('KOL_T3_') for s in bpy.data.scenes)
    first=next(r for r in rows if r['id']=='KOL_T3_OLD_01')
    saved_versions=bpy.context.preferences.filepaths.save_version
    try:
        bpy.context.preferences.filepaths.save_version=0
        frame(first)
        bpy.ops.wm.save_as_mainfile(filepath=str(master),check_existing=False,compress=True)
        for row in rows:
            source=BASE/row['source']
            bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
            assert len(bpy.data.scenes)==1 and len(bpy.data.objects)==row['meshGroups'],row['id']
            frame(row)
            bpy.ops.wm.save_as_mainfile(filepath=str(source),check_existing=False,compress=True)
        bpy.ops.wm.open_mainfile(filepath=str(master),load_ui=False)
        frame(first)
    finally:bpy.context.preferences.filepaths.save_version=saved_versions
    print(json.dumps({'packagedSourceFiles':27,'masterScenes':len(bpy.data.scenes),'activeScene':first['id'],'file':bpy.data.filepath}))

if __name__=='__main__':package()
