# New Market — Sir Stuart Hogg Market

Images 7–10 and 12 define the red market frontage, repeated gables, roof sheds,
iron verandah and off-axis clock tower. The entrance elevation follows image 10,
with the tower on the viewer's right. The tower has four clock faces, green
louvred crown, corner pinnacles, stone bands and shuttered openings. The clock
hands are static geometry. The major entrance and covered street arcade have
actual depth; dark closures end the exterior package. Shed ends are enclosed.
The revised main portal is 22 studs wide and 18 studs deep, with stone jambs,
keystone, a larger projecting iron canopy, two levels of entrance lettering and
a distinct paved approach. The lower verandah stops at the entrance. Roof ends
now extend into both facade wall thicknesses, closing the former front/rear
strips; no floating inner parapet posts remain in the gap.
The semicircular upper fanlight is smaller, lowered and centred with a shared
spoke origin and clear brick margins beneath both gable slopes. A separate
pavilion roof covers the entrance passage and joins the main roof mass.
The rear/side ranges retain arches and the brick/material rhythm with simpler
detail. Forecourt paving, low kerbs, bollards and edge planters finish the plot.
No bazaar, neighbourhood or complete marketplace interior is included.

Night: ground fixtures light entry bays; fixtures on the verandah roof reach
the gables without the canopy blocking them. Clock washes mount at the upper
tower bands; a separate wash reaches the green crown. Two rear washes support
the return elevation; two washes on each side cover the side ranges. Keep the
clock faces opaque ivory, not Neon. The reverse night preview checks the rear
and opposite side in addition to the primary night view.

Building envelope **279.05 × 148.04 × 94.95 studs**; whole plot **310 × 184 × 97 studs** (width × depth × height).
Unique source **11,960** triangles; assembled/placed **39,124** triangles.
7 FBX sections; 31 export mesh objects; largest mesh 6,432 triangles.

Open the named master `.blend`. The linked authoring modules are in the source collection. The hidden `80_ExportReady` collection contains baked section/material snapshots; keep it hidden when editing/rendering to avoid duplicate geometry. Preview lights/cameras are separate and excluded from every FBX.

Import all files with this asset prefix together at **Stud / scale 1 / Merge Meshes off / Anchored on**. Preserve the common ground-centre origin and section offsets. Do not centre each section individually. Front is Blender +Y / Roblox -Z. Do not import a whole building as one mesh. See the batch README for materials, collision and streaming guidance.

Materials (original sRGB colours, opaque):

| Slot | Colour | Original texture |
|---|---|---|
| KOL_T1_B4_Brass | #AD925F | None |
| KOL_T1_B4_Brick | #A74634 | ../textures/B4_Brick.png |
| KOL_T1_B4_BrickLight | #B45540 | None |
| KOL_T1_B4_Dark | #202D30 | None |
| KOL_T1_B4_Glass | #435B60 | None |
| KOL_T1_B4_Glow | #E7C58B | None |
| KOL_T1_B4_Green | #225D49 | None |
| KOL_T1_B4_Iron | #364747 | None |
| KOL_T1_B4_Ivory | #DFD3B6 | None |
| KOL_T1_B4_Lawn | #61764B | None |
| KOL_T1_B4_Paving | #ACA38E | None |
| KOL_T1_B4_Slate | #515C59 | None |
| KOL_T1_B4_Stone | #D2D0BE | ../textures/B4_Stone.png |
| KOL_T1_B4_Trim | #E8E2CE | None |

Recommended Roblox light stations, relative to the shared ground origin. Coordinates are **X, Y-up, Z studs**. `asset.json` includes target, RGB, suggested brightness, range, angle and shadows for each station. These are tuning starting points, not a tested Studio lighting configuration. Blender preview watts do not convert to Roblox brightness.

| Station | Position | Aim target | Range |
|---|---|---|---:|
| Frontage_wash_-113 | [113, 0.5, -73] | [113, 15, -57] | 42 |
| Gabled_frontage_-113 | [113, 17.7, -65] | [113, 30, -57] | 27 |
| Frontage_wash_-62 | [62, 0.5, -73] | [62, 15, -57] | 42 |
| Gabled_frontage_-62 | [62, 17.7, -65] | [62, 30, -57] | 27 |
| Frontage_wash_15 | [-15, 0.5, -73] | [-15, 15, -57] | 42 |
| Gabled_frontage_15 | [-15, 17.7, -65] | [-15, 30, -57] | 27 |
| Frontage_wash_69 | [-69, 0.5, -73] | [-69, 15, -57] | 42 |
| Gabled_frontage_69 | [-69, 17.7, -65] | [-69, 30, -57] | 27 |
| Entrance_canopy | [27, 15, -67] | [27, 7, -62] | 23 |
| Clock_tower_0_-21 | [-128, 57, -70] | [-128, 75, -49] | 36 |
| Clock_tower_21_0 | [-149, 57, -49] | [-128, 75, -49] | 36 |
| Clock_tower_0_21 | [-128, 57, -28] | [-128, 75, -49] | 36 |
| Clock_tower_-21_0 | [-107, 57, -49] | [-128, 75, -49] | 36 |
| Crown_wash | [-128, 79, -67] | [-128, 87, -49] | 25 |
| Rear_range_-90 | [90, 0.5, 80] | [90, 23, 68] | 38 |
| Rear_range_65 | [-65, 0.5, 80] | [-65, 23, 68] | 38 |
| Side_range_-1_-28 | [144, 0.5, -28] | [136, 23, -28] | 37 |
| Side_range_-1_35 | [144, 0.5, 35] | [136, 23, 35] | 37 |
| Side_range_1_-28 | [-144, 0.5, -28] | [-136, 23, -28] | 37 |
| Side_range_1_35 | [-144, 0.5, 35] | [-136, 23, 35] | 37 |
| Entrance_portal_wash | [27, 1, -79] | [27, 23, -59] | 34 |

All proposed lights have shadows disabled. Use warm architectural light with limited overlap. Enable lights only during the later authored night period; no runtime scripts or native light instances are included here. Preserve soft ambient readability when tuning.

Essential geometry/normal checks, triangle/FBX inventory, UV/material presence and one representative section scale round trip passed; see `validation.json`. Original final hero/elevated/grounds/night PNGs plus a reverse night view are beside this file. Actual Studio import, collisions and device performance remain unverified, as this task excludes integration.
