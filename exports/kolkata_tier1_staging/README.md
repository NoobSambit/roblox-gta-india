# Completed Tier 1 export staging

One master Blender scene contains **16 completed landmark packages** in a 4×4
inspection grid. This is an offline asset showcase, not Kolkata's city layout.
The original completed masters and exports are unchanged.

The master is `assets/kolkata/tier1_showcase/Kolkata_Tier1_Staging.blend` in the
repository. Its numbered landmark collections include source architecture,
linked repeated meshes, foundation/grounds, fixtures and original collision
guides where present. `PIVOT | <landmark>` moves the entire package: select it
and use Select Hierarchy for whole-landmark selection. Subcollections retain the
authored modular structure. The `00 | Staging presentation` collection holds
only the showcase camera and daylight. Original architectural lights are
retained with render visibility disabled for the daytime showcase.

## Import packages

Each named folder below is independently importable. Import its root FBXs
together with **Stud units, scale 1, Merge Meshes off**. Preserve their common
ground origin and relative transforms. FBX orientation is Roblox Y up, -Z front;
Blender authoring is Z up, +Y front. Staging pivots apply translation only; those
grid translations are absent from the packaged FBXs.

There are **131 default modular FBXs**, plus one optional single-shrine master
under `dakshineshwar/modules/`. No giant scene FBX is supplied. Dakshineshwar's
default row already includes twelve shrines; its master/placement helper offers
an alternative shared-MeshId workflow. Each asset's package manifest uses paths
relative to its own folder and includes the original material, collision,
socket/module and lighting metadata. Keep the sibling `shared/` folder with
the packages; it contains the five image dependencies and existing light helpers.
Images are also packed in the Blender master; completed FBXs were copied
unchanged, except for the existing assembled Shiva row exported at local origin.

| Collection | Landmark / package | Width × height × depth (studs) | Default FBXs |
|---|---|---|---:|
| 01 | [New Market](new_market/README.md) | 310 × 97 × 184 | 7 |
| 02 | [Indian Museum](indian_museum/README.md) | 282 × 64.47 × 218 | 7 |
| 03 | [St Pauls Cathedral](st_pauls/README.md) | 156 × 114.1 × 252 | 7 |
| 04 | [Dakshineshwar](dakshineshwar/README.md) | 418 × 159.6 × 219.853 | 14 |
| 05 | [Writers Building](writers/README.md) | 326 × 85.49 × 102 | 10 |
| 06 | [Metropolitan Building](metropolitan/README.md) | 160 × 91.6 × 116 | 10 |
| 07 | [General Post Office](gpo/README.md) | 160.25 × 99.2 × 149 | 11 |
| 08 | [Town Hall](town_hall/README.md) | 124 × 49.75 × 110 | 9 |
| 09 | [Rajbari Estate](rajbari/README.md) | 202 × 66 × 220 | 6 |
| 10 | [Jorasanko Thakurbari](jorasanko/README.md) | 196 × 51.9 × 282 | 4 |
| 11 | [ITC Sonar](sonar/README.md) | 258 × 81.9 × 228 | 9 |
| 12 | [ITC Royal Bengal](royal/README.md) | 240 × 297.6 × 210 | 8 |
| 13 | [Atmosphere and Deya](atmosphere/README.md) | 292 × 390.258 × 156 | 6 |
| 14 | [Trump Tower Kolkata](trump/README.md) | 142 × 351 × 132 | 5 |
| 15 | [Urbana Seven Towers](urbana/README.md) | 416 × 379 × 304 | 10 |
| 16 | [JW Marriott Kolkata](jw/README.md) | 316 × 251.9 × 236 | 8 |

## Verification and source ownership

The essential pass verified one scene, all 16 asset collections, unit scale,
source geometry/UV/material preservation, repeated linked meshes, unchanged
canonical file hashes, dependency availability and modular FBX geometry/normals.
The measured nearest footprint separation is **218 studs**.
All FBX meshes are below 15,000 triangles; the largest is **11,972**.
Totals: **298,998 unique source / 1,136,464 placed triangles** across the showcase.
The newly exported shrine row passed a Blender round trip with unit scale,
matching bounds, materials and original UV inventory. The overview was visually inspected.
See `validation.json` and `export-manifest.json` for the inventory and hashes.

Canonical per-landmark `.blend` files remain the editable source of truth.
Rebuild this staging copy using `build.py` after future canonical changes.
For deliberate edits to the staging copy, `reexport.py -- KOL_T1_ASSET_ID`
exports only that landmark's named sections into its separate `reexported/`
folder after stripping the grid pivot. Run it with Blender's `--background
--python` arguments; no whole-scene export action is provided.

Native lights, collision settings, streaming and water are later Studio work.
Blender node graphs are preserved in the master but are not executable Studio
materials. This task did not change Studio, place a city, run gameplay checks
or measure device performance. No new architecture, textures or external assets
were produced; provenance remains with the original landmark packages.
