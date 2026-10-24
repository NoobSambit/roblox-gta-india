# Dakshineshwar

14 modular FBXs in this folder, including the finished foundation/grounds.
Dimensions **418 × 159.6 × 219.853 studs (width × height × depth)**.
Geometry: **40,772 unique / 75,580 placed triangles**.

Import all root-level FBXs together with **Stud / scale 1**, mesh merging off and
the common authored origin preserved. Keep each section's relative transform;
do not recenter the sections independently. Anchor the resulting scenery later.
These FBXs contain no staging-grid offset. The [package manifest](package-manifest.json)
lists each section, material/texture dependencies and original authoring metadata.

The default `10_Shiva_Temples.fbx` contains all twelve existing shrines.
`modules/` holds the optional single-shrine master, placements and original
assembly helper for reusing one set of MeshIds. Use either the complete row or
the master/clone workflow; importing both duplicates the shrines.
`InstallNightLights.luau` is the existing optional native-light installer.
Water remains native Terrain work for later integration: local Y=-5, river
towards -Z, ghat front Z=-133.8 and lowest tread Y=-7. No water mesh is missing.

Blender lights and collision guides are retained in the master, outside the
visible-geometry FBX exports. Configure native lights and simplified collision
during later Studio integration, using the preserved authoring metadata/helpers.
Source shader graphs remain exact in Blender; Studio uses imported supported
materials/textures rather than arbitrary Blender shader graphs. No Studio
import or world modification has been performed for this staging task.
