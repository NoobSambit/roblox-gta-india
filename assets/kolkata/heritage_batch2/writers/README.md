# Writers' Building — Tier 1 heritage exterior

Long red three-register facade, six giant columns, central pediment, raised mansard pavilions, dormers, roof ironwork and original simplified allegorical figures.

Editable source: `KOL_T1_WRITERS.blend`. Original review PNGs: `preview-day.png`,
`preview-rear.png`, `preview-night.png`, `preview-night-rear.png`. Repeated bays/columns retain linked
mesh data. `asset.json` contains section exports, assembly transforms, material
roles, collision boxes and recommended night-lighting zones.

Geometry: **28,344 unique source / 127,040
assembled triangles**. Largest exported mesh: **5,496**.
Bounds in studs: {'width': 326.0, 'height': 85.49, 'depth': 102.0}. Unique source counts measure editable
mesh reuse; material/section export batching bakes the assembled geometry.

All FBXs are together in `../../../../exports/kolkata_heritage_batch2/`.
Import files with this asset prefix together at **Stud / scale 1 / Merge Meshes
off / Anchored on**, retaining their common ground origin. Blender front +Y
maps to Roblox -Z. Opaque flat-color materials; no photographic textures.

Night zones: Six central columns and pediment relief; Mansard pavilion crests and statue groups; Selected ground arches; broad facade washes rather than one light per window. **19 installed Blender
lights** cover front, sides, rear and crowns. The plan is included in `asset.json`.
Lights/camera are excluded from FBX. `InstallHeritageLights.luau` in the export
folder creates the matching native lights later; Studio execution is untested.

The source contains hidden empty-box collision guides, mirrored by
`collisionBoxes` metadata. Rebuild these as simple native collisions later;
keep decorative facade meshes noncolliding. The exterior shell intentionally
has no full room network. `validation.json` records geometry, winding, mesh
limits, one FBX round trip and column-bearing checks. Actual Studio import,
gameplay, collisions and mobile performance were not tested in this asset task.

Reference provenance: `references.json`. Photographs remain local in
`artifacts/references/heritage_batch2/writers/`; they are not redistributed.
Rebuild with the corresponding `writers.py` module through `build.py` in the parent
folder. The older Tier 2 asset is preserved separately.
