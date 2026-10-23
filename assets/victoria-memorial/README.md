# Victoria Memorial — Blender source package

**Integrated in Hood Testing, place 96105551033653.** Complete import, corrected scale, exterior appearance and entrance-to-central-hall traversal were checked in Studio. The final landmark uses 350 MeshParts sharing 54 mesh IDs, native structures/collision and a Para01 road connector. Focused results and limitations are in `docs/task-002-verification.md`; physical phone hardware remains untested.

## Files and ownership

Task 007 adds a Studio-owned interior heist greybox without changing this Blender
shell or any approved original geometry. See [the layout and recovery notes](../../docs/task007/README.md).
The old Blender/FBX exports do not contain this additive greybox. Preserve the
live `VictoriaMemorial.HeistGreybox` and its Task 007 recovery package during any
future reimport; do not rerun the landmark builder over it.

- `VictoriaMemorial.blend`: editable original mesh library, linked architecture instances, structural parts, interior, grounds, simple extra collision, and metadata. `VM_Presentation` contains review lights/camera only.
- `VictoriaMemorial_Architecture.fbx`: assembled exterior and interior shell, separated by component and material.
- `VictoriaMemorial_MeshLibrary.fbx`: 54 reusable material-separated meshes. Their origins overlap intentionally; this is a component library, not the assembled scene.
- `VictoriaMemorial_Grounds.fbx`: lawns, paths, pools, vegetation, boundaries, gates and perimeter drive.
- `VictoriaMemorial_Collision.fbx`: 58 extra simple boxes for portal piers, tower bases and colonnade shafts. The visible structural floors/walls/steps also need their normal simple collision.
- `assembly-manifest.json`: authoritative generated placements, colours, native part dimensions, collision flags and 8 future-use markers.
- `mesh-library.json`: vertices, triangle winding and split corner normals for all unique reusable meshes, in Roblox coordinates. This supports direct mesh transfer if Studio's local-file importer cannot be driven with available tools.

Blender owns mesh source. Studio continues to own the integrated world. There is no automatic sync. `build_victoria.py` replaces only its `VM_*` Blender collections; **rerunning it replaces manual changes within those collections**. No generator runs in the game.

## Scale, import and reuse

Authoring coordinates are **studs**, Y up, north at -Z. Blender maps them to `(x, -z, y)`. Blender units are None / scale 1, with one coordinate equal to one Roblox stud. Object scale is positive and unscaled; placements use translation and yaw. The building's terrace is 272 × 214 studs, external stairs extend the depth to about 243 studs, and the Angel reaches about 143 studs. The grounds foundation is 600 × 620 studs.

**Import handoff: `VictoriaMemorial_Roblox.fbx`.** This contains the assembled architecture, structural shell, interior and grounds: 858 visible mesh objects, 117,450 triangles, intended bounds 600 × 144.6 × 620 studs. Import with Scale Unit **Stud**, Scale Factor **1**, Merge Meshes **off**, Anchored **on**. Keep the full scene together for the edit-only assembly step. Studio validation is still required.

The earlier export and handoff were defective: the default FBX scaling baked a 28× multiplier into object transforms, and the component library was handed over before automated placement existed. User screenshots confirmed oversize warnings and overlapping template pieces. Corrected all FBX exports using `FBX_SCALE_UNITS`, neutral scene units and scale 1. The library remains an intentionally overlapping authoring file, not a complete landmark. Blender roundtrip checks alone did not establish Studio compatibility; previous roundtrip results describe the superseded exports.

For production assembly, `authoring/VictoriaMemorial.luau` takes one reference per template/material from the assembled import, clones it with manifest placements, and rebuilds simple primitives as native anchored Roblox parts. Repeated facade bays, towers, columns and vegetation therefore share mesh IDs. Four ground tiles establish the imported scene frame and reject incorrect scale before world edits. The imported original moves to ServerStorage for recovery. No runtime generator is installed.

Use separate asset-sized models for wings, towers, dome assemblies, quadrangles and grounds sections. Do not put the entire campus in one Atomic streaming model. All geometry is static. Decorative meshes should use simple/disabled collision and touch; preserve useful raycast surfaces on major architecture. Structural floors, walls, stairs and the 58 extra boxes provide traversal collision. Final query flags and streaming settings must be checked in Studio.

## Content and geometry

Original hero exterior: central dome, drum, lantern and winged Angel of Victory; four chhatris; four domed corner towers; two monumental portals; paired pilasters, oculi, cornices and repeated facade bays; curved colonnades and open checkerboard quadrangles.

Interior foundation: circular Queen's Hall with radial floor, arcade/balustrade, clerestory and blue/gold inner dome; original simplified standing figure; vaulted entry halls and four gallery shells; courtyard doors and side escape openings. Museum exhibitions, detailed upper-floor access and robbery systems are not implemented.

Grounds: formal paths and pools, lawns, original low-poly palms/trees, hedges, benches, marble boundary bases, iron rails, open gate leaves and simplified original lion sculptures. The perimeter road is authored; its connector to Para01 must be placed against the live map.

Final file counts (not measured game rendering cost):

| Item | Count |
| --- | ---: |
| Reusable module types | 24 |
| Unique material-separated library meshes | 54 |
| Unique library triangles | 34,442 |
| Largest unique library mesh | 4,288 triangles |
| Full architecture triangles, including interior | 106,738 |
| Full grounds triangles | 10,712 |
| Extra collision boxes | 58 |

Repeated source objects share Blender mesh data. Plain colour materials need no texture images, external libraries or shader effects. These counts do not establish phone/tablet FPS, memory or draw-call performance.

## Validation and continuation

`audit_asset.py` checks finite vertices, triangle area, normals, marker IDs, sizes, inward interior surfaces, tower-oculus masonry backing and a broad authored box envelope for walking routes. It does not simulate a Roblox character; the central statue is deliberately walked around, not treated as an open straight path.

`validate_fbx.py`, run inside Blender, temporarily imports each FBX, compares objects/triangles/bounds/materials/scales and removes the imported copies. Results are in `fbx-roundtrip.json`. All four files passed; export warnings are zero. `review_views.py` renders player-height, exterior, dome and campus review cameras.

Integrated scene: `Workspace/World/Cities/Kolkata/Districts/Maidan/VictoriaMemorial`, at (820, 0, 0), facing west. The edit-only builder and manifest live under `ServerStorage/WorldAuthoring`. The imported original is retained in `VictoriaImportRecovery`. Local recovery: `artifacts/VictoriaMemorial-Task002.rbxm` (landmark, connector and authoring modules). `studio-integration.json` records mesh IDs and rendering measurements. No runtime builder exists. Inspect manual Studio edits before rerunning integration.

References are recorded in `artifacts/references/victoria/sources.json`, with exterior, interior and cardinal reference boards. The 18 photographs are reference-only; none is used as a texture. All game geometry is original. Source category/cardinal labels are photographic context, not a surveyed plan; the campus is deliberately compressed and adapted for gameplay.

### Surface correction after integration
The live Studio scene, authoring modules, build_victoria.py and placement manifest lower CampusGround to Y=-1.08 to separate grass from roads. Blender was disconnected during this correction, so the cached .blend and FBX files still contain the previous ground height and should be regenerated from the updated source before a fresh import. The previous recovery binary also predates this fix. No tests were run for this screenshot-directed fix.
