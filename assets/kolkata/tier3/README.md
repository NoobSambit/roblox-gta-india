# Kolkata Tier 3 building library

Task 004: **27 original exterior building designs**, made in Blender through MCP.
Ready for the next Studio import and assembly milestone. No city placement,
landmark changes, interiors, gameplay or street-prop production is included.

## Assets

| Family | Count | Triangles per whole building |
|---|---:|---:|
| Old North Kolkata | 10 | 632–1,380 |
| Modern Kolkata | 9 | 384–1,416 |
| Mixed-use | 5 | 648–1,320 |
| Informal residential | 3 | 332–420 |

Total **22,472 triangles** across all 27 unique designs. Highest: `KOL_T3_MOD_04`,
1,416 triangles. Each building contains **3–5 grouped meshes**, each with one
opaque colour material. No image textures or external texture dependencies.

- [Master Blender library](Kolkata_Tier3_Library.blend): 27 independent scenes,
  one building at the origin in each scene. Choose the asset using Blender's scene selector.
- [Asset index](asset-index.md): individual source/export links, dimensions,
  floor counts, triangles and photographic source links.
- [Asset manifest](asset-manifest.json): machine-readable records including
  source URL, local photograph, observed features, materials and stable mesh keys.
- [Validation results](validation.json).

Each `family/ASSET_ID/` contains `ASSET_ID.blend`, `ASSET_ID.fbx` and `asset.json`.
The master is an authoring convenience; import the individual FBX files.

## Architectural simplification

- **Old:** tall paired shutters, oxide/ochre/cream plaster, cornice bands,
  simple veranda rails, polygonal projecting bays and a chamfered wrap gallery.
  Carvings, dense grille patterns and photographed deterioration are omitted.
- **Modern:** compact two- through six-storey concrete blocks, solid balcony
  parapets, service strips, offset projections and one small eight-sided tank.
  Facade arrangements and silhouettes differ, rather than only paint colours.
- **Mixed-use:** two- or three-bay closed shops, shallow shutter ribs and blank
  signboard surfaces, with varied residential balconies and roof parapets.
- **Informal:** small masonry volumes, shallow integrated corrugations, a partial
  upper room and supported roof extensions. No exaggerated decay or clutter.

Rear and side windows are deliberately sparse. All windows are opaque sealed
surfaces. Masses contain no room, stair or corridor geometry. A minimal plinth
grounds each building. Roofs and exterior masses are closed volumes. Separate
closed components intersect where needed; these are render assets, not boolean
unions or precision collision meshes.

## Scale, orientation and FBX import

- Source coordinates: **one unit = one Roblox stud**, 12-stud main storeys;
  informal structures use shorter masonry levels. Dimensions include projections.
- Roblox frame: X right, Y up, **front -Z**. Blender frame: Z up, front +Y.
- All grouped objects share ground origin `(0,0,0)`, zero rotation and unit scale.
- Same assembled FBX convention as Victoria: scene units None/1,
  `FBX_SCALE_UNITS`, global scale 1, forward -Z/up Y, mesh objects only, no animation.
- Studio: choose **Stud / scale factor 1**, keep mesh groups separate, anchor
  the imported model. Confirm its height and front before placing it in the map.
- The intended ground pivot is stored by every source object and FBX transform.
  Confirm the imported Model pivot in Studio; use its ground centre if Studio
  chooses a bounding-box pivot.
- Import each unique design once, then clone/reuse the same underlying mesh IDs.
  Record those IDs beside the stable `ASSET_ID__Role` mesh keys during assembly.
- Use simple bounds/collision proxies in Studio. Do not enable detailed
  per-triangle collision for decorative facade groups. No collision proxies are
  supplied in this exterior library milestone.

## Reference provenance

**27/27 designs have distinct retrieved and visually examined Kolkata photos.**
See the per-asset manifest records and
[assigned reference manifest](../../../artifacts/references/tier3/reference-manifest.json).
Photographs remain the property of their sources. No photo pixels, signage,
scanned geometry or third-party building models are incorporated in the assets.

The supplementary `extraOld` batch was incorrectly classified during retrieval.
It was excluded from all asset assignments, moved to `rejected_modern_supplement`,
and replaced by four examined traditional Kolkata house photographs. The original
ten `old` assignments were retained. One further supplementary URL returned 404
and was not used.

## Minimal validation performed

- Exact 10/9/5/3 distribution; 27 distinct assigned photo URLs and local photos.
- All 27 individual source files opened, checked for their single asset scene,
  and saved as normal Blender files with a framed authoring view.
- Triangle counts, finite coordinates, positive dimensions, neutral transforms,
  ground origins, no modifiers, no zero-area faces and closed manifold components.
- Consistent face winding and outward volume for each connected component.
- All 27 actual FBX files parsed; geometry/object counts, triangle totals and
  scale transforms matched their sources. No texture/video dependencies.
- Brief front/corner review of every asset using four family sheets. Fixed
  overlapping door/window panels, the wrap-gallery corner and roof intersections;
  rechecked the affected exports and previews.

No export or parsing failures remain. **These new assets were not imported into
Roblox Studio in Task 004.** The exporter/unit convention is the established
project pipeline; final Studio material appearance, collision and map-scale
performance belong to assembly. No gameplay test or city benchmark was run.

## Review sheets and maintenance

- [Old Kolkata](../../../artifacts/review/tier3/old_kolkata-review.jpg)
- [Modern](../../../artifacts/review/tier3/modern-review.jpg)
- [Mixed-use](../../../artifacts/review/tier3/mixed_use-review.jpg)
- [Informal](../../../artifacts/review/tier3/informal-review.jpg)

`designs.json`, `lowpoly.py` and `build_library.py` preserve original generation
sources. Run the builder in Blender only when intentionally regenerating owned
Tier 3 scenes; preserve manual edits first. It does not edit Tier 1/Tier 2 data.
After regeneration, open the isolated Tier 3 master and run `package_blends.py`
to package normally opening standalone sources and the framed master file.
The editable per-asset `.blend` files own subsequent manual geometry changes;
re-export after editing and refresh the master/manifest. FBX files are import
products, not an independent modelling source of truth.

Official specifications checked for this milestone:
[mesh specifications](https://create.roblox.com/docs/art/modeling/specifications),
[export requirements](https://create.roblox.com/docs/art/modeling/export-requirements),
[Blender export](https://create.roblox.com/docs/art/blender),
[performance guidance](https://create.roblox.com/docs/performance-optimization/improve).
The project's working budgets are deliberately much lower than import ceilings.
