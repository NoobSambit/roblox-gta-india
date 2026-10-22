"""Final original preview PNGs, saved beside each delivered asset and tracked."""
import bpy,json,math
from mathutils import Vector
from pipeline import BASE

def setup():
 scene=bpy.data.scenes.get('HBR_PREVIEW_ONLY')
 if scene:return scene
 scene=bpy.data.scenes.new('HBR_PREVIEW_ONLY');scene.render.engine='CYCLES'
 scene.cycles.samples=16;scene.cycles.use_denoising=True;scene.view_settings.view_transform='Standard'
 scene.render.image_settings.file_format='PNG';scene.render.resolution_percentage=100
 world=bpy.data.worlds.new('HBR_PreviewWorld');world.use_nodes=True
 bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.32,.39,.42,1);bg.inputs['Strength'].default_value=.8;scene.world=world
 camera=bpy.data.objects.new('HBR_PreviewCamera',bpy.data.cameras.new('HBR_PreviewCamera'))
 scene.collection.objects.link(camera);scene.camera=camera
 sun=bpy.data.objects.new('HBR_PreviewSun',bpy.data.lights.new('HBR_PreviewSun','SUN'))
 sun.data.energy=1.7;sun.data.angle=.35;sun.rotation_euler=(.45,-.55,-.4);scene.collection.objects.link(sun)
 return scene

def render_row(row,extra=False):
 scene=setup();next(w for wm in bpy.data.window_managers for w in wm.windows).scene=scene
 for collection in list(scene.collection.children):scene.collection.children.unlink(collection)
 asset=bpy.data.scenes[row['assetId']];scene.collection.children.link(next(iter(asset.collection.children)))
 points=[o.matrix_world@v.co for o in asset.objects if o.type=='MESH' for v in o.data.vertices]
 low=Vector(tuple(min(p[i] for p in points) for i in range(3)));high=Vector(tuple(max(p[i] for p in points) for i in range(3)))
 target=(low+high)/2;radius=max(high-low);folder=(BASE/row['source']).parent
 specs=[('preview.png',(1,1.5,.9),640,640)]
 if row['category']=='bridge':specs=[('preview.png',(1,.45,.28),1600,740),('preview-side.png',(1,0,.08),1600,600),('preview-road.png',None,1200,800)]
 elif row['category']=='ghat':specs=[('preview.png',(.65,1,.7),1300,950),('preview-road.png',(.65,-1,.6),1300,950)]
 elif row['category']=='riverfront_structures':specs=[('preview.png',(1,1.4,.9),800,650)]
 for name,direction,w,h in specs:
  if not extra and name!='preview.png':continue
  scene.render.resolution_x=w;scene.render.resolution_y=h
  camera=scene.camera
  if direction:
   camera.data.type='ORTHO';camera.location=target+Vector(direction).normalized()*radius*2.5
   camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
   inverse=camera.matrix_world.inverted();bpy.context.view_layer.update();inverse=camera.matrix_world.inverted()
   projected=[inverse@p for p in points]
   width=max(p.x for p in projected)-min(p.x for p in projected);height=max(p.y for p in projected)-min(p.y for p in projected)
   camera.data.ortho_scale=max(width,height*w/h)*1.12
  else:
   camera.data.type='PERSP';camera.data.lens=28;camera.location=(0,420,39)
   camera.rotation_euler=(Vector((0,120,44))-camera.location).to_track_quat('-Z','Y').to_euler()
  camera.data.clip_end=10000;scene.render.filepath=str(folder/name)
  bpy.ops.render.render(write_still=True);print('PNG '+row['assetId']+'/'+name,flush=True)
 for collection in list(scene.collection.children):scene.collection.children.unlink(collection)

def render_category(category):
 rows=json.loads((BASE/'asset-manifest.json').read_text(encoding='utf8'))
 for row in rows:
  if row['category']==category:render_row(row,extra=True)

if __name__=='__main__':
 for category in ['bridge','ghat','riverfront_structures','props','context']:render_category(category)
