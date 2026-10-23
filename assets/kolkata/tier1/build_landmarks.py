"""Six original landmark interpretations from the supplied photographic brief.

Run with Blender --background --python this_file. Never modifies the live world.
"""
import bpy
import json
import math
import sys
from pathlib import Path

BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
from pipeline import Asset, Geometry, panel, ellipse, foundation, entrance, floor_band, palm_geometry


def atmosphere():
    a=Asset('atmosphere','Atmosphere Twin Towers / Deya')
    foundation(a,292,156)
    for tower,x in enumerate([-93,93]):
        name='Tower_'+str(tower+1)
        core=Geometry();core.box((0,186,9),(52,350,40),'Graphite')
        for xx in [-22,-8,9,24]:
            core.box((xx,191,-13),(1.3,360,2),'Silver')
        core.box((-13,198,-15),(5,374,4),'Graphite')
        core.box((24,198,11),(5,374,44),'Graphite')
        a.put('atmo_core',core if tower==0 else None,(x,0,8),section=name,role='TowerEnvelope')
        for level in range(35):
            pat=level%3
            a.put('atmo_floor_'+str(pat),floor_band(54,42,10,pat,'Silver') if tower==0 and level<3 else None,
                  (x,11+level*10,17),section=name)
        b=Geometry();b.box((0,0,0),(18,1,16),'Pearl')
        b.box((0,2,-7.7),(18,3.2,.45),'GlassLight')
        for s in [-1,1]:b.box((s*8.8,2,0),(.4,3.2,15),'Glass')
        b.box((0,2.5,7),(18,4,1),'Leaf')
        for level in range(3,35,3):
            a.put('atmo_terrace',b if tower==0 and level==3 else None,(x+(-19 if tower==0 else 19),11+level*10,-13),section=name)
        crown=Geometry()
        for xx in [-24,-13,13,24]:
            crown.box((xx,370,9),(2.1,27,42),'Silver')
        crown.box((0,384,9),(52,1.2,43),'Silver')
        for xx in range(-22,25,4):crown.beam((xx,385,-12),(xx+1.5,390,29),.26,'Silver',4)
        crown.box((0,384.9,-13),(52,.25,.3),'Accent')
        a.put('atmo_crown',crown if tower==0 else None,(x,0,8),section=name)
    # The supplied Deya images show deep rounded lobes, a pinched waist,
    # perforated silver skin and a raised oval pool, not a flat footbridge.
    bridge=Geometry();steps=64;half=98;deck_y=329
    def profile(x):
        s=(x+half)/(2*half)
        lobes=math.sin(s*math.tau)**2
        width=max(7,math.sin(s*math.pi)**.4*(16+20*lobes))
        thickness=29+5*lobes
        return width,thickness
    def skin(x,t,offset=0):
        r,h=profile(x)
        return (x,deck_y-(h+offset)*math.sin(t),8+(r+offset)*math.cos(t))
    strips=[]
    for i in range(steps+1):
        x=-half+2*half*i/steps
        strips.append([skin(x,j*math.pi/16) for j in range(17)])
    for i in range(steps):
        for j in range(16):bridge.polygon([strips[i][j],strips[i+1][j],strips[i+1][j+1],strips[i][j+1]],'Silver',True)
        bridge.polygon([strips[i][0],strips[i][-1],strips[i+1][-1],strips[i+1][0]],'Paving')
        for j in [0,16]:bridge.beam(strips[i][j],strips[i+1][j],.3,'Accent',5)
        # Sparse contour ribs retain the engineered skin at medium distance.
        if i%4==0:
            x=-half+2*half*i/steps
            for j in range(16):bridge.beam(skin(x,j*math.pi/16,.35),skin(x,(j+1)*math.pi/16,.35),.19,'Pearl',4)
    bridge.polygon(list(reversed(strips[0])),'Silver');bridge.polygon(strips[-1],'Silver')
    # Geometric dark slots suggest perforations without alpha textures or
    # thousands of individually framed openings. Clear offset avoids z-fighting.
    for row in range(10):
        t=.24+row*.27
        for col in range(47):
            x=-89+col*3.8+(row%2)*1.5
            if x>90:continue
            bridge.polygon([skin(x-.7,t-.024,.52),skin(x+.7,t-.024,.52),skin(x+.7,t+.024,.52),skin(x-.7,t+.024,.52)],'Graphite')
    # One continuous landscaped sky deck, two raised timber terraces and an
    # elliptical pool wrapping a central island, as in the user references.
    for x in [-50,50]:
        ellipse(bridge,(x,329.5,8),24,23,.65,'Leaf',40)
        ellipse(bridge,(x,330.3,12),13,12,1.4,'Louvre',32)
        ellipse(bridge,(x,331.15,12),11.5,10.5,.3,'Paving',32)
        for angle in range(0,360,45):
            t=math.radians(angle)
            bridge.cylinder((x+10*math.cos(t),332.5,12+9*math.sin(t)),.22,2.5,'Bronze',5)
    ellipse(bridge,(0,331,8),31,17,3,'Stone',56)
    ellipse(bridge,(0,332.65,8),29,15,.3,'Water',56)
    ellipse(bridge,(0,333.2,8),18,7,1,'Paving',48)
    ellipse(bridge,(0,334,8),10,3,1,'Leaf',32)
    # Short curved glass guard on the outer pool edge; opaque blue tint keeps
    # Roblox sorting and export simple while retaining the crown silhouette.
    for i in range(56):
        t=i*math.tau/56;u=(i+1)*math.tau/56
        p=(30*math.cos(t),334.2,8+16*math.sin(t));q=(30*math.cos(u),334.2,8+16*math.sin(u))
        bridge.beam(p,q,.16,'Silver',4)
    a.put('Deya_cloud_and_skygarden',bridge,section='Deya_Skybridge')
    for x in [-65,-39,39,65]:a.put('palm',None,(x,331,12),section='Deya_Skybridge')
    pod=Geometry();pod.box((0,8,22),(226,13,50),'Graphite')
    for xx in range(-108,109,9):
        panel(pod,xx,8,-3.1,7.5,10,'GlassLight');pod.box((xx+4,8,-4),(1,14,1.5),'Silver')
    pod.box((0,15.5,22),(232,1.5,56),'Pearl')
    entrance(pod,0,-16,54,h=15)
    a.put('atmo_podium_arrival',pod,section='Podium',role='PodiumEnvelope')
    a.text('ATMOSPHERE',(0,17,-27),4,70,section='Podium')
    a.sockets['ExteriorEntrance']={'positionStuds':[0,1.3,-20],'clearHeightStuds':14}
    return a.finish()


def trump():
    a=Asset('trump','Trump Tower Kolkata')
    foundation(a,142,132)
    core=Geometry();core.box((0,170,12),(48,324,40),'Graphite')
    core.box((6,176,-10),(5,342,3),'Bronze')
    core.box((21,174,12),(5,338,42),'Graphite')
    for xx in [-24,-14,-4,12,24]:core.box((xx,170,-9.6),(.35,324,.4),'Silver')
    a.put('trump_stepped_glass_core',core,section='Tower',role='TowerEnvelope')
    for level in range(32):
        pat=level%4
        a.put('trump_glass_floor_'+str(pat),floor_band(48,40,10,pat,'Graphite',False,6) if level<4 else None,(0,9+level*10,12),section='Tower')
        bars=Geometry();bars.box((0,0,-20.3),(48,.48,.5),'Silver')
        bars.box((0,0,20.3),(48,.48,.5),'Silver')
        for xx in [-24.3,24.3]:bars.box((xx,0,0),(.5,.48,40),'Silver')
        a.put('trump_floor_rail',bars if level==0 else None,(0,9+level*10,12),section='Tower')
        if level%4==3:
            g=Geometry();g.box((-10,0,-22),(25,.6,3.5),'Graphite');g.box((17,0,-20),(14,.6,2),'Graphite')
            a.put('trump_projecting_ledge',g if level==3 else None,(0,9+level*10,12),section='Tower')
    crown=Geometry();crown.box((7,340,13),(7,22,38),'Bronze')
    for xx in [-24,24]:crown.box((xx,338,12),(.75,18,41),'Silver')
    for zz in [-8,32]:crown.box((0,348,zz),(49,.8,.8),'Silver')
    for xx in range(-24,25,6):crown.box((xx,348,12),(.45,.6,40),'Silver')
    crown.box((0,349,-8),(49,.3,.4),'Accent')
    a.put('trump_open_roof_pergola',crown,section='Crown')
    a.text('TRUMP',(7,341,-9.8),3.3,23,section='Crown')
    pod=Geometry();pod.box((0,6,16),(78,9,52),'Graphite')
    pod.box((0,11,16),(82,1.1,56),'Bronze');entrance(pod,0,-16,36,h=12,material='Graphite')
    for xx in [-31,31]:pod.box((xx,4.5,-41),(16,7,2.6),'Graphite')
    pod.box((-31,8,-41),(16,.3,3),'Accent')
    a.put('trump_black_stone_arrival',pod,section='Podium',role='PodiumEnvelope')
    a.text('TRUMP TOWER',(-31,5,-42.5),1.7,14,section='Podium')
    return a.finish()


def urbana():
    from landmark_refinements import urbana as refined
    return refined()


def pediment(g,x,y,z,w,h,d,mat='PaleStone'):
    p=[(x-w/2,y,z-d/2),(x+w/2,y,z-d/2),(x,y+h,z-d/2),
       (x-w/2,y,z+d/2),(x+w/2,y,z+d/2),(x,y+h,z+d/2)]
    for f in [(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)]:g.polygon([p[i] for i in f],mat)


def royal():
    # The accepted hero is maintained in its staged generator.
    import royal_bengal
    royal_bengal.begin();royal_bengal.facades();royal_bengal.signature()
    royal_bengal.arrival()
    return royal_bengal.finish()


def sonar():
    from landmark_refinements import sonar as refined
    return refined()


def marriott():
    from landmark_refinements import marriott as refined
    return refined()


if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    builders={'atmosphere':atmosphere,'trump':trump,'urbana':urbana,'royal':royal,'sonar':sonar,'jw':marriott}
    rows=[]
    for key in args or builders:
        rows.append(builders[key]())
    path=BASE/'batch-manifest.json'
    old=json.loads(path.read_text(encoding='utf8')) if path.exists() else []
    changed={r['assetId'] for r in rows}
    rows=[r for r in old if r['assetId'] not in changed]+rows
    path.write_text(json.dumps(rows,indent=2),encoding='utf8')
    print('BATCH SAVED',flush=True)
