# Victoria heist — planning photo pack

Start with the two coordinate maps, then the contact sheets. Open each numbered room folder for clean approach/reverse Studio views. All photos show the actual approved museum, not ImageGen concepts.

- [Ground coordinate map](00_floor_1_map.png) / [Upper coordinate map](00_floor_2_map.png)
- [Ground room sheet](00_floor_1_contact_sheet.png) / [Upper room sheet](00_floor_2_contact_sheet.png)
- [Machine-readable planning index](planning-index.json) / [Room index CSV](room-index.csv)

## Planning rules

This is ONE future robbery across both floors: one event/timer, individual bags, shared loot availability, one police alert and one cooldown/reset. Alert on the first unauthorized restricted entry OR theft start. Public entry alone does not trigger it. Ground-floor loot can be taken without completing upstairs. Both stairs and all four bidirectional exterior routes remain available.

CCTV and motion sensors are decorative only. Lasers, electrical hazards, terminal hacking, protected-case interactions, loot collection, bags, payouts, alerts and reset logic are NOT implemented. The 16 security reservations are inactive visual/planning locations. Provisional values/capacities are planning numbers, not a balanced economy.

The architecture is approved. Plan security around its routes and clearances; do not redesign it from these photos. Exact IDs, coordinates, case bindings, room graph, restrictions and camera poses are available in the index and source files. Photos have no fake marker overlays.

## Coordinate and photograph notes

Plans use landmark-local X/Z, with negative Z at the main portal; this is not geographic north. Ground Y is 6.8 (hall approximately 7), upper Y is 34. World = (820+z, y, -x). Upper hall arch visual clearance is 10.8 studs inside the 14-stud structural opening; balcony floor radii are 23–30.8, with rails/piers reducing usable clearance.

Security 010 is associated with the north antechamber metadata but physically lies inside the screening branch. The map shows its actual location. Security labels G01–G09 and U01–U07 resolve to full stable IDs in planning-index.json.

Studio views were captured at existing afternoon lighting with a temporary fixed medium editor quality (Level10), then Automatic was restored. They are not mobile/FPS evidence. Approach and reverse refer to camera views, not enforced one-way routes.

## Rooms

| Floor | Room | Loot | Security | Photos |
|---|---|---:|---:|---|
| 1 | A  QUEEN'S HALL | 0 | 0 | [Open](01_ground/01_queens_hall/README.md) |
| 1 | B  PUBLIC EXHIBITION | 4 | 0 | [Open](01_ground/02_public_gallery/README.md) |
| 1 | C3  COLLECTIONS | 3 | 0 | [Open](01_ground/03_collections/README.md) |
| 1 | C1  PAINTING GALLERY | 4 | 0 | [Open](01_ground/04_painting_gallery/README.md) |
| 1 | C2  SCULPTURE GALLERY | 3 | 0 | [Open](01_ground/05_sculpture_gallery/README.md) |
| 1 | D  HIGH SECURITY | 2 | 6 | [Open](01_ground/06_high_security/README.md) |
| 1 | E  RESTRICTED ARCHIVE | 2 | 3 | [Open](01_ground/07_archive/README.md) |
| 2 | Hall overlook | 0 | 0 | [Open](02_upper/01_overlook/README.md) |
| 2 | North stair / security antechamber | 0 | 1 | [Open](02_upper/02_north_landing/README.md) |
| 2 | South stair / landing | 0 | 0 | [Open](02_upper/03_south_landing/README.md) |
| 2 | Security screening chamber | 0 | 1 | [Open](02_upper/04_screening/README.md) |
| 2 | Heritage treasury | 3 | 1 | [Open](02_upper/05_treasury/README.md) |
| 2 | Ceremonial collection | 3 | 4 | [Open](02_upper/06_royal_collection/README.md) |
| 2 | River / navigation | 2 | 0 | [Open](02_upper/07_river_gallery/README.md) |
| 2 | Sculpture / craft | 2 | 0 | [Open](02_upper/08_craft_gallery/README.md) |

## Inter-floor / escape views

- [03_circulation/north_stair](03_circulation/north_stair/01_route.png)
- [03_circulation/south_stair](03_circulation/south_stair/01_route.png)
- [04_routes/main_portal](04_routes/main_portal/01_route.png)
- [04_routes/rear_portal](04_routes/rear_portal/01_route.png)
- [04_routes/side_a](04_routes/side_a/01_route.png)
- [04_routes/side_b](04_routes/side_b/01_route.png)
