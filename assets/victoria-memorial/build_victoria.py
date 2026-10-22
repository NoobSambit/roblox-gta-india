"""Original Victoria Memorial game asset. Run inside Blender via MCP.

Coordinates in authoring data are Roblox studs, Y up, north = -Z.
Blender uses (x, -z, y); conversion is a rotation, never a reflection.
Only the VM_ collection is replaced. Existing unrelated Blender content is preserved.
"""
import bpy
import bmesh
import math
import json
from pathlib import Path
from mathutils import Vector

ROOT = Path(r"C:\Users\Sambit Pradhan\Documents\Indian_Hood")
OUT = ROOT / "assets/victoria-memorial"
OUT.mkdir(parents=True, exist_ok=True)
# One Blender coordinate is one Roblox stud. Keep units neutral; the physical
# 0.28 metre conversion must not be baked into FBX object transforms.
bpy.context.scene.unit_settings.system="NONE"
bpy.context.scene.unit_settings.scale_length=1
PALETTE = {
    "Marble": (0.88, 0.89, 0.85, 1),
    "Trim": (0.98, 0.965, 0.90, 1),
    "StoneShadow": (0.65, 0.69, 0.65, 1),
    "Glazing": (0.105, 0.19, 0.205, 1),
    "Bronze": (0.14, 0.22, 0.205, 1),
    "FloorDark": (0.19, 0.245, 0.25, 1),
    "DomeBlue": (0.37, 0.58, 0.61, 1),
    "WindowLight": (0.57, 0.75, 0.76, 1),
    "Gilt": (0.69, 0.53, 0.26, 1),
    "Lawn": (0.265, 0.43, 0.245, 1),
    "Leaf": (0.16, 0.33, 0.22, 1),
    "LeafLight": (0.31, 0.47, 0.255, 1),
    "Bark": (0.33, 0.27, 0.20, 1),
    "Path": (0.69, 0.64, 0.52, 1),
    "Asphalt": (0.18, 0.215, 0.235, 1),
    "Water": (0.16, 0.41, 0.43, 1),
}

for col in list(bpy.data.collections):
    if col.name.startswith("VM_"):
        for obj in list(col.objects):
            owned_mesh=obj.data if obj.type=="MESH" else None
            bpy.data.objects.remove(obj, do_unlink=True)
            if owned_mesh is not None and owned_mesh.users==0:bpy.data.meshes.remove(owned_mesh)
        bpy.data.collections.remove(col)

def collection(name):
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col

LIB = collection("VM_Library_Export")
ARCH = collection("VM_Architecture")
SHELL = collection("VM_Structure_Collision")
INTERIOR = collection("VM_Interior")
GROUNDS = collection("VM_Grounds")
META = collection("VM_Metadata")
COLLISION = collection("VM_CollisionOnly")
PRESENT = collection("VM_Presentation")
MATS = {}
for name, rgba in PALETTE.items():
    mat = bpy.data.materials.get("VM_" + name) or bpy.data.materials.new("VM_" + name)
    mat.diffuse_color = rgba
    mat.use_nodes = True
    node = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    node.inputs["Base Color"].default_value = rgba
    node.inputs["Roughness"].default_value = 0.76 if name not in ("Glazing", "Water") else 0.28
    node.inputs["Metallic"].default_value = 0.5 if name in ("Bronze", "Gilt") else 0.0
    MATS[name] = mat

def bv(p):
    return (p[0], -p[2], p[1])

def rotate(p, angle):
    c, s = math.cos(angle), math.sin(angle)
    return (c*p[0] + s*p[2], p[1], -s*p[0] + c*p[2])

class Geometry:
    def __init__(self):
        self.v, self.f, self.mat, self.smooth = [], [], [], []

    def polygon(self, vertices, mat="Marble", smooth=False):
        offset = len(self.v)
        self.v.extend(vertices)
        self.f.append(tuple(range(offset, offset+len(vertices))))
        self.mat.append(mat)
        self.smooth.append(smooth)

    def box(self, pos, size, mat="Marble", angle=0):
        x,y,z=pos; w,h,d=(s/2 for s in size)
        points=[(-w,-h,-d),(w,-h,-d),(w,h,-d),(-w,h,-d),(-w,-h,d),(w,-h,d),(w,h,d),(-w,h,d)]
        points=[tuple(a+b for a,b in zip(rotate(p,angle),pos)) for p in points]
        for face in [(0,3,2,1),(4,5,6,7),(0,4,7,3),(1,2,6,5),(0,1,5,4),(3,7,6,2)]:
            self.polygon([points[i] for i in face],mat)

    def lathe(self, profile, segments=24, mat="Marble", center=(0,0,0), smooth=True, cap=True, start=0, sweep=2*math.pi):
        rings=[]
        closed=abs(sweep-2*math.pi)<0.001
        for y,r in profile:
            rings.append([(center[0]+r*math.cos(start+i*sweep/segments),center[1]+y,center[2]+r*math.sin(start+i*sweep/segments)) for i in range(segments+(0 if closed else 1))])
        for lower,upper in zip(rings,rings[1:]):
            for i in range(segments):
                j=(i+1)%len(lower)
                self.polygon([lower[i],upper[i],upper[j],lower[j]],mat,smooth)
        if cap:
            self.polygon(rings[0],mat)
            self.polygon(list(reversed(rings[-1])),mat)

    def cylinder(self,pos,r,h,mat="Marble",segments=12,r2=None):
        self.lathe([(-h/2,r),(h/2,r if r2 is None else r2)],segments,mat,pos)

    def ellipsoid(self,pos,size,mat="Marble",segments=12,rings=6):
        rows=[]
        for j in range(rings+1):
            phi=-math.pi/2+j*math.pi/rings
            rows.append([(pos[0]+size[0]*math.cos(phi)*math.cos(i*math.tau/segments),pos[1]+size[1]*math.sin(phi),pos[2]+size[2]*math.cos(phi)*math.sin(i*math.tau/segments)) for i in range(segments)])
        for a,b in zip(rows,rows[1:]):
            for i in range(segments):
                j=(i+1)%segments
                self.polygon([a[i],b[i],b[j],a[j]],mat,True)

    def beam(self,a,b,r,mat="Marble",segments=8):
        direction=Vector(b)-Vector(a)
        axis=direction.normalized()
        u=axis.cross(Vector((0,1,0)))
        if u.length<0.1: u=axis.cross(Vector((1,0,0)))
        u.normalize(); v=axis.cross(u)
        rings=[]
        for p in [Vector(a),Vector(b)]:
            rings.append([tuple(p+r*(math.cos(i*math.tau/segments)*u+math.sin(i*math.tau/segments)*v)) for i in range(segments)])
        for i in range(segments):
            j=(i+1)%segments
            self.polygon([rings[0][i],rings[0][j],rings[1][j],rings[1][i]],mat,True)
        self.polygon(list(reversed(rings[0])),mat)
        self.polygon(rings[1],mat)

    def arch(self, width, spring, thickness, depth, pos=(0,0,0), mat="Trim", segments=16, angle=0):
        r=width/2
        def pt(radius,t,z):
            p=(radius*math.cos(t),spring+radius*math.sin(t),z)
            return tuple(a+b for a,b in zip(rotate(p,angle),pos))
        for i in range(segments):
            t0,t1=i*math.pi/segments,(i+1)*math.pi/segments
            coords=[pt(r,t0,-depth/2),pt(r,t1,-depth/2),pt(r+thickness,t1,-depth/2),pt(r+thickness,t0,-depth/2),pt(r,t0,depth/2),pt(r,t1,depth/2),pt(r+thickness,t1,depth/2),pt(r+thickness,t0,depth/2)]
            for ids in [(0,1,2,3),(7,6,5,4),(4,5,1,0),(3,2,6,7)]:
                self.polygon([coords[j] for j in ids],mat)
            if i==0: self.polygon([coords[j] for j in (0,3,7,4)],mat)
            if i==segments-1: self.polygon([coords[j] for j in (1,5,6,2)],mat)
        for side in [-1,1]:
            p=rotate((side*(r+thickness/2),spring/2,0),angle)
            self.box(tuple(a+b for a,b in zip(p,pos)),(thickness,spring,depth),mat,angle)

    def column(self,x,z,bottom,height,r=0.7,mat="Trim"):
        self.box((x,bottom+0.25,z),(r*3,0.5,r*3),mat)
        self.lathe([(0,r*1.35),(.55,r),(height-1.7,r*.87),(height-.65,r*1.5)],8,mat,(x,bottom+.5,z))
        self.box((x,bottom+height,z),(r*3.5,.8,r*3.5),mat)
        # Readable capital silhouette, no tiny carved leaves.
        self.box((x,bottom+height-.8,z),(r*2.7,.55,r*2.7),mat,math.pi/4)

    def transformed(self,pos=(0,0,0),angle=0):
        result=Geometry()
        result.v=[tuple(a+b for a,b in zip(rotate(v,angle),pos)) for v in self.v]
        result.f=list(self.f); result.mat=list(self.mat); result.smooth=list(self.smooth)
        return result

    def merge(self,other):
        offset=len(self.v)
        self.v.extend(other.v)
        self.f.extend(tuple(i+offset for i in face) for face in other.f)
        self.mat.extend(other.mat);self.smooth.extend(other.smooth)

TEMPLATES={}
INSTANCES=[]
PRIMITIVES=[]
MARKERS=[]

def mesh_object(name, geom, col, material_filter=None):
    verts=[]; faces=[]; mids=[]; smooth=[]
    names=[material_filter] if material_filter else list(dict.fromkeys(geom.mat))
    for f,mat,sm in zip(geom.f,geom.mat,geom.smooth):
        if material_filter and mat!=material_filter: continue
        offset=len(verts)
        verts.extend(bv(geom.v[i]) for i in f)
        faces.append(tuple(range(offset,offset+len(f))))
        mids.append(names.index(mat));smooth.append(sm)
    mesh=bpy.data.meshes.new("VM_"+name)
    mesh.from_pydata(verts,[],faces);mesh.update()
    for mat in names:mesh.materials.append(MATS[mat])
    for poly,mid,sm in zip(mesh.polygons,mids,smooth):
        poly.material_index=mid;poly.use_smooth=sm
    # Weld vertices for clean topology and continuous smooth normals.
    bm=bmesh.new();bm.from_mesh(mesh)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001)
    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.000001)
    # Winding is authored explicitly. Recalculating open dome/vault surfaces can
    # turn their intended inward normals outward, which Roblox would cull.
    bm.to_mesh(mesh);bm.free();mesh.update()
    obj=bpy.data.objects.new(name,mesh);col.objects.link(obj)
    return obj

def template(name,geom):
    objects=[]
    for mat in dict.fromkeys(geom.mat):
        obj=mesh_object(name+"__"+mat,geom,LIB,mat)
        obj["TemplateId"]=name;obj["MaterialRole"]=mat
        objects.append(obj)
    TEMPLATES[name]=objects

def instance(template_id,name,pos=(0,0,0),yaw=0,group="Exterior"):
    target=INTERIOR if group=="Interior" else GROUNDS if group=="Grounds" else ARCH
    for source in TEMPLATES[template_id]:
        obj=bpy.data.objects.new(name+"__"+source["MaterialRole"],source.data)
        target.objects.link(obj)
        obj.location=bv(pos);obj.rotation_euler[2]=yaw
        obj["TemplateId"]=source.name;obj["Group"]=group
    INSTANCES.append(dict(template=template_id,name=name,position=pos,yaw=yaw,group=group))

def box(name,pos,size,mat="Marble",solid=True,group="Structure",yaw=0,shape="Block"):
    geom=Geometry()
    if shape=="Cylinder":geom.cylinder((0,0,0),size[0]/2,size[1],mat,32)
    else:geom.box((0,0,0),size,mat)
    obj=mesh_object(name,geom,GROUNDS if group=="Grounds" else INTERIOR if group=="Interior" else SHELL)
    obj.location=bv(pos);obj.rotation_euler[2]=yaw
    obj["Collision"]=solid;obj["Group"]=group
    PRIMITIVES.append(dict(name=name,position=pos,size=size,material=mat,solid=solid,group=group,yaw=yaw,shape=shape))
    return obj

def marker(name,pos,size,role):
    obj=bpy.data.objects.new(name,None);META.objects.link(obj)
    obj.location=bv(pos);obj.empty_display_type="CUBE";obj.empty_display_size=2
    obj["Role"]=role
    MARKERS.append(dict(name=name,position=pos,size=size,role=role,id="kolkata.victoria."+name.lower()))

def collider(name,pos,size,yaw=0):
    geom=Geometry();geom.box((0,0,0),size,"StoneShadow")
    obj=mesh_object(name,geom,COLLISION)
    obj.location=bv(pos);obj.rotation_euler[2]=yaw
    obj.hide_render=True;obj.display_type="WIRE"
    PRIMITIVES.append(dict(name=name,position=pos,size=size,material="StoneShadow",solid=True,group="Collision",yaw=yaw,shape="Block",invisible=True))

# WINDOW BAY — two levels and paired pilaster rhythm, repeated along wings.
g=Geometry()
g.box((0,20.7,0),(11.2,.85,1),"Trim")
g.box((0,43.4,.15),(11.2,1.05,1.3),"Trim")
g.box((0,44.4,.1),(11.2,.6,1.65),"Trim")
g.box((0,45.25,.1),(11.2,.7,1.25),"StoneShadow")
g.box((0,46.15,0),(11.2,1.1,1.8),"Trim")
for x in [-5.15,5.15]:
    g.box((x,32.2,-.12),(.7,19.7,.85),"Trim")
    g.box((x,42,-.1),(1.35,.8,1.2),"Trim")
for bottom,top,width in [(7.7,17.2,3.6),(26,39.8,4.1)]:
    g.box((0,(bottom+top)/2,-.25),(width+.8,top-bottom+.7,.65),"StoneShadow")
    g.box((0,(bottom+top)/2,-.64),(width,top-bottom,.12),"Glazing")
    for sx in [-1,1]:g.box((sx*(width/2+.2),(bottom+top)/2,-.8),(.4,top-bottom+.6,.4),"Trim")
    for y in [bottom,top]:g.box((0,y,-.8),(width+.8,.4,.5),"Trim")
    g.box((0,bottom-.5,-.85),(width+1.4,.5,.8),"Trim")
    g.box((0,(bottom+top)/2,-.8),(.13,top-bottom,.2),"Trim")
    for y in [bottom+(top-bottom)*.35,bottom+(top-bottom)*.7]:g.box((0,y,-.8),(width,.13,.2),"Trim")
    # Low, segmented classical pediment.
    g.beam((-width*.65,top+.7,-.55),(0,top+1.7,-.55),.20,"Trim",4)
    g.beam((0,top+1.7,-.55),(width*.65,top+.7,-.55),.20,"Trim",4)
for x in [-3.7,-1.85,0,1.85,3.7]:g.box((x,44.9,-.65),(.6,1,1.0),"Trim")
template("FacadeBay",g)
door=Geometry()
for face,mat,sm in zip(g.f,g.mat,g.smooth):
    if min(g.v[i][1] for i in face)>19.5:
        door.polygon([g.v[i] for i in face],mat,sm)
door.arch(7,10,.7,1.1,(0,1.5,-.4),"Trim",12)
template("GalleryDoorBay",door)

# CORNER TOWER — open arched pavilion and curved Mughal crown.
g=Geometry()
g.box((0,2,0),(33,4,33),"Marble")
g.box((0,26,0),(30,48,30),"Marble")
g.box((0,55,0),(30,10,30),"Marble")
g.box((0,60.5,0),(31.5,1.6,31.5),"Trim")
g.box((0,84.5,0),(28,3.5,28),"Marble")
for y,w,h in [(1,34,1),(22,32,1.2),(48,33,1.5),(50,34,1),(58,33,1.3),(60,35,1.2),(84,29,1.1),(86,31,1.3)]:g.box((0,y,0),(w,h,w),"Trim")
for angle in [0,math.pi/2,math.pi,3*math.pi/2]:
    face=Geometry()
    for bottom,top in [(8,18),(28,41)]:
        face.box((0,(bottom+top)/2,-15.2),(5.4,top-bottom,.3),"StoneShadow")
        face.box((0,(bottom+top)/2,-15.45),(4.3,top-bottom-.8,.15),"Glazing")
        for x in [-2.65,2.65]:face.box((x,(bottom+top)/2,-15.8),(.5,top-bottom+.7,.65),"Trim")
        for y in [bottom-.4,top+.4]:face.box((0,y,-15.8),(6.4,.65,1.1),"Trim")
        face.box((0,(bottom+top)/2,-15.65),(.15,top-bottom,.22),"Trim")
        for y in [bottom+4,top-3]:face.box((0,y,-15.65),(4.3,.14,.22),"Trim")
        face.beam((-3.3,top+.9,-15.65),(0,top+2,-15.65),.23,"Trim",4)
        face.beam((0,top+2,-15.65),(3.3,top+.9,-15.65),.23,"Trim",4)
    # Circular oculus, genuinely circular rather than a square plaque.
    for i in range(16):
        a,b=i*math.tau/16,(i+1)*math.tau/16
        face.polygon([(2*math.cos(a),53.3+2*math.sin(a),-15.5),(2*math.cos(b),53.3+2*math.sin(b),-15.5),(2.6*math.cos(b),53.3+2.6*math.sin(b),-15.5),(2.6*math.cos(a),53.3+2.6*math.sin(a),-15.5)],"Trim")
        face.polygon([(0,53.3,-15.43),(2*math.cos(a),53.3+2*math.sin(a),-15.43),(2*math.cos(b),53.3+2*math.sin(b),-15.43)],"Glazing")
    face.arch(13.4,14,1.1,1.5,(0,61,-10.7),"Trim",16)
    for side in [-1,1]:face.box((side*9.1,72.2,-10.7),(4.3,22.4,2.1),"Marble")
    for i in range(16):
        x0=-6.7+i*13.4/16;x1=-6.7+(i+1)*13.4/16
        y0=75+math.sqrt(max(0,6.7**2-x0**2));y1=75+math.sqrt(max(0,6.7**2-x1**2))
        face.polygon([(x0,y0,-11.5),(x1,y1,-11.5),(x1,84,-11.5),(x0,84,-11.5)],"Marble")
        face.polygon([(x0,84,-9.8),(x1,84,-9.8),(x1,y1,-9.8),(x0,y0,-9.8)],"Marble")
    face.arch(17,0,.7,.8,(0,58.5,-16),"Trim",16)
    for i in range(16):
        a,b=i*math.pi/16,(i+1)*math.pi/16
        front=[(0,58.5,-16.25),(8.5*math.cos(a),58.5+8.5*math.sin(a),-16.25),(8.5*math.cos(b),58.5+8.5*math.sin(b),-16.25)]
        face.polygon(list(reversed(front)),"Marble")
        face.polygon([(x,y,-15.3) for x,y,z in front],"Marble")
    g.merge(face.transformed(angle=angle))
for x in [-10.7,10.7]:
    for z in [-10.7,10.7]:g.column(x,z,61,21.5,.8)
# Large, shallow courses are visible close up without carving a brick mesh.
for y in [7,12,17,27,32,37,42]:
    for side in [-1,1]:
        g.box((0,y,side*15.04),(30,.11,.1),"StoneShadow")
        g.box((side*15.04,y,0),(.1,.11,30),"StoneShadow")
g.lathe([(86,13.6),(87,14.6),(88,14.6),(88.7,13.2),(90,13.4),(93,14.4),(96,13.6),(99,11.4),(102,7.3),(104,3.6),(105,1.7)],32,"Marble")
for y,r in [(89,13.5),(94,14.35),(98,12.7),(102,7.4)]:g.lathe([(y,r),(y+.26,r+.17),(y+.5,r)],32,"Trim")
g.lathe([(104.5,1.8),(106,2),(107.3,1.25),(108.3,1.1),(109,.35),(111,0)],16,"Trim")
for x in [-14.5,14.5]:
    for z in [-14.5,14.5]:g.lathe([(60,1.7),(61.5,2),(63,1.5),(64,.75),(65.5,0)],12,"Trim",(x,0,z))
template("CornerTower",g)

# CENTRAL DOME — shell, readable courses, base cornices, shallow meridional ribs.
g=Geometry()
profile=[(90,30),(91,31),(92,31),(93,29.8),(96,29),(100,27.8),(104,25.8),(108,22.8),(112,19),(116,14.1),(119,8.1),(120.5,3.3)]
g.lathe(profile,64,"Marble",cap=False)
for y,r in [(94,29.55),(97,28.75),(100,27.8),(103,26.35),(106,24.4),(109,22),(112,19),(115,15.4),(118,10.2)]:
    g.lathe([(y,r),(y+.22,r+.08)],48,"Trim",cap=False)
for i in range(8):
    a=i*math.tau/8
    pts=[(r*math.cos(a),y+.06,r*math.sin(a)) for y,r in profile[3:]]
    for p,q in zip(pts,pts[1:]):g.beam(p,q,.085,"Trim",4)
g.lathe([(120,3.6),(121,4),(122,4),(122.4,3.3)],24,"Trim")
for i in range(8):
    a=i*math.tau/8
    g.column(2.85*math.cos(a),2.85*math.sin(a),122.2,5,.22)
g.lathe([(127,3.7),(127.5,4),(128,3.6),(130,2.7),(131,0)],24,"Marble")
g.lathe([(130,1.2),(131.5,1),(132,.25)],12,"Trim")
template("CentralDome",g)

# THE ANGEL — original low-poly winged figure, trumpet and raised wreath.
g=Geometry()
g.lathe([(131.5,.8),(132,.9),(132.5,.55),(136,.42),(137,.9),(138,.55)],12,"Bronze")
g.cylinder((0,139,0),.62,1.3,"Bronze",12,r2=.45)
for side in [-1,1]:
    g.beam((side*.45,137.2,0),(side*1.1,139.0,.0),.27,"Bronze",8)
    g.beam((side*1.1,139,0),(side*1.75,141.1,-.2),.2,"Bronze",8)
    # Tapered wings with a saw-tooth feather silhouette.
    verts=[(side*.45,137.7,.3),(side*1.5,140.2,.7),(side*3,142.6,1.1),(side*3.25,140.8,1),(side*2.7,140.2,1),(side*2.8,139.3,.8),(side*2.15,138.9,.65),(side*2.2,138,.6),(side*1.3,137,.4)]
    g.polygon(verts,"Bronze");g.polygon(list(reversed([(x,y,z+.25) for x,y,z in verts])),"Bronze")
    for a,b in zip(verts,verts[1:]+verts[:1]):g.polygon([a,b,(b[0],b[1],b[2]+.25),(a[0],a[1],a[2]+.25)],"Bronze")
g.beam((1.7,141,-.2),(3.8,141.4,-.4),.12,"Bronze",8)
g.beam((3.8,141.4,-.4),(4.4,141.55,-.45),.32,"Bronze",8)
for i in range(12):
    a,b=i*math.tau/12,(i+1)*math.tau/12
    g.beam((-1.75+.7*math.cos(a),141.7+.7*math.sin(a),-.2),(-1.75+.7*math.cos(b),141.7+.7*math.sin(b),-.2),.09,"Bronze",6)
template("AngelOfVictory",g)

# DRUM — hollow and windowed; exterior columns, square reliefs and scroll-like buttresses.
g=Geometry()
g.lathe([(64,29.3),(65,30.2),(67,30.2),(67.6,29)],48,"Marble",cap=False)
g.lathe([(67.6,28.4),(89,28.4)],48,"StoneShadow",cap=False)
for i in range(16):
    a=i*math.tau/16
    p=(29.05*math.cos(a),0,29.05*math.sin(a))
    g.column(p[0],p[2],69,18.3,.62)
    face=Geometry()
    face.box((0,78,-28.6),(3.5,13,.18),"Glazing")
    face.arch(3.5,10,.42,.35,(0,71.5,-28.9),"Trim",10)
    g.merge(face.transformed(angle=-a-math.pi/2))
for y,r in [(68,30.2),(88,30.7),(89,32),(90,31.7)]:g.lathe([(y,r),(y+.65,r)],64,"Trim",cap=False)
for i in range(8):
    a=i*math.tau/8+math.pi/8
    face=Geometry()
    for y,width,depth in [(65,5,4),(68,4.4,3.5),(71,3.8,2.8),(74,3,2.2),(77,2.1,1.7),(79,1.7,1.2)]:
        face.box((0,y,-30-depth/2),(width,3.1,depth),"Trim")
    face.arch(2.2,0,.55,.5,(0,68,-34),"StoneShadow",12)
    g.merge(face.transformed(angle=a))
template("DomeDrum",g)

# Square-to-round roof transition seals the four corners of the hollow central mass.
g=Geometry()
for i in range(64):
    a,b=i*math.tau/64,(i+1)*math.tau/64
    outer_a=35.3/max(abs(math.cos(a)),abs(math.sin(a)))
    outer_b=35.3/max(abs(math.cos(b)),abs(math.sin(b)))
    for y,reverse in [(66,False),(64.7,True)]:
        pts=[(28.5*math.cos(a),y,28.5*math.sin(a)),(28.5*math.cos(b),y,28.5*math.sin(b)),(outer_b*math.cos(b),y,outer_b*math.sin(b)),(outer_a*math.cos(a),y,outer_a*math.sin(a))]
        g.polygon(list(reversed(pts)) if reverse else pts,"Marble")
template("RotundaRoofRing",g)

# CHHATRI — four octagonal pavilions clustered around the central dome.
g=Geometry()
g.lathe([(0,6.7),(1,7.3),(2,7.3),(2.8,6.4)],8,"Trim",smooth=False)
for i in range(8):
    a=i*math.tau/8+math.pi/8
    g.column(5.2*math.cos(a),5.2*math.sin(a),2.7,12,.36)
    face=Geometry();face.arch(3.5,7.7,.5,.7,(0,3,-5.2),"Trim",8)
    g.merge(face.transformed(angle=-a-math.pi/2))
g.lathe([(15,6.6),(16,7.2),(16.8,7.2),(17.5,6.5),(19,7),(21,6.4),(23,4.5),(24.5,2),(25.5,.7),(26.5,1.1),(28,.35),(29,0)],24,"Marble")
for y,r in [(18,6.7),(21,6.4)]:g.lathe([(y,r),(y+.3,r+.12)],24,"Trim",cap=False)
template("Chhatri",g)

# MONUMENTAL PORTAL — real opening through its barrel-vaulted arch.
g=Geometry()
g.arch(25,29,2.2,8,(0,6,0),"Trim",24)
for side in [-1,1]:
    g.box((side*24,31,0),(16,50,8),"Marble")
    for x in [side*17.7,side*29.3]:g.column(x,-5,6,48,.72)
    for y in [21,48]:g.box((side*24,y,-4.4),(15,.9,1.5),"Trim")
    g.box((side*23.7,35,-4.7),(5.4,11,.4),"Glazing")
    g.arch(5.8,8,.7,.5,(side*23.7,29.5,-5.2),"Trim",12)
    for x in [-1.8,0,1.8]:g.box((side*23.7+x,28.4,-5.3),(.22,2.1,.45),"Trim")
for y,w,h,d in [(52,66,1.6,10),(54,68,1.2,11),(56,65,2.2,9),(59,58,4,7),(63,50,4,6),(66,53,1,8)]:g.box((0,y,0),(w,h,d),"Trim" if y in (52,54,66) else "Marble")
# Fill the area over the arch without sealing the opening.
for i in range(24):
    x0=-12.5+i*25/24;x1=-12.5+(i+1)*25/24
    y0=35+math.sqrt(max(0,12.5**2-x0**2));y1=35+math.sqrt(max(0,12.5**2-x1**2))
    for z,rev in [(-4,False),(4,True)]:
        pts=[(x0,y0,z),(x1,y1,z),(x1,51.3,z),(x0,51.3,z)]
        g.polygon(list(reversed(pts)) if rev else pts,"Marble")
for x in [-24,-8,8,24]:
    g.box((x,67,0),(5,1,5),"Trim")
    # Simplified allegorical sculpture masses, original geometric figures.
    g.lathe([(0,1.2),(.5,1.3),(3,.7),(4,1.2),(4.6,.55),(5.6,.58),(6.2,0)],10,"Trim",(x,67,0))
    g.beam((x-1.1,70,0),(x-2.1,68.7,0),.38,"Trim",8)
    g.beam((x+1,70,0),(x+1.8,72,0),.32,"Trim",8)
template("GrandPortal",g)

g=Geometry()
g.arch(17,18,1.5,2,(0,6,-35.5),"Trim",20)
for x in [-14,14]:g.column(x,-36,6,48,.68)
g.box((0,49,-35.25),(8,15,.3),"Glazing")
g.arch(8,11,.7,.8,(0,41.5,-35.7),"Trim",12)
g.box((0,49,-35.8),(.18,14,.2),"Trim")
for y in [44,49,54]:g.box((0,y,-35.8),(8,.18,.2),"Trim")
for y in [34,60,64,66]:g.box((0,y,-35),(70,1,2),"Trim")
for y in [38,42,46,50,54,58]:g.box((0,y,-35.04),(69,.1,.1),"StoneShadow")
template("RotundaSideFacade",g)

g=Geometry()
g.lathe([(0,9),(.65,9),(1.2,8.3),(3,8.3),(3.6,9),(4.2,9),(5.3,8.6),(7.5,6.8),(9,3.8),(9.8,0)],32,"Marble")
for i in range(8):
    a=i*math.tau/8
    face=Geometry();face.box((0,2.3,-8.4),(2.6,2.2,.15),"Glazing")
    g.merge(face.transformed(angle=a))
template("EntryRoofCupola",g)

g=Geometry()
g.box((0,.25,0),(4.8,.5,7),"Trim")
g.ellipsoid((0,1.2,.9),(1.35,.9,2.15),"Marble",12,6)
g.ellipsoid((0,2.2,-1.2),(1.15,1.3,.9),"Marble",12,6)
g.ellipsoid((0,2.5,-1.8),(.78,.85,.75),"Trim",10,6)
g.box((0,2.25,-2.42),(1.05,.55,.65),"Trim")
for x in [-.8,.8]:
    g.ellipsoid((x,.65,-1.8),(.48,.38,1.25),"Trim",8,4)
    g.ellipsoid((x*.85,3.13,-1.5),(.28,.33,.22),"Marble",8,4)
g.beam((.8,1.3,2.4),(1.4,.5,2.8),.22,"Marble",8)
template("GateLion",g)

# CURVED COLONNADE — continuous curved cornice, repeated on the opposite side.
g=Geometry()
points=[]
for i in range(25):
    t=-math.pi/2+i*math.pi/24
    x,z=91+32*math.cos(t),77*math.sin(t)
    points.append((x,z))
    if i!=12:g.column(x,z,0,19,.64)
for (ax,az),(bx,bz) in zip(points,points[1:]):
    length=math.hypot(bx-ax,bz-az)+.12
    angle=math.atan2(-(bz-az),bx-ax)
    x,z=(ax+bx)/2,(az+bz)/2
    for y,h,depth,mat in [(20,1.5,4.8,"Trim"),(21.2,.8,5.5,"Trim"),(22.4,1.5,4.6,"Marble"),(25.8,.65,4.8,"Trim")]:
        g.box((x,y,z),(length,h,depth),mat,angle)
    for t in [.2,.5,.8]:g.box((ax+(bx-ax)*t,24.2,az+(bz-az)*t),(.4,2.7,.4),"Trim")
template("CurvedColonnade",g)

# ROTUNDA INTERIOR — repetitive arch bays and radial floor inlay.
g=Geometry()
g.arch(10.8,19,1,1.5,(0,0,0),"Trim",16)
for x in [-6.7,6.7]:g.column(x,-.9,0,25,.62)
g.box((0,27,0),(15,1.2,2.8),"Trim")
g.box((0,29,0),(15,1.1,3.4),"Marble")
g.box((0,34.5,0),(15,.8,3.3),"Trim")
for x in [-5.7,-3.8,-1.9,0,1.9,3.8,5.7]:g.lathe([(30,.2),(30.7,.34),(32,.22),(34,.2)],8,"Trim",(x,0,-.5))
g.arch(9.5,2.8,.6,.7,(0,36,0),"Trim",16)
template("RotundaArcade",g)

g=Geometry()
g.lathe([(74,27.6),(88,27.6),(89,28.5)],64,"Marble",cap=False)
# Interior sky blue dome is a separate inward-facing skin, never relying on double-sided materials.
inner=[(89,28.3),(93,27.5),(98,25.7),(103,22.3),(108,17.5),(111,11),(112,0.2)]
g.lathe(inner,64,"DomeBlue",cap=False)
for i in range(16):
    a=i*math.tau/16
    pts=[(r*math.cos(a),y-.09,r*math.sin(a)) for y,r in inner[1:]]
    for p,q in zip(pts,pts[1:]):g.beam(p,q,.13,"Gilt",4)
g.lathe([(111.7,3),(111.8,3)],32,"Gilt",cap=True)
g.f=[tuple(reversed(face)) for face in g.f]
template("InteriorDome",g)

g=Geometry()
g.box((0,8.5,.12),(5.8,13,.15),"WindowLight")
g.arch(5.8,10,.5,.6,(0,2,0),"Trim",12)
g.box((0,8.8,-.15),(.17,12,.2),"Trim")
for y in [5.5,9,12.5]:g.box((0,y,-.15),(5.8,.16,.2),"Trim")
for x in [-4.5,4.5]:g.column(x,-.2,0,17,.36)
template("InnerClerestoryBay",g)

g=Geometry()
g.lathe([(35,30),(74,30)],64,"Marble",cap=False)
for y,r in [(35,29.6),(40,29),(66.5,29),(68,28.6)]:
    g.lathe([(y,r),(y+.6,r)],64,"Trim",cap=False)
for i in range(12):
    if i%3:
        a=i*math.tau/12-math.pi/12
        g.lathe([(7,30),(35,30)],4,"Marble",cap=False,start=a,sweep=math.pi/6)
g.f=[tuple(reversed(face)) for face in g.f]
template("RotundaInnerLining",g)

g=Geometry()
for i in range(32):
    a,b=i*math.tau/32,(i+1)*math.tau/32
    for r0,r1 in [(6,7),(21,22.2),(26,27)]:
        g.polygon([(r0*math.cos(a),.02,r0*math.sin(a)),(r0*math.cos(b),.02,r0*math.sin(b)),(r1*math.cos(b),.02,r1*math.sin(b)),(r1*math.cos(a),.02,r1*math.sin(a))],"FloorDark")
    if i%2==0:
        g.polygon([(7*math.cos(a),.025,7*math.sin(a)),(19*math.cos(a+.055),.025,19*math.sin(a+.055)),(22*math.cos(a+.09),.025,22*math.sin(a+.09)),(19*math.cos(a+.13),.025,19*math.sin(a+.13))],"FloorDark")
template("RotundaInlay",g)

# Original simplified standing figure, informed by the central hall reference.
g=Geometry()
g.lathe([(0,1.6),(.45,1.8),(1.3,1.4),(4,.82),(5.7,.75),(6.6,1.1),(7.3,.6)],12,"Trim")
g.lathe([(7.3,.55),(7.7,.65),(8.4,.62),(8.8,.44),(9,0)],12,"Trim")
g.lathe([(8.55,.5),(8.8,.62),(9.2,.45),(9.45,0)],10,"Gilt")
g.beam((-.8,6.8,0),(-1.4,4.7,-.15),.3,"Trim",8)
g.beam((.8,6.8,0),(1.5,5.6,-.2),.3,"Trim",8)
g.beam((1.5,5.6,-.2),(1.6,6.5,-.65),.22,"Trim",8)
g.beam((1.6,3,-.65),(1.6,7,-.65),.08,"Gilt",6)
template("QueensHallFigure",g)

# GALLERY VAULT — a real barrel shell with broad transverse ribs.
g=Geometry()
for i in range(24):
    a,b=i*math.pi/24,(i+1)*math.pi/24
    g.polygon([(12*math.cos(a),25+10*math.sin(a),11),(12*math.cos(b),25+10*math.sin(b),11),(12*math.cos(b),25+10*math.sin(b),-11),(12*math.cos(a),25+10*math.sin(a),-11)],"Marble",True)
for z in [-10.8,10.8]:g.arch(24,25,.55,.7,(0,0,z),"Trim",24)
template("GalleryVault",g)

# ORIGINAL VEGETATION; shared geometry rather than imported toolbox objects.
g=Geometry()
g.lathe([(0,.9),(9,.65),(17,.35)],10,"Bark")
for i in range(8):
    a=i*math.tau/8
    p=(0,16,0);q=(9*math.cos(a),17+((i%3)-1)*1.5,9*math.sin(a));tip=(13*math.cos(a),13.5,13*math.sin(a))
    perpendicular=(-math.sin(a)*1.6,0,math.cos(a)*1.6)
    g.polygon([p,(q[0]+perpendicular[0],q[1],q[2]+perpendicular[2]),tip,(q[0]-perpendicular[0],q[1],q[2]-perpendicular[2])],"Leaf" if i%2 else "LeafLight")
    g.polygon(list(reversed([(v[0],v[1]-.12,v[2]) for v in [p,(q[0]+perpendicular[0],q[1],q[2]+perpendicular[2]),tip,(q[0]-perpendicular[0],q[1],q[2]-perpendicular[2])]])),"Leaf")
template("GardenPalm",g)

g=Geometry()
g.lathe([(0,.75),(7,.55),(11,.15)],8,"Bark")
for y,r,mat,dx,dz in [(11,7,"Leaf",0,0),(15,6,"LeafLight",-2,1),(14,5.7,"Leaf",3,-1)]:
    g.lathe([(-r*.6,0),(-r*.25,r*.85),(r*.25,r),(r*.7,r*.55),(r,0)],10,mat,(dx,y,dz),smooth=False)
template("GardenTree",g)

# ASSEMBLY — plinth, playable shell, quadrangles and facades.
box("TerraceFoundation",(0,2.4,0),(272,4.8,216),"StoneShadow")
box("MarbleTerrace",(0,5.25,0),(270,1.5,214),"Trim")
for z in [-105.8,105.8]:box("TerraceEdgeCourse",(0,4.8,z),(271,.55,1),"Trim",False)
for x in [-134,134]:box("TerraceEdgeCourse",(x,4.8,0),(1,.55,212),"Trim",False)
for side in [-1,1]:
    for i in range(8):
        y=(i+1)*.75
        z=side*(108+(7-i)*1.7)
        box("ApproachStair",(0,y/2,z),(42,y,3.6),"Marble")
    # Secondary side stairs, 18 studs clear.
    for i in range(8):
        y=(i+1)*.75;x=side*(136+(7-i)*1.45)
        box("SideStair",(x,y/2,0),(3,y,20),"Marble")
    instance("GrandPortal","NorthPortal" if side<0 else "SouthPortal",(0,0,side*93),0 if side<0 else math.pi)
    for x in [-24,24]:collider("PortalPierCollision",(x,31,side*93),(16,50,8))
    collider("PortalUpperCollision",(0,51,side*93),(32,6,8))
    # Wide gallery wings on either side of the entry halls.
    for wing in [-1,1]:
        cx=wing*64.5;cz=side*76
        box("WingFloor",(cx,6.4,cz),(65,0.8,35),"Trim")
        box("WingRoof",(cx,47.9,cz),(66,1.8,36),"Marble")
        box("WingOuterWall",(cx,27,side*94),(65,42,2),"Marble")
        # Inner courtyard elevation; leave the main gallery connection open.
        for a,b in [(32,55.5),(64.5,97)]:box("WingCourtyardWall",(wing*(a+b)/2,27,side*58),(b-a,42,2),"Marble")
        box("GalleryDoorLintel",(wing*60,36,side*58),(9,24,2),"Marble")
        for y in [10,14,18,27,31,35,39]:
            box("WingMarbleCourse",(cx,y,side*95.025),(65,.10,.08),"StoneShadow",False,"Exterior")
        for k in range(5):
            x=wing*(37.6+k*11.2)
            instance("FacadeBay",f"OuterBay_{side}_{wing}_{k}",(x,4.5,side*95.1),0 if side<0 else math.pi)
            instance("GalleryDoorBay" if k==2 else "FacadeBay",f"CourtBay_{side}_{wing}_{k}",(x,4.5,side*56.9),math.pi if side<0 else 0)
        for k in range(3):instance("GalleryVault",f"WingVault_{side}_{wing}_{k}",(wing*(43+k*21),6,side*76),math.pi/2,"Interior")
    # Entrance hall sides are split around 16-stud gallery doors.
    for x in [-31,31]:
        box("EntryWall",(x,27,side*47),(2,42,22),"Marble")
        box("EntryDoorLintel",(x,39,side*75),(2,18,34),"Marble")
        box("EntryWallEnd",(x,18,side*89),(2,24,7),"Marble")
    box("EntryHallRoof",(0,57,side*65),(62,2,57),"Marble")
    instance("EntryRoofCupola",f"EntryRoofCupola_{side}",(0,58,side*66))
    for z in [side*47,side*70]:instance("GalleryVault",f"EntryVault_{z}",(0,6,z),0,"Interior")
    for x in [-105,105]:
        instance("CornerTower",f"CornerTower_{x}_{side}",(x,6,side*77))
        collider("TowerBaseCollision",(x,32,side*77),(30,52,30))

# Central square mass is a hollow octagonal chamber with 4 open axial passages.
for side in [-1,1]:
    for offset in [-1,1]:
        box("RotundaWallPier",(side*33,22,offset*24),(4,32,20),"Marble")
        box("RotundaWallPier",(offset*24,22,side*33),(20,32,4),"Marble")
    box("RotundaUpperWall",(side*33,52,0),(4,28,70),"Marble")
    box("RotundaUpperWall",(0,52,side*33),(70,28,4),"Marble")
    box("AxialPassageLintel",(side*33,35,0),(4,6,28),"Marble")
    box("AxialPassageLintel",(0,35,side*33),(28,6,4),"Marble")
box("RotundaFloor",(0,6.5,0),(66,1,66),"Trim")
for i in range(12):
    a=i*math.tau/12
    instance("RotundaArcade",f"QueensHallArch_{i}",(28.9*math.sin(a),7,28.9*math.cos(a)),a,"Interior")
for i in range(16):
    a=i*math.tau/16
    instance("InnerClerestoryBay",f"Clerestory_{i}",(27.45*math.sin(a),69,27.45*math.cos(a)),a,"Interior")
instance("RotundaInlay","QueensHallRadialFloor",(0,7.02,0),0,"Interior")
instance("InteriorDome","QueensHallCeiling",group="Interior")
instance("RotundaInnerLining","QueensHallInnerWall",group="Interior")
instance("DomeDrum","CentralDrum")
instance("RotundaRoofRing","SquareToRoundRoof")
for side in [-1,1]:instance("RotundaSideFacade",f"RotundaSideFacade_{side}",yaw=-side*math.pi/2)
instance("CentralDome","CentralDome")
instance("AngelOfVictory","AngelOfVictory")
for x in [-33,33]:
    for z in [-33,33]:instance("Chhatri",f"CentralChhatri_{x}_{z}",(x,66,z))

# Open side quadrangles; smooth bow colonnades frame the monument in side views.
for side in [-1,1]:
    instance("CurvedColonnade",f"CurvedColonnade_{side}",(0,6,0),0 if side>0 else math.pi)
    for i in range(25):
        if i==12:continue # 20-stud side escape opening in the centre of the colonnade.
        t=-math.pi/2+i*math.pi/24
        collider("ColonnadeShaftCollision",(side*(91+32*math.cos(t)),15.5,77*math.sin(t)),(1.25,19,1.25))
    # Courtyard checkerboard uses one decal-free mesh instead of hundreds of parts.
    tiles=Geometry()
    for ix in range(7):
        for iz in range(13):
            x=side*(41+ix*7.2);z=-47+iz*7.2
            if (ix+iz)%2==0:tiles.box((x,6.02,z),(7.18,.035,7.18),"FloorDark")
    template(f"CourtyardInlay_{side}",tiles)
    instance(f"CourtyardInlay_{side}",f"QuadrangleFloor_{side}",group="Interior")

# A simple, unfurnished objective-ready plinth and four safe axial routes.
box("QueensHallCentralPlinth",(0,7.7,0),(5,1.4,5),"Marble",True,"Interior")
instance("QueensHallFigure","QueensHallFigure",(0,8.4,0),0,"Interior")
for name,pos,size,role in [
    ("NorthEntrance",(0,12,-101),(24,12,12),"Entrance"),
    ("SouthEntrance",(0,12,101),(24,12,12),"Entrance"),
    ("EastServiceExit",(136,10,0),(16,8,20),"Exit"),
    ("WestServiceExit",(-136,10,0),(16,8,20),"Exit"),
    ("QueensHallObjective",(0,11,0),(14,8,14),"FutureObjectiveSpace"),
    ("NorthWestGallery",(-65,15,-76),(38,16,23),"FutureGallerySpace"),
    ("SouthEastGallery",(65,15,76),(38,16,23),"FutureGallerySpace"),
    ("LandmarkPivot",(0,0,0),(1,1,1),"Pivot"),
]:marker(name,pos,size,role)

# COMPRESSED FORMAL GROUNDS. No city outside the immediate landmark is generated.
for x in [-150,150]:
    # Grass stays below road level; coplanar surfaces flicker at shallow angles.
    for z in [-155,155]:box("CampusGround",(x,-1.08,z),(300,2,310),"Lawn",True,"Grounds")
for z in [-193,193]:box("AxialPromenade",(0,.13,z),(30,.26,170),"Path",True,"Grounds")
for x in [-179,179]:box("SidePromenade",(x,.13,0),(24,.26,480),"Path",True,"Grounds")
for z in [-125,125]:box("TerracePromenade",(0,.16,z),(360,.32,20),"Path",True,"Grounds")
for side in [-1,1]:
    for x in [-95,95]:
        z=side*193
        box("SunkenPoolBasin",(x,.25,z),(73,.5,74),"StoneShadow",True,"Grounds")
        box("StillWater",(x,.57,z),(68,.16,69),"Water",False,"Grounds")
        for dx in [-36.5,36.5]:box("PoolCoping",(x+dx,.7,z),(1.2,1,75),"Trim",True,"Grounds")
        for dz in [-37,37]:box("PoolCoping",(x,.7,z+dz),(73,1,1.2),"Trim",True,"Grounds")
    for x in [-43,43]:
        for z in [side*151,side*191,side*231]:instance("GardenPalm",f"AvenuePalm_{x}_{z}",(x,.2,z),group="Grounds")
    for x in [-216,216]:
        for z in [side*63,side*132,side*219]:instance("GardenTree",f"PerimeterTree_{x}_{z}",(x,.1,z),group="Grounds")
    for x in [-150,150]:
        for z in [side*163,side*226]:
            box("FormalHedge",(x,1.25,z),(12,2.5,42),"Leaf",True,"Grounds")
    # Marble gate piers leave the central 36 studs open.
    for x in [-25,25]:
        box("MainGatePier",(x,5,side*258),(5,10,5),"Marble",True,"Grounds")
        box("GatePierCap",(x,10.4,side*258),(6,.8,6),"Trim",False,"Grounds")
        instance("GateLion",f"GateLion_{x}_{side}",(x,10.8,side*258),0 if side<0 else math.pi,"Grounds")
    # Gate leaves are visibly folded open beside the clear central promenade.
    for side_x in [-1,1]:
        x=side_x*36
        for y in [1.4,6.4]:box("OpenGateRail",(x,y,side*258),(18,.28,.28),"Bronze",False,"Grounds")
        for dx in range(-8,9,2):box("OpenGatePicket",(x+dx,4.2,side*258),(.2,6,.2),"Bronze",False,"Grounds")
    for x in [-136,136]:box("GardenBench",(x,1.5,side*131),(9,1,3),"Marble",True,"Grounds")
# Boundary segmented to avoid turning the campus into one atomic streaming unit.
for side in [-1,1]:
    for a,b in [(-248,-32),(32,248)]:
        box("BoundaryBase",((a+b)/2,1,side*262),(b-a,2,1.8),"Marble",True,"Grounds")
        box("BoundaryRail",((a+b)/2,3.5,side*262),(b-a,.3,.3),"Bronze",False,"Grounds")
        for x in range(int(a)+4,int(b),7):box("BoundaryPicket",(x,2.7,side*262),(.18,3,.18),"Bronze",False,"Grounds")
    for z0,z1 in [(-262,-17),(17,262)]:
        box("BoundarySide",(side*248,1,(z0+z1)/2),(1.8,2,z1-z0),"Marble",True,"Grounds")
        box("BoundarySideRail",(side*248,3.5,(z0+z1)/2),(.3,.3,z1-z0),"Bronze",False,"Grounds")
        for z in range(z0+4,z1,7):box("BoundaryPicket",(side*248,2.7,z),(.18,3,.18),"Bronze",False,"Grounds")
    box("SideGatePath",(side*198,.15,0),(108,.3,24),"Path",True,"Grounds")
    box("PerimeterRoad",(side*277,-.12,0),(40,.24,614),"Asphalt",True,"Grounds")
    box("PerimeterRoad",(0,-.12,side*287),(514,.24,40),"Asphalt",True,"Grounds")
    box("PerimeterFootpath",(side*253,.2,0),(8,.4,530),"Path",True,"Grounds")

# Export manifest and all material-separated reusable mesh templates.
library={}
for name,objects in TEMPLATES.items():
    for obj in objects:
        mesh=obj.data;mesh.calc_loop_triangles()
        normals=mesh.corner_normals
        vertices=[(round(v.co.x,5),round(v.co.z,5),round(-v.co.y,5)) for v in mesh.vertices]
        triangles=[];tn=[]
        for tri in mesh.loop_triangles:
            triangles.append(list(tri.vertices))
            tn.append([[round(normals[li].vector.x,5),round(normals[li].vector.z,5),round(-normals[li].vector.y,5)] for li in tri.loops])
        library[obj.name]=dict(template=name,material=obj["MaterialRole"],vertices=vertices,triangles=triangles,normals=tn)
manifest=dict(version=1,assetId="landmark.kolkata.victoria-memorial",units="Roblox studs",blenderMapping="(x,-z,y)",palette=PALETTE,instances=INSTANCES,primitives=PRIMITIVES,markers=MARKERS,library={key:dict(template=v["template"],material=v["material"],vertices=len(v["vertices"]),triangles=len(v["triangles"])) for key,v in library.items()})
(OUT/"mesh-library.json").write_text(json.dumps(library,separators=(",",":")),encoding="utf-8")
(OUT/"assembly-manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
authoring_manifest=ROOT/"authoring/VictoriaManifest.luau"
authoring_manifest.parent.mkdir(parents=True,exist_ok=True)
authoring_manifest.write_text('--!strict\n-- Generated authoring data; edit Blender source and regenerate manifest.\nreturn game:GetService("HttpService"):JSONDecode([==['+json.dumps(manifest,separators=(",",":"))+']==])\n',encoding="utf-8")

# Hide export templates without removing them from the file.
LIB.hide_render=True;LIB.hide_viewport=True
def export_fbx(filename, collections):
    # Export duplicates own their mesh datablocks. This avoids Blender 5.2's FBX
    # material-map warnings for selected linked copies whose hidden source is excluded.
    staging=collection("VM_ExportTemporary")
    for obj in bpy.context.selected_objects:obj.select_set(False)
    duplicates=[]
    for col in collections:
        for source in col.objects:
            obj=source.copy();obj.data=source.data.copy();obj.name=source.name+"_Export"
            staging.objects.link(obj);obj.hide_set(False);obj.hide_viewport=False;obj.hide_render=False
            obj.select_set(True);duplicates.append(obj)
    bpy.context.view_layer.update()
    bpy.ops.export_scene.fbx(filepath=str(OUT/filename),use_selection=True,object_types={"MESH"},global_scale=1,apply_unit_scale=True,apply_scale_options="FBX_SCALE_UNITS",axis_forward="-Z",axis_up="Y",use_mesh_modifiers=True,bake_anim=False,path_mode="AUTO",mesh_smooth_type="FACE")
    for obj in duplicates:
        mesh=obj.data;bpy.data.objects.remove(obj,do_unlink=True);bpy.data.meshes.remove(mesh)
    bpy.data.collections.remove(staging)

export_fbx("VictoriaMemorial_Architecture.fbx",[ARCH,SHELL,INTERIOR])
export_fbx("VictoriaMemorial_MeshLibrary.fbx",[LIB])
export_fbx("VictoriaMemorial_Grounds.fbx",[GROUNDS])
export_fbx("VictoriaMemorial_Collision.fbx",[COLLISION])
# This is the assembled import handoff. The overlapping template library is
# reserved for automated assembly and must never be presented as the landmark.
export_fbx("VictoriaMemorial_Roblox.fbx",[ARCH,SHELL,INTERIOR,GROUNDS])
COLLISION.hide_viewport=True
META.hide_viewport=True

# Presentation is local authoring only; it is never exported to Roblox.
scene=bpy.context.scene
scene.unit_settings.system="NONE"
scene.unit_settings.scale_length=1
scene.world.color=(.33,.39,.44)
world=scene.world;world.use_nodes=True
world.node_tree.nodes.get("Background").inputs[0].default_value=(.43,.54,.64,1)
world.node_tree.nodes.get("Background").inputs[1].default_value=.5
for name,loc,energy,size in [("Key",(80,100,230),3500000,150),("Fill",(-130,50,170),1800000,130)]:
    data=bpy.data.lights.new("VM_"+name,"AREA");data.energy=energy;data.shape="DISK";data.size=size
    obj=bpy.data.objects.new("VM_"+name,data);PRESENT.objects.link(obj);obj.location=bv(loc)
    obj.rotation_euler=(Vector(bv((0,35,0)))-obj.location).to_track_quat("-Z","Y").to_euler()
sun_data=bpy.data.lights.new("VM_Sun","SUN");sun_data.energy=2.2;sun_data.angle=.07
sun=bpy.data.objects.new("VM_Sun",sun_data);PRESENT.objects.link(sun);sun.rotation_euler=(math.radians(24),math.radians(-20),math.radians(-25))
camera_data=bpy.data.cameras.new("VM_ReviewCamera");camera=bpy.data.objects.new("VM_ReviewCamera",camera_data);PRESENT.objects.link(camera)
camera.location=bv((285,186,-350));camera.rotation_euler=(Vector(bv((0,47,0)))-camera.location).to_track_quat("-Z","Y").to_euler()
camera_data.lens=43;camera_data.clip_end=3000;scene.camera=camera
scene.render.resolution_x=1600;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.view_settings.view_transform="AgX"
scene.render.engine="CYCLES";scene.cycles.samples=32
for area in bpy.context.screen.areas:
    if area.type=="VIEW_3D":
        area.spaces.active.region_3d.view_distance=430
        area.spaces.active.region_3d.view_location=Vector(bv((0,42,0)))
        area.spaces.active.clip_end=4000
        area.spaces.active.shading.color_type="MATERIAL"

tot_tris=sum(len(library[obj.name]["triangles"]) for tid in TEMPLATES for obj in TEMPLATES[tid])
inst_tris=sum(sum(len(library[obj.name]["triangles"]) for obj in TEMPLATES[i["template"]]) for i in INSTANCES)
summary=dict(unique_meshes=len(library),module_types=len(TEMPLATES),mesh_instances=sum(len(TEMPLATES[i["template"]]) for i in INSTANCES),unique_triangles=tot_tris,instanced_triangles=inst_tris,native_primitives=len(PRIMITIVES),markers=len(MARKERS),architecture_bounds="~272 x 143 x 246 studs, Y up; grounds 594 x 614 studs")
(OUT/"build-summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"VictoriaMemorial.blend"))
print(json.dumps(summary))
