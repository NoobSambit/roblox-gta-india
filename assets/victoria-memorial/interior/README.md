# Victoria Memorial interior art kit — Task 008

Warm ivory architecture, charcoal exhibit furniture, muted brass and deep teal;
restricted exhibits add small oxblood/amber accents. Broad shapes and four flat
original paintings carry the detail. The approved landmark and Task 007 layout
are unchanged. This package is an **offline art library and placement proposal**;
it has not been integrated into the Studio world.

## Open and review

- [VIC_Interior_Library.blend](VIC_Interior_Library.blend): categorized overview
  plus 37 asset-sized scenes. Each asset also has its own editable `.blend`,
  `_Roblox.fbx`, `preview.png` and `asset.json` beside it.
- [Asset index](asset-index.md): every source, export, preview, size and triangle cap.
- [Six selected ImageGen concepts](concepts/README.md),
  [art direction](../../../docs/task008-art-direction.md) and
  [four original 2D paintings / uploaded IDs](artwork/README.md).
- [Architecture](review/architecture-sheet.png),
  [exhibition](review/exhibition-sheet.png), [loot](review/loot-sheet.png) and
  [security](review/security-sheet.png) contact sheets are original Blender renders.
- Assembled views: [hall](review/hall_language.png),
  [public](review/public_display_language.png),
  [paintings](review/painting_gallery_language.png),
  [sculptures](review/sculpture_gallery_language.png),
  [collections](review/collections_language.png),
  [high security](review/high_security_language.png),
  [archive](review/archive_language.png).

[VIC_Interior_ArtPreview.blend](VIC_Interior_ArtPreview.blend) places the proposed
art against a read-only link to `../VictoriaMemorial.blend`, with the two exact
Task 007 partitions reconstructed for context. The four painting textures are
packed into this review file. Its lights/cameras are review helpers. Do not
export this assembled review as a replacement landmark or use its shell as a
replacement for the current Studio world. It opens on the public-gallery camera.

## Measured geometry

| Category | Assets | Unique triangles | Proposed repeated pass |
| --- | ---: | ---: | ---: |
| Architecture | 12 | 1,108 | 8,064 |
| Exhibition | 10 | 1,704 | 3,348 |
| Loot | 11 | 1,688 | 2,364 |
| Security | 4 | 440 | 824 |
| **Total** | **37** | **4,940** | **14,600** |

The proposal uses 31 assets in 168 instances; six variants remain available for
reuse. Repeated wall trims account for much of the placed total. The largest
individual asset is the 348-triangle premium case. Original shell/greybox
triangles and review helpers are excluded. These are geometry counts, not FPS
or draw-call measurements. Geometry was not added merely to fill a budget.

## Integration handoff

`layout-lock.json` records the approved seven rooms, 18 loot roots, nine security
reservations, four routes and two restricted volumes. `placement-manifest.json`
maps art instances to those IDs, in landmark-local Y-up studs. The upper volume
is untouched. Painting displays retain their exhibit positions on compact
freestanding mounts; they are not moved onto exterior walls.

Import **individual asset FBXs**, Scale Unit **Stud**, Scale Factor **1**, Merge
Meshes **off**, Anchored **on**. Authoring uses Blender `(x, -z, y)` with neutral
scene units and unit transforms, matching the existing landmark workflow. Asset
roots are ground/mount centres, front is local **-Z**. Apply the placement manifest
relative to the current landmark pivot, including its existing site rotation.
Retain the material-separated meshes and reuse imported mesh/image IDs.

Physical-kit FBXs contain no texture dependencies. Palette roles, component
names, mounting sockets and the moving-housing head pivot are in `asset.json`.
Set material colours from `asset-manifest.json`; map the separate Glass meshes
to restrained transparent glazing during integration. Artwork uses the existing
`Canvas` backing and its planar UVs or a correctly proportioned front image.
Never add sculpted artwork geometry or re-upload repeated copies of a painting.

Replace only the corresponding temporary exhibit visuals. Complete cases and
feature panels already include a base: **do not stack them over greybox
pedestals**. Protected cases referenced by loot and security are one instance.
Retain all original marker transforms, metadata, floors, simple collision and
routes. Decorative trims, runner inserts and device housings are non-colliding
visuals. Do not enable touch/damage or hazard behaviour. Check final imported
materials, transparency, scale, pivots and collisions in the later Studio pass.

The arch module includes matching spandrel infill so the rectangular greybox
door corners do not remain visible outside its curve. Ten-stud walking width
below its nine-stud spring and the fourteen-stud apex remain. Small cases and
painting mounts are slimmed to clear the existing nearby vault feet. Banners
use solid partition piers; runners avoid the high-security floor reservation;
the archive cabinet stays outside both return lanes.

## Minimal validation and maintenance

[validation.json](validation.json) records finite, non-degenerate geometry,
closed outward-facing components, unit transforms, pivots, per-asset caps and
complete FBX mesh/triangle data. Three representative FBXs (arch, premium case,
moving housing) were reimported in Blender; maximum bounds error was below
0.000003 stud. All six locked Task 007/exterior source hashes still match.

All seven assembled room views and four asset sheets were inspected. Corrections
covered arch corner gaps, the information-stand face, painting aspect ratio and
support clearance. No gameplay, device, multiplayer or performance testing was
performed. No assets were imported into Studio; image uploads succeeded, with
moderation/runtime rendering still unverified. No experience was published.

Rebuild only this kit in background Blender 5.2.3 LTS:

```powershell
blender --background --factory-startup --python assets/victoria-memorial/interior/build_library.py
python assets/victoria-memorial/interior/prepare_artwork.py
python assets/victoria-memorial/interior/plan_placements.py
blender --background --factory-startup --python assets/victoria-memorial/interior/validate_assets.py
blender --background --factory-startup --python assets/victoria-memorial/interior/render_reviews.py
python assets/victoria-memorial/interior/make_sheets.py
```

The original project primitive builder is reused; Blender Python and Pillow
generate exports/review sheets. No third-party models, textures or fonts were
adopted into the game. ImageGen prompts and original source images are retained.
The canonical `.blend` files, FBXs and generated manifests are versioned for
recovery. The live Studio world still uses Task 007's recovery record at
`docs/task007/snapshot.json` because Task 008 makes no world edits.
