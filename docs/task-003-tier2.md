# Task 003 — Tier 2 Kolkata asset library

Completed in Blender, with no Studio integration or map placement.

The five requested folders under `assets/kolkata/tier2/` contain independent editable `.blend` scenes, complete assembled FBX exports, mesh/placement/collision metadata, references and short import notes. The master `Kolkata_Tier2_Library.blend` contains all five asset scenes and preserves the original startup workspace. Blender is left showing GPO.

| Asset | Assembled triangles | Unique source meshes |
| --- | ---: | ---: |
| Writers' Building | 34,350 | 26 |
| Kolkata GPO | 21,698 | 31 |
| Metropolitan Building | 34,934 | 33 |
| Kolkata Town Hall | 11,092 | 28 |
| Jorasanko Thakur Bari | 48,198 | 47 |

Jorasanko includes a 12-stud entrance passage, open courtyard, shallow galleries and Thakur Dalan. None of the assets contains a full interior room network. Rear surfaces, capitals, sculpture, railings and shutter detail are simplified; repeated facade modules share mesh data. There are no image textures or imported third-party meshes.

22 downloaded photographs were visually inspected on reference boards, covering frontages, corners/returns, roof details and Jorasanko courtyard views. Some Commons requests were rate limited; alternate photographic sources and cached Commons photos provided the final reference set. Sources remain reference-only and are recorded under `artifacts/references/tier2/`.

Minimal validation: source files opened for scene-metadata inspection, sensible dimensions and positive unit scales checked, FBX export success and object completeness checked, largest mesh below the documented 20k triangle limit. The FBX files use the corrected Task 002 unit pipeline: neutral Blender units / scale 1, FBX Unit Scale. All five export inspections passed; largest individual mesh is 3,888 triangles. Visual authoring review comprises one exterior per asset and one additional courtyard image. Results: `assets/kolkata/tier2/export-check.json`.

Preview sheet: `artifacts/review/tier2/library-review.jpg`.

Actual Studio import appearance, final collision/query settings, streaming groups, asset-ID deduplication and device rendering cost are deliberately deferred to a later integration task. Import at Stud / factor 1 / Merge Meshes off / Anchored on. Use matching MeshKeys to preserve reuse and native collision boxes from assembly metadata. Do not make Jorasanko one convex collider that blocks the courtyard.

The generator owns the authored T2 scenes and generated files. Preserve manual edits before rerunning it. Studio remains the source of truth for the integrated world; there is no automatic sync.

## Pillar supports and minimal foundations
Writers central columns now rest on a projecting arcade/podium with grounded masonry piers. Metropolitan’s four major balcony columns now have supporting lower-storey piers and continuous base slabs. GPO’s straight and curved colonnades share connected low platforms. All five buildings have shallow stone foundations, with a visible top 0.65 studs above origin. Jorasanko retains its open entrance and courtyard. Updated independent sources, assembled FBX exports, metadata, master library and previews. Only the existing saved/export sanity inspection was rerun; no Studio or gameplay testing.
