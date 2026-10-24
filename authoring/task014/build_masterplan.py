"""Build only the Task014 Stage A planning scene. Never writes landmark sources."""
from pathlib import Path
import bpy, math, json, sys
from mathutils import Vector

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from layout import ROOT, OUT, design

D=design()
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
scene.name='Kolkata_Masterplan_Stage_A'
scene.unit_settings.system='NONE'
scene['Stage']='A — placement review; Stage B and Studio integration await approval'
scene['Coordinates']='Roblox (X,Y,Z) => Blender (X,-Z,Y), 1 unit = 1 stud'
scene['PremiumBoundary']='X -280..1920; Z -1100..1100; no Tier3 inside'
COLS={}
def collection(name):
    if name not in COLS:
        c=bpy.data.collections.new(name);scene.collection.children.link(c);COLS[name]=c
    return COLS[name]
for name in ['Existing World Anchors','Victoria Memorial','Colonial Heritage','Modern Skyline',
             'Bengali Cultural District','Commercial Cultural District','Dakshineshwar Riverfront',
             'Road Network','Flyover Network','Elevated Metro','Metro Stations','District Foundations',
             'Planning Markers Boundaries','Review Cameras','External Legacy Context']:
    collection(name)

def B(p):return (p[0],-p[2],p[1])
def mat(name,color):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1)
    if m.node_tree is None:m.use_nodes=True
    n=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    n.inputs['Base Color'].default_value=(*color,1);n.inputs['Roughness'].default_value=.78
    return m
M={k:mat('PLAN_'+k,c) for k,c in dict(
    asphalt=(.075,.091,.104),walk=(.58,.55,.46),stone=(.64,.65,.61),
    grass=(.19,.31,.22),heritage=(.30,.35,.28),modern=(.22,.31,.31),
    cultural=(.31,.32,.23),commercial=(.34,.32,.28),water=(.10,.27,.33),
    concrete=(.49,.51,.49),parapet=(.64,.66,.64),rail=(.16,.20,.23),
    station=(.74,.73,.65),roof=(.28,.40,.40),accent=(.68,.35,.19),
    marking=(.81,.75,.51),label=(.88,.87,.74),trunk=(.28,.20,.12),
    leaf=(.16,.30,.20)).items()}
MESHES={}
def cube(name,center,size,material,col):
    key=material.name
    if key not in MESHES:
        mesh=bpy.data.meshes.new('Reusable_Unit_Box_'+key)
        mesh.from_pydata([(-.5,-.5,-.5),(.5,-.5,-.5),(.5,.5,-.5),(-.5,.5,-.5),
                         (-.5,-.5,.5),(.5,-.5,.5),(.5,.5,.5),(-.5,.5,.5)],[],
                        [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
        mesh.materials.append(material);MESHES[key]=mesh
    o=bpy.data.objects.new(name,MESHES[key]);collection(col).objects.link(o)
    o.location=B(center);o.scale=(size[0],size[2],size[1]);return o
def beam(name,a,b,width,depth,material,col):
    v=Vector(B(b))-Vector(B(a));mid=(Vector(B(a))+Vector(B(b)))/2
    o=cube(name,(mid.x,mid.z,-mid.y),(width,depth,v.length),material,col)
    # Unit box local Y runs along the segment, local Z remains deck thickness.
    o.rotation_euler=v.to_track_quat('Y','Z').to_euler()
    return o
def text(name,body,p,size=20,material=None,col='Planning Markers Boundaries'):
    f=bpy.data.curves.new(name,'FONT');f.body=body;f.size=size;f.align_x='CENTER';f.extrude=0
    o=bpy.data.objects.new(name,f);collection(col).objects.link(o);o.location=B(p)
    f.materials.append(material or M['label']);return o
def line(name,pts,width,material,col):
    for i,(a,b) in enumerate(zip(pts,pts[1:])):beam(f'{name}_{i:03}',a,b,width,.18,material,col)

# Load read-only linked source objects into one local wrapper per landmark.
# Wrapper membership excludes preview lights, collision-only geometry and export duplicates.
def link_asset(r):
    path=ROOT/r['source']
    with bpy.data.libraries.load(str(path),link=True,relative=True) as (src,dst):
        dst.collections=list(r['source_collections'])
    wrapper=bpy.data.collections.new('LINKED_ASSET_'+r['id'])
    seen=set()
    for c in dst.collections:
        for o in c.all_objects:
            if o.type!='MESH' or o.hide_render:continue
            if o.name not in seen:wrapper.objects.link(o);seen.add(o.name)
            parent=o.parent
            while parent:
                if parent.name not in seen:wrapper.objects.link(parent);seen.add(parent.name)
                parent=parent.parent
    o=bpy.data.objects.new(r['id']+'__GroundOrigin',None)
    o.instance_type='COLLECTION';o.instance_collection=wrapper
    o.location=B(r['position']);o.rotation_euler.z=math.radians(r['yaw_degrees'])
    o.empty_display_size=10;collection(r['district']).objects.link(o)
    o['AssetId']=r['id'];o['RobloxPosition']=r['position'];o['RobloxYaw']=r['yaw_degrees']
    o['Source']=r['source'];o['Status']=r['status'];r['linked_mesh_objects']=len([x for x in wrapper.objects if x.type=='MESH'])
    return o
for r in D['placements']:link_asset(r)

# Terrain proxies, intentionally separate from real native Terrain.
cube('City_Land_Planning_Proxy',(835,-15,0),(2470,28,2680),M['grass'],'District Foundations')
cube('West_Bank_South_Proxy',(-514,-15,340),(228,28,2000),M['grass'],'District Foundations')
cube('West_Bank_North_Proxy',(-514,-15,-1250),(228,28,180),M['grass'],'District Foundations')
cube('Dakshineshwar_Lower_Bank_Proxy',(-514,-18.25,-910),(228,19.5,500),M['grass'],'District Foundations')
cube('Howrah_Landing_Planning_Proxy',(-1830,-15,-180),(540,28,430),M['grass'],'Existing World Anchors')
cube('Hooghly_Water_DATUM_minus13_5',(-1094,-13.7,-50),(932,.4,2460),M['water'],'Existing World Anchors')
for name,rect in D['district_plots_xz'].items():
    x0,z0,x1,z1=rect;key={'A':'heritage','B':'modern','C':'cultural','D':'commercial'}[name[0]]
    cube(name+'_Planning_Foundation',((x0+x1)/2,-1.3,(z0+z1)/2),(x1-x0,.5,z1-z0),M[key],'District Foundations')

# Protect the full measured compounds; plot slabs extend by 12 studs around the actual source envelope.
for r in D['placements']:
    if r['id'] in ['VICTORIA','HOWRAH','GHAT','KOL_T1_DAKSHINESHWAR']:continue
    lo,hi=r['world_bounds_roblox'];x0,z0,x1,z1=lo[0]-12,lo[2]-12,hi[0]+12,hi[2]+12
    r['plot_bounds_xz']=[x0,z0,x1,z1]
    cube(r['id']+'_Plot',((x0+x1)/2,-.65,(z0+z1)/2),(x1-x0,.5,z1-z0),M['walk'],'District Foundations')

# Ground road splitting produces real junctions: no sidewalks laid across a carriageway.
def cross(a,b,c,d):
    dx,dz=b[0]-a[0],b[1]-a[1];ex,ez=d[0]-c[0],d[1]-c[1]
    det=dx*ez-dz*ex
    if abs(det)<1e-8:return None
    t=((c[0]-a[0])*ez-(c[1]-a[1])*ex)/det
    u=((c[0]-a[0])*dz-(c[1]-a[1])*dx)/det
    if -1e-7<=t<=1+1e-7 and -1e-7<=u<=1+1e-7:return t,u,(a[0]+t*dx,a[1]+t*dz)
segments=[]
for road in D['roads']:
    for a,b in zip(road['points_xz'],road['points_xz'][1:]):segments.append((road,a,b))
for ri,(road,a,b) in enumerate(segments):
    length=math.dist(a,b);splits={0.:road['width']/2,1.:road['width']/2}
    for r2,c,d in segments:
        hit=cross(a,b,c,d)
        if hit:splits[round(hit[0],8)]=max(splits.get(round(hit[0],8),0),r2['width']/2)
    ts=sorted(splits)
    dx,dz=(b[0]-a[0])/length,(b[1]-a[1])/length;nx,nz=-dz,dx
    for i in range(math.ceil(length/64)):
        t0=i/math.ceil(length/64);t1=(i+1)/math.ceil(length/64)
        aa=(a[0]+(b[0]-a[0])*t0,-.3,a[1]+(b[1]-a[1])*t0)
        bb=(a[0]+(b[0]-a[0])*t1,-.3,a[1]+(b[1]-a[1])*t1)
        beam(f'{road["id"]}__Road_{i:03}',aa,bb,road['width'],.6,M['asphalt'],'Road Network')
    for j,(ta,tb) in enumerate(zip(ts,ts[1:])):
        inset0=splits[ta]+3;inset1=splits[tb]+3
        start,end=ta*length+inset0,tb*length-inset1
        if end<=start:continue
        for side in [-1,1]:
            offset=side*(road['width']/2+road['sidewalk']/2)
            aa=(a[0]+dx*start+nx*offset,.25,a[1]+dz*start+nz*offset)
            bb=(a[0]+dx*end+nx*offset,.25,a[1]+dz*end+nz*offset)
            for k in range(math.ceil((end-start)/64)):
                n=math.ceil((end-start)/64);u=k/n;v=(k+1)/n
                p=tuple(aa[q]+(bb[q]-aa[q])*u for q in range(3));q=tuple(aa[q]+(bb[q]-aa[q])*v for q in range(3))
                beam(f'{road["id"]}_Sidewalk_{side}_{j}_{k}',p,q,road['sidewalk'],.5,M['walk'],'Road Network')
        if road['median']:
            aa=(a[0]+dx*start,.10,a[1]+dz*start);bb=(a[0]+dx*end,.10,a[1]+dz*end)
            # East perimeter median remains flush: ramp footprints occupy its centre.
            beam(road['id']+'_Median',aa,bb,road['median'],.08,M['grass'],'Road Network')

# Junction corner paving stays outside both crossing road envelopes, leaving turning flares.
for i,(road,a,b) in enumerate(segments):
    for r2,c,d in segments[i+1:]:
        h=cross(a,b,c,d)
        if not h:continue
        x,z=h[2]
        if abs(a[0]-b[0])>.01:wx=r2['width']/2;wz=road['width']/2
        else:wx=road['width']/2;wz=r2['width']/2
        for sx in [-1,1]:
            for sz in [-1,1]:
                cube('Intersection_Corner_Reservation',(x+sx*(wx+8),-.03,z+sz*(wz+8)),(10,.06,10),M['walk'],'Road Network')

INFRA={'flyovers':[],'metro_supports':[],'local_access':[],'checks_note':'Planning geometry only; no vehicle or structural simulation.'}
def deck_segment(name,a,b,width,thickness,col='Flyover Network',barrier=True,end_width=None):
    # A true wedge segment has horizontal cross-section and exact endpoint top heights.
    dx,dz=b[0]-a[0],b[2]-a[2];ll=math.hypot(dx,dz);nx,nz=-dz/ll,dx/ll
    verts=[]
    for drop in [thickness,0]:
        for p,w in [(a,width),(b,end_width or width)]:
            for side in [-1,1]:verts.append(B((p[0]+side*nx*w/2,p[1]-drop,p[2]+side*nz*w/2)))
    mesh=bpy.data.meshes.new(name+'_Wedge');mesh.from_pydata(verts,[],[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)])
    mesh.materials.append(M['asphalt'] if col=='Flyover Network' else M['concrete'])
    o=bpy.data.objects.new(name,mesh);collection(col).objects.link(o)
    if barrier:
        for side in [-1,1]:
            aa=(a[0]+side*nx*(width/2-.5),a[1]+1.5,a[2]+side*nz*(width/2-.5))
            bb=(b[0]+side*nx*((end_width or width)/2-.5),b[1]+1.5,b[2]+side*nz*((end_width or width)/2-.5))
            beam(name+'_Parapet',aa,bb,1,3,M['parapet'],col)
    return o
def support(name,x,z,top,width=5,depth=7,col='Flyover Network'):
    if top<=1:return
    cube(name,(x,(top-1)/2,z),(width,top+1,depth),M['concrete'],col)
    cube(name+'_Cap',(x,top-1,z),(width+9,2,depth+2),M['concrete'],col)

# F01 reuses the exact bridge deck interface. Only the east approach is redesigned.
pts=[]
for i in range(93):
    x=-644+1104*i/92
    if x<-500:y=18.5+5.5*(.5-.5*math.cos(math.pi*(x+644)/144))
    elif x<=-20:y=24
    else:y=24*(.5+.5*math.cos(math.pi*(x+20)/480))
    pts.append([x,y,-180])
def entry_width(x):return 60-28*min(1,max(0,(x+644)/244))
for i,(a,b) in enumerate(zip(pts,pts[1:])):
    deck_segment(f'F01_Bridge_Entry_{i:03}',a,b,entry_width(a[0]),4,end_width=entry_width(b[0]))
pillars=[]
for x in [-600,-540,-460,-400,-340,-280,-270,-190,-130,-70,-10,50,110,170,230,290,350]:
    y=min(pts,key=lambda p:abs(p[0]-x))[1]-4
    support('F01_Pier',x,-180,y);pillars.append([x,y,-180])
    if y>1:cube('F01_Transverse_Pier_Head',(x,y-1,-180),(8,2,entry_width(x)-2),M['concrete'],'Flyover Network')
INFRA['flyovers'].append(dict(id='F01',name='Bridge entry connector',points=pts,width=60,end_width=32,taper_length=244,depth=4,pillars=pillars,
                             max_grade_percent=round(100*24*math.pi/(2*480),2),
                             note='Exact bridge east road socket X=-644,Y=18.5,Z=-180; new bank ramps replace old east approach in proposal only.'))
walks=[]
for side in [-1,1]:
    pp=[]
    for i,p in enumerate(pts):
        t=i/(len(pts)-1);offset=39+11*min(1,t*4)
        pp.append([p[0],p[1]+.5+.5*(1-t),-180+side*offset])
    pp.append([478,.5,-180+side*50])
    for i,(a,b) in enumerate(zip(pp,pp[1:])):deck_segment(f'Bridge_East_Pedestrian_{side}_{i}',a,b,10,1,'Flyover Network',False)
    for x in [-600,-540,-460,-400,-340,-280,-190,-130,-70,-10,50,110,170,230,290,350]:
        p=min(pp,key=lambda p:abs(p[0]-x));support('Bridge_Pedestrian_Pier',x,p[2],p[1]-1,2,6)
    walks.append(pp)
INFRA['bridge_east_pedestrian_connections']=dict(paths=walks,width=10,max_grade_percent=7.90,
    note='Each original bridge footway crosses above both bank streets and descends beside the vehicle ramp to the Victoria west-loop sidewalk; terminal crossing is at grade.')

# F02 occupies the eastern perimeter median, leaving 20-stud service lanes each side.
pts=[]
for i in range(135):
    z=-1070+2140*i/134
    if z<-550:y=26*(.5-.5*math.cos(math.pi*(z+1070)/520))
    elif z<=550:y=26
    else:y=26*(.5+.5*math.cos(math.pi*(z-550)/520))
    pts.append([1870,y,z])
for i,(a,b) in enumerate(zip(pts,pts[1:])):deck_segment(f'F02_East_Perimeter_{i:03}',a,b,32,4)
pillars=[]
zs=[z for z in range(-950,1000,60) if not any(abs(z-v)<46 for v in [-370,-40,370])]
zs=sorted(set(zs+[v+delta for v in [-370,-40,370] for delta in [-48,48]]))
for z in zs:
    y=min(pts,key=lambda p:abs(p[2]-z))[1]-4
    support('F02_Median_Pier',1870,z,y);pillars.append([1870,y,z])
    if y>1:cube('F02_Transverse_Pier_Head',(1870,y-1,z),(30,2,8),M['concrete'],'Flyover Network')
INFRA['flyovers'].append(dict(id='F02',name='Skyline eastern bypass',points=pts,width=32,depth=4,pillars=pillars,
                             max_grade_percent=round(100*26*math.pi/(2*520),2),
                             note='520-stud eased ramps; 36-stud ground median leaves two 20-stud parallel service lanes. No intermediate ramp junctions.'))
# West-bank approach has a gentle 400-stud rise; bridge geometry remains fixed.
west=[]
for i in range(26):
    t=i/25;west.append([-1940+400*t,18.5*(.5-.5*math.cos(math.pi*t)),-180])
for i,(a,b) in enumerate(zip(west,west[1:])):deck_segment(f'West_Bridge_Approach_{i}',a,b,60,3)
for x in range(-1900,-1560,60):
    y=min(west,key=lambda p:abs(p[0]-x))[1]-3;support('West_Approach_Bearing',x,-180,y,12,40)
INFRA['west_bridge_approach']=dict(points=west,width=60,max_grade_percent=round(100*18.5*math.pi/800,2),
    note='New offline western landing at X=-1940. Historical expansion marker X=-1720 is recorded, not treated as an unchanged ground junction.')

# ONE unbranched elevated metro. Regular viaduct components remain individually reusable.
for i in range(math.ceil(2140/60)):
    x=-120+i*2140/math.ceil(2140/60);xx=-120+(i+1)*2140/math.ceil(2140/60)
    cube('M01_Viaduct_Module',((x+xx)/2,56,-370),(xx-x,4,24),M['concrete'],'Elevated Metro')
    for z in [-377,-363]:
        for side in [-1,1]:cube('Metro_Rail',((x+xx)/2,59.7,z+side*2),(xx-x,.6,.55),M['rail'],'Elevated Metro')
        for tx in range(math.ceil(x/12)*12,math.floor(xx/12)*12+1,12):
            cube('Metro_Sleeper',(tx,58.5,z),(1.2,1,6),M['rail'],'Elevated Metro')
    for z in [-381.5,-358.5]:cube('Metro_Parapet',((x+xx)/2,59.3,z),(xx-x,2.6,.7),M['parapet'],'Elevated Metro')
xs=[x for x in range(-110,1811,60) if x not in [370,430,1210,1270]]+[330,410,1230,1310,1818,1922,1982,2020]
xs=sorted(set(xs))
for x in xs:
    support('Metro_Median_Pier',x,-370,54,4,5,'Elevated Metro');INFRA['metro_supports'].append([x,54,-370])
    cube('Metro_Transverse_Head',(x,52.5,-370),(6,3,24),M['concrete'],'Elevated Metro')
cube('Metro_Flyover_Crossing_TransferGirder',(1870,51,-370),(104,6,10),M['concrete'],'Elevated Metro')

# Stage A station volumes only: platforms, canopy shells, access stairs, lift reservations.
for s in D['metro']['stations']:
    x,_,z=s['position'];length=s['length'];prefix=s['id']+'_'+s['name'].replace(' ','_')
    for side in [-1,1]:
        cube(prefix+'_Platform',(x,60.55,z+side*17.5),(length,1.5,9),M['station'],'Metro Stations')
        cube(prefix+'_Canopy',(x,82,z+side*17.5),(length+6,2,11),M['roof'],'Metro Stations')
        for dx in [-length/2+12,0,length/2-12]:
            cube(prefix+'_Canopy_Post',(x+dx,71,z+side*21),(1.2,20,1.2),M['station'],'Metro Stations')
        # Columns outside the ground boulevard and sidewalks, carrying the station deck.
        for dx in [-length/2+20,length/2-20]:
            support(prefix+'_Portal_Column',x+dx,z+side*39,53,4,4,'Metro Stations')
        cx=x+side*(length/2-18);cz=z+side*50
        # Three double-flight levels. The greybox omits individual treads and finishes.
        for flight in range(6):
            level=flight//2;direction=1 if flight%2==0 else -1
            a=(cx-direction*23,flight*10.2,cz+(flight%2*2-1)*4.5)
            b=(cx+direction*23,(flight+1)*10.2,cz+(flight%2*2-1)*4.5)
            deck_segment(prefix+'_Stair_Flight',a,b,8,.7,'Metro Stations',False)
            cube(prefix+'_Landing',(b[0],b[1]-.35,cz),(5,.7,18),M['station'],'Metro Stations')
        # A compact future lift shaft is solid greybox with an explicit ID, not a working lift.
        cube(prefix+'_FUTURE_LIFT',(cx+33,30.6,cz),(8,61.2,8),M['station'],'Metro Stations')
        cube(prefix+'_Upper_Access_Concourse',(cx+3,60.8,cz),(70,1,20),M['station'],'Metro Stations')
        beam(prefix+'_Access_Bridge',(cx,60.8,cz),(cx,60.8,z+side*20),8,1,M['station'],'Metro Stations')
        cube(prefix+'_Access_Forecourt',(cx,-.1,cz),(68,.2,24),M['walk'],'District Foundations')
    for dx in [-length/2+20,length/2-20]:
        cube(prefix+'_Station_Portal_Head',(x+dx,52,-370),(6,3,82),M['concrete'],'Metro Stations')
    # Wayfinding lies beside the station so roof volumes remain uncluttered.
    text(prefix+'_Label',s['id']+'  '+s['name'].upper(),(x,1,z-85),14)

# Destination access: descend beside the campus, never lower an entire city street.
dak=[]
for i in range(15):
    t=i/14;dak.append([-435,-7.7*(.5-.5*math.cos(math.pi*t)),-1160+160*t])
dak.extend([[-435,-7.7,-910],[-459,-7.7,-910]])
for i,(a,b) in enumerate(zip(dak,dak[1:])):deck_segment('Dakshineshwar_Lower_Access_'+str(i),a,b,16,1,'Road Network',False)
beam('Dakshineshwar_Arrival_Junction',(-400,-.3,-1160),(-435,-.3,-1160),20,.6,M['asphalt'],'Road Network')
INFRA['local_access'].append(dict(id='DAK_ACCESS',points=dak,width=16,max_grade_percent=round(100*7.7*math.pi/320,2),
                                rear_gate=[-459,-7.7,-910],note='One low-speed access lane and parallel pedestrian reservation; meets the existing rear gate.'))
cube('Dakshineshwar_Campus_Bank',(-542,-12.7,-910),(172,9,418),M['stone'],'Dakshineshwar Riverfront')
beam('Established_Ghat_Road_Connection',(-554,-.1,380),(-500,-.1,380),22,.2,M['walk'],'Road Network')

# Compact, legible civic spaces instead of filler buildings in the prestige zone.
cube('Bridge_Reveal_Civic_Promenade',(110,-.1,-75),(610,.2,92),M['walk'],'District Foundations')
cube('Victoria_West_Approach_Square',(365,-.1,0),(125,.2,140),M['walk'],'District Foundations')
cube('Heritage_Civic_Garden',(100,-.2,-780),(340,.2,62),M['grass'],'District Foundations')
cube('Heritage_Reflecting_Basin',(100,0,-780),(180,.1,30),M['water'],'District Foundations')
cube('Hotel_Shared_Promenade',(1510,-.1,-330),(570,.2,20),M['walk'],'District Foundations')
cube('Museum_Market_Forum',(1400,-.15,735),(350,.2,42),M['walk'],'District Foundations')
cube('Cultural_Community_Lawn',(80,-.2,950),(380,.2,140),M['grass'],'District Foundations')
paths=[('VM_West',[(-230,.1,0),(510,.1,0)],16),
       ('TownHall_Front',[(80,.1,-490),(80,.1,-404)],12),
       ('Metropolitan_Front',[(600,.1,-480),(600,.1,-404)],12),
       ('Rajbari_Front',[(70,.1,730),(70,.1,798)],14),
       ('Jorasanko_West',[(392,.1,794),(492,.1,794)],14),
       ('Jorasanko_South',[(590,.1,582),(590,.1,642)],14),
       ('Museum_Front',[(1400,.1,679),(1400,.1,756)],16),
       ('Market_Front',[(1400,.1,838),(1400,.1,804)],16),
       ('Cathedral_Front',[(1730,.1,474),(1730,.1,402)],14)]
for name,pts,w in paths:line('Path_'+name,pts,w,M['walk'],'Road Network')

# Retain suitable existing Tier3 placements ONLY outside the premium square.
# Their historical positions are evidence of continuity, not permission to move the live world.
legacy=json.loads((ROOT/'authoring/task006/world-plan.json').read_text())['placements']
legacy_rows=[];loaded={}
for r in legacy:
    if r['kind']!='residential' or r['position'][0]>=-310:continue
    if -330<r['position'][2]<100:continue # preserve the proposed historic bridge reveal corridor
    meta=next((ROOT/'assets/kolkata/tier3').glob('*/'+r['assetId']+'/asset.json'),None)
    if not meta:continue
    md=json.loads(meta.read_text());x,y,z=r['position']
    size=md['dimensionsStuds'];pad=max(size['width'],size['depth'])/2
    if x+pad>=-280 or (z<-660 and x>-460) or abs(z+370)<pad+40 or abs(z)<pad+35:continue
    if abs(z-370)<pad+35 or abs(z-1070)<pad+35:continue
    key=r['assetId']
    if key not in loaded:
        path=meta.parent/(key+'.blend')
        with bpy.data.libraries.load(str(path),link=True,relative=True) as (src,dst):dst.collections=src.collections
        wrap=bpy.data.collections.new('CONTEXT_LINK_'+key)
        names=set()
        for c in dst.collections:
            if 'presentation' in c.name.lower() or 'collision' in c.name.lower():continue
            for ob in c.all_objects:
                if ob.type=='MESH' and not ob.hide_render and ob.name not in names:wrap.objects.link(ob);names.add(ob.name)
        loaded[key]=wrap
    ob=bpy.data.objects.new('Historical_'+r['id'],None);ob.instance_type='COLLECTION';ob.instance_collection=loaded[key]
    ob.location=B(r['position']);ob.rotation_euler.z=math.radians(r['yaw']);collection('External Legacy Context').objects.link(ob)
    legacy_rows.append(dict(id=r['id'],asset_id=key,position=r['position'],yaw=r['yaw'],source=str((meta.parent/(key+'.blend')).relative_to(ROOT)).replace('\\','/')))
D['external_legacy_context']=legacy_rows

# A restrained planting rhythm uses shared native proxy meshes, not new building assets.
def tree(x,z):
    cube('Tree_Placeholder_Trunk',(x,5,z),(1.5,10,1.5),M['trunk'],'District Foundations')
    cube('Tree_Placeholder_Canopy',(x,13,z),(12,12,12),M['leaf'],'District Foundations')
for x in range(-170,410,44):
    for z in [-18,18]:tree(x,z+110)
for z in range(-260,300,48):
    for x in [491,1149]:tree(x,z)
for x in range(900,1830,60):tree(x,415)

# Planning line is the ENTIRE exclusion boundary, independent of district foundation shapes.
line('PREMIUM_BOUNDARY',[(-280,.8,-1100),(1920,.8,-1100),(1920,.8,1100),(-280,.8,1100),(-280,.8,-1100)],2,M['marking'],'Planning Markers Boundaries')
for body,x,z in [('A  COLONIAL HERITAGE',230,-1030),('B  MODERN SKYLINE',1420,-1030),
                 ('C  BENGALI CULTURAL',180,1030),('D  COMMERCIAL / CULTURAL',1320,1030)]:text(body,body,(x,1,z),23)
text('VM_Label','VICTORIA MEMORIAL',(820,1,330),22)
text('Dak_Label','DAKSHINESHWAR',(-510,1,-1180),17)
text('Water_Label','HOOGHLY',(-1100,-13.1,720),40)
text('Boundary_Note','2,200 x 2,200 STUD PREMIUM CENTRE  /  NO TIER 3', (820,1,1140),23)
text('Plan_Title','KOLKATA  /  TASK 014  /  STAGE A', (820,1,-1190),30)
text('North_Arrow','N  ^',(-180,1,-1160),30)

CAMERAS={}
def camera(name,eye,target,lens=35,ortho=None):
    data=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,data);collection('Review Cameras').objects.link(o)
    o.location=B(eye);v=Vector(B(target))-o.location;o.rotation_euler=v.to_track_quat('-Z','Y').to_euler()
    data.lens=lens;data.clip_start=.5;data.clip_end=20000
    if ortho:data.type='ORTHO';data.ortho_scale=ortho
    CAMERAS[name]=o;return o
camera('01_Full_City_Top_Down',(70,4500,0),(70,0,0),ortho=4600)
camera('02_Full_City_Isometric',(-2500,2800,2550),(380,0,-40),ortho=4450)
camera('03_Howrah_Bridge_Entry',(-760,32,-200),(1100,130,-210),lens=32)
camera('04_Victoria_Surroundings',(-40,550,650),(820,35,0),lens=36)
camera('05_Modern_Skyline_Ground',(450,9,-720),(1360,160,-700),lens=26)
camera('06_Road_Flyover_Metro',(2260,180,-730),(1790,40,-370),lens=39)
camera('07_Premium_Centre_Top',(820,3500,0),(820,0,0),ortho=3500)
camera('08_Dakshineshwar_Riverfront',(-1050,300,-1290),(-530,40,-910),lens=43)
scene.camera=CAMERAS['02_Full_City_Isometric']
scene.frame_start=1;scene.frame_end=8
for frame,(name,cam) in enumerate(CAMERAS.items(),1):
    marker=scene.timeline_markers.new(name,frame=frame);marker.camera=cam
scene.frame_set(2)
scene.render.engine='BLENDER_WORKBENCH'
scene.render.resolution_x=1800;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
sh=scene.display.shading
sh.light='STUDIO';sh.color_type='MATERIAL';sh.show_shadows=False;sh.show_cavity=True
sh.cavity_type='BOTH';sh.curvature_ridge_factor=1.2;sh.curvature_valley_factor=1.0
sh.show_specular_highlight=False;sh.background_type='WORLD';sh.background_color=(.055,.065,.075)
scene.world=bpy.data.worlds.new('Planning_Background');scene.world.color=(.055,.065,.075)
scene.view_settings.view_transform='Standard'
scene.render.image_settings.file_format='PNG'
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.clip_end=20000
            area.spaces.active.shading.type='SOLID';area.spaces.active.shading.color_type='MATERIAL'
            area.spaces.active.region_3d.view_perspective='CAMERA'
D['flyovers']=INFRA['flyovers'];D['western_bridge_approach']=INFRA['west_bridge_approach'];D['destination_access']=INFRA['local_access']
D['review_cameras']={n:dict(eye_blender=list(o.location),lens=o.data.lens,type=o.data.type) for n,o in CAMERAS.items()}
(OUT/'masterplan-manifest.json').write_text(json.dumps(D,indent=2))
(OUT/'infrastructure-manifest.json').write_text(json.dumps(INFRA,indent=2))
note=bpy.data.texts.new('START_HERE_STAGE_A')
note.write('TASK014 STAGE A — PROPOSED MASTERPLAN\n\nUse Review Cameras 01–08. Numpad 0 shows current camera.\nEvery landmark is a read-only linked asset at scale 1.\nCoordinates: Roblox (X,Y,Z) = Blender (X,Z,-Y), one unit/stud.\nSee masterplan-manifest.json and README.md beside this file.\nMetro stations are PLANNING SHELLS, not detailed Tier2 assets.\nNo Studio edits. Stage B awaits user approval.\n')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Kolkata_Masterplan_Stage_A.blend'),compress=True,relative_remap=True)
print('MASTER_SAVED',len(D['placements']),'landmarks;',len(legacy_rows),'external legacy buildings;',len(scene.objects),'scene objects',flush=True)
