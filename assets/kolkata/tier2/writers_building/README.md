# Writers' Building — Tier 2 exterior

Long red three-register frontage, six giant central columns, triangular pediment, mansard roof, dormers and sparse original rooftop figures. Repeated bays share meshes; carved masonry, statues and rear windows are simplified.

## Files

- `WB_writers_building.blend` — independent editable Blender scene, including non-exported presentation and hidden collision guides.
- `exports\WB_writers_building_Roblox.fbx` — **complete assembled visual building**, separated into modular/material meshes. Not an overlapping component library.
- `assembly.json` — pivot, palette, mesh keys, placements and simple collision boxes for later Studio assembly.
- `references.json` — multiple inspected photographic sources. Reference-only; no image is used as a texture or game asset.
- `asset-summary.json` — geometry and file counts.

## Scale and preparation

Authored in studs, Y up in the manifest, front -Z, pivot at ground-level origin. Blender maps `(x,-z,y)`. Scene units None / 1; positive unit object scales; FBX Apply Scalings = FBX Unit Scale, Y Up, no animation. Bounds: [240.0, 68.725, 64.5] studs.

34,350 assembled triangles in 175 mesh objects; 26 unique shared mesh datablocks. Largest mesh: 3,888 triangles. These are file counts, not rendering/FPS measurements.

For later Studio import: Scale Unit **Stud**, Scale Factor **1**, Merge Meshes **off**, Anchored **on**. Reuse matching MeshKeys when placing repetitions, use Automatic render fidelity, disable decorative collision/touch, and rebuild the simple collision boxes natively. Do not use a single convex hull for Jorasanko's courtyard. Presentation objects and collision guides are excluded from the FBX.

No Studio import, city placement, gameplay, mobile or performance test was performed for Task 003. Saved-source/export inspection and a small visual review set are the validation scope. Verify actual Studio appearance, scale and collision when integration is requested.

## Maintenance

`../build_library.py` and `../geometry.py` generate all five assets. Rebuilding replaces generated T2 scenes and these outputs; preserve manual source edits before regenerating. Studio has no automatic synchronization with these files.
