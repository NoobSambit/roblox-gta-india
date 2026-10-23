"""Broad Town Hall portico, heavy Doric order and distinct facade registers."""
from common import *


def hall_bay():
    g=G();g.merge(arch_fill(7.2,13,-.22,'HeritageDark').transformed((0,4.2,0)))
    g.arch(7.2,9.4,.42,.7,(0,4.2,-.45),'HeritageCream',12)
    # Recessed rectangular door within the lower arched portico opening.
    g.box((0,8,-.45),(5.2,7.5,.24),'HeritageGlass')
    for x in [-2.65,0,2.65]:g.box((x,8,-.65),(.16,7.7,.24),'HeritageCream')
    upper=window(5.5,12.5,False,True,'HeritageCream')
    g.merge(upper.transformed((0,25.5,0)))
    g.box((0,38.9,-.5),(7.4,.8,1.4),'HeritageCream')
    g.box((0,40,-.1),(6.5,.3,.4),'HeritageCream')
    return g


def build():
    a=HeritageAsset('town_hall','Kolkata Town Hall')
    a.foundation(114,70,30)
    a.box('Classical_main_shell',(0,24,2),(112,44,68),'HeritageWhite')
    a.box('Raised_hall_base',(0,2.4,2),(114,3.2,70),'HeritageStone','00_Foundation')
    a.box('Deep_portico_landing',(0,2.4,-41),(88,3.2,23),'HeritageStone','00_Foundation')
    a.steps('Broad_entry_stairs',86,-52.5,4,count=9,tread=1.4)
    a.put('Hall_horizontal_cornices',cornices(112,68,[4.6,22.5,44.5],(0,0,2),'HeritageCream',dentils=False),section='02_Cornices')
    xs=[-34,-20.4,-6.8,6.8,20.4,34]
    for x in xs:
        a.instance('Doric_portico_column',column(35.6,2.05,'HeritageWhite',False),(x,4,-46.5),section='03_Portico')
        a.collisions.append(dict(name='Portico_column',positionStuds=[x,21.8,-46.5],sizeStuds=[4.2,35.6,4.2],yaw=0))
    for sign in [-1,1]:
        for z in [-37,-27]:a.instance('Doric_return_column',column(35.6,2.05,'HeritageWhite',False),(sign*34,4,z),section='03_Portico')
    g=G()
    for y,w,d,h in [(40.1,88,28,2),(42.4,89,29,3),(44.5,91,30,1.2),(45.6,92,31,.7)]:g.box((0,y,-36.8),(w,h,d),'HeritageWhite')
    for i in range(12):
        x=-40+i*80/11;g.merge(disk(x,42.4,-51.6,.9,'HeritageCream',16))
        for j in range(8):
            t=j*math.tau/8;g.ellipsoid((x+.6*math.cos(t),42.4+.6*math.sin(t),-51.75),(.2,.2,.12),'HeritageWhite',6,3)
    for x in range(-42,43,4):g.box((x,44.3,-51.7),(1,.6,1.3),'HeritageCream')
    a.put('Doric_entablature_rosettes_and_modillions',g,section='03_Portico')
    # Five broad arched entry bays align with the six columns. Side wings
    # retain narrower windows, avoiding a repeated apartment-window facade.
    for x in [-27.2,-13.6,0,13.6,27.2]:a.instance('Main_hall_arch_and_shutter_bay',hall_bay(),(x,0,-32.15),section='04_Facades')
    flank=G();flank.merge(window(4.8,11,False,True).transformed((0,5,0)))
    flank.merge(window(4.8,12.5,False,True).transformed((0,25.5,0)))
    for x in [-48,-41,41,48]:a.instance('Hall_flank_window',flank,(x,0,-32.15),section='04_Facades')
    for sign in [-1,1]:
        for z in [-23,-8,7,22]:a.instance('Hall_flank_window',flank,(sign*56.15,0,z),-sign*math.pi/2,'04_Facades')
    for x in [-43,-22,0,22,43]:a.instance('Hall_flank_window',flank,(x,0,36.15),math.pi,'05_Rear')
    g=G()
    for i in range(8):a.instance('Portico_roof_rail',balustrade(11,3.2,2,'HeritageWhite',False),(-38.5+11*i,46.1,-50),section='06_Roofline')
    for x in [-44,-26.4,-8.8,8.8,26.4,44]:g.box((x,47.4,-50),(2.6,3.5,1.8),'HeritageWhite')
    for i in range(10):a.instance('Rear_roof_rail',balustrade(11.2,3,2.2,'HeritageWhite',False),(-50.4+11.2*i,46.2,35.6),section='06_Roofline')
    for sign in [-1,1]:
        for i in range(6):a.instance('Side_roof_rail',balustrade(68/6,3,2.2,'HeritageWhite',False),(sign*55.8,46.2,-32+68/12+i*68/6),-sign*math.pi/2,'06_Roofline')
    a.put('Balustrade_masonry_piers',g,section='06_Roofline')
    g=G();g.merge(pediment(9,17.8,2,-.5,'HeritageWhite'))
    g.arch(6.1,2.2,.3,.4,(0,36.3,-.3),'HeritageCream',12)
    a.put('Central_door_crown_and_upper_fanlight',g,(0,0,-32.3),section='04_Facades')
    a.night=['Heavy Doric portico and rosette entablature','Side and rear pilasters/entrances','Roof balustrade and broad entry stairs']
    a.save_live('Town Hall — reworked portico proportions and distinct door/window registers')
    return a,a.finish()
