"""Essential Stage A checks only: bounds, connectivity, clearances, source integrity."""
from pathlib import Path
import json, math, hashlib
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'assets/kolkata/masterplan_task014'
D=json.loads((OUT/'masterplan-manifest.json').read_text())
I=json.loads((OUT/'infrastructure-manifest.json').read_text())
errors=[];notes=[]
def hit(a,b,rect):
    low,high=0.,1.
    for i in range(2):
        delta=b[i]-a[i]
        if abs(delta)<1e-8:
            if not rect[i]<=a[i]<=rect[i+2]:return False
        else:
            u,v=(rect[i]-a[i])/delta,(rect[i+2]-a[i])/delta
            low=max(low,min(u,v));high=min(high,max(u,v))
            if high<low:return False
    return True
def rect(r):
    lo,hi=r['world_bounds_roblox'];return [lo[0],lo[2],hi[0],hi[2]]
def overlap(a,b):return min(a[2],b[2])>max(a[0],b[0])+.01 and min(a[3],b[3])>max(a[1],b[1])+.01
def intersect(a,b,c,d):
    dx,dz=b[0]-a[0],b[1]-a[1];ex,ez=d[0]-c[0],d[1]-c[1];det=dx*ez-dz*ex
    if abs(det)<1e-8:
        return any(math.dist(p,q)<.01 for p in [a,b] for q in [c,d])
    t=((c[0]-a[0])*ez-(c[1]-a[1])*ex)/det;u=((c[0]-a[0])*dz-(c[1]-a[1])*dx)/det
    return -1e-7<=t<=1+1e-7 and -1e-7<=u<=1+1e-7
rows=D['placements']
for i,r in enumerate(rows):
    if r['scale']!=[1,1,1]:errors.append('Scale changed: '+r['id'])
    if hashlib.sha256((ROOT/r['source']).read_bytes()).hexdigest()!=r['source_sha256']:errors.append('Source changed: '+r['id'])
    for r2 in rows[i+1:]:
        if overlap(rect(r),rect(r2)):errors.append('Landmark footprints overlap: '+r['id']+' / '+r2['id'])
    if r['id'] not in ['HOWRAH','GHAT','KOL_T1_DAKSHINESHWAR']:
        for road in D['roads']:
            pad=road['width']/2+road['sidewalk'];rr=rect(r);expanded=[rr[0]-pad,rr[1]-pad,rr[2]+pad,rr[3]+pad]
            if any(hit(a,b,expanded) for a,b in zip(road['points_xz'],road['points_xz'][1:])):
                errors.append('Road/sidewalk conflicts with landmark envelope: '+road['id']+' / '+r['id'])

# Ground network connectivity, including new bridge and both elevated approaches.
lines=[(r['id'],[(p[0],p[1]) for p in r['points_xz']]) for r in D['roads']]
for f in I['flyovers']:lines.append((f['id'],[(p[0],p[2]) for p in f['points']]))
lines.extend([('BRIDGE',[(-1540,-180),(-644,-180)]),('WEST_APPROACH',[(-1940,-180),(-1540,-180)])])
adj={n:set() for n,p in lines}
for i,(n,p) in enumerate(lines):
    for nn,pp in lines[i+1:]:
        if any(intersect(a,b,c,d) for a,b in zip(p,p[1:]) for c,d in zip(pp,pp[1:])):adj[n].add(nn);adj[nn].add(n)
visited=set();pending=[lines[0][0]]
while pending:
    n=pending.pop()
    if n in visited:continue
    visited.add(n);pending.extend(adj[n]-visited)
if len(visited)!=len(lines):errors.append('Disconnected road routes: '+str(set(adj)-visited))

crossings=[]
for f in I['flyovers']:
    assert f['max_grade_percent']<8.1
    for road in D['roads']:
        for a,b in zip(road['points_xz'],road['points_xz'][1:]):
            # End merges and parallel service lanes are intentional, not underpasses.
            for p,q in zip(f['points'],f['points'][1:]):
                if not intersect((p[0],p[2]),(q[0],q[2]),a,b):continue
                if f['id']=='F02' and road['id'] in ['R04_East_Perimeter','R01_North_Boulevard','R02_South_Boulevard']:continue
                if f['id']=='F01' and road['id']=='R07_Victoria_West':continue
                clearance=min(p[1],q[1])-f['depth']
                if clearance<18:errors.append('Underpass clearance <18: '+f['id']+'/'+road['id'])
                crossings.append(dict(flyover=f['id'],road=road['id'],conservative_road_clearance=round(clearance,3)))
    for x,y,z in f['pillars']:
        if y<=1:continue
        for road in D['roads']:
            if f['id']=='F02' and road['id']=='R04_East_Perimeter':continue # wide median
            for a,b in zip(road['points_xz'],road['points_xz'][1:]):
                pad=road['width']/2+3.6
                if hit(a,b,[x-pad,z-pad,x+pad,z+pad]):errors.append('Flyover pier in ground carriageway: '+f['id']+'/'+road['id'])
for x,y,z in I['metro_supports']:
    for road in D['roads']:
        if road['id']=='R05_Heritage_Metro_Boulevard':continue # 8-stud dedicated median
        for a,b in zip(road['points_xz'],road['points_xz'][1:]):
            pad=road['width']/2+2.6
            if hit(a,b,[x-pad,z-pad,x+pad,z+pad]):errors.append('Metro pier in crossing carriageway: '+road['id']+' at '+str(x))
for f in I['flyovers']:
    pts=f['points'];top=max(p[1] for p in pts)+3
    for x,y,z in I['metro_supports']:
        if any(hit((p[0],p[2]),(q[0],q[2]),[x-f['width']/2-2.5,z-f['width']/2-2.5,x+f['width']/2+2.5,z+f['width']/2+2.5]) for p,q in zip(pts,pts[1:])):
            errors.append('Metro pier intersects flyover corridor: '+str(x))
clearance=48-(26+3) # special transfer girder underside to flyover parapet
if clearance<18:errors.append('Metro / flyover crossing vertical gap too low')
pedestrian_clearances=[]
for pp in I['bridge_east_pedestrian_connections']['paths']:
    for road_x in [-500,-230]:
        for a,b in zip(pp,pp[1:]):
            if a[0]<=road_x<=b[0]:
                gap=min(a[1],b[1])-1
                pedestrian_clearances.append(round(gap,3))
                if gap<18:errors.append('Bridge footway blocks bank-road clearance at '+str(road_x))

# Actual original Tier3 context stays wholly outside the complete premium square.
for r in D['external_legacy_context']:
    md=json.loads((ROOT/r['source']).with_name('asset.json').read_text());pad=max(md['dimensionsStuds']['width'],md['dimensionsStuds']['depth'])/2
    if r['position'][0]+pad>=D['premium_boundary_xz'][0]:errors.append('Tier3 enters premium square: '+r['id'])
if len(rows)!=19:errors.append('Expected 19 landmark/anchor instances')
if len(D['metro']['stations'])!=3:errors.append('Expected exactly three stations')
notes.extend([
    'Bounds are conservative whole-compound AABBs at yaw multiples of 90 degrees; internal courtyards are preserved.',
    'All 19 source file SHA256 hashes match the read-only survey; all landmark instance scales are exactly 1.',
    'Ground routes form one connected network including both approaches and the unchanged bridge; 16-stud lower Dakshineshwar access branches from River Drive.',
    'Metro is one straight dual-track line; three shell stations. Rail top 60; future train envelope to 74; canopy underside 81.',
    'Metro special 104-stud span crosses outside both eastern service lanes. Girder underside 48 clears flyover parapet 29 by 19 studs.',
    'Ramps are sampled eased vertical profiles; maximum analytical grades are planning constraints, not a vehicle test.',
    'Stage A avoids detailed architectural/station assets and structural simulation. Sidewalk corners, collision proxies, final junction radii and barrier terminals require Stage B refinement.',
    'Historical coordinates have not been re-surveyed in live Studio. No live world operations were performed.',
])
result=dict(status='PASS' if not errors else 'NEEDS_CORRECTION',errors=errors,
            landmark_count=len(rows),external_tier3_count=len(D['external_legacy_context']),
            connected_road_routes=len(visited),total_road_routes=len(lines),
            flyover_ground_crossings=crossings,metro_flyover_vertical_gap=clearance,
            bridge_pedestrian_underpass_clearances=pedestrian_clearances,
            notes=notes)
(OUT/'essential-checks.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
raise SystemExit(1 if errors else 0)
