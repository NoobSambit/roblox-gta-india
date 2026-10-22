"""Save dependency-isolated sources as normally opening Blender projects.

Run after modelling/export/PNG review; only Task 005 files are opened or saved.
"""
import bpy,json
from mathutils import Vector
from pipeline import BASE

def frame(row):
 scene=bpy.data.scenes[row['assetId']]
 window=next(w for wm in bpy.data.window_managers for w in wm.windows);window.scene=scene
 for obj in scene.objects:obj.select_set(False,view_layer=scene.view_layers[0])
 lo=row['boundsMinStuds'];hi=row['boundsMaxStuds']
 centre=Vector(((lo[0]+hi[0])/2,-(lo[2]+hi[2])/2,(lo[1]+hi[1])/2))
 for screen in bpy.data.screens:
  for area in screen.areas:
   if area.type!='VIEW_3D':continue
   space=area.spaces.active
   if 'MATERIAL' in [e.identifier for e in space.shading.bl_rna.properties['color_type'].enum_items]:space.shading.color_type='MATERIAL'
   space.overlay.show_floor=False;space.overlay.show_axis_x=False;space.overlay.show_axis_y=False
   view=space.region_3d;view.view_location=centre
   direction=(.65,-1,.6) if row['category']=='ghat' else (1,1.5,.8)
   view.view_rotation=Vector(direction).to_track_quat('Z','Y')
   view.view_distance=max(row['dimensionsStuds'].values())*1.4;view.view_perspective='ORTHO'

def package():
 rows=json.loads((BASE/'asset-manifest.json').read_text(encoding='utf8'))
 master=BASE/'Howrah_Riverfront_Library.blend'
 bpy.ops.wm.open_mainfile(filepath=str(master),load_ui=False)
 assert len(bpy.data.scenes)==26 and all(s.get('Task')=='005' for s in bpy.data.scenes)
 for row in rows:
  assert sum(len(p.vertices)-2 for o in bpy.data.scenes[row['assetId']].objects for p in o.data.polygons)==row['assembledTriangles']
 first=next(r for r in rows if r['category']=='ghat')
 versions=bpy.context.preferences.filepaths.save_version
 try:
  bpy.context.preferences.filepaths.save_version=0
  frame(first);bpy.ops.wm.save_as_mainfile(filepath=str(master),check_existing=False,compress=True)
  for row in rows:
   source=BASE/row['source'];bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
   assert len(bpy.data.scenes)==1 and len(bpy.data.objects)==row['meshInstances'],row['assetId']
   assert sum(len(p.vertices)-2 for o in bpy.data.objects for p in o.data.polygons)==row['assembledTriangles'],row['assetId']
   frame(row);bpy.ops.wm.save_as_mainfile(filepath=str(source),check_existing=False,compress=True)
  bpy.ops.wm.open_mainfile(filepath=str(master),load_ui=False);frame(first)
 finally:bpy.context.preferences.filepaths.save_version=versions
 report=json.loads((BASE/'validation.json').read_text(encoding='utf8'))
 report['sourceFilesReopenedAndPackaged']=len(rows);report['masterSceneCount']=len(bpy.data.scenes)
 (BASE/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
 print(json.dumps(dict(packagedSourceFiles=len(rows),masterScenes=len(bpy.data.scenes),activeScene=first['assetId'])))

if __name__=='__main__':package()
