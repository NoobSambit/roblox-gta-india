"""Build the original reusable Task008 kit in an isolated background Blender."""
import bpy
import json
import math
import sys
from pathlib import Path
BASE = Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
from pipeline import Asset, Geo, save_library, PALETTE

ASSETS = []
def asset(code, category, name, cap, geo, **kwargs):
    a = Asset("VIC_"+code,category,name,cap,geo,**kwargs)
    a.save()
    ASSETS.append(a)
    return a

def box(g,p,s,m):
    g.box(p,s,m)

def plinth(g,width=3.8,height=1.6,octagonal=False):
    if octagonal:
        # Faceted base silhouette instead of a dense rounded profile.
        g.lathe((0,0,0),[(0,width*.46),(.18,width*.46),(.28,width*.40),(height-.32,width*.40),(height-.18,width*.46),(height,width*.46)],"Charcoal",8)
        g.lathe((0,0,0),[(height-.26,width*.43),(height-.17,width*.43)],"Brass",8)
    else:
        for y,h,w,m in [(.12,.24,width,"Charcoal"),(.77,1.06,width-.25,"Charcoal"),(1.35,.10,width-.20,"Brass"),(1.50,.20,width,"Ivory")]:
            box(g,(0,y,0),(w,h,w),m)

def frame(g,width=3.6,height=2.7,base=0):
    box(g,(0,base+height/2,.08),(width,height,.12),"Charcoal")
    for x in [-1,1]: box(g,(x*(width/2-.09),base+height/2,-.06),(.18,height,.24),"Brass")
    for y in [base+.09,base+height-.09]: box(g,(0,y,-.06),(width-.36,.18,.24),"Brass")
    box(g,(0,base+height/2,-.065),(width-.40,height-.40,.045),"Canvas:Paper")

def case(g,width=3.8,height=5.0,depth=None,premium=False):
    depth = depth or width
    # Compact complete support replaces a greybox pedestal, never stacks over it.
    box(g,(0,.12,0),(width,.24,depth),"Charcoal")
    box(g,(0,.87,0),(width-.18,1.26,depth-.18),"Charcoal")
    box(g,(0,1.54,0),(width,.08,depth),"Brass")
    box(g,(0,1.65,0),(width-.20,.14,depth-.20),"Ivory")
    top, bottom = height-.12, 1.73
    innerW,innerD = width-.24,depth-.24
    for x in [-1,1]:
        for z in [-1,1]:box(g,(x*(innerW/2-.06),(top+bottom)/2,z*(innerD/2-.06)),(.12,top-bottom,.12),"Brass")
    for y in [bottom,top]:
        for z in [-1,1]:box(g,(0,y,z*(innerD/2-.06)),(innerW,.12,.12),"Brass")
        for x in [-1,1]:box(g,(x*(innerW/2-.06),y,0),(.12,.12,innerD-.24),"Brass")
    for x in [-1,1]:box(g,(x*(innerW/2-.09),(top+bottom)/2,0),(.035,top-bottom-.12,innerD-.24),"Glass")
    for z in [-1,1]:box(g,(0,(top+bottom)/2,z*(innerD/2-.09)),(innerW-.24,top-bottom-.12,.035),"Glass")
    box(g,(0,top-.04,0),(innerW-.24,.035,innerD-.24),"Glass")
    box(g,(0,.96,-depth/2+.025),(.78,.38,.05),"Brass")
    if premium:
        # Broad corner guards and one service lock, all within the 6-stud reservation.
        for x in [-1,1]:
            for z in [-1,1]:box(g,(x*(width/2-.18),.87,z*(depth/2-.18)),(.25,1.25,.25),"Brass")
        for x in [-1,1]:box(g,(x*(width/2-.18),height-.23,0),(.28,.22,depth),"Charcoal")
        box(g,(0,1.25,-depth/2-.035),(.48,.42,.08),"Oxblood")

def architecture():
    g=Geo();g.column(0,0,0,14,.62,"Ivory",8)
    for y in [1.2,12.5]:g.cylinder((0,y,0),.72,.12,"Brass",8)
    asset("A01_COLUMN", "Architecture","Simple 8-sided column",350,g,note="Optional library piece; existing landmark columns are reused, not replaced")
    g=Geo()
    for p,s,m in [((0,.2,0),(1.5,.4,.65),"Stone"),((0,6.7,.04),(1.05,12.6,.42),"Ivory"),((0,13.4,0),(1.7,.4,.75),"Ivory"),((0,1.2,-.23),(1.15,.12,.08),"Brass"),((0,12.7,-.23),(1.15,.12,.08),"Brass")]:box(g,p,s,m)
    asset("A02_PILASTER","Architecture","Shallow partition pilaster",150,g,pivot="Wall-foot centre; back +Z")
    g=Geo();g.arch((0,0,0),10,9,.55,.32,"Ivory",10)
    g.arch((0,0,-.19),10.12,9,.10,.06,"Brass",10)
    # Fill the rectangular greybox opening outside the curved crown. Without
    # these two spandrels the old square aperture remains visible as wall gaps.
    outer_radius=5.55
    right=[(outer_radius*math.cos(i*math.pi/10),9+outer_radius*math.sin(i*math.pi/10)) for i in range(6)]
    right += [(0,14.8),(5.8,14.8),(5.8,9)]
    for sign in [-1,1]:
        g.extrude([(sign*x,y) for x,y in right],.24,(0,0,.10),"Stone")
    asset("A03_ARCH_10","Architecture","10-stud-clear arch with spandrel infill",350,g,note="14-stud inner apex; ten-stud width below nine-stud spring. Matching spandrels close square-aperture corners above avatar clearance; visual only")
    g=Geo()
    for y,h,d,m in [(.12,.24,.24,"Stone"),(.6,.72,.12,"Stone"),(1.02,.12,.22,"Ivory"),(1.12,.08,.18,"Brass")]:box(g,(0,y,0),(8,h,d),m)
    asset("A04_DADO_8","Architecture","8-stud dado strip",150,g,pivot="Wall-foot centre")
    g=Geo()
    for y,w,d,m in [(.12,8,.18,"Stone"),(.35,8,.26,"Ivory"),(.53,8,.38,"Ivory"),(.66,8,.50,"Ivory"),(.75,8,.40,"Brass")]:box(g,(0,y,0),(w,.16,d),m)
    asset("A05_CORNICE_8","Architecture","8-stud stepped cornice",150,g,pivot="Lower wall-mount centre")
    g=Geo();plinth(g)
    box(g,(0,.86,-1.80),(.7,.32,.04),"Brass")
    asset("A06_PLINTH_SQUARE","Architecture","Square exhibit plinth",180,g,sockets={"ExhibitMount":(0,1.6,0)})
    g=Geo();plinth(g,3.8,1.6,True)
    asset("A07_PLINTH_OCTAGON","Architecture","Octagonal exhibit plinth",180,g,sockets={"ExhibitMount":(0,1.6,0)})
    g=Geo()
    for x in [-1.8,1.8]:
        g.cylinder((x,.12,0),.30,.24,"Charcoal",6)
        g.cylinder((x,1.15,0),.11,2.1,"Brass",6)
    for y in [.9,1.9]:box(g,(0,y,0),(3.6,.10,.10),"Charcoal")
    asset("A08_BARRIER_4","Architecture","Low 4-stud museum barrier",200,g,note="Optional only; never span an approved route")
    g=Geo()
    for x in [-5.25,5.25]:
        box(g,(x,7.15,0),(.5,14.3,.26),"Charcoal")
        box(g,(x,7.2,-.15),(.18,14.0,.06),"Oxblood")
    box(g,(0,14.3,0),(11,.35,.26),"Charcoal")
    box(g,(0,14.3,-.16),(2.6,.18,.05),"Amber")
    asset("A09_RESTRICTED_PORTAL","Architecture","10-stud restricted doorway overlay",150,g,pivot="Opening ground-centre; front -Z",note="Non-colliding overlay; no new door or changed aperture")
    # A slim support leaves a visible gap to the approved vault feet beside
    # VIC_LOOT_002, without changing that marker or the original architecture.
    g=Geo();plinth(g,3.6)
    box(g,(0,3.7,.15),(3.55,4.2,.28),"Charcoal")
    box(g,(0,5.74,-.08),(2.8,.16,.32),"Brass")
    asset("A10_FEATURE_PANEL","Architecture","Compact freestanding painting panel",150,g,sockets={"FrameMount":(0,2.15,-.04),"ArtworkMount":(0,2.37,-.23)},note="4-stud support envelope; replaces original pedestal")
    g=Geo()
    box(g,(0,3,0),(2.6,6,.12),"Teal")
    for y in [.10,5.90]:box(g,(0,y,-.08),(2.85,.20,.18),"Brass")
    box(g,(0,.55,-.075),(1.9,.08,.035),"Brass")
    asset("A11_MUSEUM_BANNER","Architecture","Plain teal heritage wall banner",150,g,pivot="Lower wall-mount centre; front -Z",note="Broad colour accent only, not sculpted painting artwork; mount above and outside circulation")
    g=Geo()
    box(g,(0,.012,0),(8,.024,6),"Teal")
    for z in [-2.94,2.94]:box(g,(0,.028,z),(8,.02,.10),"Brass")
    for z in [-2.67,2.67]:box(g,(0,.028,z),(8,.02,.06),"Ivory")
    asset("A12_FLOOR_RUNNER_8","Architecture","8-stud flat museum runner",150,g,note="0.038-stud high non-colliding floor colour insert; no raised threshold or gameplay obstacle")

def exhibition():
    for code,label,w,h,prem,cap in [
        ("E01_CASE_SMALL","Small display case",3.6,4.8,False,300),
        ("E02_CASE_MEDIUM","Medium display case",4.0,5.6,False,450),
        ("E03_CASE_PREMIUM","Premium protected case",5.6,6.2,True,700)]:
        g=Geo();case(g,w,h,premium=prem)
        asset(code,"Exhibition",label,cap,g,sockets={"ExhibitMount":(0,1.72,0)},note="Glass exported separately; map its transparency in Studio")
    for code,name,w,h in [("E04_FRAME_LANDSCAPE","3:2 landscape frame",3.5,2.466666667),("E05_FRAME_PORTRAIT","Portrait frame",2.7,3.5)]:
        g=Geo();frame(g,w,h)
        asset(code,"Exhibition",name,120,g,pivot="Lower frame edge centre; mount front -Z")
    g=Geo()
    for x in [-1.35,1.35]:box(g,(x,1,0),(.25,2,2.2),"Charcoal")
    box(g,(0,2.05,0),(3.8,.20,2.8),"Charcoal")
    for x in [-1,1]:box(g,(x*1.8,2.28,0),(.14,.25,2.8),"Brass")
    for z in [-1.3,1.3]:box(g,(0,2.28,z),(3.6,.25,.14),"Brass")
    box(g,(0,2.25,0),(3.35,.04,2.35),"Paper")
    box(g,(0,3.25,1.2),(3.6,1.8,.035),"Glass")
    box(g,(0,2.47,-1.42),(1.4,.22,.06),"Teal")
    asset("E06_DOCUMENT_DESK","Exhibition","Open-front document display",220,g,sockets={"ExhibitMount":(0,2.31,0)},note="Compact readable desk; front open for display, no blocking transparent cube")
    g=Geo()
    for p,s,m in [((0,.15,0),(3.8,.3,1.1),"Charcoal"),((0,2.9,.12),(3.6,5.5,.8),"Teal"),((0,5.72,0),(3.9,.20,1.2),"Charcoal"),((0,2.9,-.32),(.12,5.3,.08),"Brass")]:box(g,p,s,m)
    for x in [-.88,.88]:
        for y in [1.05,2.3,3.55,4.8]:
            box(g,(x,y,-.32),(1.6,1.1,.08),"Charcoal")
            box(g,(x,y,-.40),(.45,.08,.10),"Brass")
    asset("E07_ARCHIVE_CABINET","Exhibition","Shallow secure archive cabinet",350,g,note="Optional wall dressing only; 1.2-stud depth, keep outside reserved lanes")
    g=Geo()
    box(g,(0,.12,0),(1.8,.24,1.5),"Charcoal")
    box(g,(0,1.55,.1),(.42,2.85,.4),"Charcoal")
    # Closed sloped lectern profile; broad screen plane, no tiny text.
    g.extrude([(-.6,2.9),(.6,3.35),(.6,3.52),(-.6,3.07)],2.0,(0,0,0),"Brass",math.pi/2)
    top=[(-.8,3.50,-.5),(.8,3.50,-.5),(.8,3.125,.5),(-.8,3.125,.5)]
    g.solid(top+[(x,y-.015,z) for x,y,z in top],[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],"Teal")
    asset("E08_INFO_STAND","Exhibition","Museum information stand",180,g)
    g=Geo()
    for p,s,m in [((0,.5,.04),(1.8,1,.12),"Brass"),((0,.5,-.04),(1.55,.75,.05),"Teal"),((0,.6,-.075),(1.1,.08,.025),"Ivory"),((0,.37,-.075),(.7,.06,.025),"Ivory")]:box(g,p,s,m)
    asset("E09_PLAQUE","Exhibition","Plain reusable information plaque",100,g,pivot="Lower wall-mount centre; front -Z")
    g=Geo()
    for x in [-1.8,1.8]:box(g,(x,2.8,0),(.2,5.6,1.5),"Charcoal")
    box(g,(0,2.8,.72),(3.8,5.6,.12),"Teal")
    for y in [.15,1.9,3.7,5.45]:box(g,(0,y,0),(3.8,.2,1.5),"Charcoal")
    for y in [1.1,2.85,4.6]:
        for x in [-1.1,1.1]:
            box(g,(x,y,.08),(1.25,1.15,1.05),"Paper")
            box(g,(x,y,-.47),(.58,.22,.05),"Teal")
    asset("E10_ARCHIVE_SHELF","Exhibition","Simple closed-box archive shelving",350,g,note="Optional off-route dressing; no loose book clutter")

def loot():
    g=Geo()
    for y,w,d,m in [(.07,2.6,1.9,"Oxblood"),(.17,2.45,1.72,"Paper"),(.28,2.6,1.9,"Paper"),(.34,.24,1.92,"Brass")]:box(g,(0,y,0),(w,.10,d),m)
    for x in [-.7,.5]:box(g,(x,.345,-.2),(.6,.025,.15),"Ink")
    asset("L01_FOLIO","Loot","Common folded folio",120,g)
    g=Geo()
    box(g,(0,.08,0),(2.2,.16,1.45),"Paper")
    g.extrude([(-1.1,.17),(0,.7),(1.1,.17)],.10,(0,0,-.12),"Paper")
    box(g,(0,.24,-.78),(.28,.26,.08),"Oxblood")
    asset("L02_LETTER","Loot","Common correspondence packet",120,g)
    g=Geo()
    for x in [-.8,.8]:
        g.lathe((x,0,0),[(0,.35),(.15,.45),(.65,.4),(.8,.2),(1.1,.26),(1.22,.26)],"Bronze",8)
    box(g,(0,.12,0),(2.6,.24,1.45),"Teal")
    asset("L05_TRADE_COLLECTION","Loot","Fictional trade collection",260,g)
    g=Geo()
    g.arch((-.25,.15,0),1.5,.55,.28,.4,"Bronze",6)
    other=Geo();other.arch((0,.2,0),1.4,.75,.25,.4,"Brass",6)
    g.merge(other,(.2,0,0),math.pi/2)
    box(g,(0,.08,0),(2.5,.16,1.8),"Charcoal")
    asset("L06_ABSTRACT_BRONZE","Loot","Interlocking faceted abstract bronze",260,g)
    g=Geo()
    box(g,(0,.12,0),(2.6,.24,1.8),"Teal")
    for x in [-.75,0,.75]:
        g.lathe((x,.24,0),[(0,.26),(.15,.32),(.32,.2),(.55,.26),(.65,.26)],"Brass",6)
    asset("L07_PRESENTATION_SET","Loot","Fictional presentation set",260,g)
    g=Geo()
    g.lathe((0,0,0),[(0,.38),(.13,.55),(.25,.55),(.38,.32),(.65,.40),(1.1,.72),(1.4,.64),(1.65,.38),(1.85,.42),(1.98,.42)],"Bronze",10)
    for x in [-.76,.76]:
        h=Geo();h.arch((0,0,0),.50,.18,.12,.16,"Brass",4)
        g.merge(h,(x,.78,0),math.pi/2)
    asset("L08_CEREMONIAL_VESSEL","Loot","Fictional ceremonial vessel",350,g)
    g=Geo()
    g.lathe((0,0,0),[(0,.62),(.18,.62),(.3,.5),(.45,.7),(.85,.8),(1.15,.6),(1.28,.6)],"Brass",10)
    box(g,(0,.75,-.76),(.62,.48,.1),"Teal")
    box(g,(0,1.4,0),(.35,.25,.35),"Gem")
    asset("L09_KEEPSAKE","Loot","Fictional ceremonial keepsake",350,g)
    g=Geo()
    box(g,(0,.1,0),(2.6,.2,1.7),"Charcoal")
    box(g,(0,.3,0),(1.5,.2,1.1),"Brass")
    for x in [-.5,.5]:g.beam((x,.4,0),(x,1,0),.13,.13,"Brass")
    points=[]
    for i in range(16):
        a=math.pi/2+i*math.tau/16;r=1.05 if i%2==0 else .70
        points.append((math.cos(a)*r,1.7+math.sin(a)*r))
    g.extrude(points,.18,(0,0,0),"Brass")
    diamond=[(0,1.08),(.42,1.7),(0,2.32),(-.42,1.7)]
    g.extrude(diamond,.15,(0,0,-.18),"Gem")
    for i in range(8):
        a=i*math.tau/8;cx,cy=.82*math.cos(a),1.7+.82*math.sin(a)
        g.extrude([(cx,cy+.13),(cx+.10,cy),(cx,cy-.13),(cx-.10,cy)],.07,(0,0,-.14),"Teal")
    asset("L10_PREMIUM_INSIGNIA","Loot","Fictional jewelled insignia",600,g,note="Hero silhouette gets broad facets, not filigree")
    g=Geo()
    for y,w,d,m in [(.07,2.7,2,"Oxblood"),(.18,2.48,1.8,"Paper"),(.30,2.7,2,"Oxblood")]:box(g,(0,y,0),(w,.12,d),m)
    for x in [-1.15,1.15]:
        for z in [-.8,.8]:
            box(g,(x,.40,z),(.35,.08,.12),"Brass")
            box(g,(x,.40,z),(.12,.08,.35),"Brass")
    for x in [-1.25,1.25]:box(g,(x,.39,0),(.10,.08,1.6),"Brass")
    for z in [-.9,.9]:box(g,(0,.39,z),(2.5,.08,.10),"Brass")
    box(g,(0,.42,0),(.30,.10,1.8),"Brass")
    g.extrude([(-.35,0),(0,-.25),(.35,0),(0,.25)],.12,(0,.5,0),"Gem")
    asset("L11_RARE_ARCHIVE_FOLIO","Loot","Premium archive folio",600,g)
    g=Geo()
    box(g,(0,.12,0),(2.5,.24,1.7),"Stone")
    for x in [-.7,.7]:box(g,(x,.65,0),(.65,.85,.75),"Ivory")
    box(g,(0,.55,0),(.5,.65,.75),"Ivory")
    g.lathe((0,0,0),[(.86,.43),(1.05,.43),(1.4,.30),(1.55,.14)],"Ivory",8)
    asset("L12_MINIATURE","Loot","Fictional architectural miniature",180,g,note="Broad pavilion silhouette; not a detailed landmark replica")
    g=Geo()
    for x,y,w,d,m in [(-.35,.06,2.1,1.7,"Teal"),(.35,.22,2.0,1.7,"Paper"),(-.2,.38,2.1,1.7,"Paper")]:box(g,(x,y,0),(w,.12,d),m)
    for x in [-.7,.15,.8]:box(g,(x,.46,-.1),(.28,.035,1.1),"Brass")
    asset("L14_RIVER_PORTFOLIO","Loot","Fictional river-trade portfolio",260,g)

def security():
    g=Geo()
    g.plan([(-.18,-.26),(.18,-.26),(.26,-.18),(.26,.18),(.18,.26),(-.18,.26),(-.26,.18),(-.26,-.18)],.24,2.86,"Charcoal")
    for p,s,m in [((0,.12,0),(.68,.24,.68),"Charcoal"),((0,2.92,0),(.62,.16,.62),"Brass"),((0,1.55,-.275),(.17,1.65,.04),"Amber"),((0,.60,-.275),(.23,.4,.04),"Teal")]:box(g,p,s,m)
    asset("S01_STATIC_EMITTER","Security","Static laser emitter housing",100,g,sockets={"Lens":(0,1.7,-.30)},note="No beam or detection component")
    g=Geo()
    g.cylinder((0,.12,0),.72,.24,"Base:Charcoal",8)
    g.cylinder((0,1.1,0),.22,1.96,"Base:Charcoal",6)
    g.extrude([(-.625,1.875),(.625,1.875),(.725,1.975),(.725,2.525),(.625,2.625),(-.625,2.625),(-.725,2.525),(-.725,1.975)],.85,(0,0,0),"Head:Charcoal")
    box(g,(0,2.25,-.46),(1.1,.4,.08),"Head:Brass")
    box(g,(0,2.25,-.515),(.7,.18,.04),"Head:Amber")
    asset("S02_MOVING_HOUSING","Security","Pivot-ready moving-laser housing",180,g,
        component_pivots={"Head":(0,2.25,0)},sockets={"SweepAxis":(0,2.25,0),"Lens":(0,2.25,-.54)},note="Head meshes retain a shared local sweep pivot; no animation")
    g=Geo()
    box(g,(0,.025,0),(8,.05,8),"Charcoal")
    for sign in [-1,1]:
        box(g,(sign*3.9,.06,0),(.16,.04,8),"Amber")
        box(g,(0,.06,sign*3.9),(7.68,.04,.16),"Amber")
    for x in [-2.0,0,2.0]:box(g,(x,.058,0),(.08,.035,7.5),"Stone")
    box(g,(0,.08,-3.25),(1.2,.04,.42),"Oxblood")
    asset("S03_ELECTRIC_FLOOR","Security","Flush 8-stud electrical floor visual",120,g,note="0.10-stud maximum height; inactive colour inlays only")
    g=Geo()
    for p,s,m in [((0,.12,0),(1.8,.24,1.4),"Charcoal"),((0,1.65,.15),(1.3,2.85,.9),"Charcoal"),((0,3.25,0),(1.9,1.1,.7),"Charcoal"),((0,3.25,-.40),(1.65,.90,.12),"Brass"),((0,3.25,-.48),(1.40,.65,.05),"Teal"),((0,3.95,0),(1.9,.16,.7),"Charcoal"),((0,2.15,-.34),(.9,.18,.05),"Amber")]:box(g,p,s,m)
    for x in [-.45,0,.45]:box(g,(x,2.55,-.34),(.18,.12,.05),"Stone")
    for y,w in [(3.4,.85),(3.22,.6),(3.05,1.0)]:box(g,(0,y,-.515),(w,.035,.02),"Sky")
    asset("S04_TERMINAL","Security","Compact security terminal visual",350,g,sockets={"InteractionSurface":(0,3.25,-.53)},note="Blank broad UI blocks only; no hacking script")

def main():
    architecture();exhibition();loot();security()
    rows=[a.row for a in ASSETS]
    (BASE/"asset-manifest.json").write_text(json.dumps(dict(task="008",assetCount=len(rows),units="Stud / 1",palette=PALETTE,assets=rows),indent=2)+"\n")
    save_library(ASSETS)
    print(json.dumps(dict(assetCount=len(rows),triangles=sum(r['triangles'] for r in rows),categories={c:sum(r['triangles'] for r in rows if r['category']==c) for c in ['Architecture','Exhibition','Loot','Security']})),flush=True)

if __name__ == "__main__":main()
