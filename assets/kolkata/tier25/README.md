# Tier 2.5 commercial shells

Five original, fictional commercial buildings for replaceable Kolkata plots.
Each directory contains an editable Blender source, assembled FBX, asset/collision
metadata and an original preview PNG. `review.png` is the family contact sheet.

| Asset | Triangles | Grouped meshes |
|---|---:|---:|
| Bank | 3,984 | 7 |
| Jewellery | 3,436 | 8 |
| Retail | 3,324 | 7 |
| Electronics | 3,248 | 7 |
| Fashion | 3,340 | 7 |

Opaque palette materials; no image textures or third-party assets. Ground-floor
shells have open front/rear entries, floors and ceilings. Upper floors are closed.
The corrected arches/canopies have visible supports; all five were imported by
the user and checked in Studio. A local-client walk passed through every shell.

Use FBX Unit Scale, Stud / scale 1, Merge Meshes off, anchored. Front is -Z,
ground pivot is the origin. Studio restores source palette colours and uses the
simple collision boxes in asset.json. Geometry stays separate from permanent
plot infrastructure and future gameplay attachments.

`build_commercial.py` uses the project's existing `howrah_geometry.py` helper.
No Blender-only effects or runtime generation are required. Canonical exports
are here; five matching convenience copies are in `exports/roblox_import`.

Task 006 world persistence is pending after a Studio disconnect; consult
`docs/task006/status.md` before assuming the city session has been saved.
