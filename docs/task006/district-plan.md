# Task 006 — compact Kolkata rebuild

The user supplied the full design brief and technical autonomy. Work only on main.
The user explicitly waived the full-place pre-rebuild save when Studio MCP could
only provide an engine model package. A 2,433,928-byte pre-rebuild package with
72 root bindings is preserved locally; its service bindings are in pre-snapshot.json.
No existing Blender asset is regenerated.

## Fixed context and selected layout

Victoria Memorial and its existing west connection remain at their exact current
transforms. The retained main boulevard runs along Z=0, through the original
neighbourhood to the Victoria connection at X=320. Existing useful ground tiles,
main-road/pavement modules and streetscape masters are reused. Obsolete building
models and builders are archived outside Workspace, with regeneration disabled.

The urban bank occupies approximately X=-620..420 and Z=-800..700, joining the
existing Maidan east of it. The bridge projects west across a bounded river
corridor; its far end is an expansion landing, not another district. Main roads
remain around 40 studs, cross streets 20–24, gullies 16; footpaths around 12.

| District | Initial focus / anchor | Character |
|---|---|---|
| Civic | Writers (-130,-280), Town Hall (270,-285), GPO (-340,150), Metropolitan (240,290) | Four separate blocks, forecourts and connecting avenues |
| NorthKolkata | Jorasanko (-230,-650), primarily X=-470..50, Z=-800..-400 | Dense older houses, shared courts, 16-stud gullies |
| ModernResidential | X=100..420, Z=-740..-400 | Newer concrete blocks, varied existing heights, cleaner local roads |
| Commercial | X=-240..350, Z=40..390 | Five replaceable usable shops plus mixed-use buildings |
| InformalResidential | X=-450..-260, Z=500..650 | One small modest housing pocket |
| Maidan | Existing approved Victoria Memorial | Preserved campus and connection |
| HooghlyRiverfront | Western bank, bridge at Z=-180, ghat around Z=380 | Single ghat, promenades, restrained river props |

The authored layout contains 112 Tier 3 placements using all 27 unique designs.
Density was adjusted after reviewing footprint clearance; no mesh stretching.
No travel-time guarantee is assumed. Plots and road connections remain separate
from replaceable building geometry; asset masters live in ServerStorage.

## Network and relative elevations

Riverfront drive X=-500 and an eastern city street near X=400 connect east–west
avenues at Z=-400, -180, 0 and 400, with northern/southern cross connections and
local neighbourhood gullies. The old boulevard remains connected to Victoria.
This creates multiple loops instead of a single linear sightseeing road.

Street datum remains around world Y=0. Ghat local street Y=13.5 therefore gives
water datum Y=-13.5. Apply that translation consistently to bridge/ghat/supports.
Bridge road top becomes Y=18.5. The 128-stud approach returns it to Y=0; reconcile
the small sidewalk offsets with native connector slabs. Do not move Victoria.
Native Terrain Water is bounded to the western river corridor, below road level.

## Replaceable commercial plots

KOL_PLOT_BANK_001, KOL_PLOT_JEWELLERY_001, KOL_PLOT_RETAIL_001,
KOL_PLOT_ELECTRONICS_001 and KOL_PLOT_FASHION_001 own permanent pavement/parking
and entrance connectors. Separate building models reference those PlotIds and
store AssetId, street-facing transform, footprint, ground elevation, front/back
entry sockets and future objective attachment. Ground floors are open shells;
upper floors closed. No shop, robbery, police or economy mechanics.

## Execution and focused evidence

1. Preserve recovery and audit; normalize the 58 existing imported masters and
   deduplicate repeated MeshKeys, restore source palette colours and add proxies.
2. Save five Tier 2.5 sources/FBXs and import their grouped meshes.
3. Archive obsolete Para01 buildings/builders; retain useful infrastructure.
4. Build permanent roads/plots, place landmarks and all residential families.
5. Integrate bridge, ghat, native water and restrained street dressing.
6. Inspect all districts and walk the required entrances/bridge/ghat routes.
   Sample dense and landmark render cost and desktop host FPS. Check streaming
   traversal; record environment limits. Save recovery, mappings and screenshots.

The exact authored coordinates, asset mappings and measured results will be
recorded with the completed world, replacing tentative placement assumptions.
