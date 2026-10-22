# Jorasanko Thakur Bari — Tier 2 exterior

Red/green outer elevations, white inner galleries and a five-arched Thakur Dalan. A real 12-stud-wide ground-level entry opens into the courtyard, with shallow gallery slabs, lawn and paved circulation. Closed room volumes contain no room network; full interiors are not authored.

## Files

- `JTB_jorasanko_thakur_bari.blend` — independent editable Blender scene, including non-exported presentation and hidden collision guides.
- `exports\JTB_jorasanko_thakur_bari_Roblox.fbx` — **complete assembled visual building**, separated into modular/material meshes. Not an overlapping component library.
- `assembly.json` — pivot, palette, mesh keys, placements and simple collision boxes for later Studio assembly.
- `references.json` — multiple inspected photographic sources. Reference-only; no image is used as a texture or game asset.
- `asset-summary.json` — geometry and file counts.

## Scale and preparation

Authored in studs, Y up in the manifest, front -Z, pivot at ground-level origin. Blender maps `(x,-z,y)`. Scene units None / 1; positive unit object scales; FBX Apply Scalings = FBX Unit Scale, Y Up, no animation. Bounds: [134.0, 38.4, 114.0] studs.

48,198 assembled triangles in 297 mesh objects; 47 unique shared mesh datablocks. Largest mesh: 1,516 triangles. These are file counts, not rendering/FPS measurements.

For later Studio import: Scale Unit **Stud**, Scale Factor **1**, Merge Meshes **off**, Anchored **on**. Reuse matching MeshKeys when placing repetitions, use Automatic render fidelity, disable decorative collision/touch, and rebuild the simple collision boxes natively. Do not use a single convex hull for Jorasanko's courtyard. Presentation objects and collision guides are excluded from the FBX.

No Studio import, city placement, gameplay, mobile or performance test was performed for Task 003. Saved-source/export inspection and a small visual review set are the validation scope. Verify actual Studio appearance, scale and collision when integration is requested.

## Maintenance

`../build_library.py` and `../geometry.py` generate all five assets. Rebuilding replaces generated T2 scenes and these outputs; preserve manual source edits before regenerating. Studio has no automatic synchronization with these files.
