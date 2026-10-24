# Batch 4 production plan

**Goal:** Three independent, recognizable Tier 1 exterior landmarks for later Roblox integration.
**Spec:** User's supplied Batch 4 objective and images 1–12, received 24 October 2026.
**Architecture:** Editable linked modules in neutral stud coordinates; reuse existing geometry/export utilities read-only. New source and exports stay in their own batch folders. No Studio operations.
**Tools:** Blender 5.2.3, Python, existing indexed geometry helpers, original small shared textures.

## Constraints and decisions

- Main only; at most three commits, push completed files. Preserve all earlier batches.
- One neutral Blender unit = one stud. Authoring X/Y-up/Z maps to Blender (X,-Z,Y); front is Blender +Y, Roblox -Z.
- Unique preferred total 53–85k, review at 95k; placed preferred 85–125k, review at 145k. These are allowances, not quotas.
- Export connected geometry in section/material chunks below 15k triangles. Keep source modules linked/editable.
- Four original previews each: hero, elevated, complete grounds, night; one combined contact sheet.
- Exterior only; actual depth at authentic entrances/arcades; no galleries, marketplace rooms or nave furnishings.
- New Market: approximately 280×140 building, substantial repeated red frontage, clock tower at right-hand frontage end; dark multi-ridge market roofs. Photos 7–10,12.
- Museum: approximately 250×175 building, projecting three-arch central entrance with giant upper columns, ivory quadrangle and two levels of courtyard arcades. Photos 4–6. Image 11 is inconsistent with those museum images (retail colonnade, different elevation); do not transplant it into the museum.
- Cathedral: approximately 200-long nave, projecting transept, dominant square crossing tower and pinnacle/spirelets as shown in photos 1–3, rather than inventing a tall conical spire. Compact calm landscape.
- Grounds add limited margins. All dimensions are compressed design decisions; final measured envelopes go in asset manifests.
- Small original tiling masonry maps and opaque materials; no photo textures or external assets. Preview light rigs excluded from FBX; local light positions documented for future Studio tuning.

## Review focus

Check clock-tower placement/profile, roof continuity, museum entrance depth and open quadrangle, cathedral long-nave/transept proportions, full-foundation camera framing, and source/export scale and material correspondence.

## Tasks and evidence

- [x] Read project instructions, current Tier 1 notes, all supplied references; inspect clean main and Blender connection.
- [x] Build New Market using original reusable gables, arches, brickwork, clock faces, crown and roof kit.
- [x] Build museum with open entrance and court, two-storey galleries, cornices, restrained flat parapets and compact compound.
- [x] Build cathedral with pointed tracery, buttresses, crenellation, tower/pinnacles and complete grounds.
- [x] Finish materials, reusable fixtures and bounded night light stations; export modular FBXs.
- [x] Run essential geometry/normals/scale/triangle/FBX checks per asset and rerun changed assets after meaningful fixes. No gameplay or Studio tests.
- [x] Render and inspect the required final views plus three reverse night views; produce contact sheet, concise asset/import/provenance notes, record counts and dimensions.
- Final delivery: inspect staged scope, then use a normal commit/push on main (maximum three commits); Git history records the delivered revision.

User's explicit minimal-validation and autonomous execution instructions govern this art-production workflow; no software test suite, extra design approval gate, or exhaustive validation pipeline is added.

## Review record

Meaningful issues found and fixed during production: shared roof-ridge edges; museum coplanar roof and front-corner wall overlaps; market crown slats buried inside the cap; low lights blocked by the verandah/cornices; cathedral exposed inner transept gables. The independent read-only review confirmed the corner/slat findings and identified the transept opening. Changed assets receive only their essential checks and required final views.

User feedback added: physically close the market front/rear roof strips, broaden and deepen its entrance, separate the canopy/verandah, balance the smaller fanlight, distinguish the museum's wall/trim/plinth/recess colours, deepen gallery presentation, add limited cathedral pinnacle/buttress/porch detail, and confirm rear/left/right night coverage. All three asset scenes are loaded and refreshed through Blender MCP. One reverse night view per asset supplements the four required views. Roof-coverage and entrance-clearance rays specifically check the reported market defects; they are source geometry checks, not Studio traversal tests.

Rulings: preserve the cathedral's photo-led square pinnacled tower; exclude inconsistent image 11 from the museum; retain the two-storey court arcade despite the placed count exceeding the preferred 125k (still below 145k). No geometry is added just to reach the preferred unique count. Studio import, native lighting, collisions and physical-device performance remain outside this task and unverified.

Final verified package: 48,608 unique / 144,320 placed triangles, 21 modular FBXs, 15 original previews and one contact sheet. Largest exported mesh 11,972 triangles; representative round-trip bound error below 0.000016 stud. Market-specific checks: 24 front/rear roof coverage rays and three clear source entry rays. Final visual review includes all grounds and both night bearings. The read-only review's architectural findings are resolved; no minor issue is deferred. Subsequent user feedback was applied and the changed sources/exports checked again.
