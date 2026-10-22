# Kolkata Tier 2 building library — Task 003

**All five assets are created and saved.** This is an exterior asset library; no Studio world placement or gameplay work is included.

Open `Kolkata_Tier2_Library.blend` to access the five independent building scenes, or use each building's individual `.blend`. Full assembled FBX exports are in each `exports/` folder. Preview: [library-review.jpg](../../../artifacts/review/tier2/library-review.jpg).

| Building | Assembled triangles | Shared mesh datablocks | Largest mesh |
| --- | ---: | ---: | ---: |
| Writers' Building | 34,350 | 26 | 3,888 |
| General Post Office | 21,698 | 31 | 3,548 |
| Metropolitan Building | 34,934 | 33 | 1,288 |
| Kolkata Town Hall | 11,092 | 28 | 1,296 |
| Jorasanko Thakur Bari | 48,198 | 47 | 1,516 |

## Approach

22 downloaded photographic references cover the five buildings, with facade, perspective/return and defining-detail views; Jorasanko includes its red exterior and white inner courtyard from several directions. Boards and source records are under `artifacts/references/tier2`. Photographs are reference-only; all exported geometry is original. No external meshes, textures, generators, fonts or Toolbox models are used.

Repeated windows, columns, shutters and railings share source meshes. Sections remain separate; no building is a monolithic mesh. Palette materials are plain colors, with no image textures or Blender-only shader effects. Ornament is reduced to architectural profiles. Rear faces are simplified. See the per-building notes for preserved identity and adaptations.

Jorasanko has a 12-stud entrance passage into an open-to-sky courtyard, paved access around a lawn, shallow gallery floors and a stepped Thakur Dalan. It has no full room network.

## Minimal validation

One saved-source/export inspection checks independent scene files, FBX object completeness and unit scales, sensible bounds and per-mesh triangle counts; results are in `export-check.json`. Reviewed one exterior image for each building plus Jorasanko's courtyard. All exports succeeded. No broad test suite, gameplay testing, benchmarking or city placement was performed.

Actual Studio import/rendering/collision validation remains part of the later integration task. The export configuration follows the corrected Task 002 pipeline: neutral Blender units, unit object scales, FBX Unit Scale, and complete assembled handoffs. Import at Stud / scale factor 1 / Merge Meshes off / Anchored on. Keep repeated mesh IDs shared during assembly, native collision simple and streaming boundaries smaller than a whole district.

## Source of truth

The `.blend` files are editable mesh sources; `build_library.py` and `geometry.py` preserve reproducible generation. `assembly.json` files preserve mesh keys, transforms, palette and collision box specifications. Existing Studio content is untouched. There is no automatic synchronization.
