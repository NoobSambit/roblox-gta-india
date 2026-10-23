"""Writers' long red civic frontage, stepped pavilions and central colonnade."""
from common import *


def civic_bay(width=11,pavilion=False):
    g=G()
    # Ground register is wider, barred and rusticated, with no upper-storey
    # shutter/balcony treatment. The two upper registers remain more delicate.
    ground=window(7.3,11.8,True,False)
    for xx in [-2.7,-1.8,-.9,0,.9,1.8,2.7]:ground.box((xx,4,-.7),(.09,7.8,.2),'HeritageIron')
    ground.box((0,0,-.7),(8.2,.5,1.3),'HeritageRedLight')
    ground.box((0,12.2,-.7),(.9,1.3,.7),'HeritageCream')
    g.merge(ground.transformed((0,4,0)))
    for sign in [-1,1]:
        for yy in [4,6.5,9,11.5,14,16.5,19]:g.box((sign*4.75,yy,-.32),(1.45,.75,.85),'HeritageRedLight')
    for y,h,w,arched in [(24,13,6,True),(45,10.5,5.6,True)]:
        g.merge(window(w,h,arched,True,balcony=y==24).transformed((0,y,0)))
    for sign in [-1,1]:
        x=sign*(width/2-.6);g.box((x,32.5,.1),(.9,59,1.2),'HeritageRedLight')
        for y in [20.4,40.6,60.2]:g.box((x,y,-.35),(1.7,.7,1.8),'HeritageCream')
        # Broad foliate capitals, readable below the main cornice.
        g.merge(prism([(x-.7,57.9),(x+.7,57.9),(x+1.15,59.6),(x,60.2),(x-1.15,59.6)],.5,-.55))
        for dx in [-.75,.75]:g.merge(disk(x+dx,59.7,-.9,.35,n=8))
    for y in [3.2,19.5,39.5,59.6]:g.box((0,y,-.15),(width,.5,1),'HeritageCream')
    if pavilion:
        for y in [5,8,11,14,17]:g.box((0,y,.12),(width,.2,.55),'HeritageRedLight')
    return g


def build():
    a=HeritageAsset('writers',"Writers' Building")
    a.foundation(316,76,16)
    a.box('Main_red_envelope',(0,32,0),(314,62,62),'HeritageRed')
    a.box('Continuous_stone_base',(0,1.7,0),(316,1.8,64),'HeritageStone','00_Foundation')
    for x,w in [(-137,40),(0,64),(137,40)]:
        depth=74 if x==0 else 70;top=68 if x==0 else 66
        a.box('Pavilion_'+str(x),(x,(top+2.6)/2,-2),(w,top-2.6,depth),'HeritageRed')
    a.put('Main_cornices',cornices(314,62,[20,40.5,61.3]),section='02_Cornices')
    for x in [-94,-50,50,94]:
        g=G();g.box((x,7,-31.15),(1.3,12,1),'HeritageRedLight')
        a.put('Wing_masonry_'+str(x),g,section='02_Cornices')
    for sign in [-1,1]:
        for i in range(7):a.instance('Wing_three_register_bay',civic_bay(),(sign*(40+11*i),0,-31.1))
        for x in [sign*126,sign*137,sign*148]:a.instance('Wing_three_register_bay',civic_bay(),(x,0,-37.1))
        for i in range(5):
            p=(sign*157.1,0,-23+12*i);a.instance('Return_three_register_bay',civic_bay(width=12),p,-sign*math.pi/2,'04_Returns')
    # Five arches remain visible behind six two-storey Corinthian columns.
    for x in [-22,-11,0,11,22]:
        a.instance('Wing_three_register_bay',civic_bay(),(x,0,-39.1))
    g=G();g.box((0,21.3,-42),(64,1.4,10),'HeritageCream')
    g.box((0,60.4,-42),(64,2,10),'HeritageCream')
    g.box((0,62.5,-42),(66,2.2,11),'HeritageCream')
    for x in [-27.5,-16.5,-5.5,5.5,16.5,27.5]:
        g.box((x,11.5,-42),(3.4,19.2,6),'HeritageRedLight')
        a.instance('Giant_Corinthian_column',column(38,1.2),(x,22,-44.5),section='05_Central_Portico')
        a.collisions.append(dict(name='Central_pier',positionStuds=[x,11.5,-42],sizeStuds=[3.4,19.2,6],yaw=0))
    for x in [-22,-11,0,11,22]:
        g.arch(7.4,10.2,.65,6,(x,3,-42),'HeritageRedLight',12)
        g.arch(7.4,10.2,.16,.3,(x,3,-45.12),'HeritageCream',12)
        g.box((x,17.2,-45.3),(1,1.6,.65),'HeritageCream')
    a.put('Central_supported_entablature',g,section='05_Central_Portico')
    a.put('Central_triangular_pediment',pediment(67,64,13,-45),section='05_Central_Portico')
    g=G()
    # A restrained original civic crest, not a copy of a scanned emblem.
    g.lathe([(0,.7),(1,1.8),(2.6,1.1)],8,'HeritageGold',(0,66,-46))
    for x in [-1.2,0,1.2]:g.ellipsoid((x,70.4,-46),(1,1.4,.6),'HeritageGold',8,4)
    a.put('Central_civic_relief',g,section='05_Central_Portico')
    a.steps('Main_entry_steps',44,-40.8,2.6,count=5)
    # Separate raised roofs are essential to the pavilion/wing silhouette.
    for x,w,d,bottom,rise in [(0,64,74,68.5,11),(-137,40,70,66.5,12),(137,40,70,66.5,12),(-74,84,62,63,7),(74,84,62,63,7)]:
        a.put('Mansard_'+str(x),mansard(w,d,bottom,rise),(x,0,-2 if abs(x) in [0,137] else 0),section='06_Roofs')
        a.put('Pavilion_cornice_'+str(x),cornices(w,d,[bottom-.5],(x,0,-2 if abs(x) in [0,137] else 0)),section='02_Cornices')
        if abs(x) in [0,137]:
            g=G();crest=roof_iron(w-8)
            for sign in [-1,1]:g.merge(crest.transformed((0,bottom+rise,(-2)+sign*(d/2-6))))
            a.instance('Iron_roof_crest_'+str(w),g,(x,0,0),section='07_Roof_Ornaments')
            for dx in [-w*.3,0,w*.3]:
                dormer=G();dormer.merge(arch_fill(4.2,4.5,-.2));dormer.arch(4.2,2.4,.5,.9,(0,0,-.5),'HeritageCream',10)
                dormer.merge(prism([(-3.2,0),(3.2,0),(3.2,4.5),(0,6),(-3.2,4.5)],1,.3,'HeritageRed'))
                dormer.box((0,-.5,.4),(6.4,1.2,1.2),'HeritageRed')
                # Glazing and arch must sit in front of the red dormer body.
                a.instance('Mansard_dormer',dormer,(x+dx,bottom+1,-d/2-2.2),section='07_Roof_Ornaments')
    # Allegorical groups and urns are original simplified sculptural silhouettes.
    g=G()
    for x,h,pose in [(-14,5.8,1),(-8,7,0),(0,8,0),(8,7,1),(14,5.8,0)]:
        # A level statue plinth bears on a wedge cut to the actual pediment
        # pitch. The earlier independent height formula left the feet in air.
        edge=lambda xx:64+13*(1-abs(xx)/33.5)+.48
        xs=[x-1.2,x,x+1.2];top=max(edge(xx) for xx in xs)+.65
        wedge=[(xx,edge(xx)-.18) for xx in xs]+[(x+1.2,top),(x-1.2,top)]
        g.merge(prism(wedge,1.8,-45.4,'HeritageCream'))
        g.merge(figure(h,pose).transformed((x,top-.04,-45.4)))
    a.put('Pediment_allegorical_group',g,section='07_Roof_Ornaments')
    for x in [-153,-121,121,153]:
        statue=figure(5.5);statue.box((0,-.6,0),(2.2,1.2,1.8),'HeritageCream')
        a.instance('Pavilion_roof_statue',statue,(x,68.5,-36.8),section='07_Roof_Ornaments')
    g=G()
    for x in [-108,-72,-36,36,72,108]:
        g.box((x,64,-31),(4,.7,3),'HeritageCream')
        g.lathe([(0,.65),(.6,.45),(1.5,.85),(2.3,.6),(2.6,.25)],10,'HeritageCream',(x,64.3,-31))
    a.put('Roofline_urn_rhythm',g,section='07_Roof_Ornaments')
    # Secondary elevations retain the rhythm with far less ornamental density.
    rear=G()
    for y in [7,26,46]:rear.merge(window(4.6,9,False,False).transformed((0,y,0)))
    for x in range(-144,145,18):a.instance('Rear_three_register_bay',rear,(x,0,31.15),math.pi,'04_Returns')
    a.night=['Six central columns and pediment relief','Mansard pavilion crests and statue groups','Selected ground arches; broad facade washes rather than one light per window']
    a.save_live("Writers' Building — long red facade, pavilions and civic roofline")
    return a,a.finish()
