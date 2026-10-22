# Task 001 — verification and handoff

Environment: connected Roblox Studio, Hood Testing (96105551033653), one local client. Final scene is left in Edit mode with the normal viewport and a heritage-street camera view. No publication was performed.

## Implemented

- 24 buildings: 8 commercial main-road blocks and 16 residential buildings, including 3 ground-floor shops.
- Three distinct larger heritage commercial anchors; four reusable residential heritage types; simpler houses and apartments.
- Expanded connected lane loop, chai courtyard, shop displays, fixed produce counters, forecourts, benches, planters, utility infrastructure, static bus shelters and 88 blue-and-white railing panels.
- Warm afternoon Soft lighting, restrained grading/haze/bloom, and 27 unshadowed practical lights.
- 7,297 anchored scene parts; 1,038 colliders; no touch-enabled district parts, runtime world scripts or gameplay remotes. These are scene counts, not universal performance budgets.

## Essential checks

Visual inspection covered the boulevard, emporium, market, exchange, gullies, shop alcoves, chai courtyard and overview. A Samsung Galaxy A06 landscape viewport was inspected after construction; it is a screen-size check, not hardware performance evidence.

The final client walk passed all 14 named routes without jumping: market north entrance, market through passage to street, west gully, emporium arcade, north back lane, provisions alcove, north residential loop, west outer north/south, south outer lane, sweets-shop aisle, east gully, zebra crossing and exchange courtyard. The manual command is preserved in authoring/WalkRoutes.client.luau and is not installed as game code. It removes its input callback when finished.

Respawn returned the player to the courtyard at approximately (60, 3.81, -129), with 100 health. Server checks confirmed unique building location IDs, anchored geometry and no runtime district scripts.

Fixed during inspection: coplanar road/ground surfaces; a narrow gap behind heritage stoops; a detached reflected cupola component; market arch/roof intersections; and produce counters overlapping low forecourt walls. The final walk was rerun after moving the counters fully inside their plots.

## Rendering samples

Desktop Studio scene-analysis samples after the visual pass, excluding shadows:

| View | Opaque triangles | Opaque draw calls |
| --- | ---: | ---: |
| Heritage boulevard | 56,084 | 20 |
| Market | 74,250 | 15 |
| Gully | 18,810 | 11 |
| Elevated district overview | 271,168 | 43 |

These are viewpoint-dependent samples. No physical phone/tablet FPS, mobile memory guarantee, multiplayer load, vehicle traversal or long-session streaming performance is claimed. No further testing passes were run after the user requested minimal validation.

## Saved work and next action

The engine-serialized local recovery package is artifacts/Kolkata-Task001.rbxm. It contains the World, authoring modules/kits, original template and lighting settings. It is a model recovery package, not a complete .rbxl place file or a published place version. The HTTP-based export was unavailable because experience HTTP requests are disabled; the package was transferred directly through MCP without changing that setting.

Reviewed images: artifacts/review/final-boulevard.png and artifacts/review/final-overview.png. Authoring sources and ownership are documented in README.md. Intermediate generated revisions were removed; original template content remains in ServerStorage/WorldAuthoring/OriginalTemplate.

The next creative step is visual approval of this environmental slice. A subsequent milestone can introduce the first playable game loop; no gameplay implementation is included here.
