"""One inexpensive contact-sheet pass. Helpers are never saved into the source."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[3]
bpy.ops.wm.open_mainfile(filepath=str(BASE.parents[1]/'VictoriaMemorial.blend'))
manifest=json.loads((BASE/'two-storey-manifest.json').read_text())
for row in manifest['assets']:
    if (BASE/row['preview']).exists():continue
    source=bpy.data.scenes[row['assetId']]
    scene=source.copy()
    scene.name='Review_'+row['assetId']
    scene.render.engine='CYCLES'
    scene.cycles.samples=12
    scene.cycles.use_denoising=True
    scene.render.resolution_x=512
    scene.render.resolution_y=512
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.view_settings.view_transform='AgX'
    world=bpy.data.worlds.new('AssetReviewWorld')
    world.use_nodes=True
    world.node_tree.nodes['Background'].inputs['Color'].default_value=(.17,.19,.22,1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value=.5
    scene.world=world
    points=[o.matrix_world@Vector(v) for o in source.objects if o.type=='MESH' for v in o.bound_box]
    low=Vector([min(p[i] for p in points) for i in range(3)])
    high=Vector([max(p[i] for p in points) for i in range(3)])
    center=(low+high)/2
    span=max(high-low)
    cameraData=bpy.data.cameras.new('AssetReviewCamera')
    camera=bpy.data.objects.new('AssetReviewCamera',cameraData)
    scene.collection.objects.link(camera)
    camera.location=center+Vector((1.1,1.65,.9))*span
    camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
    cameraData.type='ORTHO'
    cameraData.ortho_scale=span*1.45
    scene.camera=camera
    helpers=[camera]
    for offset, power, size in [((1,1.5,2),70,1.4),((-1,1,.6),35,1),((0,-1,1.2),55,1)]:
        data=bpy.data.lights.new('AssetReviewArea','AREA')
        data.energy=span*span*power
        data.shape='DISK'
        data.size=span*size
        obj=bpy.data.objects.new('AssetReviewArea',data)
        obj.location=center+Vector(offset)*span
        obj.rotation_euler=(center-obj.location).to_track_quat('-Z','Y').to_euler()
        scene.collection.objects.link(obj)
        helpers.append(obj)
    out=BASE/row['preview']
    out.parent.mkdir(parents=True,exist_ok=True)
    scene.render.filepath=str(out)
    bpy.ops.render.render(write_still=True,scene=scene.name)
    print('PREVIEW '+row['assetId'],flush=True)
    for obj in helpers:bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.scenes.remove(scene)
    bpy.data.worlds.remove(world)
print('Previews complete. Run host Python authoring/task009/make_review_sheet.py for the contact sheet.',flush=True)
