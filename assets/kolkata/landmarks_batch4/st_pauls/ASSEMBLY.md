# St. Paul's Cathedral, Kolkata

Images 1–3 define the long nave, projecting transept, tall square crossing
tower, crenellated parapets, stepped buttresses and pinnacle/spirelet silhouette.
The supplied present-day photos take precedence over a generic needle spire.
The nave, transept and tower remain separate editable structures. Pointed
windows have shallow glass, lancets, transoms and small rose tracery; the larger
end windows receive more detail. The side entrance porch has an actual pointed
opening and covered depth. Main interior space is unfurnished and undetailed;
no pews, elaborate nave interior or gameplay has been created. Lawn strips,
paths, four trees, benches and a low boundary keep the compound compact.
The user's additional facade photograph informed a restrained extra detail
pass: recessed panels on the stepped buttresses, crockets on the four tower
pinnacles and small porch pinnacles. Continuous annular trim removes hidden
internal segment caps to offset the added detail's placed cost.

Night: six nave washes, two transept washes, west/east end washes, three elevated
tower/pinnacle washes and one porch light. Mount upper tower lights to the
transept roof/appropriate brackets, then tune their aim after import. Keep
roof/window values darker than the pale masonry and avoid glowing entire walls.

Building envelope **102.1 × 198.75 × 111.65 studs**; whole plot **156 × 252 × 114.1 studs** (width × depth × height).
Unique source **19,812** triangles; assembled/placed **46,296** triangles.
7 FBX sections; 32 export mesh objects; largest mesh 11,856 triangles.

Open the named master `.blend`. The linked authoring modules are in the source collection. The hidden `80_ExportReady` collection contains baked section/material snapshots; keep it hidden when editing/rendering to avoid duplicate geometry. Preview lights/cameras are separate and excluded from every FBX.

Import all files with this asset prefix together at **Stud / scale 1 / Merge Meshes off / Anchored on**. Preserve the common ground-centre origin and section offsets. Do not centre each section individually. Front is Blender +Y / Roblox -Z. Do not import a whole building as one mesh. See the batch README for materials, collision and streaming guidance.

Materials (original sRGB colours, opaque):

| Slot | Colour | Original texture |
|---|---|---|
| KOL_T1_B4_Dark | #202D30 | None |
| KOL_T1_B4_Glass | #435B60 | None |
| KOL_T1_B4_Glow | #E7C58B | None |
| KOL_T1_B4_GothicRecess | #9EA494 | None |
| KOL_T1_B4_Iron | #364747 | None |
| KOL_T1_B4_Ivory | #DFD3B6 | None |
| KOL_T1_B4_Lawn | #61764B | None |
| KOL_T1_B4_Leaf | #3E6548 | None |
| KOL_T1_B4_LeafLight | #69834E | None |
| KOL_T1_B4_Paving | #ACA38E | None |
| KOL_T1_B4_Plaster | #E2DCCB | ../textures/B4_Plaster.png |
| KOL_T1_B4_Slate | #515C59 | None |
| KOL_T1_B4_Stone | #D2D0BE | ../textures/B4_Stone.png |
| KOL_T1_B4_Trim | #E8E2CE | None |
| KOL_T1_B4_Wood | #624E3C | None |

Recommended Roblox light stations, relative to the shared ground origin. Coordinates are **X, Y-up, Z studs**. `asset.json` includes target, RGB, suggested brightness, range, angle and shadows for each station. These are tuning starting points, not a tested Studio lighting configuration. Blender preview watts do not convert to Roblox brightness.

| Station | Position | Aim target | Range |
|---|---|---|---:|
| Nave_wash_-1_-79 | [-36, 0.4, -79] | [-26, 35, -79] | 42 |
| Nave_wash_-1_-24 | [-36, 0.4, -24] | [-26, 35, -24] | 42 |
| Nave_wash_-1_79 | [-36, 0.4, 79] | [-26, 35, 79] | 42 |
| Transept_wash_-1 | [-61, 0.4, 40] | [-49, 49, 40] | 58 |
| Nave_wash_1_-79 | [36, 0.4, -79] | [26, 35, -79] | 42 |
| Nave_wash_1_-24 | [36, 0.4, -24] | [26, 35, -24] | 42 |
| Nave_wash_1_79 | [36, 0.4, 79] | [26, 35, 79] | 42 |
| Transept_wash_1 | [61, 0.4, 40] | [49, 49, 40] | 58 |
| West_window | [0, 0.4, -110] | [0, 42, -96] | 54 |
| East_window | [0, 0.4, 110] | [0, 40, 96] | 54 |
| Tower_pinnacle_-1 | [-28, 54, 40] | [-8, 103, 40] | 60 |
| Tower_pinnacle_1 | [28, 54, 40] | [8, 103, 40] | 60 |
| Tower_front | [0, 53, 17] | [0, 90, 28] | 48 |
| Porch_entry | [43, 13, -59] | [37, 3, -59] | 18 |

All proposed lights have shadows disabled. Use warm architectural light with limited overlap. Enable lights only during the later authored night period; no runtime scripts or native light instances are included here. Preserve soft ambient readability when tuning.

Essential geometry/normal checks, triangle/FBX inventory, UV/material presence and one representative section scale round trip passed; see `validation.json`. Original final hero/elevated/grounds/night PNGs plus a reverse night view are beside this file. Actual Studio import, collisions and device performance remain unverified, as this task excludes integration.
