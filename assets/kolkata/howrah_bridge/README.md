# Howrah Bridge and Kolkata riverfront library — Task 005

Completed Blender asset-generation milestone: **26 independently reusable assets**.
No Studio placement, water body, gameplay or performance benchmark is included.

## Review

- Howrah Bridge: [quarter view](bridge/KOL_HBR_HOWRAH/preview.png), [side silhouette](bridge/KOL_HBR_HOWRAH/preview-side.png), [roadway](bridge/KOL_HBR_HOWRAH/preview-road.png).
- One upgraded Kolkata Ganga ghat: [river-facing steps](ghat/KOL_HBR_GHAT/preview.png), [horizontal road entrance](ghat/KOL_HBR_GHAT/preview-road.png).
- [Fifteen-prop sheet](review/props-library.png) and [support/context sheet](review/riverfront-and-context.png).

Every asset also has its own original PNG beside its `.blend` and `.fbx`.
Original PNGs are tracked in Git. Downloaded photographic references are local only.

## Geometry inventory

| Category | Assets | Full assembled triangles | Unique source triangles |
|---|---:|---:|---:|
| Howrah Bridge | 1 | 40,024 | 21,708 |
| Major ghat | 1 | 11,936 | 7,672 |
| Riverfront / approach modules | 7 | 9,064 | 3,684 |
| Prop library | 15 | 4,584 | 4,584 |
| Minimal context shells | 2 | 264 | 264 |

All category budgets are met. Assembled totals include **all repeated components**.
Unique counts count a shared mesh once per asset, not once per entire city.
The largest individual mesh is **2,112 triangles**, below the project's preferred
10,000 and the documented Roblox individual import ceiling of 20,000.

The bridge has seven manageable 128-stud groups across 28 bays, separate road
and pedestrian surfaces, twin cantilever peaks, portal frames and simplified
laced members. There are **no exposed piers in the river opening**. Small end
bearing shoes belong at the future bank/approach interfaces.

The single ghat interprets examined Ahiritola, Bagbazar and Baje Kadamtala photos:
broad bathing steps, landing terraces, three open barrel canopies and two small
side shade bays. Its road side has a **104-stud horizontal entrance entablature
over three open archways**, substantial masonry piers and buried shallow footings.
There are no windows, upper storey, enclosed rooms or red building facade.

## Sources, exports and reuse

- [Master Blender library](Howrah_Riverfront_Library.blend): 26 separate scenes; opens on the ghat.
- [Asset index](asset-index.md): dimensions, counts and individual source/export/PNG links.
- [Machine-readable manifest](asset-manifest.json): materials, references, sockets, collision recommendations and assembly transforms.
- Each category/asset folder contains the individual `.blend`, assembled `.fbx`, `asset.json` and preview PNGs.

Linked mesh datablocks are preserved as shared FBX Geometry definitions:
the bridge has **25 unique meshes / 91 instances**. MeshKeys and assembly
transforms identify repeated components for later Studio reuse. Import each
unique asset once, then reuse its MeshIds; do not repeatedly import copies for
every placement. Confirm the importer's resulting MeshId reuse during assembly.

All source objects are meshes with unit scale and no live modifiers. Intentional
module translations/yaws remain editable. Triangles/quads, outward closed solids
and simple opaque `HBR_*` palette materials are used. There are **no image texture
dependencies**, Blender-only shader effects, animations or water meshes.
Closed components can intersect at structural joints; these are grouped solids,
not boolean-unioned architectural scans.

## Placement conventions for the next milestone

The established pipeline is unchanged in units/axes: one neutral Blender unit
represents one Roblox stud; Roblox X right, Y up, front -Z maps to Blender
`(x, -z, y)`. Export uses FBX Unit Scale, forward -Z / up Y, without animation.
Origins use useful ground/water datums; exact sockets/bounds are in the manifest.

- Future Terrain Water surface: **Y=0**. No water is delivered in Blender.
- Bridge: 896 studs long, 60-stud road, two 10-stud sidewalks; road top Y=32,
  pedestrian top Y=33. Approach ends Z=±448. Keep overhead clearance when placing.
- Approach ramp: 128 studs long, connects road top Y=32 to Y=13.5.
- Ghat promenade and street: **Y=13.5**; lowest river landing Y=1.
  Road socket `[0,13.5,66]`. Street apron underside Y=12.7 is shallow enough
  to embed in the road bank; the river-bank foundation is separate.
- Rail/promenade/retaining modules can extend the immediate environment without
  creating a district. Boats are static visual props with waterline origins.

For Studio, anchor static scenery and use box/ramp collision proxies for deck,
sidewalks, stairs, landings and retaining edges. Use boxes for substantial columns
and entrance piers; avoid convex collision spanning the open archways. Keep fine
truss lacing, balusters, canopy shells, signs and small trim noncollidable. Use a
smooth stair ramp proxy, with deliberate landings, to reduce snagging. Review
raycast/query requirements when assigning collision settings. Collision geometry
and Terrain Water are **recommendations for later integration**, not authored
Studio changes in this milestone.

## Minimum validation performed

[validation.json](validation.json) records the required inventory:

- All 26 independent source files were reopened, their mesh inventory/counts
  checked, and saved as normal Blender projects; the master has 26 scenes.
- Scale, finite geometry, triangle budgets, nonzero faces, closed manifold
  components and outward consistent normals checked. No live modifiers or image
  texture dependencies found.
- All 26 actual FBX files parsed successfully. Geometry/instance totals match
  source counts, linked geometry is retained, and every mesh instance has exactly
  one valid palette material binding to slot 0.
- Assigned reference IDs resolve to locally retrieved, examined photos.
- All 29 individual original preview PNGs exist. The two review sheets, bridge
  views and final ghat views were visually inspected; observed overlaps/gaps were
  fixed before final delivery.

Blender 5.2's FBX exporter prints a material-index warning when a linked mesh's
same material is encountered again. The installed exporter branch was inspected:
it warns on an already registered material, even with the same slot layout.
The exported slot indices and one-material-per-model connections were explicitly
audited and passed. This warning did not prevent any export.

**Studio import, appearance, collision behaviour and real device FPS remain
unverified.** This task deliberately stops at the asset-library boundary.
There were no failed exports or category budget exceedances.

## Maintenance and provenance

Builders: `build_bridge.build()`, `build_ghat.build()`, `build_support.build()`,
`build_support.context()` and `prop_shapes.build()`, run in Blender with this
directory on `sys.path`. They modify Task 005 scenes only. `pipeline.py` owns
units/export/materials and `howrah_geometry.py` owns efficient primitive geometry.

After an intentional rebuild: render the changed category with
`render_previews.render_category(category)`, run `python delivery_index.py` to
refresh preview links/index/sheets, run `validate_assets.check(require_previews=True)`
in Blender, then `package_blends.package()` to package the individual sources and
master. Avoid rerunning builders over manual edits; editable `.blend` files are
also delivered for direct work.

Reference page/image URLs are preserved in [references/catalogue.json](references/catalogue.json)
and the retrieval/supplement manifests. Retrieval failures are recorded, not
presented as examined references. Photographs were studied for architecture and
proportions, not copied as textures. No third-party meshes, textures, code packages
or fonts are incorporated into the game assets. Photo rights remain with their
respective owners; downloads are excluded from Git.

Official constraints consulted: [Roblox mesh specifications](https://create.roblox.com/docs/art/modeling/specifications),
[export requirements](https://create.roblox.com/docs/art/modeling/export-requirements)
and [performance guidance](https://create.roblox.com/docs/performance-optimization/improve).

Current Task 005 delivery is approximately **22 MB**, with the largest file
approximately **1.4 MiB**. This is below GitHub's 50 MiB file warning and 100 MiB
file block thresholds. See [GitHub's large-file guidance](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).
Normal Git is sufficient for this delivery; use LFS before substantially larger
or frequently revised binaries grow repository history.
