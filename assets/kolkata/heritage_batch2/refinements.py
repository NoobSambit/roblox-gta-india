"""Authored foundations, secondary elevations and installed perimeter lighting."""
from common import *

pipeline.COLORS['HeritageGlow']='F4CE8C'


def pilaster(height,role='HeritageCream'):
    g=G();g.box((0,.4,0),(2.2,.8,1.2),role)
    g.box((0,height/2,0),(1.25,height,.85),role)
    g.box((0,height-.5,-.2),(2.6,1,1.5),role)
    for y in [height*.35,height*.69]:g.box((0,y,-.12),(2,.65,1.2),role)
    return g


def rear_door(w=10,h=13):
    g=window(w,h,True,False)
    g.box((0,h*.32,-.7),(w*.65,h*.64,.3),'HeritageDark')
    for sign in [-1,1]:g.box((sign*w*.16,h*.32,-.91),(.12,h*.6,.2),'HeritageCream')
    g.box((0,-.4,-1.3),(w+3,.8,3.2),'HeritageStone')
    g.merge(pediment(w+3,h+1.3,2.5,-.65,'HeritageCream'))
    return g


def foundations(a):
    cfg={'writers':(314,62,0,2.9),'metropolitan':(148,94,0,2.7),
        'town_hall':(112,68,2,4.3)}
    if a.key in cfg:
        w,d,z,y=cfg[a.key]
        a.put('Molded_masonry_socle',cornices(w,d,[y],(0,0,z),'HeritageStone',False),section='09_Foundation_Detail')
    elif a.key=='gpo':
        g=cornices(108,54,[3.5],(25,0,-24),'HeritageStone',False)
        g.merge(cornices(44,100,[3.5],(-39,0,24),'HeritageStone',False))
        a.put('GPO_continuous_stepped_socles',g,section='09_Foundation_Detail')
    planter=G();planter.box((0,1.5,0),(6,1.4,5),'HeritageStone')
    planter.box((0,2.2,0),(6.5,.35,5.5),'HeritageCream');planter.box((0,2.45,0),(5.4,.3,4.4),'Leaf')
    bench=G()
    for x in [-2,2]:bench.box((x,1.25,0),(.5,.9,1.7),'HeritageIron')
    bench.box((0,1.85,0),(5.6,.35,2),'HeritageSlate');bench.box((0,2.5,.8),(5.6,1.2,.3),'HeritageSlate')
    if a.key=='writers':
        for x in [-148,148]:a.instance('Forecourt_planter',planter,(x,0,-49),section='09_Foundation_Detail')
        for x in [-61,61]:a.instance('Forecourt_bench',bench,(x,0,-53),section='09_Foundation_Detail')
        for sign in [-1,1]:
            g=roof_iron(58,2.6);g.box((-30,1.4,0),(2.6,2.8,2.6),'HeritageStone');g.box((30,1.4,0),(2.6,2.8,2.6),'HeritageStone')
            a.instance('Low_civic_forecourt_fence',g,(sign*104,.8,-56),section='09_Foundation_Detail')
        # Two additional stoops articulate the long base without adding a campus.
        for x in [-93,93]:
            a.box('Wing_entry_stoop_'+str(x),(x,1.2,-34),(12,.8,5),'HeritageStone','09_Foundation_Detail')
    elif a.key=='metropolitan':
        for x,z in [(-66,-56),(73,40)]:a.instance('Forecourt_planter',planter,(x,0,z),section='09_Foundation_Detail')
        for x in [-61,-39,9,32,61]:
            g=G();g.lathe([(0,.35),(1.4,.28),(1.65,.4),(1.8,.1)],8,'HeritageIron')
            a.instance('Street_bollard',g,(x,.8,-59),section='09_Foundation_Detail')
        g=G()
        for x in [-62,-40,16,38]:g.box((x,1.05,-57),(15,.4,.6),'HeritageStone')
        a.put('Inset_entry_approach_borders',g,section='09_Foundation_Detail')
    elif a.key=='gpo':
        for x,z in [(76,-65),(-73,70)]:a.instance('Civic_approach_planter',planter,(x,0,z),section='09_Foundation_Detail')
        g=G()
        for x in [-31,-15,1,17,33,49,65]:g.box((x,1.1,-68.7),(11,.6,.5),'HeritageStone')
        a.put('GPO_front_approach_coping',g,section='09_Foundation_Detail')
    else:
        for x in [-52,52]:a.instance('Town_Hall_urn_planter',planter,(x,0,-50),section='09_Foundation_Detail')
        for x in [-51,51]:a.instance('Town_Hall_bench',bench,(x,0,-61),section='09_Foundation_Detail')
        g=G()
        for sign in [-1,1]:
            g.box((sign*44,2.1,-43),(1.4,2.6,18),'HeritageStone')
            g.box((sign*44,3.55,-43),(1.8,.35,18.5),'HeritageCream')
        a.put('Portico_retaining_edges_and_coping',g,section='09_Foundation_Detail')


def secondary_elevations(a):
    if a.key=='writers':
        a.box('Rear_central_entry_projection',(0,31,37),(40,56.8,5),'HeritageRed','10_Rear_Architecture')
        a.put('Rear_pavilion_belt_courses',cornices(40,5,[5,22,42,59],(0,0,37),'HeritageCream',False),section='10_Rear_Architecture')
        a.instance('Rear_civic_door',rear_door(9,13),(0,3,39.65),math.pi,'10_Rear_Architecture')
        for x in [-16,16]:
            for y in [7,27,46]:a.instance('Rear_pavilion_window',window(4.5,10,True,True),(x,y,39.65),math.pi,'10_Rear_Architecture')
        for x in [-144,-108,-72,-36,36,72,108,144]:
            a.instance('Rear_ordered_pilaster',pilaster(56),(x,3,31.25),math.pi,'10_Rear_Architecture')
        for sign in [-1,1]:
            a.instance('Rear_return_pilaster',pilaster(56),(sign*157.25,3,15),-sign*math.pi/2,'10_Rear_Architecture')
    elif a.key=='metropolitan':
        for x in [-68,-48,-28,-8,12,32,52,68]:a.instance('Rear_commercial_pilaster',pilaster(54),(x,3,47.25),math.pi,'10_Rear_Architecture')
        for z in [-35,-12,12,35]:a.instance('Rear_commercial_pilaster',pilaster(54),(-74.25,3,z),math.pi/2,'10_Rear_Architecture')
        a.instance('Rear_service_portal',rear_door(8.5,13),(-14,2.4,47.3),math.pi,'10_Rear_Architecture')
        g=G()
        for y in [20.7,39.5,58.2]:g.box((0,y,47.6),(148,.45,.9),'HeritageCream')
        for x in [-42,0,42]:
            g.box((x,60,32),(3,4,3),'HeritageCream');g.box((x,62.2,32),(4,.6,4),'HeritageStone')
        a.put('Rear_belt_courses_and_roof_stacks',g,section='10_Rear_Architecture')
    elif a.key=='gpo':
        g=cornices(108,54,[4.7,23,43.5],(25,0,-24),'HeritageCream',False)
        g.merge(cornices(44,100,[4.7,23,43.5],(-39,0,24),'HeritageCream',False))
        a.put('Rear_wing_belt_courses',g,section='10_Rear_Architecture')
        for x in [-25,-7,11,29,47,65,78]:a.instance('Rear_GPO_pilaster',pilaster(38),(x,5,3.25),math.pi,'10_Rear_Architecture')
        for x in [-58,-39,-20]:a.instance('Rear_GPO_pilaster',pilaster(38),(x,5,74.25),math.pi,'10_Rear_Architecture')
        bay=G()
        for y in [7,26]:bay.merge(window(5.4,12,False,False).transformed((0,y,0)))
        for z in [-42,-25,-8]:a.instance('GPO_end_window_bay',bay,(79.2,0,z),-math.pi/2,'10_Rear_Architecture')
        for z in [18,37,56]:a.instance('GPO_end_window_bay',bay,(-16.8,0,z),-math.pi/2,'10_Rear_Architecture')
        for z in [-48,-33,-16,0]:a.instance('GPO_end_pilaster',pilaster(38),(79.25,5,z),-math.pi/2,'10_Rear_Architecture')
        for z in [11,29,48,66]:a.instance('GPO_end_pilaster',pilaster(38),(-16.75,5,z),-math.pi/2,'10_Rear_Architecture')
        a.instance('GPO_rear_arched_portal',rear_door(8.2,13),(-39,3.1,74.3),math.pi,'10_Rear_Architecture')
    else:
        for x in [-53,-32,-11,11,32,53]:a.instance('Hall_rear_pilaster',pilaster(39),(x,5,36.25),math.pi,'10_Rear_Architecture')
        for sign in [-1,1]:
            for z in [-29,-15,0,15,31]:a.instance('Hall_side_pilaster',pilaster(39),(sign*56.25,5,z),-sign*math.pi/2,'10_Rear_Architecture')
        a.instance('Hall_rear_service_entry',rear_door(8.4,12.2),(0,4,36.4),math.pi,'10_Rear_Architecture')
        g=G();g.merge(pediment(24,44.7,3.5,0,'HeritageWhite'))
        a.put('Rear_civic_pavilion_crown',g,(0,0,36.4),math.pi,section='10_Rear_Architecture')


def install_lights(a):
    specs=[]
    def flood(name,pos,target,power=22000,range_=60):
        specs.append(dict(name=name,positionStuds=list(pos),targetStuds=list(target),rangeStuds=range_,
            brightness=2,angleDegrees=100,colorRGB=[255,218,167],blenderWatts=power,shadows=False))
    if a.key=='writers':
        for i,x in enumerate([-137,-94,-48,0,48,94,137]):flood('Front_'+str(i),(x,3,-53),(x,40,-35))
        for i,x in enumerate([-137,-70,0,70,137]):flood('Rear_'+str(i),(x,3,41),(x,38,32))
        for sign in [-1,1]:
            for z in [-17,20]:flood('Side_'+str(sign)+'_'+str(z),(sign*161,3,z),(sign*156,37,z))
        for i,x in enumerate([-137,0,137]):flood('Crown_'+str(i),(x,64,-36),(x,80,-25),10000,40)
    elif a.key=='metropolitan':
        for i,x in enumerate([-60,-25,15,55]):flood('Front_'+str(i),(x,3,-60),(x,38,-47))
        for i,x in enumerate([-58,-18,22,62]):flood('Rear_'+str(i),(x,3,51),(x,38,47))
        for sign in [-1,1]:
            for z in [-14,26]:flood('Side_'+str(sign)+'_'+str(z),(sign*78,3,z),(sign*74,36,z))
        flood('Clock_crown',(61,60,-45),(61,82,-34),16000,42)
        flood('Satellite_crown',(-65,59,-42),(-65,71,-38),8000,30)
    elif a.key=='gpo':
        for i,x in enumerate([-52,-20,16,54]):flood('Front_'+str(i),(x,3,-66),(x,29,-51))
        for i,x in enumerate([-48,-24]):flood('Rear_return_'+str(i),(x,3,77),(x,33,74))
        for i,x in enumerate([5,44,74]):flood('Rear_east_'+str(i),(x,3,7),(x,30,3))
        for i,z in enumerate([-15,26,62]):flood('West_'+str(i),(-73,3,z),(-61,30,z))
        for i,z in enumerate([23,59]):flood('Inner_return_'+str(i),(-12,3,z),(-17,30,z))
        flood('Dome_front',(-50,46,-56),(-39,87,-30),25000,60)
        flood('Dome_back',(-27,46,-17),(-39,87,-30),25000,60)
    else:
        for i,x in enumerate([-32,0,32]):flood('Portico_'+str(i),(x,3,-65),(x,32,-40))
        for i,x in enumerate([-39,0,39]):flood('Rear_'+str(i),(x,3,39),(x,30,36))
        for sign in [-1,1]:
            for z in [-14,20]:flood('Side_'+str(sign)+'_'+str(z),(sign*60,3,z),(sign*56,30,z))
    rig=bpy.data.collections.new('INSTALLED_NIGHT_LIGHTS__NOT_FBX');a.scene.collection.children.link(rig)
    fixture=G();fixture.box((0,1,0),(1.3,.4,1.2),'HeritageStone')
    fixture.cylinder((0,1.8,0),.12,1.3,'HeritageIron',6)
    fixture.box((0,2.5,0),(1.1,.55,.85),'HeritageIron');fixture.box((0,2.8,0),(.8,.1,.65),'HeritageGlow')
    for spec in specs:
        pos=spec['positionStuds']
        if pos[1]<10:a.instance('Installed_ground_flood_fixture',fixture,(pos[0],0,pos[2]),section='09_Foundation_Detail')
        data=bpy.data.lights.new(spec['name'],'SPOT');data.energy=spec['blenderWatts'];data.color=(1,.76,.49)
        data.spot_size=math.radians(spec['angleDegrees']);data.spot_blend=.65;data.use_shadow=False
        data.use_custom_distance=True;data.cutoff_distance=spec['rangeStuds']
        obj=bpy.data.objects.new(spec['name'],data);rig.objects.link(obj);obj.location=bv(pos)
        obj.rotation_euler=(Vector(bv(spec['targetStuds']))-obj.location).to_track_quat('-Z','Y').to_euler()
        obj['NightWatts']=spec['blenderWatts']
    mat=pipeline.material('HeritageGlow');node=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    node.inputs['Emission Color'].default_value=(1,.7,.3,1);node.inputs['Emission Strength'].default_value=1.5
    a.light_specs=specs


def apply(a):
    foundations(a);secondary_elevations(a);install_lights(a)
    a.scene['RevisedGroundRearFoundationLighting']=True
