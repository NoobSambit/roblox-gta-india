# Kolkata Tier 1 skyline batch

Accepted exterior batch; six independent Blender scenes plus an asset review grid. The grid is an asset browser, not a city layout. No gameplay or full interiors were built.

Open `Kolkata_Tier1_Library.blend`; it opens on the revised Marriott. Select another `KOL_T1_*` scene from Blender?s scene selector. Each asset also has an editable blend, original day/reverse/night PNGs, metadata and validation in its own folder.

All **46 FBXs** are together in [`exports/kolkata_tier1`](../../../exports/kolkata_tier1/). Import all files with the same building prefix together.

| Asset | Assembled triangles | Unique linked-source triangles | Export mesh objects | Largest export mesh |
|---|---:|---:|---:|---:|
| Atmosphere Twin Towers / Deya | 48,640 | 21,508 | 46 | 5,496 |
| Trump Tower Kolkata | 13,804 | 3,076 | 22 | 5,496 |
| Urbana / seven towers with folded facade wings | 57,460 | 10,748 | 45 | 5,500 |
| ITC Royal Bengal / hero exterior | 117,560 | 12,900 | 50 | 5,496 |
| ITC Sonar / terracotta water gardens and flaring canopy | 25,788 | 13,668 | 39 | 5,496 |
| JW Marriott Kolkata / swept diagrid arrival | 66,688 | 24,772 | 48 | 5,496 |

Unique source counts measure authoring reuse; the assembled count is the geometry actually exported. The whole batch has 86,672 unique source triangles and 329,940 assembled triangles. These are geometry counts, not device performance measurements.

Every exported mesh is at or below **5,500 triangles**, under the current Roblox 20,000-per-mesh limit. All source/export mesh checks pass for closed geometry, triangle-only faces, finite vertices, nondegenerate faces and consistent winding. Representative FBX re-imports preserve material slots, unit scales and bounds. Royal?s column bearings were checked directly against the supporting geometry.

Import at **Stud / scale factor 1 / Merge Meshes off / Anchored on**, preserving the common scene origin for every section. Blender front is +Y, up Z; FBX is Y-up/front -Z. Do not merge a whole building into one mesh. Use Upload to Roblox off for iteration. The user will perform the actual Studio import; Studio appearance, collision and physical-device performance remain unverified. Add simple native collision during later integration rather than using ornate facade geometry for collision.

The materials use original flat colors and geometry, with opaque glass tints. Blender emission is a preview aid; set up selected window/crown lighting in Studio. Preview lights/cameras are excluded from the FBXs. No downloaded photos or third-party meshes/textures are incorporated.

Architectural and night notes:

- **ATMOSPHERE:** Deep lobed Deya bridge, pinched waist, perforation pattern, pool/island and paired tower terraces. Night focus: Bridge coping, roof fins, selected windows and arrival columns.
- **TRUMP:** Slender glazed tower, bronze spine, open roof pergola and compact dark arrival. Night focus: Crown perimeter, bronze spine and entrance monuments.
- **URBANA:** Seven reused towers with folded zigzag footprints, white fins and spandrels; complete curved clubhouse, pool and roundabout. Night focus: Roof frames, tower doors, clubhouse edge and landscaped arrival.
- **ROYAL:** Accepted stepped classical hero, reduced loggias, ochre masonry, arches, columns and pediment; 44 bearing contacts verified. Night focus: Portico, giant colonnade, corner loggias, main cornices and crown sign.
- **SONAR:** Terracotta wings, lily-water court, complete screened pavilions and curved flaring white canopy. Only this asset has a simple internal floor shell. Night focus: Arrival canopy underside, pavilion screens and water-court paths.
- **JW:** Broad main slab, narrower balcony tower, diamond crowns, deeply curved diagrid podium, pool ribbon and open vaulted arrival. Night focus: Diagrid frontage, pool coping, arrival vault and crown rims.

Rebuild in Blender background mode with `--python build_landmarks.py -- <asset keys>`, review changed assets with `--python review_assets.py -- <asset keys>`, then run `--python package_batch.py`. Pass `--python-exit-code 1`. `royal_bengal.py` maintains the accepted staged Royal exterior; `landmark_refinements.py` maintains Marriott, Sonar and Urbana. Source meshes retain linked modules; exports bake material/section chunks to keep the imported object count controlled.

Specifications: [Roblox modeling requirements](https://create.roblox.com/docs/art/modeling/specifications) and [Studio Importer](https://create.roblox.com/docs/studio/importer).
