"""File-level geometry and clearance checks. This does not replace Studio QA."""
import json
import math
from collections import Counter
from pathlib import Path

OUT=Path(__file__).resolve().parent

def sub(a,b):return [x-y for x,y in zip(a,b)]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]

def ray_distance(origin,direction,vertices):
    a,b,c=vertices;e1,e2=sub(b,a),sub(c,a)
    h=cross(direction,e2);det=dot(e1,h)
    if abs(det)<1e-8:return None
    f=1/det;s=sub(origin,a);u=f*dot(s,h)
    if not 0<=u<=1:return None
    q=cross(s,e1);v=f*dot(direction,q)
    if v<0 or u+v>1:return None
    distance=f*dot(e2,q)
    return distance if distance>1e-7 else None

def inspect():
    library=json.loads((OUT/"mesh-library.json").read_text())
    manifest=json.loads((OUT/"assembly-manifest.json").read_text())
    errors=[];counts=Counter();normal_checks={}
    for key,mesh in library.items():
        counts[mesh["template"]]+=len(mesh["triangles"])
        for index,(face,normals) in enumerate(zip(mesh["triangles"],mesh["normals"])):
            vertices=[mesh["vertices"][i] for i in face]
            if not all(math.isfinite(x) for v in vertices for x in v):errors.append(f"{key}: non-finite vertex {index}")
            area=cross(sub(vertices[1],vertices[0]),sub(vertices[2],vertices[0]))
            if dot(area,area)<1e-13:errors.append(f"{key}: degenerate triangle {index}")
            for n in normals:
                if abs(dot(n,n)-1)>.003:errors.append(f"{key}: invalid corner normal {index}")
        if key in ("InteriorDome__DomeBlue","RotundaInnerLining__Marble"):
            facing=[]
            for face in mesh["triangles"]:
                vs=[mesh["vertices"][i] for i in face]
                center=[sum(v[j] for v in vs)/3 for j in range(3)]
                normal=cross(sub(vs[1],vs[0]),sub(vs[2],vs[0]))
                radial=[center[0],0,center[2]]
                if dot(radial,radial)>4 and abs(normal[0])+abs(normal[2])>.001:facing.append(dot(normal,radial)<0)
            normal_checks[key]="inward" if all(facing) and facing else "CHECK"
            if normal_checks[key]!="inward":errors.append(f"{key}: some surfaces face outwards")
    ids=[m["id"] for m in manifest["markers"]]
    if len(ids)!=len(set(ids)):errors.append("duplicate marker id")
    for primitive in manifest["primitives"]:
        if min(primitive["size"])<=0:errors.append("invalid native primitive size: "+primitive["name"])
    # Regression: the four oculi must be embedded in attic masonry, not left
    # floating in the 50..60 stud gap between the tower body and pavilion deck.
    attic_backing={}
    tower=library["CornerTower__Marble"]
    for name,origin,direction in [("north",(0,53.3,-40),(0,0,1)),("south",(0,53.3,40),(0,0,-1)),("east",(40,53.3,0),(-1,0,0)),("west",(-40,53.3,0),(1,0,0))]:
        distances=[distance for face in tower["triangles"] if (distance:=ray_distance(origin,direction,[tower["vertices"][i] for i in face])) is not None]
        closest=min(distances) if distances else None
        attic_backing[name]=closest
        if closest is None or abs(closest-25)>.01:errors.append(f"tower attic {name}: oculus has no continuous masonry backing")
    # Broad-phase 3-stud-wide, 6-stud-high walking envelope, foot elevation 7.05.
    # Paths are at gallery/terrace elevation; ascending stairs need an engine walk.
    routes={
        "north-to-south-interior": [(0,z) for z in range(-100,101,2)],
        "east-side-escape": [(x,0) for x in range(0,137,2)],
        "west-side-escape": [(-x,0) for x in range(0,137,2)],
    }
    for sx in [-1,1]:
        for sz in [-1,1]:routes[f"gallery-door-{sx}-{sz}"]=[(sx*60,sz*z) for z in range(44,87,2)]
    clearance={}
    for route,points in routes.items():
        blockers=set()
        for x,z in points:
            for p in manifest["primitives"]:
                if not p["solid"] or abs(p["yaw"])>.0001:continue
                if p["name"]=="QueensHallCentralPlinth":continue # deliberately walk around the statue
                px,py,pz=p["position"];w,h,d=p["size"]
                if py+h/2<=7.08 or py-h/2>=13.05:continue
                if abs(x-px)<w/2+1.5 and abs(z-pz)<d/2+1.5:blockers.add(p["name"])
        clearance[route]=sorted(blockers) if blockers else "clear in authored box envelope"
        if blockers:errors.append(f"{route}: blocked by {sorted(blockers)}")
    report=dict(scope="Offline authoring checks only; Studio import, actual collision, streaming and performance pending",unique_meshes=len(library),unique_triangles=sum(counts.values()),largest_unique_mesh=max(len(v["triangles"]) for v in library.values()),module_triangles=dict(counts),inward_normal_checks=normal_checks,tower_attic_backing_distances=attic_backing,box_clearance=clearance,errors=errors)
    (OUT/"offline-audit.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
    return not errors

if __name__=="__main__":raise SystemExit(0 if inspect() else 1)
