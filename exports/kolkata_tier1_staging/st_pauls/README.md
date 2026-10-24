# St Pauls Cathedral

7 modular FBXs in this folder, including the finished foundation/grounds.
Dimensions **156 × 114.1 × 252 studs (width × height × depth)**.
Geometry: **19,812 unique / 46,296 placed triangles**.

Import all root-level FBXs together with **Stud / scale 1**, mesh merging off and
the common authored origin preserved. Keep each section's relative transform;
do not recenter the sections independently. Anchor the resulting scenery later.
These FBXs contain no staging-grid offset. The [package manifest](package-manifest.json)
lists each section, material/texture dependencies and original authoring metadata.

Blender lights and collision guides are retained in the master, outside the
visible-geometry FBX exports. Configure native lights and simplified collision
during later Studio integration, using the preserved authoring metadata/helpers.
Source shader graphs remain exact in Blender; Studio uses imported supported
materials/textures rather than arbitrary Blender shader graphs. No Studio
import or world modification has been performed for this staging task.
