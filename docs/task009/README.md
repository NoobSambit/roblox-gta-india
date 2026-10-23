# Task 009 — two-storey Victoria museum

**Status: Blender source and the revised import batch are saved. Two-storey Studio integration, final Studio reviews and final engine recovery remain pending.** Hood Testing is currently disconnected. The previous single-floor Studio finishing pass is not the completed revision.

## Authored layout

The original `assets/victoria-memorial/VictoriaMemorial.blend` now contains the rebuilt interior. The approved facade, dome, towers and landmark placement remain intact. Interior-only arcades, linings, wing envelopes, vault ribs and stair transitions were reconstructed. Original replaced interior objects remain in the unlinked `VM009_ArchivedInterior` collection; `two-storey-manifest.json` records them.

Queen’s Hall retains its memorial plinth, radial floor, original upper dome and a 46-stud-wide central void. A traversable annular balcony surrounds that void. Two mirrored eight-and-a-half-stud-wide dogleg stairs connect ground and upper levels. Upper wing entrances have actual paired openings, not decorative door outlines.

The seven ground-floor roles, eighteen original loot coordinates/IDs, nine original security reservations and four exterior routes remain the foundation. Ten upper exhibits (`VIC_LOOT_019`–`028`) and seven upper security reservations extend the **same future event**, `VIC_HEIST_007`. Eight upper zone definitions include the overlook, two landings, four galleries and a security-only screening room. Decorative courtyards and passages do not gain arbitrary loot.

Precise Roblox-stud coordinates, stair footprints, paired openings and the connection graph are in `assets/victoria-memorial/interior/layout-lock.json` and `authoring/task009/final-plan.json`. Blender coordinates are `(x,-z,y)`. The Studio site is `(820,0,0)` rotated +90° about Y; one Blender authoring unit equals one Roblox stud.

## Room composition and corrections

| Area | Final source direction |
| --- | --- |
| Queen’s Hall | Open memorial composition; repaired two-level arcade, curved balcony and stronger low-poly memorial figure on the preserved plinth |
| Public | Broad low display groupings, documents and a clear walking lane |
| Collections | Grouped historical cases and wall framing, separate from painting-only presentation |
| Painting | Painting monoliths and wall art, continuous teal runner with double brass edge; no sculpture/boat island |
| Sculpture | Gilded abstract knot, handled teal vessel and stronger sculptural focal pieces |
| High security | Premium cases, restrained oxblood and inactive equipment with open obstacle lanes |
| Archive | Open charter and ceremonial collection; cabinet fronts face the room and fit between pilasters |
| Upper Treasury / Royal | Larger charter, regalia and crown compositions; optional security-only approach to Treasury |
| Upper River / Craft | River-trade model and portfolio / gilded craft and teal vessel; distinct exhibits and wall treatment |

User-reported clashes were corrected: upper rib/ceiling intersections, wall paintings crossing pilasters or banners, reversed archive cabinets, clipped end-wall banners and exposed original window trim. Ground paired passages remain ten studs wide; upper wing openings are twelve studs wide. Courtyard rectangular gaps above the original arches now receive fitted spandrels and stepped thresholds. Intended open-air quadrangles remain open.

The latest user explicitly authorized a grounds revision. Four low planter islands, eight facing benches and four interpretation stands furnish the two checkerboard quadrangles without occupying the central escape axis. Twenty-four additional trees reuse the original GardenTree meshes. Grounds receive grass/sandstone/stone colour separation; existing fence pieces are raised to a maximum 7.14 studs while retaining gate gaps. This is an authorized change to grounds, not an unchanged-grounds claim. Facade geometry is checked separately.

## Materials and lighting

Warm ivory limestone, differentiated pale masonry, a shared subtle stone floor, charcoal furniture, muted brass, teal fabric and selective oxblood form the palette. Existing four original 480×320 painting images remain flat 3:2 artwork. The two existing Task009 material uploads are retained: floor `111127937664295`, wall `74587698959678`. Revised Studio appearance is not yet verified.

There are **52 authored light stations**, including gallery, stair and courtyard lights. Queen’s Hall has independent lower fill, balcony lamps, six high-arcade washes, six clerestory uplights and three dome washes. Lower fixtures are not expected to illuminate the 112-stud dome. Only two lights request Roblox shadows; upper washes use bounded ranges and no shadows. No city-wide Lighting settings are changed by the integration script.

`render_lighting_review.py` excludes the Blender presentation lamps and uses the actual authored museum lights. These renders demonstrate source lighting coverage; Blender watts do not establish Roblox brightness or device performance. Studio light tuning remains necessary after integration.

## Geometry and reuse

Current source counts are generated in `source-statistics.json`:

| Measure | Count |
| --- | ---: |
| New modular designs | 24 |
| New unique design triangles | 6,784 |
| Used imported designs, including Task008 | 44 |
| Used unique imported triangles | 9,780 |
| Imported placed instances / triangles | 268 / 50,572 |
| Reused original trees / placed triangles | 24 / 5,376 |
| Native visible geometry estimate | 2,616 |
| Total visible additive estimate | **58,564** |
| Separate invisible collision estimate | 1,440 |
| Largest new material mesh | 576 triangles |

The visible estimate excludes the preserved shell. Collision is reported separately; these are authoring counts, not GPU measurements or a device guarantee. Modules share MeshIds after adoption; new designs contain 69 material/component meshes. Transparent cases remain restrained. Architectural details are concentrated in the arcade, stairs, vault transitions and balcony rather than micro-ornament.

## References, tooling and recovery

Selected concepts live in `assets/victoria-memorial/interior/task009/lookdev/`. Full prompts are under `authoring/task009/`: revised layout prompts, perspective prompts, painting correction and upper-room/collections sheets. Task008 room concepts remain the main exhibit-language references. Generated drawings guide composition; the stud-coordinate plan determines geometry.

The final native-import batch is `exports/victoria_task009_rebuild/`: **24 individual FBXs**, checksums and importer instructions. Do not import the assembled landmark as a replacement. `ImportRebuild.luau` adopts permanent uploaded mesh IDs; `IntegrateTwoStorey.luau` performs the edit-only assembly and preserves stable gameplay markers. Neither is a runtime generator.

Pre-change full-world recovery is local and Git-ignored: `artifacts/recovery/HoodTesting-pre-Task009.rbxm`; `pre-snapshot.json` records service bindings and checksums. An intermediate full-world recovery also precedes the two-floor revision. The final Victoria model and final full-world recovery **have not yet been saved** because Studio is disconnected. Engine `.rbxm` service packages are not native `.rbxl` place files.

Before completion: reconnect Hood Testing, import/adopt the final batch, integrate, inspect all rooms and upper-level lighting in Studio, perform one focused clearance/marker/exterior check, save and reopen final recovery packages, capture final Studio views, then make the single authorized commit on main and push. No robbery, damage, detection, alert or reward systems are implemented.

Reference sources: [official Victoria gardens](https://victoriamemorial-cal.org/gardens/), [Roblox mesh specifications](https://create.roblox.com/docs/art/modeling/specifications), [Roblox light sources](https://create.roblox.com/docs/effects/light-sources).
