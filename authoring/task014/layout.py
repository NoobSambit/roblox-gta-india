"""Task 014 design data. All coordinates are Roblox studs, Y up, north -Z."""
from pathlib import Path
import json, math

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/kolkata/masterplan_task014'
BOUNDARY = [-280, -1100, 1920, 1100]
# id, district, world ground-origin, Roblox yaw in degrees
PLACEMENTS = [
    ('VICTORIA', 'Victoria Memorial', (820,0,0), 90),
    ('HOWRAH', 'Existing World Anchors', (-1092,-13.5,-180),90),
    ('GHAT', 'Existing World Anchors', (-620,-13.5,380),90),
    ('KOL_T1_WRITERS','Colonial Heritage',(100,0,-930),180),
    ('KOL_T1_GPO','Colonial Heritage',(590,0,-930),180),
    ('KOL_T1_TOWN_HALL','Colonial Heritage',(80,0,-530),180),
    ('KOL_T1_METROPOLITAN','Colonial Heritage',(600,0,-540),180),
    ('KOL_T1_ATMOSPHERE','Modern Skyline',(1040,0,-850),180),
    ('KOL_T1_URBANA','Modern Skyline',(1550,0,-800),180),
    ('KOL_T1_JW','Modern Skyline',(1080,0,-570),180),
    ('KOL_T1_TRUMP','Modern Skyline',(1400,0,-480),180),
    ('KOL_T1_ROYAL','Modern Skyline',(1370,0,-190),0),
    ('KOL_T1_SONAR','Modern Skyline',(1660,0,-190),0),
    ('KOL_T1_RAJBARI','Bengali Cultural District',(70,0,620),180),
    ('KOL_T1_JORASANKO','Bengali Cultural District',(590,0,780),0),
    ('KOL_T1_INDIAN_MUSEUM','Commercial Cultural District',(1400,0,570),180),
    ('KOL_T1_NEW_MARKET','Commercial Cultural District',(1400,0,930),0),
    ('KOL_T1_ST_PAULS','Commercial Cultural District',(1730,0,600),0),
    ('KOL_T1_DAKSHINESHWAR','Dakshineshwar Riverfront',(-542,-8.5,-910),90),
]
DISTRICTS = {
    'A Colonial Heritage':[-250,-1070,820,-370],
    'B Modern Skyline':[820,-1070,1870,-40],
    'C Bengali Cultural':[-250,370,820,1070],
    'D Commercial Cultural':[820,370,1870,1070],
}
# polylines in world X,Z; road top Y=0. Divided roads reserve a centre median.
ROADS = [
    ('R01_North_Boulevard',[(-400,-1070),(1870,-1070)],40,10,0),
    ('R02_South_Boulevard',[(-500,1070),(1870,1070)],40,10,0),
    ('R03_West_Perimeter',[(-230,-1070),(-230,1070)],36,10,0),
    ('R04_East_Perimeter',[(1870,-1070),(1870,1070)],76,10,36),
    ('R05_Heritage_Metro_Boulevard',[(-500,-370),(2020,-370)],48,10,8),
    ('R06_South_Prestige_Boulevard',[(-500,370),(1870,370)],40,12,0),
    ('R07_Victoria_West',[(450,-370),(450,370)],36,10,0),
    ('R08_Victoria_East',[(1190,-370),(1190,370)],36,10,0),
    ('R09_North_Meridian',[(820,-1070),(820,-370)],32,10,0),
    ('R10_South_Meridian',[(820,370),(820,1070)],32,10,0),
    ('R11_Civic_Avenue',[(-230,-720),(820,-720)],28,10,0),
    ('R12_Civic_Cross',[(370,-1070),(370,-370)],24,10,0),
    ('R13_Skyline_Access',[(1280,-1070),(1280,-370)],28,10,0),
    ('R14_Skyline_Cross',[(820,-730),(1280,-730)],24,10,0),
    ('R15_Hotel_Arrival',[(1190,-40),(1870,-40)],24,10,0),
    ('R16_Cultural_Avenue',[(-230,820),(370,820)],24,10,0),
    ('R17_Cultural_Cross',[(370,370),(370,1070)],24,10,0),
    ('R18_Jorasanko_Access',[(370,560),(820,560)],24,10,0),
    ('R19_Market_Museum_Street',[(820,780),(1610,780)],28,10,0),
    ('R20_Cathedral_Avenue',[(1610,370),(1610,1070)],24,10,0),
    ('R21_River_Drive',[(-500,-600),(-500,1070)],32,10,0),
    ('R22_Dakshineshwar_Drive',[(-400,-1230),(-400,-700),(-500,-600)],32,10,0),
    ('R23_North_River_Link',[(-500,-600),(-230,-600)],24,10,0),
    ('R24_Existing_Victoria_Connector',[(-500,0),(450,0)],40,12,0),
    ('R25_West_Bridge_Expansion',[(-2020,-180),(-1940,-180)],60,10,0),
]
STATIONS = [
    dict(id='M01',name='Heritage',position=[100,0,-370],length=170,width=46),
    dict(id='M02',name='Victoria Connector',position=[820,0,-370],length=180,width=46),
    dict(id='M03',name='Skyline',position=[1640,0,-370],length=170,width=46),
]
METRO = dict(id='KOL_METRO_01',points=[[-120,60,-370],[2020,60,-370]],
             rail_top=60,deck_top=58,deck_bottom=54,deck_width=24,
             train_envelope_height=14,track_centres_offset=7,
             normal_support_spacing=60,special_crossing_span=104,stations=STATIONS)

def flyover_height(t, length, rise, plateau, start=0):
    if t < rise:
        return start+(plateau-start)*(.5-.5*math.cos(math.pi*t/rise))
    if t > length-rise:
        return plateau*(.5+.5*math.cos(math.pi*(t-(length-rise))/rise))
    return plateau

def design():
    survey=json.loads((OUT/'source-survey.json').read_text())
    byid={r['id']:r for r in survey}
    records=[]
    for key,district,pos,yaw in PLACEMENTS:
        r=byid[key]
        if key=='VICTORIA':
            selected=[c for c in r['collections'] if c['name'] in ['VM_Architecture','VM_Structure_Collision','VM_Interior','VM_Grounds','VM009_NativeArchitecture']]
        else:
            selected=[c for c in r['collections'] if c['meshes'] and not c['hidden']]
        bounds=[c['bounds_blender'] for c in selected if c['bounds_blender']]
        lo=[min(b[0][i] for b in bounds) for i in range(3)]
        hi=[max(b[1][i] for b in bounds) for i in range(3)]
        a=math.radians(yaw); c,s=math.cos(a),math.sin(a)
        pts=[]
        for x in [lo[0],hi[0]]:
            for by in [lo[1],hi[1]]:
                z=-by
                for y in [lo[2],hi[2]]:
                    pts.append([pos[0]+c*x+s*z,pos[1]+y,pos[2]-s*x+c*z])
        worldlo=[round(min(p[i] for p in pts),4) for i in range(3)]
        worldhi=[round(max(p[i] for p in pts),4) for i in range(3)]
        records.append(dict(id=key,district=district,source=r['source'],source_sha256=r['sha256'],
                            source_collections=[c['name'] for c in selected],position=list(pos),yaw_degrees=yaw,
                            scale=[1,1,1],source_bounds_blender=[lo,hi],world_bounds_roblox=[worldlo,worldhi],
                            dimensions_roblox=[round(worldhi[i]-worldlo[i],4) for i in range(3)],
                            status='historical_record_anchor' if key in ['VICTORIA','HOWRAH','GHAT'] else 'stage_a_proposal'))
    return dict(stage='A: proposed layout for review, not Studio integration',
                conversion={'blender_from_roblox':'(X,-Z,Y)','roblox_from_blender':'(X,Z,-Y)',
                            'units':'1 neutral Blender unit = 1 Roblox stud','yaw':'Roblox +Y yaw = Blender +Z rotation',
                            'origin':'Existing world origin retained; no scene offset'},
                premium_boundary_xz=BOUNDARY,premium_dimensions_studs=[2200,2200],district_plots_xz=DISTRICTS,
                placements=records,roads=[dict(id=k,points_xz=p,width=w,sidewalk=f,median=m) for k,p,w,f,m in ROADS],
                metro=METRO,water=dict(datum_y=-13.5,historical_bounds_xz=[-1560,-830,-628,750],
                                      proposed_visual_bounds_xz=[-1560,-1280,-628,1180],
                                      note='Planning water proxy only. Native Terrain remains authoritative at integration.'),
                assumptions=[
                    'Fixed anchor transforms come from Task002/006/009 records, not a live Studio survey in Task014.',
                    'Historical districts and Tier3 within the proposed premium boundary require a preservation/relocation decision during integration. No live content changed.',
                    'No old Tier2 landmarks are linked. Existing external Tier3 context may remain outside the boundary.',
                    'Dakshineshwar Y=-8.5 aligns its local -5 water datum to world -13.5; paving is -7.7, with a separate descending approach.',
                    'Bridge-entry flyover supersedes the old short east approach only in this proposal. The bridge itself is untouched.',
                    'Station architecture is a shell/reservation only in Stage A; Tier2 detailing belongs to Stage B.',
                ])

if __name__=='__main__':
    (OUT/'masterplan-manifest.json').write_text(json.dumps(design(),indent=2))
    print('MEASURED_DESIGN_READY')
