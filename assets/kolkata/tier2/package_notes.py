"""Write concise library notes and a contact sheet from finished asset files."""
import json
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
SIMPLIFICATIONS={
 'writers_building':"Long red three-register frontage, six giant central columns, triangular pediment, mansard roof, dormers and sparse original rooftop figures. Repeated bays share meshes; carved masonry, statues and rear windows are simplified.",
 'gpo':"White L-shaped wings, rounded corner colonnade, tall ribbed dome/drum and projected clock. Columns and drum bays repeat; capitals and roof ornament are reduced to readable profiles.",
 'metropolitan_building':"Clipped street corner, prominent clock tower, three gold cupolas, arched upper bays, pediment balconies and parapet. Simplified capitals/railings replace fine carving; no shops or rooms are built inside.",
 'town_hall':"Six tall Doric columns, broad stair, flat entablature with relief medallions, roof balustrade and shuttered two-storey body. Preserves the flat roofline; no invented temple pediment. Rear detailing is reduced.",
 'jorasanko_thakur_bari':"Red/green outer elevations, white inner galleries and a five-arched Thakur Dalan. A real 12-stud-wide ground-level entry opens into the courtyard, with shallow gallery slabs, lawn and paved circulation. Closed room volumes contain no room network; full interiors are not authored."
}
rows=json.loads((BASE/'library-summary.json').read_text(encoding='utf8'))
refs=json.loads((ROOT/'artifacts/references/tier2/sources.json').read_text(encoding='utf8'))
for row in rows:
 folder=BASE/Path(row['path']).name
 source_refs=[r for r in refs if r['building']==folder.name and 'path' in r]
 (folder/'references.json').write_text(json.dumps(source_refs,indent=2),encoding='utf8')
 text=f"""# {row['building']} — Tier 2 exterior

{SIMPLIFICATIONS[folder.name]}

## Files

- `{row['source']}` — independent editable Blender scene, including non-exported presentation and hidden collision guides.
- `{row['fbx']}` — **complete assembled visual building**, separated into modular/material meshes. Not an overlapping component library.
- `assembly.json` — pivot, palette, mesh keys, placements and simple collision boxes for later Studio assembly.
- `references.json` — multiple inspected photographic sources. Reference-only; no image is used as a texture or game asset.
- `asset-summary.json` — geometry and file counts.

## Scale and preparation

Authored in studs, Y up in the manifest, front -Z, pivot at ground-level origin. Blender maps `(x,-z,y)`. Scene units None / 1; positive unit object scales; FBX Apply Scalings = FBX Unit Scale, Y Up, no animation. Bounds: {row['boundsStuds']} studs.

{row['triangles']:,} assembled triangles in {row['meshObjects']} mesh objects; {row['uniqueMeshes']} unique shared mesh datablocks. Largest mesh: {row['largestMeshTriangles']:,} triangles. These are file counts, not rendering/FPS measurements.

For later Studio import: Scale Unit **Stud**, Scale Factor **1**, Merge Meshes **off**, Anchored **on**. Reuse matching MeshKeys when placing repetitions, use Automatic render fidelity, disable decorative collision/touch, and rebuild the simple collision boxes natively. Do not use a single convex hull for Jorasanko's courtyard. Presentation objects and collision guides are excluded from the FBX.

No Studio import, city placement, gameplay, mobile or performance test was performed for Task 003. Saved-source/export inspection and a small visual review set are the validation scope. Verify actual Studio appearance, scale and collision when integration is requested.

## Maintenance

`../build_library.py` and `../geometry.py` generate all five assets. Rebuilding replaces generated T2 scenes and these outputs; preserve manual source edits before regenerating. Studio has no automatic synchronization with these files.
"""
 (folder/'README.md').write_text(text,encoding='utf8')
review=ROOT/'artifacts/review/tier2'
sheet=Image.new('RGB',(1500,1245),'#17252b');draw=ImageDraw.Draw(sheet)
names=[(Path(r['path']).name,r['building']) for r in rows]+[('jorasanko_thakur_bari_courtyard','Jorasanko accessible courtyard')]
for i,(slug,title) in enumerate(names):
 x,y=i%2*750,i//2*415
 with Image.open(review/(slug+'.png')) as img:
  thumb=ImageOps.contain(img.convert('RGB'),(734,375))
  sheet.paste(thumb,(x+(750-thumb.width)//2,y+34))
 draw.text((x+14,y+10),title,fill='white')
sheet.save(review/'library-review.jpg',quality=94)
table='\n'.join(f"| {r['building']} | {r['triangles']:,} | {r['uniqueMeshes']} | {r['largestMeshTriangles']:,} |" for r in rows)
readme=f"""# Kolkata Tier 2 building library — Task 003

**All five assets are created and saved.** This is an exterior asset library; no Studio world placement or gameplay work is included.

Open `Kolkata_Tier2_Library.blend` to access the five independent building scenes, or use each building's individual `.blend`. Full assembled FBX exports are in each `exports/` folder. Preview: [library-review.jpg](../../../artifacts/review/tier2/library-review.jpg).

| Building | Assembled triangles | Shared mesh datablocks | Largest mesh |
| --- | ---: | ---: | ---: |
{table}

## Approach

{sum('path' in r for r in refs)} downloaded photographic references cover the five buildings, with facade, perspective/return and defining-detail views; Jorasanko includes its red exterior and white inner courtyard from several directions. Boards and source records are under `artifacts/references/tier2`. Photographs are reference-only; all exported geometry is original. No external meshes, textures, generators, fonts or Toolbox models are used.

Repeated windows, columns, shutters and railings share source meshes. Sections remain separate; no building is a monolithic mesh. Palette materials are plain colors, with no image textures or Blender-only shader effects. Ornament is reduced to architectural profiles. Rear faces are simplified. See the per-building notes for preserved identity and adaptations.

Jorasanko has a 12-stud entrance passage into an open-to-sky courtyard, paved access around a lawn, shallow gallery floors and a stepped Thakur Dalan. It has no full room network.

## Minimal validation

One saved-source/export inspection checks independent scene files, FBX object completeness and unit scales, sensible bounds and per-mesh triangle counts; results are in `export-check.json`. Reviewed one exterior image for each building plus Jorasanko's courtyard. All exports succeeded. No broad test suite, gameplay testing, benchmarking or city placement was performed.

Actual Studio import/rendering/collision validation remains part of the later integration task. The export configuration follows the corrected Task 002 pipeline: neutral Blender units, unit object scales, FBX Unit Scale, and complete assembled handoffs. Import at Stud / scale factor 1 / Merge Meshes off / Anchored on. Keep repeated mesh IDs shared during assembly, native collision simple and streaming boundaries smaller than a whole district.

## Source of truth

The `.blend` files are editable mesh sources; `build_library.py` and `geometry.py` preserve reproducible generation. `assembly.json` files preserve mesh keys, transforms, palette and collision box specifications. Existing Studio content is untouched. There is no automatic synchronization.
"""
(BASE/'README.md').write_text(readme,encoding='utf8')
print('Saved building notes and library contact sheet')
