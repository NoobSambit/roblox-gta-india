# Indian Museum, Kolkata

Images 4–5 define the rectangular central entrance pavilion: three deep
ground arches, giant upper columns, tall arched windows and a restrained attic.
Image 6 defines the open quadrangle, two levels of covered exterior arcade,
flat roofline, repeated parapet lights and small central pool. The quadrangle
is compressed and has 13 bays along each long side and seven on each short side.
The ground-level entrance centre connects to the court. Gallery structures
have actual floors/covers and depth; complete galleries and exhibits are absent.
The exterior room volumes can be replaced later while retaining the separate
facades, portico and roof sections. Compact forecourt, lawns, boundary and four
small trees finish the compound. Image 11's different retail-colonnade elevation
was deliberately excluded rather than mixing it into the museum architecture.
The front and side roof panels meet without coplanar overlaps.
Warm ivory wall plaster, pale raised trim, a sandstone plinth, muted taupe
arcade backing and dark green doors/windows separate the registers. Backing
and door panels sit behind the actual covered galleries, adding readable
depth without modelling rooms. This palette follows the user's colour/depth
feedback while retaining the museum's light heritage character.

Night: six frontage washes, two elevated portico-column washes, two side washes,
four court stations, three rear washes and one entrance-vault light. The upper
portico lights avoid relying on ground lights to reach behind projecting cornices.

Building envelope **249.6 × 181.1 × 61.82 studs**; whole plot **282 × 218 × 64.47 studs** (width × depth × height).
Unique source **16,836** triangles; assembled/placed **58,900** triangles.
7 FBX sections; 33 export mesh objects; largest mesh 11,972 triangles.

Open the named master `.blend`. The linked authoring modules are in the source collection. The hidden `80_ExportReady` collection contains baked section/material snapshots; keep it hidden when editing/rendering to avoid duplicate geometry. Preview lights/cameras are separate and excluded from every FBX.

Import all files with this asset prefix together at **Stud / scale 1 / Merge Meshes off / Anchored on**. Preserve the common ground-centre origin and section offsets. Do not centre each section individually. Front is Blender +Y / Roblox -Z. Do not import a whole building as one mesh. See the batch README for materials, collision and streaming guidance.

Materials (original sRGB colours, opaque):

| Slot | Colour | Original texture |
|---|---|---|
| KOL_T1_B4_Brass | #AD925F | None |
| KOL_T1_B4_Dark | #202D30 | None |
| KOL_T1_B4_Glass | #435B60 | None |
| KOL_T1_B4_Glow | #E7C58B | None |
| KOL_T1_B4_Green | #225D49 | None |
| KOL_T1_B4_Iron | #364747 | None |
| KOL_T1_B4_Lawn | #61764B | None |
| KOL_T1_B4_Leaf | #3E6548 | None |
| KOL_T1_B4_LeafLight | #69834E | None |
| KOL_T1_B4_MuseumBand | #C4B18C | None |
| KOL_T1_B4_MuseumRecess | #B3A68F | None |
| KOL_T1_B4_MuseumRoof | #4B5B5D | None |
| KOL_T1_B4_MuseumStone | #A6977D | None |
| KOL_T1_B4_MuseumTrim | #EDE5D1 | None |
| KOL_T1_B4_MuseumWall | #CDBE9F | ../textures/B4_MuseumWall.png |
| KOL_T1_B4_Paving | #ACA38E | None |
| KOL_T1_B4_Water | #5E9EA5 | None |
| KOL_T1_B4_Wood | #624E3C | None |

Recommended Roblox light stations, relative to the shared ground origin. Coordinates are **X, Y-up, Z studs**. `asset.json` includes target, RGB, suggested brightness, range, angle and shadows for each station. These are tuning starting points, not a tested Studio lighting configuration. Blender preview watts do not convert to Roblox brightness.

| Station | Position | Aim target | Range |
|---|---|---|---:|
| Street_uplight_-108 | [-108, 0.4, -96] | [-108, 34, -83] | 48 |
| Street_uplight_-68 | [-68, 0.4, -96] | [-68, 34, -83] | 48 |
| Street_uplight_-32 | [-32, 0.4, -96] | [-32, 34, -83] | 48 |
| Street_uplight_32 | [32, 0.4, -96] | [32, 34, -83] | 48 |
| Street_uplight_68 | [68, 0.4, -96] | [68, 34, -83] | 48 |
| Street_uplight_108 | [108, 0.4, -96] | [108, 34, -83] | 48 |
| Portico_giant_column_-1 | [-15, 25, -95] | [-12, 49, -87] | 32 |
| Side_wash_-1 | [-132, 0.4, 5] | [-124, 35, 5] | 46 |
| Portico_giant_column_1 | [15, 25, -95] | [12, 49, -87] | 32 |
| Side_wash_1 | [132, 0.4, 5] | [124, 35, 5] | 46 |
| Court_arcade_-68_-44 | [-68, 0.45, -44] | [-68, 30, -53.0] | 40 |
| Court_arcade_68_-44 | [68, 0.45, -44] | [68, 30, -53.0] | 40 |
| Court_arcade_-68_44 | [-68, 0.45, 44] | [-68, 30, 53.0] | 40 |
| Court_arcade_68_44 | [68, 0.45, 44] | [68, 30, 53.0] | 40 |
| Entrance_vault | [0, 22, -77] | [0, 4, -85] | 25 |
| Rear_institution_wash_-75 | [-75, 0.4, 100] | [-75, 35, 86] | 44 |
| Rear_institution_wash_0 | [0, 0.4, 100] | [0, 35, 86] | 44 |
| Rear_institution_wash_75 | [75, 0.4, 100] | [75, 35, 86] | 44 |

All proposed lights have shadows disabled. Use warm architectural light with limited overlap. Enable lights only during the later authored night period; no runtime scripts or native light instances are included here. Preserve soft ambient readability when tuning.

Essential geometry/normal checks, triangle/FBX inventory, UV/material presence and one representative section scale round trip passed; see `validation.json`. Original final hero/elevated/grounds/night PNGs plus a reverse night view are beside this file. Actual Studio import, collisions and device performance remain unverified, as this task excludes integration.
