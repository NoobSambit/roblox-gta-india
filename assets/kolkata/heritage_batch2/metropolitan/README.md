# Metropolitan Building — Tier 1 heritage exterior

Two commercial street elevations, clipped rounded corner, wraparound balconies, tall clock cupola and two lower satellite cupolas. Carved ornament is simplified.

Editable source: `KOL_T1_METROPOLITAN.blend`. Original review PNGs: `preview-day.png`,
`preview-rear.png`, `preview-night.png`, `preview-night-rear.png`. Repeated bays/columns retain linked
mesh data. `asset.json` contains section exports, assembly transforms, material
roles, collision boxes and recommended night-lighting zones.

Geometry: **16,744 unique source / 90,874
assembled triangles**. Largest exported mesh: **5,500**.
Bounds in studs: {'width': 160.0, 'height': 91.6, 'depth': 116.0}. Unique source counts measure editable
mesh reuse; material/section export batching bakes the assembled geometry.

All FBXs are together in `../../../../exports/kolkata_heritage_batch2/`.
Import files with this asset prefix together at **Stud / scale 1 / Merge Meshes
off / Anchored on**, retaining their common ground origin. Blender front +Y
maps to Roblox -Z. Opaque flat-color materials; no photographic textures.

Night zones: Clock faces and upper cupola ribs; Rounded corner balconies; Two street pediments and ground entrances; avoid lighting every bay. **14 installed Blender
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
`artifacts/references/heritage_batch2/metropolitan/`; they are not redistributed.
Rebuild with the corresponding `metropolitan.py` module through `build.py` in the parent
folder. The older Tier 2 asset is preserved separately.
