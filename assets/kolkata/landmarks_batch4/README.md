# Kolkata Tier 1 landmarks — Batch 4

Three independent exterior landmark packages: New Market / Sir Stuart Hogg Market,
Indian Museum and St. Paul's Cathedral. No Studio integration, district assembly,
gameplay, complete interiors, or changes to earlier landmark batches are included.

Open the master `.blend` in each asset folder, or `Batch4_Live.blend` and choose a
landmark scene. The latter is a review library, not a city layout. Four required
PNG views plus a reverse night view per asset and `contact-sheet.png` provide
the review set. The two night bearings show lighting on all four elevations.

| Landmark | Building W×D×H studs | Plot W×D×H studs | Unique tris | Placed tris | FBXs |
|---|---|---|---:|---:|---:|
| New Market — Sir Stuart Hogg Market | 279.05 × 148.04 × 94.95 | 310 × 184 × 97 | 11,960 | 39,124 | 7 |
| Indian Museum, Kolkata | 249.6 × 181.1 × 61.82 | 282 × 218 × 64.47 | 16,836 | 58,900 | 7 |
| St. Paul's Cathedral, Kolkata | 102.1 × 198.75 × 111.65 | 156 × 252 × 114.1 | 19,812 | 46,296 | 7 |

Batch: **48,608 unique / 144,320 placed triangles**. Unique counts
measure linked source reuse; placed counts measure the FBX geometry actually
exported. Source counts are below the preferred 53–85k allowance; no extra detail
was added merely to exhaust it. Placed cost exceeds the preferred 125k upper end
but stays below the 145k soft review threshold. The retained museum quadrangle
and its two levels of exterior arcades account for much of that cost. These
are mesh counts, not device benchmarks.

All **21 modular FBXs** are in
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
