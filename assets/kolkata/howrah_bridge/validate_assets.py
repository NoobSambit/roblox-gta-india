"""One required geometry/file/FBX inventory; no gameplay or performance test."""
import bpy,bmesh,json,math
from io_scene_fbx import parse_fbx
from pipeline import BASE

def check(require_previews=False):
 rows=json.loads((BASE/'asset-manifest.json').read_text(encoding='utf8'))
 refs={r['id']:r for r in json.loads((BASE/'references/retrieved.json').read_text(encoding='utf8'))}
 counts={c:sum(r['category']==c for r in rows) for c in ['bridge','ghat','riverfront_structures','props','context']}
 assert counts==dict(bridge=1,ghat=1,riverfront_structures=7,props=15,context=2),counts
 results=[]
 tri=lambda mesh:sum(len(p.vertices)-2 for p in mesh.polygons)
 for row in rows:
  for key in row['references']:
   ref=refs[key];assert ref.get('examined') and (BASE/ref['localPhoto']).is_file(),key
  source=BASE/row['source'];export=BASE/row['export']
  assert source.is_file() and source.stat().st_size>1000 and export.is_file() and export.stat().st_size>1000
  with bpy.data.libraries.load(str(source),link=False) as (available,unused):assert available.scenes==[row['assetId']]
  scene=bpy.data.scenes[row['assetId']];objects=[o for o in scene.objects if o.type=='MESH'];unique={o.data for o in objects}
  assert scene.unit_settings.system=='NONE' and scene.unit_settings.scale_length==1
  assert len(objects)==row['meshInstances'] and len(unique)==row['uniqueMeshes']
  assert sum(tri(o.data) for o in objects)==row['assembledTriangles']
  assert sum(tri(m) for m in unique)==row['uniqueGeometryTriangles']
  assert all(all(abs(s-1)<1e-6 for s in o.scale) and not o.modifiers for o in objects)
  for mesh in unique:
   assert tri(mesh)<10000
   assert all(math.isfinite(v) for p in mesh.vertices for v in p.co)
   assert all(p.area>1e-7 for p in mesh.polygons),(row['assetId'],mesh.name,'zero area')
   assert all(len(p.vertices)<=4 for p in mesh.polygons)
   bm=bmesh.new();bm.from_mesh(mesh)
   assert all(e.is_manifold and e.is_contiguous for e in bm.edges),(row['assetId'],mesh.name,'edge/winding')
   faces=set(bm.faces)
   while faces:
    start=faces.pop();component=[start];stack=[start]
    while stack:
     f=stack.pop()
     for edge in f.edges:
      for adjacent in edge.link_faces:
       if adjacent in faces:faces.remove(adjacent);component.append(adjacent);stack.append(adjacent)
    volume=sum(f.calc_center_median().dot(f.normal)*f.calc_area()/3 for f in component)
    assert volume>1e-7,(row['assetId'],mesh.name,'inward solid',volume)
   bm.free()
   assert len(mesh.materials)==1 and mesh.materials[0]
   assert not any(n.type=='TEX_IMAGE' for n in mesh.materials[0].node_tree.nodes)
  root,version=parse_fbx.parse(str(export));fbx_objects=next(e for e in root.elems if e.id==b'Objects')
  models={e.props[0]:e for e in fbx_objects.elems if e.id==b'Model' and e.props[-1]==b'Mesh'}
  materials={e.props[0] for e in fbx_objects.elems if e.id==b'Material'}
  geometry={}
  for e in fbx_objects.elems:
   if e.id!=b'Geometry':continue
   indices=next(x for x in e.elems if x.id==b'PolygonVertexIndex').props[0];count=0;total=0
   for index in indices:
    count+=1
    if index<0:assert count>=3;total+=count-2;count=0
   assert count==0
   vertices=next(x for x in e.elems if x.id==b'Vertices').props[0];assert all(math.isfinite(v) for v in vertices)
   layer=next(x for x in e.elems if x.id==b'LayerElementMaterial')
   indices=next(x for x in layer.elems if x.id==b'Materials').props[0]
   assert len(indices)>0 and all(i==0 for i in indices),(row['assetId'],'material slot')
   geometry[e.props[0]]=total
  connections=next(e for e in root.elems if e.id==b'Connections')
  bound={model:[] for model in models}
  for connection in connections.elems:
   if connection.id==b'C' and connection.props[0]==b'OO' and connection.props[1] in materials and connection.props[2] in bound:
    bound[connection.props[2]].append(connection.props[1])
  assert all(len(slots)==1 for slots in bound.values()),(row['assetId'],'missing/duplicate FBX material binding')
  assert len(geometry)==row['uniqueMeshes'] and sum(geometry.values())==row['uniqueGeometryTriangles'],(row['assetId'],'FBX reuse')
  actual=sum(geometry[c.props[1]] for c in connections.elems if c.id==b'C' and c.props[0]==b'OO' and c.props[1] in geometry and c.props[2] in models)
  assert len(models)==len(objects) and actual==row['assembledTriangles'],(row['assetId'],len(models),actual)
  assert not any(e.id in [b'Video',b'Texture'] for e in fbx_objects.elems)
  if require_previews:assert (source.parent/'preview.png').is_file()
  results.append(dict(assetId=row['assetId'],status='passed',assembledTriangles=actual,
   uniqueSourceTriangles=row['uniqueGeometryTriangles'],fbxUniqueGeometries=len(geometry),
   fbxMeshInstances=len(models),fbxMaterialBindings='one palette material per mesh instance',largestMeshTriangles=row['largestMeshTriangles'],fbxVersion=version))
 totals={c:sum(r['assembledTriangles'] for r in rows if r['category']==c) for c in counts}
 assert 35000<=totals['bridge']<=55000 and 8000<=totals['ghat']<=15000
 assert 5000<=totals['riverfront_structures']<=12000 and 4000<=totals['props']<=8000
 assert not any('Pier' in o.name for o in bpy.data.scenes['KOL_HBR_HOWRAH'].objects)
 assert not any(o.get('PaletteRole') in ['Oxide','Green','Window','DarkWood'] for o in bpy.data.scenes['KOL_HBR_GHAT'].objects)
 report=dict(assetCount=len(rows),counts=counts,assembledCategoryTriangles=totals,
  uniqueCategoryTriangles={c:sum(r['uniqueGeometryTriangles'] for r in rows if r['category']==c) for c in counts},
  largestMeshTriangles=max(r['largestMeshTriangles'] for r in rows),budgetExceedances=[],textureDependencies=0,
  scope='Source inventory, geometry/normals/transforms/scale, reference coverage, parsed FBX geometry/reuse/material bindings and final PNG inventory. No Studio import or in-game performance claims.',assets=results)
 (BASE/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
 print(json.dumps({k:v for k,v in report.items() if k!='assets'}));return report

if __name__=='__main__':check()
