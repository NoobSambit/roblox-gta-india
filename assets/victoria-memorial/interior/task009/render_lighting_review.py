"""Actual authored museum lights; no presentation lamps or HDRI fill."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
bpy.ops.wm.open_mainfile(filepath=str(BASE.parents[1] / 'VictoriaMemorial.blend'))
original = next(s for s in bpy.data.scenes if s.collection.children.get('VM009_TwoStoreyInterior'))
scene = original.copy()
scene.name = 'Task009_LightingReview_Unsaved'
def exclude(layer):
    if layer.collection.name in ['VM_Presentation', 'VM_Metadata', 'VM009_GameplayMarkers']:
        layer.exclude = True
    for child in layer.children:
        exclude(child)
for layer in scene.view_layers:
    exclude(layer.layer_collection)
world = bpy.data.worlds.new('Review_LowAmbient')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (.45,.5,.6,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = .12
scene.world = world
scene.render.engine = 'CYCLES'
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_x = 1056
scene.render.resolution_y = 1280
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.view_settings.view_transform = 'AgX'
scene.view_settings.exposure = 0
data = bpy.data.cameras.new('LightingReviewCamera')
camera = bpy.data.objects.new('LightingReviewCamera', data)
scene.collection.objects.link(camera)
scene.camera = camera
def bp(p): return Vector((p[0], -p[2], p[1]))
dest = ROOT / 'artifacts/review/task009/blender'
dest.mkdir(parents=True, exist_ok=True)
for name, eye, target, lens in [
    ('hall_actual_lighting', (0,13,-25), (0,47,0), 17),
    ('upper_hall_actual_lighting', (0,40,-26), (0,75,0), 17),
]:
    camera.location = bp(eye)
    camera.rotation_euler = (bp(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    data.lens = lens
    data.clip_end = 800
    scene.render.filepath = str(dest / (name+'.png'))
    bpy.ops.render.render(write_still=True, scene=scene.name)
    print(json.dumps({'render':name,'authoredLights':len(bpy.data.collections['VM009_Lighting'].objects),'presentationLightsExcluded':True}), flush=True)
