"""Apply the same final art/native-structure plan to the original editable source."""
import bpy,bmesh,json,sys,math
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3];KIT=BASE.parent
sys.path.insert(0,str(KIT));import pipeline;pipeline.PALETTE['Mushroom']='A29D93'
from pipeline import Geo,bp,material
path=BASE.parents[1]/'VictoriaMemorial.blend';bpy.ops.wm.open_mainfile(filepath=str(path))
scene=next(s for s in bpy.data.scenes if s.collection.children.get('VM009_TwoStoreyInterior'))
bpy.context.window.scene=scene
plan=json.loads((ROOT/'authoring/task009/final-plan.json').read_text())
for name in ['VM009_ExhibitArt','VM009_NativeArchitecture','VM009_Lighting','VM009_GameplayMarkers']:
 old=bpy.data.collections.get(name)
 if old:
  for o in list(old.objects):bpy.data.objects.remove(o,do_unlink=True)
  bpy.data.collections.remove(old)
collections={}
for key,name in [('art','VM009_ExhibitArt'),('native','VM009_NativeArchitecture'),('lights','VM009_Lighting'),('markers','VM009_GameplayMarkers')]:
 c=bpy.data.collections.new(name);scene.collection.children.link(c);collections[key]=c
catalog={a['assetId']:(KIT,a) for a in json.loads((KIT/'asset-manifest.json').read_text())['assets']}
catalog.update({a['assetId']:(BASE,a) for a in json.loads((BASE/'two-storey-manifest.json').read_text())['assets']})
def master(id):
 if id not in bpy.data.collections:
  base,row=catalog[id]
  with bpy.data.libraries.load(str(base/row['source']),link=False) as (available,data):data.collections=[id]
 col=bpy.data.collections[id]
 if id=='VIC_B14_COURTYARD_SPANDREL':
  for o in col.objects:
   if o.type=='MESH':o.data.materials.clear();o.data.materials.append(bpy.data.objects['WingCourtyardWall'].data.materials[0])
 if id=='VIC_A03_ARCH_10':
  for o in col.objects:
   if o.type=='MESH' and o.get('PaletteRole')=='Stone':o.data.materials.clear();o.data.materials.append(material('Ivory'))
 return col
artworks=json.loads((KIT/'artwork/manifest.json').read_text())['artworks']
bindings={b['frameInstance']:b['artworkId'] for b in plan['artworkBindings']}
wall=[p for p in plan['instances'] if p['role']=='WallArtwork']
for i,p in enumerate(wall):bindings[p['instanceId']]=p.get('artworkId',artworks[i%4]['artworkId'])
variants={}
for p in plan['instances']:
 if p['role']=='TwoStoreyArchitecture':
  o=bpy.data.objects.get(p['instanceId'])
  if o:
   stretch=p.get('stretch',[1,1,1]);o.scale=(p['scale']*stretch[0],p['scale']*stretch[2],p['scale']*stretch[1]);o.location=bp(p['position']);o.rotation_euler.z=p['yaw']
  continue
 col=master(p['assetId'])
 if p.get('materialOverrides'):
  key=p['assetId']+json.dumps(p['materialOverrides'],sort_keys=True)
  if key not in variants:
   c=bpy.data.collections.new('VIC009_RoomMaterial_'+p['assetId'])
   for obj in col.objects:
    duplicate=obj.copy();c.objects.link(duplicate)
    if obj.type=='MESH' and obj.get('PaletteRole') in p['materialOverrides']:
     duplicate.data=obj.data.copy();duplicate.data.materials.clear();duplicate.data.materials.append(material(p['materialOverrides'][obj['PaletteRole']]))
   variants[key]=c
  col=variants[key]
 if p['role']=='PremiumBanner':
  if 'PremiumBanner' not in variants:
   c=bpy.data.collections.new('VIC009_PremiumBanner')
   for obj in col.objects:
    copy=obj.copy();c.objects.link(copy)
    if obj.type=='MESH' and obj.get('PaletteRole')=='Teal':copy.data=obj.data.copy();copy.data.materials.clear();copy.data.materials.append(material('Oxblood'))
   variants['PremiumBanner']=c
  col=variants['PremiumBanner']
 aid=bindings.get(p['instanceId'])
 if aid:
  if aid not in variants:
   variant=bpy.data.collections.new('VIC009_Artwork_'+aid)
   item=next(a for a in artworks if a['artworkId']==aid)
   image=bpy.data.images.load(str(KIT/item['texture']),check_existing=True);image.pack()
   for obj in col.objects:
    duplicate=obj.copy();variant.objects.link(duplicate)
    if obj.type=='MESH' and obj.get('Component')=='Canvas':
     duplicate.data=obj.data.copy();mat=material('Paper').copy();node=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image;mat.node_tree.links.new(tex.outputs['Color'],node.inputs['Base Color']);duplicate.data.materials.clear();duplicate.data.materials.append(mat)
   variants[aid]=variant
  col=variants[aid]
 o=bpy.data.objects.new(p['instanceId'],None);o.instance_type='COLLECTION';o.instance_collection=col;o.location=bp(p['position']);o.rotation_euler.z=p['yaw'];o.rotation_euler.x=p.get('pitch',0);stretch=p.get('stretch',[1,1,1]);o.scale=(p['scale']*stretch[0],p['scale']*stretch[2],p['scale']*stretch[1]);o['AssetId']=p['assetId'];o['SourceMarker']=p['sourceMarker'];collections['art'].objects.link(o)
def native(row):
 g=Geo();g.box((0,0,0),row['size'],row['material'])
 verts,faces=next(iter(g.groups.values()));m=bpy.data.meshes.new(row['name']);m.from_pydata([bp(v) for v in verts],[],faces);m.update();o=bpy.data.objects.new(row['name'],m);o.location=bp(row['position']);o.rotation_euler.z=row['yaw'];o.data.materials.append(material(row['material']));o['Task009Native']=True;o['Collision']=row['solid'];o['Purpose']=row['purpose'];collections['native'].objects.link(o)
 if row['purpose']=='InvisibleCollision':o.hide_render=True;o.hide_viewport=True
for row in plan['nativeStructure']:native(row)
# Mirror Task007's still-authoritative paired partitions into the editable source.
for x in [-66,69]:
 for lo,hi in [(-93,-89),(-79,-71),(-61,-59)]:native(dict(name='ApprovedGroundPartition',position=[x,17,(lo+hi)/2],size=[1,20.4,hi-lo],material='Ivory',yaw=0,solid=True,purpose='PreservedGroundLayout'))
 for z in [-84,-66]:native(dict(name='ApprovedGroundLintel',position=[x,24,z],size=[1,6.4,10],material='Ivory',yaw=0,solid=True,purpose='PreservedGroundLayout'))
for row in plan['lights']:
 data=bpy.data.lights.new(row['id'],'SPOT' if row['kind']=='Spot' else 'POINT');data.energy=row.get('blenderPower',2200 if row['kind']=='Spot' else 1200);data.color=(1,.89,.72);data.use_custom_distance=True;data.cutoff_distance=row['range']
 if row['kind']=='Spot':data.spot_size=math.radians(row['angle']);data.spot_blend=.6
 o=bpy.data.objects.new(row['id']+'_PreviewLight',data);o.location=bp(row['position']);collections['lights'].objects.link(o);o['RobloxRange']=row['range'];o['RobloxBrightness']=row['brightness'];o['RobloxShadows']=row.get('shadows',False)
 if row.get('target'):
  from mathutils import Vector
  o.location.z+=.3;o.rotation_euler=(Vector(bp(row['target']))-o.location).to_track_quat('-Z','Y').to_euler()
scene['Task009ArtInstances']=len(plan['instances']);scene['Task009PlacedArtTriangles']=plan['statistics']['importedPlacedTriangles'];scene['Task009LightCount']=len(plan['lights'])
def marker(id,pos,attrs):
 o=bpy.data.objects.new(id,None);o.location=bp(pos);o.empty_display_type='CUBE';o.empty_display_size=1
 for k,v in attrs.items():o[k]=v
 collections['markers'].objects.link(o)
layout=plan['upperLayout'];ground=layout['groundFloorOriginal']
for o in list(bpy.data.collections['VM_Metadata'].objects):
 if o.name.startswith('VIC_LOOT_') and o.get('Floor')==2:bpy.data.objects.remove(o,do_unlink=True)
for item in ground['loot']+layout['upperLoot']:
 attrs=dict(LootId=item['lootId'],GalleryId=item['roomId'],Floor=item.get('floor',1),HeistId='VIC_HEIST_007',LootCategory=item['category'],ExhibitName=item['name'],AlertOnTheftStart=True)
 for src,dst in [('provisionalValue','ProvisionalValue'),('capacityCost','CapacityCost'),('collectionSeconds','CollectionSeconds')]:
  if src in item:attrs[dst]=item[src]
 marker(item['lootId'],item['rootPosition'],attrs)
for item in layout['upperSecurity']:marker(item['securityId'],item['position'],dict(SecurityId=item['securityId'],SecurityType=item['securityType'],Floor=2,Active=False))
for item in ground['security']:marker(item['securityId'],item['padCenter'],dict(SecurityId=item['securityId'],SecurityType=item['type'],Floor=1,Active=False))
for item in ground['exits']:marker(item['routeId'],item['position'],dict(RouteId=item['routeId'],Bidirectional=True))
for item in ground['restricted']+layout['restrictedUpper']:marker(item['id'],item['center'],dict(RestrictedId=item['id'],GalleryId=item['roomId'],HeistId='VIC_HEIST_007'))
for item in ground['rooms']+layout['upperRooms']:marker(item['roomId'],[item['centerXZ'][0],34 if item in layout['upperRooms'] else 6.8,item['centerXZ'][1]],dict(RoomId=item['roomId'],RoomName=item['name']))
scene['SharedRobberyEvent']='VIC_HEIST_007';scene['RoomConnectionGraph']=json.dumps(layout['connections']);scene['FutureAlertPolicy']=layout['sharedEvent']['alert']
# Align new material roles with Studio without touching preserved VM exterior materials.
m=material('Stone');srgb=[215/255,207/255,189/255];linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in srgb]
m.diffuse_color=(*linear,1);next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'].default_value=(*linear,1)
floorMat=bpy.data.materials.get('VIC009_HonedFloor')
if floorMat is None:
 floorMat=material('Ivory').copy();floorMat.name='VIC009_HonedFloor';nodes=floorMat.node_tree.nodes;links=floorMat.node_tree.links
 image=bpy.data.images.load(str(BASE/'materials/VIC009_PaleStoneFloor_512.png'),check_existing=True);image.pack()
 tex=nodes.new('ShaderNodeTexImage');tex.image=image;tex.extension='REPEAT'
 coord=nodes.new('ShaderNodeTexCoord');scale=nodes.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs['Scale'].default_value=1/12
 links.new(coord.outputs['Object'],scale.inputs[0]);links.new(scale.outputs['Vector'],tex.inputs['Vector']);bsdf=next(n for n in nodes if n.type=='BSDF_PRINCIPLED');links.new(tex.outputs['Color'],bsdf.inputs['Base Color']);bsdf.inputs['Roughness'].default_value=.8
for col in [bpy.data.collections['VM_Structure_Collision']]+[bpy.data.collections[r['assetId']] for r in json.loads((BASE/'two-storey-manifest.json').read_text())['assets']]:
 for o in col.objects:
  if o.type=='MESH' and (str(o.get('Component','')).startswith('Floor') or o.get('Component')=='Landing' or o.name.startswith(('WingFloor','RotundaFloor'))):o.data.materials.clear();o.data.materials.append(floorMat)
lamp=bpy.data.materials.get('VIC009_LampDiffuser')
if lamp is None:
 lamp=material('Paper').copy();lamp.name='VIC009_LampDiffuser';node=next(n for n in lamp.node_tree.nodes if n.type=='BSDF_PRINCIPLED');node.inputs['Base Color'].default_value=(1,.84,.57,1);node.inputs['Emission Color'].default_value=(1,.84,.57,1);node.inputs['Emission Strength'].default_value=.3
for id in ['VIC_B12_LIGHT','VIC_F01_PAINTING_MONOLITH']:
 for o in bpy.data.collections[id].objects:
  if o.type=='MESH' and o.get('Component')=='Diffuser':o.data.materials.clear();o.data.materials.append(lamp)
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
print(json.dumps(plan['statistics']),flush=True)
