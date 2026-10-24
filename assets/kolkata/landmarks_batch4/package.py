"""Package the reviewed assets, concise handoff notes and one combined PNG sheet."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import json

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
KEYS=['new_market','indian_museum','st_pauls']
NOTES={
    'new_market':"""Images 7–10 and 12 define the red market frontage, repeated gables, roof sheds,
iron verandah and off-axis clock tower. The entrance elevation follows image 10,
with the tower on the viewer's right. The tower has four clock faces, green
louvred crown, corner pinnacles, stone bands and shuttered openings. The clock
hands are static geometry. The major entrance and covered street arcade have
actual depth; dark closures end the exterior package. Shed ends are enclosed.
The revised main portal is 22 studs wide and 18 studs deep, with stone jambs,
keystone, a larger projecting iron canopy, two levels of entrance lettering and
a distinct paved approach. The lower verandah stops at the entrance. Roof ends
now extend into both facade wall thicknesses, closing the former front/rear
strips; no floating inner parapet posts remain in the gap.
The semicircular upper fanlight is smaller, lowered and centred with a shared
spoke origin and clear brick margins beneath both gable slopes. A separate
pavilion roof covers the entrance passage and joins the main roof mass.
The rear/side ranges retain arches and the brick/material rhythm with simpler
detail. Forecourt paving, low kerbs, bollards and edge planters finish the plot.
No bazaar, neighbourhood or complete marketplace interior is included.

Night: ground fixtures light entry bays; fixtures on the verandah roof reach
the gables without the canopy blocking them. Clock washes mount at the upper
tower bands; a separate wash reaches the green crown. Two rear washes support
the return elevation; two washes on each side cover the side ranges. Keep the
clock faces opaque ivory, not Neon. The reverse night preview checks the rear
and opposite side in addition to the primary night view.
""",
    'indian_museum':"""Images 4–5 define the rectangular central entrance pavilion: three deep
ground arches, giant upper columns, tall arched windows and a restrained attic.
Image 6 defines the open quadrangle, two levels of covered exterior arcade,
flat roofline, repeated parapet lights and small central pool. The quadrangle
is compressed and has 13 bays along each long side and seven on each short side.
The ground-level entrance centre connects to the court. Gallery structures
have actual floors/covers and depth; complete galleries and exhibits are absent.
The exterior room volumes can be replaced later while retaining the separate
facades, portico and roof sections. Compact forecourt, lawns, boundary and four
small trees finish the compound. Image 11's different retail-colonnade elevation
was deliberately excluded rather than mixing it into the museum architecture.
The front and side roof panels meet without coplanar overlaps.
Warm ivory wall plaster, pale raised trim, a sandstone plinth, muted taupe
arcade backing and dark green doors/windows separate the registers. Backing
and door panels sit behind the actual covered galleries, adding readable
depth without modelling rooms. This palette follows the user's colour/depth
feedback while retaining the museum's light heritage character.

Night: six frontage washes, two elevated portico-column washes, two side washes,
four court stations, three rear washes and one entrance-vault light. The upper
portico lights avoid relying on ground lights to reach behind projecting cornices.
""",
    'st_pauls':"""Images 1–3 define the long nave, projecting transept, tall square crossing
tower, crenellated parapets, stepped buttresses and pinnacle/spirelet silhouette.
The supplied present-day photos take precedence over a generic needle spire.
The nave, transept and tower remain separate editable structures. Pointed
windows have shallow glass, lancets, transoms and small rose tracery; the larger
end windows receive more detail. The side entrance porch has an actual pointed
opening and covered depth. Main interior space is unfurnished and undetailed;
no pews, elaborate nave interior or gameplay has been created. Lawn strips,
paths, four trees, benches and a low boundary keep the compound compact.
The user's additional facade photograph informed a restrained extra detail
pass: recessed panels on the stepped buttresses, crockets on the four tower
pinnacles and small porch pinnacles. Continuous annular trim removes hidden
internal segment caps to offset the added detail's placed cost.

Night: six nave washes, two transept washes, west/east end washes, three elevated
tower/pinnacle washes and one porch light. Mount upper tower lights to the
transept roof/appropriate brackets, then tune their aim after import. Keep
roof/window values darker than the pale masonry and avoid glowing entire walls.
"""}


def font(size,bold=False):
    return ImageFont.truetype(str(Path('C:/Windows/Fonts')/('segoeuib.ttf' if bold else 'segoeui.ttf')),size)


def dims(r,field='dimensionsStuds'):
    d=r[field];return f"{d['width']:g} × {d['depth']:g} × {d['height']:g}"


def package():
    rows=[]
    for key in KEYS:
        folder=BASE/key;r=json.loads((folder/'asset.json').read_text());v=json.loads((folder/'validation.json').read_text())
        assert v['status']=='passed',(key,v)
        assert set(v['previews'])=={'preview-hero.png','preview-elevated.png','preview-grounds.png','preview-night.png','preview-night-rear.png'}
        for preview in v['previews']:assert (folder/preview).is_file()
        for material in r['materials']:
            if material['texture']:
                material['texture']='../textures/'+Path(material['texture']).name
                assert (folder/material['texture']).is_file()
        (folder/'asset.json').write_text(json.dumps(r,indent=2),encoding='utf8')
        lines=[f"# {r['name']}", '',NOTES[key].strip(),'',
            f"Building envelope **{dims(r,'buildingDimensionsStuds')} studs**; whole plot **{dims(r)} studs** (width × depth × height).",
            f"Unique source **{r['uniqueSourceTriangles']:,}** triangles; assembled/placed **{r['assembledTriangles']:,}** triangles.",
            f"{len(r['exports'])} FBX sections; {sum(e['meshInstances'] for e in r['exports'])} export mesh objects; largest mesh {max(e['largestExportMeshTriangles'] for e in r['exports']):,} triangles.", '',
            'Open the named master `.blend`. The linked authoring modules are in the source collection. The hidden `80_ExportReady` collection contains baked section/material snapshots; keep it hidden when editing/rendering to avoid duplicate geometry. Preview lights/cameras are separate and excluded from every FBX.', '',
            'Import all files with this asset prefix together at **Stud / scale 1 / Merge Meshes off / Anchored on**. Preserve the common ground-centre origin and section offsets. Do not centre each section individually. Front is Blender +Y / Roblox -Z. Do not import a whole building as one mesh. See the batch README for materials, collision and streaming guidance.', '',
            'Materials (original sRGB colours, opaque):', '', '| Slot | Colour | Original texture |','|---|---|---|']
        for m in r['materials']:lines.append(f"| {m['name']} | #{m['color']} | {m['texture'] or 'None'} |")
        lines += ['', 'Recommended Roblox light stations, relative to the shared ground origin. Coordinates are **X, Y-up, Z studs**. `asset.json` includes target, RGB, suggested brightness, range, angle and shadows for each station. These are tuning starting points, not a tested Studio lighting configuration. Blender preview watts do not convert to Roblox brightness.', '',
            '| Station | Position | Aim target | Range |','|---|---|---|---:|']
        for light in r['nightLights']:
            lines.append(f"| {light['name']} | {light['positionStuds']} | {light['targetStuds']} | {light['rangeStuds']} |")
        lines += ['', 'All proposed lights have shadows disabled. Use warm architectural light with limited overlap. Enable lights only during the later authored night period; no runtime scripts or native light instances are included here. Preserve soft ambient readability when tuning.', '',
            'Essential geometry/normal checks, triangle/FBX inventory, UV/material presence and one representative section scale round trip passed; see `validation.json`. Original final hero/elevated/grounds/night PNGs plus a reverse night view are beside this file. Actual Studio import, collisions and device performance remain unverified, as this task excludes integration.', '']
        (folder/'ASSEMBLY.md').write_text('\n'.join(lines),encoding='utf8');rows.append(r)
    total_unique=sum(r['uniqueSourceTriangles'] for r in rows);total_placed=sum(r['assembledTriangles'] for r in rows)
    manifest=dict(assets=[dict(key=k,assetId=r['assetId'],source=f"{k}/{r['source']}",metadata=f'{k}/asset.json',
        dimensionsStuds=r['dimensionsStuds'],buildingDimensionsStuds=r['buildingDimensionsStuds'],uniqueSourceTriangles=r['uniqueSourceTriangles'],
        assembledTriangles=r['assembledTriangles'],fbxSections=len(r['exports']),exportMeshObjects=sum(e['meshInstances'] for e in r['exports']),
        lightStations=len(r['nightLights'])) for k,r in zip(KEYS,rows)],
        uniqueSourceTriangles=total_unique,assembledTriangles=total_placed,
        budgetReview='Unique count is below the preferred 53k floor because of linked authoring reuse; geometry is not inflated to meet a quota. Placed total is above the preferred 125k upper end but below the 145k soft review threshold. The museum compound and covered two-level arcades are the largest repeated cost.',
        validation='Essential Blender/FBX checks passed. Original final preview PNGs inspected separately. No Studio or gameplay testing.',
        sourceOwnership='Blender masters and their generators own these offline assets; no Studio synchronization. Rebuilding replaces manual edits to these batch assets.',
        provenance='Original meshes and four original 512px maps. No third-party geometry, photographic textures or ImageGen.')
    assert total_unique<95000 and total_placed<145000
    (BASE/'batch-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
    table=['| Landmark | Building W×D×H studs | Plot W×D×H studs | Unique tris | Placed tris | FBXs |','|---|---|---|---:|---:|---:|']
    for r in rows:table.append(f"| {r['name']} | {dims(r,'buildingDimensionsStuds')} | {dims(r)} | {r['uniqueSourceTriangles']:,} | {r['assembledTriangles']:,} | {len(r['exports'])} |")
    text='''# Kolkata Tier 1 landmarks — Batch 4

Three independent exterior landmark packages: New Market / Sir Stuart Hogg Market,
Indian Museum and St. Paul's Cathedral. No Studio integration, district assembly,
gameplay, complete interiors, or changes to earlier landmark batches are included.

Open the master `.blend` in each asset folder, or `Batch4_Live.blend` and choose a
landmark scene. The latter is a review library, not a city layout. Four required
PNG views plus a reverse night view per asset and `contact-sheet.png` provide
the review set. The two night bearings show lighting on all four elevations.

'''+ '\n'.join(table)+f'''

Batch: **{total_unique:,} unique / {total_placed:,} placed triangles**. Unique counts
measure linked source reuse; placed counts measure the FBX geometry actually
exported. Source counts are below the preferred 53–85k allowance; no extra detail
was added merely to exhaust it. Placed cost exceeds the preferred 125k upper end
but stays below the 145k soft review threshold. The retained museum quadrangle
and its two levels of exterior arcades account for much of that cost. These
are mesh counts, not device benchmarks.

All **{sum(len(r['exports']) for r in rows)} modular FBXs** are in
`exports/kolkata_landmarks_batch4/` at repository root. Keep each prefix's sections
aligned to their shared ground-centre origin. Import at **Stud / scale 1 / Merge
Meshes off / Anchored on**. Front is Blender +Y / Roblox -Z; one neutral Blender
coordinate equals one stud. Every mesh is below 15k triangles, within Roblox's
[current 20k individual mesh maximum](https://create.roblox.com/docs/art/modeling/specifications)
(checked 24 October 2026). Keep camera/light rigs out of import.

Use simple native boxes/convex collision at later integration: foundation,
plinth, steps, structural walls and roof surfaces as needed. Treat small trim,
tracery, foliage and ironwork as decoration. Check door/porch clearance in Studio
when that integration is authorized. Group wing/tower/grounds sections into
appropriate streaming models; do not force an entire compound to stay loaded.

Four small original 512px maps supply shared brick, stone and plaster variation,
plus the museum's warmer wall finish.
They are packed in the masters and embedded in the FBXs; originals are in
`textures/`. UVs use physical-scale box projection. Other materials use opaque
colours and restrained roughness/metal values. Preserve the material assignments
and UVs; if Studio does not extract an embedded map automatically, use the
original image with its matching material meshes. No large PBR sets, procedural
shader dependency, photo texture or external asset is required.

`asset.json` and `ASSEMBLY.md` beside each master include material manifests,
reference adaptations and local night-light stations. Physical uplights are
reused; elevated positions identify later bracket/roof mounts. Preview watts
serve Blender only. Native Roblox lights must be placed/tuned later; the
suggested lights are shadowless, range-limited and use no giant Neon surfaces.

The supplied photos are primary evidence. `references.json` records attachment
IDs and hashes; photos stay outside Git. Museum images 4–6 control its entry and
court; inconsistent image 11 was excluded. Cathedral images 1–3 control its
present square tower/pinnacle silhouette. Historical steeple collapse is also
documented by the [Royal Museums Greenwich collection](https://www.rmg.co.uk/collections/objects/rmgc-object-1214942).
The museum quadrangle is corroborated by the [museum's historical publication](https://ignca.gov.in/Asi_data/22382.pdf).

Essential source finite-data, closed-geometry, normals, UV, triangle/FBX inventory
and representative scale/material round-trip checks passed in `validation.json`
for each asset. The final original views were visually inspected. No Studio,
gameplay, multiplayer, collision or device-performance testing was performed.

Rebuild: run `python prepare.py` from this folder, then Blender background with
`--python-exit-code 1 --python build.py -- new_market indian_museum st_pauls`.
Review with the same Blender flags and `--python review.py` (four required views
plus a reverse night view each).
Run `python package.py`, then Blender `--python library.py`. Builders reuse existing
indexed geometry/export helpers read-only, and replace only this new batch's
outputs. Preserve manual edits before regeneration; no automatic Studio sync
exists. `production-plan.md` records this task's scope and completed checklist.
'''
    (BASE/'README.md').write_text(text,encoding='utf8')
    ex=ROOT/'exports/kolkata_landmarks_batch4'
    (ex/'README.md').write_text('''# Batch 4 modular import files

New Market, Indian Museum and St. Paul's Cathedral, each independent.
Import all files sharing a `KOL_T1_*` prefix together; keep section offsets.
Stud / Scale 1 / Merge Meshes off / Anchored on. Common ground centre; front -Z.
Meshes remain below 15k triangles. Textures are embedded, with original 512px
maps and material notes in `assets/kolkata/landmarks_batch4/`.

Do not merge a whole landmark or centre each section separately. No light,
camera, gameplay script or complex collision is included in these FBXs. Configure
simple collision, streaming boundaries and the documented native lights during
later authorized Studio integration. See the batch README and asset ASSEMBLY.md.
''',encoding='utf8')
    # Single review contact sheet: columns are landmarks, rows are required views.
    cw,ch=800,550;header=150;rh=590
    sheet=Image.new('RGB',(cw*3,header+rh*5),(29,37,39));draw=ImageDraw.Draw(sheet)
    draw.text((25,16),'KOLKATA  /  TIER 1 — BATCH 4',font=font(32,True),fill=(235,225,202))
    draw.text((26,61),'Original Blender assets • compressed heroic scale • exterior packages',font=font(20),fill=(178,191,187))
    names=['NEW MARKET','INDIAN MUSEUM',"ST. PAUL’S CATHEDRAL"]
    for col,(key,r,name) in enumerate(zip(KEYS,rows,names)):
        x=col*cw;draw.text((x+24,105),name,font=font(26,True),fill=(230,212,174))
        for ri,view in enumerate(['hero','elevated','grounds','night','night-rear']):
            y=header+ri*rh
            im=Image.open(BASE/key/f'preview-{view}.png').convert('RGB');im=ImageOps.contain(im,(cw-8,ch))
            sheet.paste(im,(x+(cw-im.width)//2,y))
            draw.text((x+20,y+ch+4),view.upper(),font=font(20,True),fill=(211,219,213))
    sheet.save(BASE/'contact-sheet.png',optimize=True)
    print(json.dumps({k:manifest[k] for k in ['uniqueSourceTriangles','assembledTriangles']})+f'; {len(rows)} assets, {sum(len(r["exports"]) for r in rows)} FBXs, 15 previews and contact sheet.')


if __name__=='__main__':package()
