# Bengali Rajbari Estate

Editable source: `KOL_T1_RAJBARI.blend`. Source front is Blender +Y, exported Roblox -Z.
One neutral Blender unit = one Roblox stud. Align all section FBXs at the same
ground-center origin; import at Stud/1, retain separate meshes and material slots.
Files are together in `../../../../exports/kolkata_cultural/`.

27,458 unique source triangles; 123,800 placed.
Source bays share mesh data. Exported section chunks bake placements; do not
mistake unique source counts for the assembled rendering cost. Largest export
mesh: 5,500 triangles.

Visible architecture, simple collision-box guides and lighting are separate
collections. Guides are excluded from FBX, and `asset.json` records their sizes.
Use simple shell/plinth/step collisions and non-colliding decorative rails,
windows and trim at integration. Preserve the courtyard voids and entry routes.
Set static content anchored, use automatic render fidelity, and stream the two
main houses/estate sections at practical distances. Small fixtures/ornament can
hide earlier than the shell. No mobile performance claim is made.

20 working Blender lights cover external elevations,
galleries, entrances and cultural focal zones. `CulturalLighting.luau` beside
the FBXs reproduces the authored light positions with native shadowless spots
after import. FBX contains meshes only. Its origin must be the common ground
origin, not an automatically recentered model bounding-box pivot. No global
Lighting properties or day/night runtime system are changed.

Original day, reverse, courtyard and night PNGs are saved here. `validation.json`
records source/FBX checks and clear court/entry samples; these are not Studio,
player collision, full navigation, gameplay or physical-device tests.
