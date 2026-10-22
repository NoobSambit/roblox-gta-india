"""Build only the 27 owned Tier 3 assets, sources and assembled FBX exports.

Run inside Blender through MCP. Calling build_family saves each completed asset.
Rerunning replaces that family's generated T3 scenes; it never edits T1/T2 data.
"""
import bpy,bmesh,json,math,sys
from pathlib import Path
from mathutils import Vector

BASE=Path(r'C:\Users\Sambit Pradhan\Documents\Indian_Hood\assets\kolkata\tier3')
ROOT=BASE.parents[2]
if str(BASE) not in sys.path:sys.path.insert(0,str(BASE))
from lowpoly import Geometry,blender_point

DESIGNS=json.loads((BASE/'designs.json').read_text(encoding='utf8'))
REFERENCES={r['assetId']:r for r in json.loads((ROOT/'artifacts/references/tier3/reference-manifest.json').read_text(encoding='utf8'))}
PALETTE={
 'Oxide':'984C40','Brick':'A95F4D','BlueGrey':'939E9E','DustBlue':'719EAD',
 'Cream':'E0D1A8','Ochre':'D1AE69','Peach':'D7A28C','Sand':'C3B493',
 'Grey':'9EA4A2','Rose':'B68D87','Plaster':'D6D4C4','Trim':'E5DECA',
 'Dark':'34444B','Green':'426958','Clay':'855B50','Roof':'7C8583',
 'BlueAccent':'527D8A','Concrete':'818582'}

def material(name):
    key='T3_'+name
    if key in bpy.data.materials:return bpy.data.materials[key]
    h=PALETTE[name];srgb=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in srgb]
    m=bpy.data.materials.new(key);m.diffuse_color=(*linear,1);m.use_nodes=True
    node=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');node.inputs['Base Color'].default_value=(*linear,1)
    node.inputs['Roughness'].default_value=.86
    return m

class Building:
    def __init__(self,d):
        self.d=d;self.g=Geometry();self.w=d['width'];self.depth=d['depth']
        self.n=d['floors'];self.h=12*self.n;self.front=-self.depth/2;self.recipe=d['recipe']
        self.old=d['family']=='old_kolkata'

    def box(self,*args,**kw):return self.g.box(*args,**kw)

    def shell(self,chamfer=False,top=None):
        w,d=self.w,self.depth;h=self.h if top is None else top
        self.box((0,.3,0),(w+.6,.6,d+.6),'Trim')
        if chamfer:
            cut=4
            self.g.prism([(-w/2,-d/2),(w/2-cut,-d/2),(w/2,-d/2+cut),(w/2,d/2),(-w/2,d/2)],.45,h)
        else:self.box((0,(h+.45)/2,0),(w,h-.45,d))
        self.box((0,h+.22,0),(w+.7,.5,d+.7),'Trim')

    def parapet(self,base=None,height=1.7,front=True):
        w,d=self.w,self.depth;y=(self.h+.45 if base is None else base)+height/2
        if front:self.box((0,y,-d/2),(w+.1,height,.5),'Body')
        self.box((0,y,d/2),(w+.1,height,.5),'Body')
        for sign in [-1,1]:self.box((sign*w/2,y,0),(.5,height,d),'Body')

    def secondary(self,levels=None):
        # Sparse side/rear windows. These are sealed opaque volumes, no rooms.
        for f in (range(self.n) if levels is None else levels):
            y=f*12+6.3
            for side in [-1,1]:
                angle=-side*math.pi/2;origin=(side*self.w/2,0,0)
                for x in [-self.depth*.23,self.depth*.23]:
                    self.g.window(x,y,3.6,5.4,'simple',angle=angle,origin=origin,frame=False)
            self.g.window(0,y,3.8,5.4,'simple',angle=math.pi,origin=(0,0,self.depth/2),frame=False)

    def front_window(self,x,f,w=4,h=6.6,style=None,surface=None):
        self.g.window(x,12*f+6.3,w,h,style or ('old' if self.old else 'modern'),self.front if surface is None else surface)

    def door(self,x=0,width=4,old=None):
        old=self.old if old is None else old
        self.g.window(x,4.2,width,7.5,'old' if old else 'modern',self.front)

    def bands(self,levels=None):
        for f in (range(1,self.n) if levels is None else levels):
            self.box((0,f*12+.15,self.front-.25),(self.w+.6,.55,.7),'Trim')

    def front_grid(self,columns=2,start=0,skip=None):
        xs=[(i-(columns-1)/2)*self.w/(columns+.25) for i in range(columns)]
        for f in range(start,self.n):
            for j,x in enumerate(xs):
                if skip and skip(f,j):continue
                self.front_window(x,f,w=min(4.5,self.w/(columns+1)-1))

    def old_model(self):
        r=self.recipe;w=self.w;z=self.front;h=self.h;g=self.g
        self.shell();self.secondary();self.parapet(height=1.45);self.bands()
        if r=='old_center_balcony':
            for x in [-w*.28,w*.28]:
                g.arched_panel(x,6.2,3.9,7.5,z)
                self.front_window(x,1,3.9,7.5)
            self.door(0,3)
            g.balcony(0,12.1,w*.7,3.1,z,'old')
            self.box((0,h+.85,z-.35),(w+1.5,.55,1.5),'Trim')
            for x in [-w/2+.4,w/2-.4]:self.box((x,h/2,z-.22),(.7,h-.5,.65),'Trim')
        elif r=='old_offset_verandahs':
            self.front_grid(2,skip=lambda f,j:f==0 and j==0);self.door(-w*.25,3.8)
            for f,x in [(1,-w*.18),(2,w*.14)]:
                g.balcony(x,f*12+.15,w*.63,3.4,z,'old')
                self.box((x,f*12+10.7,z-1.8),(w*.67,.45,4),'Trim')
            self.box((-w*.44,h/2,z-.25),(.6,h,.7),'Trim')
        elif r=='old_screen_verandah':
            self.front_grid(3,skip=lambda f,j:f==0 and j==0);self.door(-w*.3)
            for f in [1,2]:g.balcony(0,12*f+.1,w+1,3.6,z,'old',posts=True)
            self.box((0,h+.35,z-1.5),(w+2,.6,5),'Trim')
            for x in [-w*.49,0,w*.49]:self.box((x,6.3,z-3.4),(.5,12,.5),'Trim')
        elif r=='old_polygon_bay':
            self.front_grid(2,skip=lambda f,j:(f==0 and j==0) or (f>0 and j==1));self.door(-w*.28,3.4)
            cx=w*.19;bw=w*.6
            poly=[(cx-bw/2,z+.2),(cx+bw/2,z+.2),(cx+bw/2,z-2.3),(cx+bw*.25,z-4),(cx-bw*.25,z-4),(cx-bw/2,z-2.3)]
            g.prism(poly,12,h,'Body')
            for f in range(1,self.n):
                g.prism(poly,12*f,12*f+.6,'Trim')
                g.window(cx,12*f+6.3,4.1,7.6,'old',z-4)
            g.prism(poly,h,h+.75,'Trim')
        elif r=='old_long_gallery':
            self.front_grid(3,skip=lambda f,j:f==0 and j==1);self.door(0)
            for f in range(1,self.n):
                g.balcony(0,12*f+.1,w*.92,2.8,z,'old',posts=True)
                self.box((0,12*f+10.2,z-.2),(w,.7,.8),'Trim')
            self.box((0,h+.4,z-1.25),(w+1.5,.6,4),'Trim')
        elif r=='old_corner_balcony':
            self.front_grid(3,skip=lambda f,j:f==0 and j==0);self.door(-w*.3)
            g.balcony(w*.18,12.1,w*.6,3.5,z,'old')
            g.balcony(-self.depth*.29,12.1,self.depth*.43,3.3,0,'old',angle=-math.pi/2,origin=(w/2,0,0))
            for x in [-w*.1,w*.47]:self.box((x,18.2,z-3.25),(.45,11.8,.45),'Trim')
            self.box((w*.18,h+.35,z-1.5),(w*.65,.6,4.5),'Trim')
            self.box((w/2+1.4,h+.35,-self.depth*.29),(4.4,.6,self.depth*.48),'Trim')
        elif r=='old_wrap_corner':
            self.front_grid(3,skip=lambda f,j:f==0 and j==0);self.door(-w*.33)
            for f in [1,2]:
                g.wrap_gallery(w,self.depth,12*f+.1)
            g.wrap_gallery(w,self.depth,h+.35,canopy=True)
        elif r=='old_enclosed_bay':
            self.front_grid(3,skip=lambda f,j:(f==0 and j==0) or (f>0 and j==1));self.door(-w*.3)
            bw=w*.4
            self.box((0,24.2,z-1.3),(bw,24.4,3),'Body')
            for f in [1,2]:
                g.window(0,12*f+6.3,bw-1.5,7.2,'old',z-2.8)
                self.box((0,12*f+.3,z-1.4),(bw+1,.65,3.6),'Trim')
            self.box((0,h+.45,z-1.5),(bw+1.6,.8,4),'Trim')
            self.box((0,h+2.7,z),(w*.45,2.6,.7),'Body')
            self.box((0,h+4.05,z),(w*.5,.35,1),'Trim')
        elif r=='old_pilasters':
            for x in [-w*.31,0,w*.31]:
                g.arched_panel(x,5.3 if x==0 else 6.2,5.4,9.5 if x==0 else 8,z)
                self.front_window(x,1,5.4,8)
            self.box((0,4.3,z-.45),(.18,7.5,.16),'Dark')
            for x in [-w*.47,-w*.16,w*.16,w*.47]:
                self.box((x,12.2,z-.35),(.9,23.5,.85),'Trim')
                self.box((x,1,z-.35),(1.25,.8,1.15),'Trim')
                self.box((x,h-.5,z-.35),(1.4,.7,1.2),'Trim')
            self.box((0,h+.65,z-.5),(w+1.5,.6,1.7),'Trim')
        elif r=='old_terrace_gallery':
            # The roof pavilion is set back behind a small terrace parapet.
            self.front_grid(3,skip=lambda f,j:f==0 and j==1);self.door(0)
            for f in [1,2]:g.balcony(0,12*f+.1,w*.88,2.9,z,'old',posts=True)
            self.box((0,h+3.6,3),(w*.64,6.3,self.depth*.57),'Body')
            self.box((0,h+6.9,3),(w*.68,.5,self.depth*.61),'Trim')
            for x in [-w*.21,w*.21]:g.window(x,h+3.7,3.7,4.2,'old',3-self.depth*.285)
            for x in [-w*.45,0,w*.45]:self.box((x,h+2.2,z),(.7,1.4,.75),'Trim')

    def modern_model(self):
        r=self.recipe;w=self.w;z=self.front;h=self.h;g=self.g
        clipped=r in ['mod_chamfer_corner','mix_corner']
        self.shell(chamfer=clipped);self.secondary();self.parapet(front=not clipped)
        mixed=self.d['family']=='mixed_use'
        if mixed:self.shops()
        else:self.door(w*.22 if r=='mod_service_spine' else (-w*.22 if r=='mod_stacked_left' else -w*.31),3.7)
        start=1 if mixed else 0
        # Deliberate façade layouts, rather than randomized colour variants.
        if r in ['mod_small_house','mod_tall_fin']:
            self.front_grid(2,skip=lambda f,j:f==0 and j==0)
            bx=w*.16 if r=='mod_small_house' else -w*.1
            g.balcony(bx,12.1,w*.68,3.4,z)
            self.box((bx,23.4,z-1.4),(w*.72,.6,4),'Trim')
            if r=='mod_small_house':
                self.box((-w*.32,h+2,3),(w*.3,3.5,self.depth*.65),'Accent')
                self.box((-w*.32,h+3.9,3),(w*.33,.4,self.depth*.68),'Trim')
            else:self.box((w*.4,h/2+1,z-.5),(1.5,h+2,1.3),'Accent')
        elif r in ['mod_stacked_left','mod_service_spine']:
            bx=-w*.22 if r=='mod_stacked_left' else w*.22
            for f in range(1,self.n):
                self.front_window(bx,f,4.5)
                g.balcony(bx,12*f+.1,w*.5,3,z)
            other=-bx
            self.box((other,h/2,z-.16),(w*.12,h,.35),'Accent')
            for f in range(self.n):g.window(other,12*f+7,2.2,4,'modern',z-.36,frame=False)
        elif r=='mod_twin_balconies':
            self.front_grid(3,start,skip=lambda f,j:j==1 or (f==0 and j==0))
            for f in range(1,self.n):
                for sign in [-1,1]:g.balcony(sign*w*.3,12*f+.1,w*.32,3.3,z)
            self.box((0,h/2,z-.6),(w*.13,h,1.35),'Accent')
            for f in range(self.n):g.window(0,12*f+6.6,2.8,5.5,'modern',z-1.35,frame=False)
        elif r=='mod_chamfer_corner':
            self.front_grid(2,start,skip=lambda f,j:f==0 and j==0)
            for f in range(1,self.n):
                g.balcony(w*.05,12*f+.1,w*.65,2.5,z)
                # A clipped corner face with sealed opaque windows, not empty holes.
                g.window(0,12*f+6.5,3.2,6,'modern',angle=-math.pi/4,origin=(w/2-2,0,z+2))
            self.box((-w*.4,h/2,z-.25),(1,h,.6),'Accent')
        elif r=='mod_wide_balconies':
            self.front_grid(3,start,skip=lambda f,j:f==0 and j==0)
            for f in range(1,self.n):g.balcony(0,12*f+.1,w*.88,2.4,z)
            self.bands();self.box((0,h+.9,z-.9),(w+1,1,2.4),'Accent')
        elif r=='mod_alternating_bays':
            self.front_grid(3,start,skip=lambda f,j:f==0 and j==0)
            for f in range(1,self.n):
                bx=(-1 if f%2 else 1)*w*.22
                g.balcony(bx,12*f+.1,w*.5,3.5,z)
                self.box((-bx,12*f+3,z-.55),(w*.35,.8,1.2),'Accent')
            self.box((w*.45,h/2,z-.15),(.9,h,.4),'Accent')
        elif r=='mod_offset_boxes':
            self.front_grid(3,start,skip=lambda f,j:f==0 and j==0)
            for f in range(1,self.n):
                bx=(-.24 if f in [1,3] else .19)*w
                g.balcony(bx,12*f+.1,w*.5,3.5,z)
                self.box((bx,12*f+10.5,z-1.6),(w*.53,.5,4),'Trim')
            self.box((w*.28,h+1.8,self.depth*.25),(4,2.6,4),'Trim')
            g.cylinder((w*.28,h+4.9,self.depth*.25),2,3.7,'Dark',8)
        elif r=='mix_corner':
            self.front_grid(2,start)
            for f in range(1,self.n):
                g.balcony(-w*.25,12*f+.1,w*.44,2.6,z)
                g.window(0,12*f+6.5,3.2,6,'modern',angle=-math.pi/4,origin=(w/2-2,0,z+2))
            self.box((-w*.47,h/2,z-.3),(.8,h,.8),'Accent')
        elif r=='mix_twin_crown':
            self.front_grid(3,start)
            for f in range(1,self.n):
                for sign in [-1,1]:g.balcony(sign*w*.28,12*f+.1,w*.36,2.6,z)
            for sign in [-1,1]:
                self.box((sign*w*.27,h+2.5,z),(w*.31,3.5,.8),'Accent')
                self.box((sign*w*.27,h+4.35,z),(w*.36,.35,1.2),'Trim')
        elif r=='mix_vertical_stripe':
            self.front_grid(2,start)
            for f in range(1,self.n):g.balcony(w*.17,12*f+.1,w*.63,2.7,z)
            self.box((-w*.34,h/2,z-.45),(w*.13,h,1),'Accent')
        elif r=='mix_three_shops':
            for f in range(1,self.n):
                for x in [-w*.32,w*.05,w*.34]:self.front_window(x,f,4.3)
            g.balcony(-w*.13,24.1,w*.7,2.2,z)
            self.bands();self.box((-w*.46,h/2,z-.2),(.65,h,.6),'Accent')
        elif r=='mix_corner_balconies':
            self.front_grid(3,start)
            for f in range(1,self.n):
                g.balcony(w*.23,12*f+.1,w*.55,2.8,z)
                g.balcony(-self.depth*.28,12*f+.1,self.depth*.45,2.8,0,angle=-math.pi/2,origin=(w/2,0,0))
            self.box((-w*.37,h/2,z-.35),(w*.12,h,.8),'Accent')

    def shops(self):
        w=self.w;z=self.front;r=self.recipe
        widths=[w*.29,w*.37,w*.25] if r=='mix_three_shops' else [w*.44,w*.44]
        cursor=-sum(widths)/2
        for i,bw in enumerate(widths):
            x=cursor+bw/2;cursor+=bw
            self.box((x,4.35,z-.18),(bw-.65,7.5,.45),'Roof')
            for yy in [2.2,4.3,6.4]:self.box((x,yy,z-.47),(bw-.9,.12,.12),'Dark')
            self.box((x,9.5,z-.35),(bw-.4,2.05,.7),'Accent')
            self.box((x,9.5,z-.74),(bw-1.15,1.35,.12),'Trim')
            # Blank opaque sign surface, intentionally no invented text.
        self.box((0,11.1,z-.85),(w+.5,.4,2),'Trim')

    def informal_model(self):
        w,d,z=self.w,self.depth,self.front;g=self.g;r=self.recipe
        if r=='inf_upper_room':
            self.shell(top=11)
            self.box((-w*.18,16.1,d*.1),(w*.64,10,d*.75),'Body')
            g.sheet_roof(-w*.18,d*.1,w*.7,d*.83,21.28,ridges=7,slope=0)
            g.sheet_roof(w*.32,0,w*.4,d+1.5,11.65,ridges=4,slope=0)
            g.window(-w*.18,16.4,4.5,5,'simple',d*.1-d*.375)
        elif r=='inf_roof_extension':
            self.box((-w*.1,5.6,1),(w*.8,10.3,d-2),'Body')
            self.box((w*.38,4.7,-2),(w*.24,8.5,d*.7),'Body')
            self.box((0,.3,0),(w+.4,.6,d+.4),'Trim')
            g.sheet_roof(-w*.1,1,w*.85,d,11.2,ridges=7)
            g.sheet_roof(w*.38,-2,w*.3,d*.8,9.5,ridges=4,slope=.06)
            z=2-d/2
        else:
            self.shell(top=10.5)
            g.sheet_roof(0,0,w+1.7,d+2,11.15,ridges=8,slope=0)
        self.g.window(-w*.2,4.35,3.5,7.4,'simple',z)
        self.g.window(w*.23,6.1,3.7,3.5,'simple',z)
        # An integral small supported roof projection, not a separate street prop.
        g.sheet_roof(-w*.18,z-1.3,w*.53,3.8,9.1,ridges=4,slope=.1)
        for x in [-w*.43,w*.07]:self.box((x,4.7,z-2.9),(.24,8.8,.24),'Dark')
        for side in [-1,1]:
            origin=(side*w/2,0,0)
            g.window(0,5.8,3.6,3.3,'simple',angle=-side*math.pi/2,origin=origin,frame=False)

    def create(self):
        if self.old:self.old_model()
        elif self.d['family']=='informal':self.informal_model()
        else:self.modern_model()
        return self.g

def triangle_count(mesh):return sum(len(p.vertices)-2 for p in mesh.polygons)

def build_asset(d):
    asset_id=d['id'];old=bpy.data.scenes.get(asset_id)
    if old:
        for obj in list(old.objects):
            if obj.get('AssetId')==asset_id:bpy.data.objects.remove(obj,do_unlink=True)
        bpy.data.scenes.remove(old)
    scene=bpy.data.scenes.new(asset_id);bpy.context.window.scene=scene
    scene.unit_settings.system='NONE';scene.unit_settings.scale_length=1
    scene['AssetId']=asset_id;scene['Family']=d['family'];scene['Front']='-Z in Roblox; +Y in Blender'
    scene['SourcePhoto']=REFERENCES[asset_id]['sourcePage']
    scene['FloorCount']=d['floors'];scene['NoInteriors']=True
    collection=bpy.data.collections.new(asset_id+'__Geometry');scene.collection.children.link(collection)
    geo=Building(d).create()
    role_colors={'Body':d['paint'],'Trim':'Trim','Dark':'Dark','Roof':'Roof',
                 'Accent':'Green' if d['family']=='old_kolkata' else ('BlueAccent' if d['recipe'] in ['mod_tall_fin','mix_corner_balconies','mix_vertical_stripe'] else 'Clay')}
    objects=[]
    for role,(vertices,faces) in geo.groups.items():
        mesh=bpy.data.meshes.new(asset_id+'__'+role)
        mesh.from_pydata([blender_point(p) for p in vertices],[],faces);mesh.update()
        bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
        obj=bpy.data.objects.new(asset_id+'__'+role,mesh);collection.objects.link(obj)
        mesh.materials.append(material(role_colors[role]));obj['AssetId']=asset_id;obj['MeshKey']=obj.name;obj['Role']=role
        obj['CollisionRecommendation']='Use separate simple bounds proxies in Studio; decorative mesh collision off.'
        objects.append(obj)
    folder=BASE/d['family']/asset_id;folder.mkdir(parents=True,exist_ok=True)
    tris=sum(triangle_count(o.data) for o in objects)
    assert tris<=2000,(asset_id,tris)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    source=folder/(asset_id+'.blend');export=folder/(asset_id+'.fbx')
    bpy.data.libraries.write(str(source),{scene},fake_user=True,compress=True)
    # Same assembled FBX / neutral units convention established with Victoria.
    bpy.ops.export_scene.fbx(filepath=str(export),use_selection=True,object_types={'MESH'},
        global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',
        axis_forward='-Z',axis_up='Y',use_mesh_modifiers=True,bake_anim=False,
        path_mode='AUTO',mesh_smooth_type='FACE',use_custom_props=True)
    coords=[p for vertices,faces in geo.groups.values() for p in vertices]
    low=[min(p[i] for p in coords) for i in range(3)];high=[max(p[i] for p in coords) for i in range(3)]
    row={**d,'reference':REFERENCES[asset_id],
         'dimensionsStuds':dict(zip(['width','height','depth'],[round(high[i]-low[i],3) for i in range(3)])),
         'boundsMinStuds':low,'boundsMaxStuds':high,'triangles':tris,'meshGroups':len(objects),
         'materials':[o.data.materials[0].name for o in objects],'textures':[],
         'source':str(source.relative_to(BASE)).replace('\\','/'),'export':str(export.relative_to(BASE)).replace('\\','/'),
         'meshKeys':[o['MeshKey'] for o in objects],
         'limits':'Exterior only. Simplified side/rear faces. Collision and Studio placement deferred to assembly milestone.'}
    (folder/'asset.json').write_text(json.dumps(row,indent=2),encoding='utf8')
    print('SAVED '+asset_id+' '+str(tris)+' triangles / '+str(len(objects))+' mesh groups',flush=True)
    return row

def save_master():
    owned={s for s in bpy.data.scenes if s.get('AssetId','').startswith('KOL_T3_')}
    bpy.data.libraries.write(str(BASE/'Kolkata_Tier3_Library.blend'),owned,fake_user=True,compress=True)

def build_family(family):
    summary=BASE/'asset-manifest.json'
    rows=json.loads(summary.read_text(encoding='utf8')) if summary.exists() else []
    rows=[r for r in rows if r['family']!=family]
    for d in DESIGNS:
        if d['family']!=family:continue
        rows.append(build_asset(d));rows.sort(key=lambda r:r['id'])
        summary.write_text(json.dumps(rows,indent=2),encoding='utf8')
    save_master()
    return [{'id':r['id'],'triangles':r['triangles'],'meshGroups':r['meshGroups']} for r in rows if r['family']==family]

if __name__=='__main__':
    for family in ['old_kolkata','modern','mixed_use','informal']:print(json.dumps(build_family(family)))
