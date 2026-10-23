# ITC Royal Bengal exterior

Accepted hero exterior with reduced corner-loggia projections and deep yellow
ochre masonry. Source: `KOL_T1_ROYAL.blend`; generator: `../royal_bengal.py`.
The user-supplied front, oblique, crown and arrival photos guide the architecture.
Downloaded reference photos remain local; `references/sources.json` records
their provenance. No photographic texture or third-party model is incorporated.

The column correction seats 44 columns into both their supporting ledges and
overhead beams. Upper-loggia end columns sit inside the reduced slab edges.
Portico columns share a continuous plinth; capitals and balustrade feet overlap
their bearings slightly. `column-bearings.json` records the actual source mesh
ray checks. `preview-column-supports.png` shows the corrected front colonnade.

## Import handoff

Use the eight `KOL_T1_ROYAL__*.fbx` files in the shared
`exports/kolkata_tier1/` folder at the project root. Select them
together in Studio's File > Import. Scale Unit **Stud**, Scale Factor **1**,
Merge Meshes **off**, Anchored **on**, and scene-origin positioning/pivots.
All sections share the same ground-center origin. Blender front is +Y, up Z;
the FBX is exported Y-up, front -Z. Check the assembled bounding box against
**240 × 297.6 × 210 studs** (width × height × depth).

There are **50 exported mesh objects**, **117,560 assembled triangles** and
**12,900 unique linked-source triangles**. The largest exported mesh has
**5,496 triangles**, below the current Roblox 20,000-per-mesh requirement.
Keep meshes separate: merging the complete building would exceed that limit.

`validation.json` records closed, consistently wound, nondegenerate triangle
geometry in every FBX and a representative Blender re-import. Bounds agree
within 0.000027 stud; imported scales are 1,1,1 and material slots survive.
Re-run with Blender background mode and `../review_assets.py -- royal`.

**Studio import remains unverified; the user will perform it.** A successful
FBX round trip does not prove Studio appearance,
materials, collision or device performance. Use Upload to Roblox **off** for
the first Studio check. The 50 meshes are visual geometry; use simple native
collision at integration, with facade trim noncolliding. There is no full
interior or implemented robbery. Entrance and future service-door metadata
are reserved in `asset.json`.

## Day and night presentation

The day material palette is ochre masonry, lighter stone trim and opaque blue
window surfaces. Blender emission is only a preview aid; recreate desired
night accents in Studio. Focus limited lighting on the entrance portico,
lower colonnade, corner loggias, principal cornices and crown sign. Avoid a
shadow-casting light for every window. Preview rigs are excluded from FBXs.

Current specifications: [Roblox modeling requirements](https://create.roblox.com/docs/art/modeling/specifications)
and [Studio Importer](https://create.roblox.com/docs/studio/importer).
