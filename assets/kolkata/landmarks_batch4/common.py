"""Batch 4 original exterior kit. Public coordinates are X/Y-up/Z studs."""
import bpy
import bmesh
import json
import math
import sys
from pathlib import Path
from mathutils import Vector

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
sys.path.insert(0, str(BASE.parent / 'tier1'))
import pipeline
from pipeline import Asset, Geometry as G, tris
from geometry import bv, rotate

COLORS = dict(B4_Brick='A74634', B4_BrickLight='B45540', B4_Ivory='DFD3B6',
    B4_Plaster='E2DCCB', B4_Stone='D2D0BE', B4_Trim='E8E2CE', B4_Slate='515C59',
    B4_Green='225D49', B4_Glass='435B60', B4_Dark='202D30', B4_Iron='364747',
    B4_Brass='AD925F', B4_Paving='ACA38E', B4_Lawn='61764B', B4_Leaf='3E6548',
    B4_LeafLight='69834E', B4_Water='5E9EA5', B4_Wood='624E3C', B4_Glow='E7C58B')
COLORS.update(B4_MuseumWall='CDBE9F',B4_MuseumTrim='EDE5D1',B4_MuseumStone='A6977D',
    B4_MuseumRecess='B3A68F',B4_MuseumBand='C4B18C',B4_MuseumRoof='4B5B5D',B4_GothicRecess='9EA494')
pipeline.COLORS.update(COLORS)


def prism(points, depth=.4, z=0, mat='B4_Trim'):
    g = G()
    a = [(x,y,z-depth/2) for x,y in points]
    b = [(x,y,z+depth/2) for x,y in points]
    g.polygon(a,mat);g.polygon(list(reversed(b)),mat)
    for i in range(len(a)):
        j=(i+1)%len(a);g.polygon([a[i],b[i],b[j],a[j]],mat)
    return g


def rounded(w,h,n=12):
    r=w/2;s=h-r
    return [(-r,0),(r,0)]+[(r*math.cos(i*math.pi/n),s+r*math.sin(i*math.pi/n)) for i in range(n+1)]


def pointed(w,h,n=8):
    r=w/2;s=h-math.sqrt(3)*r
    # Follow the right-hand arc to the apex, then the left-hand arc down.
    right=[(-r+2*r*math.cos(i*math.pi/3/n),s+2*r*math.sin(i*math.pi/3/n)) for i in range(n+1)]
    left=[(-x,y) for x,y in reversed(right[:-1])]
    return [(-r,0),(r,0)]+right+left


def profile_frame(w,h,t=.3,depth=.5,gothic=False,mat='B4_Trim',n=10,bottom=True):
    fn=pointed if gothic else rounded
    inner=fn(w,h,n);outer=fn(w+2*t,h+t,n)
    outer=[(x,y-t if y==0 else y) for x,y in outer]
    g=G();count=len(inner)
    for i in range(count):
        if not bottom and i==0:continue
        j=(i+1)%count
        for z in [-depth/2,depth/2]:
            g.polygon([(inner[i][0],inner[i][1],z),(inner[j][0],inner[j][1],z),
                       (outer[j][0],outer[j][1],z),(outer[i][0],outer[i][1],z)],mat)
        for ring in [inner,outer]:
            g.polygon([(ring[i][0],ring[i][1],-depth/2),(ring[j][0],ring[j][1],-depth/2),
                       (ring[j][0],ring[j][1],depth/2),(ring[i][0],ring[i][1],depth/2)],mat)
    if not bottom:
        for i in [0,1]:g.polygon([(inner[i][0],inner[i][1],-depth/2),(outer[i][0],outer[i][1],-depth/2),
            (outer[i][0],outer[i][1],depth/2),(inner[i][0],inner[i][1],depth/2)],mat)
    return g


def archwall(w,h,opening,spring,depth=1.2,mat='B4_Plaster',n=12):
    r=opening/2
    pts=[(-w/2,h),(w/2,h),(w/2,0),(r,0),(r,spring)]
    pts += [(r*math.cos(i*math.pi/n),spring+r*math.sin(i*math.pi/n)) for i in range(1,n+1)]
    pts += [(-r,0),(-w/2,0)]
    return prism(pts,depth,0,mat)


def window(w,h,gothic=False,mat='B4_Glass',mullions=1,trim='B4_Trim',n=10):
    fn=pointed if gothic else rounded
    g=prism(fn(w,h,n),.24,0,mat)
    g.merge(profile_frame(w,h,.32,.6,gothic,trim,n).transformed((0,0,-.22)))
    g.box((0,-.26,-.35),(w+1.25,.5,1.2),trim)
    spring=h-(math.sqrt(3)*w/2 if gothic else w/2)
    for i in range(mullions):
        x=-w/2+(i+1)*w/(mullions+1)
        g.box((x,spring*.5,-.27),(.14,spring,.25),trim)
    for y in [spring*.4,spring*.8]:g.box((0,y,-.28),(w,.12,.25),trim)
    if not gothic:
        for theta in [math.pi/4,math.pi/2,3*math.pi/4]:
            g.beam((0,spring,-.28),(w*.48*math.cos(theta),spring+w*.48*math.sin(theta),-.28),.06,trim,4)
    return g


def column(h,r=1,mat='B4_Trim',capital='ionic',segments=12):
    g=G();g.box((0,.25,0),(r*3,.5,r*3),mat)
    g.lathe([(.45,r*1.15),(.8,r*1.2),(1.15,r),(h-1.8,r*.84),(h-1.5,r*1.05),(h-.6,r*1.22)],segments,mat)
    g.box((0,h-.25,0),(r*3.2,.5,r*3.2),mat)
    if capital=='ionic':
        for sign in [-1,1]:
            g.merge(prism([(sign*r*.3,h-1.6),(sign*r*1.4,h-1.4),(sign*r*1.3,h-.65),(sign*r*.3,h-.5)],r*1.8,0,mat))
    return g


def railing(w,h=2.6,spacing=2,mat='B4_Trim',balusters=True):
    g=G();g.box((0,.15,0),(w,.3,.65),mat);g.box((0,h,0),(w+.25,.35,.85),mat)
    n=max(2,round(w/spacing))
    for j in range(n):
        x=-w/2+(j+.5)*w/n
        if balusters:g.lathe([(.3,.19),(h*.55,.22),(h-.15,.16)],4,mat,(x,0,0))
        else:g.box((x,h/2,0),(.10,h,.16),mat)
    return g


def gable(w,eave,rise,depth,mat='B4_Brick',trim='B4_Trim'):
    g=prism([(-w/2,eave),(w/2,eave),(0,eave+rise)],depth,0,mat)
    for sign in [-1,1]:g.beam((sign*(w/2+.2),eave, -depth/2-.2),(0,eave+rise+.2,-depth/2-.2),.24,trim,4)
    return g


def pitched_roof(w,d,y,rise,mat='B4_Slate'):
    g=G()
    for sign in [-1,1]:
        slope=G()
        a=[(sign*w/2,y,-d/2),(0,y+rise,-d/2),(0,y+rise,d/2),(sign*w/2,y,d/2)]
        # A closed thin prism per roof slope.
        b=[(x,yy-.32,z) for x,yy,z in a]
        slope.polygon(a,mat);slope.polygon(list(reversed(b)),mat)
        for i in range(4):j=(i+1)%4;slope.polygon([a[i],b[i],b[j],a[j]],mat)
        g.merge(slope)
    g.beam((0,y+rise+.1,-d/2),(0,y+rise+.1,d/2),.20,mat,6)
    return g


def ring(r,t=.16,depth=.3,n=32,mat='B4_Trim'):
    g=G()
    for j in range(n):
        a=math.tau*j/n;b=math.tau*(j+1)/n
        for z in [-depth/2,depth/2]:
            g.polygon([(r*math.cos(a),r*math.sin(a),z),(r*math.cos(b),r*math.sin(b),z),
                ((r+t)*math.cos(b),(r+t)*math.sin(b),z),((r+t)*math.cos(a),(r+t)*math.sin(a),z)],mat)
        for rr in [r,r+t]:
            g.polygon([(rr*math.cos(a),rr*math.sin(a),-depth/2),(rr*math.cos(b),rr*math.sin(b),-depth/2),
                (rr*math.cos(b),rr*math.sin(b),depth/2),(rr*math.cos(a),rr*math.sin(a),depth/2)],mat)
    return g


def fixture():
    g=G();g.box((0,.15,0),(1.3,.3,1),'B4_Iron')
    g.cylinder((0,.65,0),.18,.9,'B4_Iron',8)
    g.box((0,1.12,0),(1,.45,.7),'B4_Iron')
    g.box((0,1.36,0),(.8,.06,.52),'B4_Glow')
    return g


def tree():
    g=G();g.cylinder((0,5.8,0),.48,11.6,'B4_Wood',7,r2=.24)
    for a in [0,2.1,4.2]:
        x=math.cos(a)*2;z=math.sin(a)*2
        g.beam((0,6,0),(x,11,z),.23,'B4_Wood',6)
        g.ellipsoid((x,13,z),(4.6,5,4),'B4_Leaf' if a else 'B4_LeafLight',9,5)
    return g


def planar_uv(mesh,role):
    # Physical-scale box mapping, retained in the exported baked chunks.
    tile=8 if role=='B4_Brick' else 12 if role=='B4_Stone' else 16
    uv=mesh.uv_layers.new(name='MasonryUV') if not mesh.uv_layers else mesh.uv_layers[0]
    for p in mesh.polygons:
        axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis]
        for li in p.loop_indices:
            v=mesh.vertices[mesh.loops[li].vertex_index].co
            uv.data[li].uv=(v[axes[0]]/tile,v[axes[1]]/tile)


def configure_materials():
    for role in COLORS:
        m=bpy.data.materials.get('KOL_T1_'+role)
        if not m:continue
        n=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        n.inputs['Metallic'].default_value=.35 if role in ['B4_Iron','B4_Brass'] else 0
        n.inputs['Roughness'].default_value=.34 if role=='B4_Glass' else .82 if role not in ['B4_Iron','B4_Brass'] else .4
        path=BASE/'textures'/(role+'.png')
        if path.exists():
            image=bpy.data.images.load(str(path),check_existing=True);image.pack()
            tex=next((x for x in m.node_tree.nodes if x.type=='TEX_IMAGE'),None) or m.node_tree.nodes.new('ShaderNodeTexImage')
            tex.image=image;m.node_tree.links.new(tex.outputs['Color'],n.inputs['Base Color'])


class Landmark(Asset):
    def __init__(self,key,name):
        super().__init__(key,name,BASE/key,ROOT/'exports/kolkata_landmarks_batch4')
        self.light_specs=[]

    def box(self,key,p,size,mat='B4_Plaster',section='01_PrimaryStructure'):
        g=G();g.box(p,size,mat);return self.put(key,g,section=section)

    def inst(self,key,g,p=(0,0,0),yaw=0,section='03_ModularArchitecture'):
        return self.put(key,g if key not in self.cache else None,p,yaw,section=section)

    def ground(self,w,d):
        self.box('Foundation',(0,-.5,0),(w,1,d),'B4_Paving','00_FoundationGrounds')
        self.box('Pedestrian_hardscape',(0,.13,0),(w-.6,.26,d-.6),'B4_Paving','00_FoundationGrounds')

    def lawn(self,key,x,z,w,d):
        g=G();g.box((x,.38,z),(w,.25,d),'B4_Lawn')
        for sign in [-1,1]:
            g.box((x+sign*(w/2+.25),.4,z),(.5,.38,d+1),'B4_Stone')
            g.box((x,.4,z+sign*(d/2+.25)),(w,.38,.5),'B4_Stone')
        self.put(key,g,section='00_FoundationGrounds')

    def steps(self,key,x,z,w,top,count=4):
        g=G()
        for i in range(count):
            h=.26+(top-.26)*(i+1)/count
            g.box((x,h/2,z-(count-i-.5)*1.25),(w,h,1.28),'B4_Stone')
        self.put(key,g,section='00_FoundationGrounds')

    def boundary(self,w,d,opening=22):
        g=G()
        # Low stone/iron compound edges, with an actual front entrance gap.
        for sign in [-1,1]:
            l=(w-opening)/2;x=sign*(opening/2+l/2)
            g.box((x,1,-d/2),(l,1.6,.9),'B4_Stone')
            g.merge(railing(l,2,3,'B4_Iron',False).transformed((x,1.8,-d/2)))
            g.box((sign*w/2,1,0),(.9,1.6,d),'B4_Stone')
            g.merge(railing(d,2,3,'B4_Iron',False).transformed((sign*w/2,1.8,0),math.pi/2))
        g.box((0,1,d/2),(w,1.6,.9),'B4_Stone')
        g.merge(railing(w,2,3,'B4_Iron',False).transformed((0,1.8,d/2)))
        self.put('Compound_boundary',g,section='00_FoundationGrounds')

    def light(self,name,p,target,range_=40,brightness=2,power=2200,color=(1,.78,.48),fixture_=True):
        if fixture_:self.inst('Architectural_uplight',fixture(),p,section='06_LightingFixtures')
        self.light_specs.append(dict(name=name,positionStuds=list(p),targetStuds=list(target),
            rangeStuds=range_,brightness=brightness,angle=85,shadows=False,color=list(color)))
        col=self.section('90_PreviewLights_NOT_FBX')
        # Stud-sized coordinates are metres to Blender's photometric renderer. These
        # preview watts are deliberately separate from the Roblox brightness notes.
        power*=5
        data=bpy.data.lights.new(name,'SPOT');data.energy=power;data.color=color;data.spot_size=math.radians(85);data.spot_blend=.65;data.shadow_soft_size=2
        o=bpy.data.objects.new(name,data);col.objects.link(o);o.location=bv((p[0],p[1]+1.4,p[2]))
        o.rotation_euler=(Vector(bv(target))-o.location).to_track_quat('-Z','Y').to_euler();o['NightWatts']=power;o['StationId']=name

    def finish(self):
        for o in self.root.all_objects:
            if o.type=='MESH':
                for slot in o.material_slots:
                    if slot.material and slot.material.name=='KOL_T1_Accent':slot.material=pipeline.material('B4_Trim')
        configure_materials();bpy.context.view_layer.update()
        objects=[o for o in self.root.all_objects if o.type=='MESH']
        for m in {o.data for o in objects}:planar_uv(m,m.materials[0].name.replace('KOL_T1_',''))
        points=[o.matrix_world@Vector(v) for o in objects for v in o.bound_box]
        lo=Vector([min(v[i] for v in points) for i in range(3)]);hi=Vector([max(v[i] for v in points) for i in range(3)])
        self.export_dir.mkdir(parents=True,exist_ok=True);parts=[]
        export_col=bpy.data.collections.new('80_ExportReady__baked_sections');self.scene.collection.children.link(export_col)
        for name,col in self.sections.items():
            obs=[o for o in col.objects if o.type=='MESH']
            if not obs:continue
            groups={}
            for o in obs:groups.setdefault(o.data.materials[0],[]).append(o)
            baked=[]
            for mat,group in groups.items():
                batches=[];batch=[];count=0
                for o in group:
                    t=tris(o.data)
                    if count+t>12000 and batch:batches.append(batch);batch=[];count=0
                    assert t<15000,(o.name,t)
                    batch.append(o);count+=t
                if batch:batches.append(batch)
                for index,batch in enumerate(batches):
                    vs=[];fs=[];smooth=[]
                    for o in batch:
                        off=len(vs);vs += [o.matrix_world@v.co for v in o.data.vertices]
                        fs += [tuple(off+i for i in p.vertices) for p in o.data.polygons]
                        smooth += [p.use_smooth for p in o.data.polygons]
                    mesh=bpy.data.meshes.new(self.scene.name+'__'+name+'__'+mat.name+f'_{index:02}')
                    mesh.from_pydata(vs,[],fs);mesh.materials.append(mat);mesh.update()
                    for p,s in zip(mesh.polygons,smooth):p.use_smooth=s
                    planar_uv(mesh,mat.name.replace('KOL_T1_',''))
                    obj=bpy.data.objects.new(mesh.name,mesh);export_col.objects.link(obj);obj['Section']=name;baked.append(obj)
            bpy.ops.object.select_all(action='DESELECT')
            for obj in baked:obj.select_set(True)
            bpy.context.view_layer.objects.active=baked[0]
            path=self.export_dir/(self.scene.name+'__'+name+'.fbx')
            bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'MESH'},global_scale=1,
                apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',
                use_mesh_modifiers=False,bake_anim=False,path_mode='COPY',embed_textures=True,mesh_smooth_type='FACE',use_custom_props=True)
            parts.append(dict(section=name,file=Path(__import__('os').path.relpath(path,self.folder)).as_posix(),
                triangles=sum(tris(o.data) for o in obs),meshInstances=len(baked),largestExportMeshTriangles=max(tris(o.data) for o in baked)))
            for obj in baked:obj.select_set(False);obj.hide_set(True);obj.hide_render=True
        export_col.hide_render=True;export_col.hide_viewport=True
        unique={o.data for o in objects}
        structure=[o for o in objects if o['Section'] not in ['00_FoundationGrounds','06_LightingFixtures']]
        sp=[o.matrix_world@Vector(v) for o in structure for v in o.bound_box]
        ext=lambda ps:dict(width=round(max(p.x for p in ps)-min(p.x for p in ps),2),height=round(max(p.z for p in ps)-min(p.z for p in ps),2),depth=round(max(p.y for p in ps)-min(p.y for p in ps),2))
        row=dict(assetId=self.scene.name,name=self.name,source=self.scene.name+'.blend',dimensionsStuds=ext(points),buildingDimensionsStuds=ext(sp),
            assembledTriangles=sum(tris(o.data) for o in objects),uniqueSourceTriangles=sum(tris(m) for m in unique),largestMeshTriangles=max(tris(m) for m in unique),
            uniqueMeshes=len(unique),meshInstances=len(objects),exports=parts,nightLights=self.light_specs,
            materials=[dict(name=m.name,color=COLORS[m.name.replace('KOL_T1_','')],texture=('../textures/'+m.name.replace('KOL_T1_','')+'.png') if (BASE/'textures'/(m.name.replace('KOL_T1_','')+'.png')).exists() else None) for m in sorted({m for mesh in unique for m in mesh.materials},key=lambda m:m.name)],
            origin='Ground center; Blender +Y front, Z up; Roblox -Z front, Y up; Stud/1',
            scope='Standalone exterior package only; no Studio import or gameplay',
            sourceCollection=self.root.name,exportCollection=export_col.name)
        (self.folder/'asset.json').write_text(json.dumps(row,indent=2),encoding='utf8')
        self.scene['ProductionStage']='Batch 4 modular exterior; previews and essential checks pending'
        self.scene['NightLightCount']=len(self.light_specs)
        # Keep the day source readable in solid/material preview.
        for screen in bpy.data.screens:
            for area in screen.areas:
                if area.type=='VIEW_3D':
                    space=area.spaces.active;space.clip_end=4000;space.shading.type='MATERIAL'
                    space.region_3d.view_location=(lo+hi)/2;space.region_3d.view_distance=max(hi-lo)*1.25
                    space.region_3d.view_rotation=Vector((1,2,1)).to_track_quat('Z','Y');space.region_3d.view_perspective='ORTHO'
                    space.overlay.show_extras=False;space.overlay.show_floor=False
        bpy.data.libraries.write(str(self.folder/row['source']),{self.scene},fake_user=True,compress=True)
        print('BATCH4_SAVED '+self.key+' '+json.dumps({k:row[k] for k in ['dimensionsStuds','buildingDimensionsStuds','assembledTriangles','uniqueSourceTriangles']}),flush=True)
        return row
