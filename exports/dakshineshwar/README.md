# Dakshineshwar export kit

Fourteen FBXs: thirteen architecture sections plus **one Shiva temple master**.
The complete twelve-shrine composition is already visible in the editable
Blender source at `../../assets/kolkata/dakshineshwar/`.

Import with scale **1**, unit **Stud**, meshes kept separate, anchored on and
the common authored origin preserved. Do not recenter each section. Use one
opaque material per mesh. Every exported mesh is at most 5,500 triangles.
FBX inventory and a representative Blender round trip passed; actual Studio
import has not been performed for this asset.

Import `KOL_T1_DAKSHINESHWAR__10_Shiva_Temple_Master.fbx` separately at the world
origin, group its four mesh parts as a Model and store that template outside
Workspace. Do not place the template itself in the campus. Clone it to the
twelve positions in `shiva-placements.json`, preserving its imported pivot
offset. `AssembleShivaRow.luau` supplies this operation as an optional
ModuleScript; clones reuse the imported MeshIds.

Both helper files return a function. For a campus assembled at the world
origin, call them in Studio's command bar after putting the ModuleScripts in
ServerStorage (substitute your actual Model names):

```luau
local storage = game:GetService("ServerStorage")
local complex = workspace.Dakshineshwar
require(storage.AssembleShivaRow)(storage.ShivaTemplate, complex, CFrame.identity)
require(storage.InstallNightLights)(complex, CFrame.identity)
```

For a moved or rotated campus, replace `CFrame.identity` with its authored
ground-origin transform. The assembly helper expects an unmoved template
imported at the original world origin. Each helper replaces only its own
previously installed folder and leaves other authored content alone.

`InstallNightLights.luau` creates twenty native lights with one shadow-casting
source and ranges no greater than 60 studs; it does not change global Lighting
or implement a day/night controller. Blender lights are already installed in
the source file. Studio helper execution and visual parity are unverified.

Water datum: local **Y=-5**, river toward **-Z**; ghat front **Z=-133.8**, lowest
tread **Y=-7**. Fill native Terrain water later; no water FBX is included.

Use simplified collision for walkable surfaces and walls; keep ornaments,
murti, rail trim and light fixtures noncolliding. Do not assign convex-hull
collision to whole architecture batches because it can bridge openings.
Runtime collision, streaming, distance visibility and quality scaling belong
to later Studio integration. Counts: **40,772 unique source / 75,580 placed**
visible triangles; one **1,516-triangle Shiva master** reused twelve times.
