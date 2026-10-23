# Kolkata heritage batch 2 — FBX imports

Import all sections with the same building prefix together: WRITERS,
METROPOLITAN, GPO or TOWN_HALL. Each section contains material-separated mesh
chunks; it is not a separate building to recenter. **Stud / scale 1 / Merge
Meshes off / Anchored on**, common origin preserved. Meshes are at most 5,500
triangles and use opaque flat colors. No textures, preview rigs or water meshes.

Sources, previews, geometry validation and per-building assembly/collision
metadata are in `../../assets/kolkata/heritage_batch2/`. Simple native collision,
distance visibility and light quality scaling belong to later Studio integration.
`InstallHeritageLights.luau` returns a function `(model, assetId, originCFrame)`.
Use the assetId from its `asset.json`, for example `KOL_T1_WRITERS`; origin is
the authored ground-center transform, `CFrame.identity` for an unmoved import.
It creates the same front/side/rear/crown spot-light plan as the Blender source,
without changing global Lighting or adding a day/night controller. Light ranges
are no greater than 60 studs; shadow casting is disabled to control cost.
The helper only replaces its own prior lighting folder. Its Studio execution
and visual parity are untested. No Studio import or device benchmark is claimed.
