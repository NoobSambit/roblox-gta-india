# Kolkata Tier 1 heritage batch 2

Four exterior landmarks, each with its own editable blend, reference notes,
original front/rear day/night PNGs, counts, collision guides and modular exports.
The supplied photos define the architecture. ImageGen was unnecessary.

| Asset | Unique source tris | Assembled tris | FBXs |
|---|---:|---:|---:|
| Writers' Building | 28,344 | 127,040 | 10 |
| Metropolitan Building | 16,744 | 90,874 | 10 |
| General Post Office | 11,742 | 51,726 | 11 |
| Kolkata Town Hall | 8,564 | 36,520 | 9 |

Total: **65,394 unique / 306,160 placed triangles**.
The unique total is within the 47k–76k batch target and below the 85k soft threshold.
Source reuse and assembled export cost are reported separately; these are not device benchmarks.

Open `Heritage_Batch2_Live.blend` and choose a KOL_T1 scene from the scene selector.
It contains only this four-building asset library, not a district layout.
All FBXs are in `../../../exports/kolkata_heritage_batch2/`.
Keep each building’s section files aligned at their common ground origin.
Import at Stud/1, meshes separate, anchored. Source front +Y becomes Roblox -Z.
Every exported mesh is capped at 5,500 triangles. Preserve the opaque material slots.

Working Blender lights cover every elevation and the major crowns, with a native
Studio light installer supplied beside the FBXs. Lights and review rigs are excluded
from mesh exports. No day/night gameplay system, Studio integration, full interiors
or gameplay was built. Actual Studio collision/appearance and device performance remain
unverified. The source files/generation modules own these assets; there is no automatic
Studio synchronization. Older Tier 2 versions are preserved.

Build with Blender `--python-exit-code 1 --python build.py`; review with
`--python-exit-code 1 --python review.py`. Run `python package.py` for notes/manifests.
One focused source/FBX and bearing check plus front/rear day/night review per building is the
validation scope. Original geometry/materials only; no external model/texture dependency.
