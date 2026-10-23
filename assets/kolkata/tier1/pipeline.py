"""Original skyline authoring; established stud-unit FBX convention."""
import bpy
import bmesh
import json
import math
import os
import sys
from pathlib import Path
from mathutils import Vector

BASE = Path(__file__).resolve().parent
EXPORT_DIR = BASE.parents[2]/'exports'/'kolkata_tier1'
sys.path.insert(0, str(BASE.parent/'tier2'))
from geometry import bv
from architecture_geometry import Geometry

COLORS = {
    'Pearl':'DEDCD0', 'Stone':'BAAB8E', 'PaleStone':'D9C9A8',
    'Graphite':'293C43', 'Glass':'405D6B', 'GlassBlue':'718F9F',
    'GlassLight':'9EB6BB', 'Silver':'AEB8B5', 'Bronze':'92754E',
    'Terra':'A55438', 'Louvre':'74513C', 'Asphalt':'484F51',
    'Paving':'9E9D92', 'Leaf':'476A4D', 'LeafLight':'708758',
    'Water':'369DA8', 'WarmWindow':'E2C889', 'Accent':'F1D7A0',
    'RoyalOchre':'B79B61', 'RoyalTrim':'D1BA83', 'RoyalStone':'927B52',
    'PondWater':'2C443D',
}


def material(role):
    name='KOL_T1_'+role
    rgb=[int(COLORS[role][i:i+2],16)/255 for i in (0,2,4)]
    rgb=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
    base_rgb=rgb
    if role=='WarmWindow':
        h=COLORS['GlassBlue'];srgb=[int(h[i:i+2],16)/255 for i in (0,2,4)]
        base_rgb=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in srgb]
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True;m.diffuse_color=(*base_rgb,1)
    n=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    n.inputs['Base Color'].default_value=(*base_rgb,1)
    n.inputs['Roughness'].default_value=.32 if 'Glass' in role else .72
    n.inputs['Metallic'].default_value=.35 if role in ('Silver','Bronze') else .08
    if role in ('Accent','WarmWindow'):
        n.inputs['Emission Color'].default_value=(*rgb,1)
        n.inputs['Emission Strength'].default_value=0
    return m


def tris(mesh):
    return sum(len(p.vertices)-2 for p in mesh.polygons)


class Asset:
    def __init__(self,key,name,folder=None,export_dir=None):
        self.key=key;self.name=name;self.cache={};self.sections={};self.sockets={}
        self.scene=bpy.data.scenes.new('KOL_T1_'+key.upper())
        bpy.context.window.scene=self.scene
        self.scene.unit_settings.system='NONE';self.scene.unit_settings.scale_length=1
        self.scene['AssetId']='KOL_T1_'+key.upper()
        self.scene['AuthoringUnits']='One neutral Blender unit = one Roblox stud'
        self.scene['Front']='Blender +Y; Roblox -Z'
        self.root=bpy.data.collections.new(self.scene.name+'__SOURCE')
        self.scene.collection.children.link(self.root)
        self.folder=Path(folder) if folder else BASE/key
        self.export_dir=Path(export_dir) if export_dir else EXPORT_DIR
        self.folder.mkdir(parents=True,exist_ok=True)

    def section(self,name):
        if name not in self.sections:
            c=bpy.data.collections.new(self.scene.name+'__'+name)
            self.root.children.link(c);self.sections[name]=c
        return self.sections[name]

    def put(self,key,geo=None,pos=(0,0,0),yaw=0,section='Foundation',role='Visual'):
        if key not in self.cache:
            assert geo is not None, key
            # Keep chunks small without exploding repeated elements into objects.
            groups={}
            for face,mat,smooth in zip(geo.f,geo.mat,geo.smooth):
                groups.setdefault(mat,[]).append((face,smooth))
            meshes=[]
            for mat,faces in groups.items():
                # Keep each connected solid intact when batching. Splitting a
                # closed primitive mid-face would create artificial cut skins.
                by_vertex={}
                for index,(face,_) in enumerate(faces):
                    for v in face:by_vertex.setdefault(v,[]).append(index)
                unseen=set(range(len(faces)));components=[]
                while unseen:
                    stack=[unseen.pop()];component=[]
                    while stack:
                        index=stack.pop();component.append(faces[index])
                        for v in faces[index][0]:
                            for other in by_vertex[v]:
                                if other in unseen:unseen.remove(other);stack.append(other)
                    components.append(component)
                batches=[];batch=[];count=0
                for component in components:
                    triangles=sum(len(face)-2 for face,_ in component)
                    assert triangles<=5500,(key,mat,triangles)
                    if count+triangles>2000 and batch:
                        batches.append(batch);batch=[];count=0
                    batch.extend(component);count+=triangles
                if batch:batches.append(batch)
                for i,batch in enumerate(batches):
                    vertices=[];polys=[];smoothing=[];index_map={}
                    for face,smooth in batch:
                        indices=[]
                        for index in face:
                            if index not in index_map:
                                index_map[index]=len(vertices);vertices.append(bv(geo.v[index]))
                            indices.append(index_map[index])
                        polys.append(tuple(indices));smoothing.append(smooth)
                    mesh=bpy.data.meshes.new(f'{key}__{mat}_{i:02}')
                    mesh.from_pydata(vertices,[],polys);mesh.update()
                    for p,smooth in zip(mesh.polygons,smoothing):p.use_smooth=smooth
                    bm=bmesh.new();bm.from_mesh(mesh)
                    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.000001)
                    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
                    # Give open façade skins/decoration physical thickness to
                    # meet Roblox's volume/watertight modeling requirements.
                    unseen=set(bm.faces);open_faces=[]
                    while unseen:
                        stack=[unseen.pop()];component=[];boundary=False
                        while stack:
                            f=stack.pop();component.append(f)
                            for edge in f.edges:
                                boundary=boundary or edge.is_boundary
                                for other in edge.link_faces:
                                    if other in unseen:unseen.remove(other);stack.append(other)
                        if boundary:open_faces.extend(component)
                    if open_faces:bmesh.ops.solidify(bm,geom=open_faces,thickness=.12)
                    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
                    bmesh.ops.triangulate(bm,faces=list(bm.faces))
                    bm.to_mesh(mesh);bm.free();mesh.update()
                    mesh.materials.append(material(mat));meshes.append(mesh)
            self.cache[key]=meshes
        result=[]
        for mesh in self.cache[key]:
            obj=bpy.data.objects.new(key+'__'+mesh.materials[0].name,mesh)
            self.section(section).objects.link(obj);obj.location=bv(pos);obj.rotation_euler.z=yaw
            obj['AssetId']=self.scene.name;obj['MeshKey']=self.scene.name+'__'+mesh.name
            obj['CollisionRole']=role;obj['Section']=section
            result.append(obj)
        return result

    def text(self,words,pos,size=4,width=None,section='Signature'):
        curve=bpy.data.curves.new('Original plain text '+words,'FONT')
        curve.body=words;curve.align_x='CENTER';curve.size=size;curve.extrude=.045;curve.resolution_u=2
        o=bpy.data.objects.new(words,curve);self.section(section).objects.link(o)
        o.location=bv(pos);o.rotation_euler=(math.pi/2,0,math.pi)
        bpy.context.view_layer.objects.active=o;o.select_set(True)
        bpy.ops.object.convert(target='MESH');o=bpy.context.object
        if width:
            bpy.context.view_layer.update()
            if o.dimensions.x>width:o.scale.x=width/o.dimensions.x
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        bm=bmesh.new();bm.from_mesh(o.data)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001)
        bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.000001)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        bmesh.ops.triangulate(bm,faces=list(bm.faces))
        bm.to_mesh(o.data);bm.free();o.data.update()
        o.data.materials.append(material('Accent'));o['AssetId']=self.scene.name
        o['Section']=section;o['MeshKey']=self.scene.name+'__SIGN_'+words
        o['CollisionRole']='Decoration';o.select_set(False)

    def finish(self):
        bpy.context.view_layer.update()
        objects=[o for o in self.root.all_objects if o.type=='MESH']
        unique={o.data for o in objects}
        points=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box]
        lo=[min(p[i] for p in points) for i in range(3)];hi=[max(p[i] for p in points) for i in range(3)]
        parts=[]
        export_dir=self.export_dir;export_dir.mkdir(parents=True,exist_ok=True)
        for name,col in self.sections.items():
            for o in self.scene.objects:o.select_set(False)
            meshes=[o for o in col.objects if o.type=='MESH']
            if not meshes:continue
            # Bake linked authoring modules into a small number of export
            # chunks per material/section. Sources retain linked editable bays;
            # imports avoid hundreds of tiny MeshParts and the Blender 5.2
            # FBX exporter's unconditional warning on repeated mesh materials.
            temp=bpy.data.collections.new('__EXPORT_STAGING')
            self.scene.collection.children.link(temp)
            groups={}
            for obj in meshes:
                mesh=obj.data;by_vertex={}
                for face in mesh.polygons:
                    for v in face.vertices:by_vertex.setdefault(v,[]).append(face.index)
                unseen=set(range(len(mesh.polygons)))
                while unseen:
                    stack=[unseen.pop()];component=[]
                    while stack:
                        index=stack.pop();component.append(index)
                        for v in mesh.polygons[index].vertices:
                            for other in by_vertex[v]:
                                if other in unseen:unseen.remove(other);stack.append(other)
                    mat=mesh.materials[mesh.polygons[component[0]].material_index]
                    groups.setdefault(mat,[]).append((obj,component))
            baked=[]
            for mat,components in groups.items():
                batches=[];batch=[];count=0
                for obj,component in components:
                    triangles=sum(len(obj.data.polygons[i].vertices)-2 for i in component)
                    assert triangles<=5500,(name,obj.name,triangles)
                    if count+triangles>5500 and batch:batches.append(batch);batch=[];count=0
                    batch.append((obj,component));count+=triangles
                if batch:batches.append(batch)
                for batch in batches:
                    vertices=[];polygons=[];mapping={}
                    for obj,component in batch:
                        for index in component:
                            face=[]
                            for v in obj.data.polygons[index].vertices:
                                key=(obj.as_pointer(),v)
                                if key not in mapping:
                                    mapping[key]=len(vertices);vertices.append(obj.matrix_world@obj.data.vertices[v].co)
                                face.append(mapping[key])
                            polygons.append(tuple(face))
                    mesh=bpy.data.meshes.new(name+'__'+mat.name)
                    mesh.from_pydata(vertices,[],polygons);mesh.materials.append(mat);mesh.update()
                    obj=bpy.data.objects.new(self.scene.name+'__'+mesh.name,mesh)
                    temp.objects.link(obj);obj['AssetId']=self.scene.name;obj['Section']=name
                    obj['CollisionRole']='VisualOnly_UseSimpleAuthoredCollisionAtIntegration'
                    obj.select_set(True);baked.append(obj)
            bpy.context.view_layer.objects.active=baked[0]
            path=export_dir/(self.scene.name+'__'+name+'.fbx')
            bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'MESH'},
                global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',
                axis_forward='-Z',axis_up='Y',use_mesh_modifiers=False,bake_anim=False,
                path_mode='AUTO',mesh_smooth_type='FACE',use_custom_props=True)
            parts.append(dict(section=name,file=Path(os.path.relpath(path,self.folder)).as_posix(),
                              triangles=sum(tris(o.data) for o in meshes),meshInstances=len(baked),
                              largestExportMeshTriangles=max(tris(o.data) for o in baked)))
            for obj in baked:
                mesh=obj.data;bpy.data.objects.remove(obj,do_unlink=True);bpy.data.meshes.remove(mesh)
            bpy.data.collections.remove(temp)
        for o in self.scene.objects:o.select_set(False)
        row=dict(assetId=self.scene.name,name=self.name,source=self.scene.name+'.blend',
            dimensionsStuds=dict(width=round(hi[0]-lo[0],3),height=round(hi[2]-lo[2],3),depth=round(hi[1]-lo[1],3)),
            assembledTriangles=sum(tris(o.data) for o in objects),uniqueSourceTriangles=sum(tris(m) for m in unique),
            largestMeshTriangles=max(tris(m) for m in unique),uniqueMeshes=len(unique),meshInstances=len(objects),
            exports=parts,origin='Common ground center; front +Y in Blender / -Z in Roblox',
            sockets=self.sockets,materials=sorted({m.name for mesh in unique for m in mesh.materials}),
            assembly=[dict(name=o.name,meshKey=o['MeshKey'],section=o['Section'],
                           matrix=[list(r) for r in o.matrix_world],collisionRole=o['CollisionRole']) for o in objects])
        (self.folder/'asset.json').write_text(json.dumps(row,indent=2),encoding='utf8')
        bpy.data.libraries.write(str(self.folder/row['source']),{self.scene},fake_user=True,compress=True)
        print('SAVED '+self.key+' '+json.dumps({k:row[k] for k in ['dimensionsStuds','assembledTriangles','uniqueSourceTriangles','largestMeshTriangles']}),flush=True)
        return row


def panel(g,x,y,z,w,h,mat='Glass',angle=0):
    # Plane outward towards local -Z. Back/side façades rotate this same module.
    pts=[(-w/2,-h/2,0),(-w/2,h/2,0),(w/2,h/2,0),(w/2,-h/2,0)]
    from geometry import rotate
    g.polygon([tuple(a+b for a,b in zip(rotate(p,angle),(x,y,z))) for p in pts],mat)


def ellipse(g,center,rx,rz,depth,mat,segments=40):
    x,y,z=center
    rings=[[(x+rx*math.cos(i*math.tau/segments),y+dy,z+rz*math.sin(i*math.tau/segments)) for i in range(segments)] for dy in [-depth/2,depth/2]]
    g.polygon(rings[0],mat);g.polygon(list(reversed(rings[1])),mat)
    for i in range(segments):
        j=(i+1)%segments;g.polygon([rings[0][i],rings[0][j],rings[1][j],rings[1][i]],mat,True)


def palm_geometry():
    g=Geometry();g.cylinder((0,7,0),.45,14,'Louvre',7,r2=.27)
    for i in range(8):
        a=i*math.tau/8
        for j in range(3):
            r0=j*2.5;r1=(j+1)*2.5
            p=(r0*math.cos(a),15.2+math.sin(j*.8)*1.4-j*.8,r0*math.sin(a))
            q=(r1*math.cos(a),15.2+math.sin((j+1)*.8)*1.4-(j+1)*.8,r1*math.sin(a))
            u=(-math.sin(a)*(.8-j*.15),0,math.cos(a)*(.8-j*.15))
            verts=[p,tuple(p[k]+u[k] for k in range(3)),q,tuple(p[k]-u[k] for k in range(3))]
            leaf=Geometry();role='LeafLight' if i%3==0 else 'Leaf'
            back=[(v[0],v[1]-.12,v[2]) for v in verts]
            leaf.polygon(verts,role);leaf.polygon(list(reversed(back)),role)
            for k in range(4):
                m=(k+1)%4;leaf.polygon([verts[k],back[k],back[m],verts[m]],role)
            g.merge(leaf)
    return g


def foundation(a,w,d,landscape=True):
    g=Geometry();g.box((0,.5,0),(w,1,d),'Stone');g.box((0,1.1,0),(w-.6,.3,d-.6),'Paving')
    g.box((0,1.31,-d/2+18),(w-3,.12,28),'Asphalt')
    for x in [-w/2+12,w/2-12]:g.box((x,1.31,2),(19,.12,d-54),'Asphalt')
    for z in [-d/2+33,d/2-3]:g.box((0,1.55,z),(w-5,.5,1.2),'Pearl')
    for x in [-w/2+1,w/2-1]:g.box((x,3,12),(1.6,3.5,d-68),'Stone')
    for x in range(int(-w/2+20),int(w/2-10),16):g.box((x,1.35,-d/2+40),(.22,.15,12),'Pearl')
    a.put('site_plinth',g,role='GroundAndBoundary')
    if landscape:
        p=Geometry();p.box((0,2,0),(13,1.7,9),'Stone');p.box((0,3,0),(11.8,1.2,7.8),'Leaf')
        for i,x in enumerate([-w/2+28,-w/4,w/4,w/2-28]):
            a.put('edge_planter',p if i==0 else None,(x,0,-d/2+45),section='Landscape')
            a.put('palm',palm_geometry() if i==0 else None,(x,3,-d/2+45),section='Landscape')
    a.sockets['RoadArrival']={'positionStuds':[0,1.3,-d/2+18],'laneWidthStuds':28}


def entrance(g,x,z,w=32,y=1.3,h=13,material='Pearl'):
    g.box((x,y+h,z),(w,1.2,18),material)
    g.box((x,y+h+.7,z-8),(w+.7,.25,.4),'Accent')
    for s in [-1,1]:
        g.box((x+s*(w/2-2),y+h/2,z-5),(1.4,h,1.4),material)
        g.box((x+s*(w/2-2),y+.35,z-5),(3,.7,3),'Stone')
    panel(g,x,y+5.8,z+5,w-7,10,'GlassLight')


def floor_band(w,d,step,pattern=0,stone='Pearl',slab=True,bays=None,glazing=.9,glazing_height=.88):
    g=Geometry()
    if slab:g.box((0,0,0),(w+1.2,.4,d+1.2),stone)
    for side in range(4):
        width=w if side%2==0 else d;depth=d if side%2==0 else w
        count=bays or max(3,round(width/7))
        angle=side*math.pi/2
        from geometry import rotate
        for j in range(count):
            pos=rotate((-width/2+(j+.5)*width/count,step/2,-depth/2-.8),angle)
            role='WarmWindow' if (j*7+side*3+pattern*5)%13==0 else 'GlassBlue'
            panel(g,*pos,(width/count-.65)*glazing,step*glazing_height,role,angle)
    return g
