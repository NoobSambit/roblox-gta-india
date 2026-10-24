"""Small human-readable handoff; retain ImageGen originals without modifying them."""
from pathlib import Path
import json, csv, shutil, hashlib
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'assets/kolkata/masterplan_task014'
CON=OUT/'concepts';CON.mkdir(exist_ok=True)
GENERATED=Path.home()/'.codex/generated_images/01a16c0e-f7f5-7573-8177-9d0ba05dbc26'
mapping={
    '01_premium_aerial':'exec-6b506aee-538d-4f4b-87b7-7f3012b457a0.png',
    '02_bridge_reveal':'exec-7e3c69f1-3190-442b-8226-124d563d53d2.png',
    '03_infrastructure':'exec-7b937ead-8217-4fe3-a931-35f6232b60e1.png',
    '04_station_family':'exec-21b6c44a-4087-47c4-84d0-f0dba921a25a.png',
}
concepts=[]
for key,filename in mapping.items():
    dest=CON/(key+'.png')
    if not dest.exists():shutil.copy2(GENERATED/filename,dest)
    concepts.append(dict(id=key,file='concepts/'+dest.name,tool='built-in ImageGen',
                         generation_file=filename,sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),
                         prompt='../../../authoring/task014/concept_prompts.json#'+key))
(OUT/'concept-provenance.json').write_text(json.dumps(concepts,indent=2))
D=json.loads((OUT/'masterplan-manifest.json').read_text())
with (OUT/'landmark-placements.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.writer(f);w.writerow(['asset_id','district','world_x','world_y','world_z','yaw_degrees_Y',
                              'world_size_x','world_height_y','world_size_z','uniform_scale','source','anchor_status'])
    for r in D['placements']:
        w.writerow([r['id'],r['district'],*r['position'],r['yaw_degrees'],*r['dimensions_roblox'],1,r['source'],r['status']])

# Exact historical records affected by the proposal, preserving continuity for later integration.
old=json.loads((ROOT/'authoring/task006/world-plan.json').read_text())
shown={r['id'] for r in D['external_legacy_context']}
handoff=[]
for r in old['placements']:
    if r['id'] in shown:status='retained_as_historical_external_context'
    elif r['kind']=='landmark':status='superseded_old_Tier2_preserve_before_later_integration'
    elif r['kind']=='residential':status='not_in_premium_proposal_preserve_or_relocate_only_after_approval'
    else:status='legacy_commercial_plot_requires_integration_review'
    handoff.append(dict(placement_id=r['id'],asset_id=r['assetId'],historical_position=r['position'],
                        historical_yaw=r['yaw'],proposal_status=status))
(OUT/'historical-content-handoff.json').write_text(json.dumps(dict(
    source='authoring/task006/world-plan.json',note='Historical records only. No live object was deleted, moved or verified in Task014.',
    placements=handoff),indent=2))

names={'VICTORIA':'Victoria Memorial','HOWRAH':'Howrah Bridge','GHAT':'Established ghat',
       'KOL_T1_ATMOSPHERE':'Atmosphere / Deya','KOL_T1_JW':'JW Marriott','KOL_T1_ROYAL':'ITC Royal Bengal',
       'KOL_T1_SONAR':'ITC Sonar','KOL_T1_TRUMP':'Trump Tower','KOL_T1_URBANA':'Urbana',
       'KOL_T1_WRITERS':"Writers’ Building",'KOL_T1_GPO':'GPO','KOL_T1_TOWN_HALL':'Town Hall',
       'KOL_T1_METROPOLITAN':'Metropolitan','KOL_T1_RAJBARI':'Rajbari / mandap',
       'KOL_T1_JORASANKO':'Jorasanko — both houses','KOL_T1_NEW_MARKET':'New Market',
       'KOL_T1_INDIAN_MUSEUM':'Indian Museum','KOL_T1_ST_PAULS':"St. Paul’s Cathedral",'KOL_T1_DAKSHINESHWAR':'Dakshineshwar / ghat'}
rows=[]
for r in D['placements']:
    dims=' × '.join(str(round(v,1)) for v in r['dimensions_roblox'])
    rows.append(f"| {names[r['id']]} | {', '.join(str(v) for v in r['position'])} | {r['yaw_degrees']}° | {dims} |")
readme='''# Kolkata masterplan — Task 014 Stage A

**Ready for layout review. Stage B is not authorized yet. No Studio operations were performed.**

Open [Kolkata_Masterplan_Stage_A.blend](Kolkata_Masterplan_Stage_A.blend). It uses read-only linked original assets; keep the repository folders together. No landmark has been rebuilt, resized or merged. The source survey retains SHA256 hashes. The master is the proposal; original sources and Studio remain separately authoritative.

Use **Numpad 0** for the camera. Timeline frames **1–8** switch between the eight bound review cameras; frame 2 opens on the isometric. Orbit normally to inspect. Collections separate the landmarks, roads, flyovers, metro, station shells, foundations, boundaries and external legacy context.

## Measured composition

The entire premium boundary is **X=-280..1920, Z=-1100..1100**, a **2,200 × 2,200-stud square** centered on Victoria. Victoria retains its full rotated **620 × 600-stud** campus at **(820,0,0), yaw +90°**, facing west. Four surrounding district envelopes are in the manifest; the central gardens and entry forecourt intentionally remain open. They are proposed park/plaza space, not future Tier 3 infill.

- **Northwest / A:** Writers and GPO form the northern civic frontage; Town Hall and Metropolitan address the metro boulevard, with a civic avenue and reflecting garden.
- **Northeast / B:** Atmosphere and seven-tower Urbana form the rear silhouette. Marriott and Trump step forward; Royal and Sonar share an arrival precinct. All original grounds remain intact.
- **Southwest / C:** Separate Rajbari/mandap and two-house Jorasanko compounds retain their courts, lawns and entry approaches.
- **Southeast / D:** Museum and New Market face a common street/forum; the cathedral has a separate north approach and east-side access avenue.
- **River:** Howrah and the existing ghat keep recorded transforms. Dakshineshwar is upstream/north on an independent rectangular terrace, not a quadrant occupant.

**No Tier 3 or obsolete Tier 2 landmark occurs inside the full premium square.** Sixteen original Tier 3 placements remain outside its western boundary. Other historical objects are recorded in [historical-content-handoff.json](historical-content-handoff.json), including four external buildings omitted from the proposed bridge reveal corridor. Their later preservation/relocation requires an integration pass after approval; this scene does not delete or move live objects.

## Roads and vertical layers

Ground boulevards are 36–48 studs, civic/local carriageways 24–28, sidewalks generally 10–12. The retained Z=0 connector feeds the west side of Victoria's perimeter rather than crossing its grounds. River Drive and the main north/south and civic/market streets create connected loops. Geometry is modular planning slabs, not final road assets; corner radii, markings, curbs and barrier end treatments belong to Stage B.

| Corridor | Stage A dimensions / levels |
|---|---|
| Bridge-entry F01 | Exact east bridge socket **(-644,18.5,-180)**. Carriageway tapers **60→32** over 244 studs; deck plateau **Y24**; 480-stud eased descent; maximum road grade **7.85%**. Separate 10-stud footways cross both bank streets overhead and descend beside the road. |
| Skyline F02 | East perimeter **X1870**, **32-stud** deck at **Y26**; 520-stud eased ramps at both ends; maximum grade **7.85%**. A 76-stud ground road reserves a 36-stud median plus two 20-stud service lanes. |
| West-bank approach | New offline **400-stud** ramp from **X=-1940,Y0** to the fixed bridge west socket **X=-1540,Y18.5**, maximum grade **7.27%**. The old western expansion marker is not silently treated as an unchanged ground junction. |
| Metro | **One straight, unbranched dual-track line**, X=-120..2020 at Z=-370. Rail top **Y60**, regular deck underside **Y54**. Normal piers about 60 studs apart, adjusted around junctions. A special **104-stud** crossing spans the eastern perimeter; girder underside **Y48** clears the flyover parapet **Y29** by **19 studs**. |
| Dakshineshwar | Origin **(-542,-8.5,-910), yaw90°**. Its local water datum -5 matches world **-13.5**; courtyard paving **Y=-7.7**. A 16-stud low-speed access lane descends beside the campus to its existing rear gate; maximum grade **7.56%**. Native terrain grading remains for integration. |

The temple plan extends the recorded water corridor northward; the Blender water/terrain slabs are **planning proxies**. Roblox native Terrain remains the intended water/terrain system. The existing bridge's river opening remains free of invented intermediate piers.

| Station | Ground-origin X,Y,Z | Shell length × width | Role |
|---|---|---|---|
| M01 Heritage | 100,0,-370 | 170 × 46 | Town Hall / civic access |
| M02 Victoria Connector | 820,0,-370 | 180 × 46 | North-side access outside Victoria's fence |
| M03 Skyline | 1640,0,-370 | 170 × 46 | Hotels and modern district |

Each shell reserves side platforms at Y61.3, canopy underside Y81, stair flights, pedestrian landings and future lift shafts. Rail clearance reserves a 14-stud train envelope. **These are greybox shells; Tier 2 architectural detailing, working lifts, ticketing and train gameplay are not implemented.** The concept sheet proposes ivory/teal contemporary structures with restrained terracotta bands and Bengali roof/arch references for Stage B.

## Actual-scene review images

1. [Full-city top-down](01_Full_City_Top_Down.png)
2. [Full-city isometric](02_Full_City_Isometric.png)
3. [Howrah Bridge entry](03_Howrah_Bridge_Entry.png)
4. [Victoria surroundings](04_Victoria_Surroundings.png)
5. [Modern skyline at ground level](05_Modern_Skyline_Ground.png)
6. [Road / flyover / metro relationship](06_Road_Flyover_Metro.png)
7. [Premium square top-down](07_Premium_Centre_Top.png)
8. [Dakshineshwar and riverfront](08_Dakshineshwar_Riverfront.png)

These Workbench renders show actual asset placement and simple infrastructure, without final lighting or fixtures. Cuboid street trees, foundations, road edges and station shells are intentional planning proxies.

## Four ImageGen concepts

[Aerial](concepts/01_premium_aerial.png) · [Bridge reveal](concepts/02_bridge_reveal.png) · [Infrastructure](concepts/03_infrastructure.png) · [Station family](concepts/04_station_family.png)

Exactly four built-in ImageGen calls used measured Blender renders as references, with no alternate-generation rounds. The complete [prompt set](../../../authoring/task014/concept_prompts.json) and [provenance](concept-provenance.json) are retained. These images guide atmosphere and architectural language only.

Observed concept deviations: the aerial invents bridge river piers and modifies some landmark silhouettes; the entry invents secondary riverfront architecture/distant massing; the infrastructure concept invents water at the east side and a truncated flyover deck; station proportions/screens/lifts are illustrative. **None of those changes was applied to the measured Blender plan.** Actual source landmarks, continuous ramps, western river, three shell stations and checked support locations govern future work.

## Placement and coordinate handoff

**Blender=(Roblox X, -Roblox Z, Roblox Y); Roblox=(Blender X, Blender Z, -Blender Y).** One neutral unit equals one stud. Roblox +Y yaw equals Blender +Z rotation. There is no new origin or scale offset. New placements are proposals; Victoria/bridge/ghat anchors come from Task002/006/009 records and were **not re-surveyed in live Studio** in this task.

[landmark-placements.csv](landmark-placements.csv) contains positions, yaw, world dimensions, source and anchor status. [masterplan-manifest.json](masterplan-manifest.json) also records measured source bounds, plot bounds, district envelopes, road alignments, flyovers, metro and cameras. [infrastructure-manifest.json](infrastructure-manifest.json) retains sampled ramps, pier positions and destination access.

| Landmark / compound | Roblox X,Y,Z | Yaw | World X × Y × Z studs |
|---|---|---|---|
'''+ '\n'.join(rows)+'''

## Essential verification and limits

[essential-checks.json](essential-checks.json) records no landmark envelope overlaps, no road/sidewalk intersections with premium landmark envelopes, one connected 29-route network including bridge/approaches, original source hashes/scales, supports clear of crossing carriageways, and basic heights/grades. All eight saved cameras were visually inspected. The approved compounds, including both Jorasanko houses, remain complete.

This is a placement/engineering greybox, not a structural certification or final vehicle/junction test. No gameplay tests, Studio import, multiplayer simulation, exhaustive benchmarking or device guarantees were performed. Final road curves/merges, detailed supports, accessible facilities, collision, terrain transitions and modular Tier 2 stations require Stage B and later Studio validation.

Reproduce with Blender background `--python-exit-code 1 --python authoring/task014/build_masterplan.py`, render with `render_reviews.py`, then run host Python `authoring/task014/check_plan.py` and `package_review.py`. Original asset files are never written by these scripts. **Stop here for masterplan approval.**
'''
(OUT/'README.md').write_text(readme,encoding='utf-8')
print('REVIEW_PACKAGE_READY',len(D['placements']),'placements;',len(concepts),'concepts')
