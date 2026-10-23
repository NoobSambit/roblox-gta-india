"""Read existing Blender sources without changing them; write exact Studio assembly data."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'assets/kolkata'

def rgb(v):return v*12.92 if v<=.0031308 else 1.055*v**(1/2.4)-.055
def roblox(p):return [round(p.x,6),round(p.z,6),round(-p.y,6)]

def inspect(source,record,meta=None):
 with bpy.data.libraries.load(str(source),link=False) as (available,loaded):loaded.scenes=available.scenes
 scene=loaded.scenes[0]
 next(w for wm in bpy.data.window_managers for w in wm.windows).scene=scene
 bpy.context.view_layer.update()
 objects=[o for o in scene.objects if o.type=='MESH' and len(o.data.materials)>0];result=[];points=[]
 specs={o['name']:o for o in meta['objects']} if meta else {}
 if meta:
  objects=[o for o in objects if o.name in specs]
  assert len(objects)==len(specs),(record['assetId'],len(objects),len(specs))
 for o in objects:
  local=[Vector(p) for p in o.bound_box];world=[o.matrix_world@p for p in local];points.extend(world)
  centre=Vector(tuple((min(p[i] for p in world)+max(p[i] for p in world))/2 for i in range(3)))
  spec=specs.get(o.name,{})
  material=o.data.materials[0];node=next(n for n in material.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
  color=[round(rgb(v),6) for v in node.inputs['Base Color'].default_value[:3]]
  result.append(dict(name=o.name,meshKey=spec.get('meshKey',o.get('MeshKey',o.name)),position=roblox(o.location),yaw=round(o.rotation_euler.z,9),centre=roblox(centre),color=color,role=o.get('PaletteRole',o.get('Role',o.name.split('__')[-1])),group=spec.get('group','Geometry'),triangles=sum(len(p.vertices)-2 for p in o.data.polygons)))
 lo=[min(roblox(p)[i] for p in points) for i in range(3)];hi=[max(roblox(p)[i] for p in points) for i in range(3)]
 record.update(objects=result,boundsMinStuds=lo,boundsMaxStuds=hi,dimensions=[round(hi[i]-lo[i],5) for i in range(3)],triangles=sum(o['triangles'] for o in result),source=str(source.relative_to(ROOT)).replace('\\','/'))
 bpy.data.scenes.remove(scene)
 return record

def main():
 catalog=[]
 for p in sorted((BASE/'tier2').glob('*/assembly.json')):
  meta=json.loads(p.read_text(encoding='utf8'));source=next(p.parent.glob('*.blend'));fbx=next((p.parent/'exports').glob('*.fbx'))
  record=dict(assetId=meta['assetId'],name=meta['label'],category='tier2',importName=fbx.stem,collisionBoxes=meta['collisionBoxes'])
  catalog.append(inspect(source,record,meta))
 for family in ['tier3','howrah_bridge']:
  folder=BASE/family;rows=json.loads((folder/'asset-manifest.json').read_text(encoding='utf8'))
  for r in rows:
   asset=r.get('assetId',r.get('id'))
   record=dict(assetId=asset,name=r['name'],category='tier3' if family=='tier3' else r['category'],family=r.get('family'),importName=Path(r['export']).stem,collisionBoxes=[],sockets=r.get('sockets',{}))
   if family=='tier3':record['bodySize']=[r['width'],r['floors']*12,r['depth']]
   catalog.append(inspect(folder/r['source'],record))
 for r in json.loads((BASE/'tier25/asset-manifest.json').read_text(encoding='utf8')):
  record=dict(assetId=r['assetId'],name=r['name'],category='tier25',importName=Path(r['export']).stem,collisionBoxes=r['collisionBoxes'],sockets={'Entrance':r['entrance'],'RearExit':r['rearExit'],'Objective':r['objectiveAttachment']})
  catalog.append(inspect(BASE/'tier25'/r['source'],record))
 assert len(catalog)==63 and len({r['assetId'] for r in catalog})==63
 out=ROOT/'authoring/task006/asset-catalog.json';out.write_text(json.dumps(catalog,separators=(',',':')),encoding='utf8')
 print(json.dumps({'catalogAssets':len(catalog),'meshInstances':sum(len(r['objects']) for r in catalog),'sourceMeshes':sum(len({o['meshKey'] for o in r['objects']}) for r in catalog),'fileBytes':out.stat().st_size}),flush=True)

if __name__=='__main__':main()
