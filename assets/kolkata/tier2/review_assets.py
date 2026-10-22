"""Small authoring preview set; not a gameplay or performance test suite."""
import bpy,json
from pathlib import Path
from mathutils import Vector

ROOT=Path(r'C:\Users\Sambit Pradhan\Documents\Indian_Hood')
OUT=ROOT/'artifacts/review/tier2';OUT.mkdir(parents=True,exist_ok=True)

def render_asset(slug,courtyard=False):
 scene=next(s for s in bpy.data.scenes if s.get('AssetId')=='kolkata.tier2.'+slug)
 bpy.context.window.scene=scene
 camera=scene.camera
 original=camera.matrix_world.copy();scale=camera.data.ortho_scale
 if courtyard:
  # A view inside the accessible court, rather than another exterior roof view.
  camera.location=(18,25,17)
  target=Vector((-3,-30,17));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
  camera.data.type='PERSP';camera.data.lens=22
 name=slug+('_courtyard' if courtyard else '')
 scene.render.filepath=str(OUT/(name+'.png'))
 try:bpy.ops.render.render(write_still=True)
 finally:camera.matrix_world=original;camera.data.ortho_scale=scale;camera.data.type='ORTHO'
 print('REVIEW_SAVED '+name,flush=True)

if __name__=='__main__':
 for slug in ['writers_building','gpo','metropolitan_building','town_hall','jorasanko_thakur_bari']:render_asset(slug)
 render_asset('jorasanko_thakur_bari',True)
