# Task 007 — Victoria Memorial heist greybox

Built in **Hood Testing, place 96105551033653**, under
`Workspace.World.Cities.Kolkata.Districts.Maidan.VictoriaMemorial.HeistGreybox`.
Studio owns the world. This milestone contains **no robbery, loot, alert or hazard
logic**. All 96 new BaseParts are anchored native Parts. No external assets,
ImageGen, Blender work or runtime scripts were added.

## Layout and player choices

Seven functional rooms occupy the existing lower floor. Entrance vestibules and
open quadrangles are circulation spaces, not additional rooms. The available
upper volume is reserved for a later expansion; this milestone adds no upper
floor or stairs. Four to eight criminals is a design target, not a tested limit.

Coordinates below are landmark-local studs: the original north/front portal
faces world west because the landmark is rotated. Room IDs have prefix
`VIC_ROOM_`; gallery dimensions describe usable floor allocations.

| Room | Local location / size | Loot IDs | Routes |
| --- | --- | --- | --- |
| MAIN_HALL — Queen's Hall | Centre, 54 × 54 clear zone | None | Both vestibules and both quadrangles |
| PUBLIC — public exhibition | NW wing, 33 × 34 | 001–004 | Front vestibule, courtyard door, two collection-gallery doorways |
| GALLERY_C — collections | Outer NW wing, 22 × 34 | 005–007 | Two 10-stud doorways return to the public gallery |
| GALLERY_A — paintings | SW wing, 57 × 34 | 008–011 | Rear vestibule and west-local quadrangle |
| GALLERY_B — sculpture | SE wing, 57 × 34 | 012–014 | Rear vestibule and east-local quadrangle |
| HIGH_SECURITY | Inner NE wing, 36 × 34 | 015–016 | Front vestibule, courtyard door, paired archive doorways |
| ARCHIVE | Outer NE wing, 19 × 34 | 017–018 | Two 10-stud doorways return through high security |

An easy run takes any public exhibit and returns to the front portal or side A.
Medium runs can use either opposite gallery and exit through the rear portal or
its quadrangle. Collections offer a compact side loop. High security and the
archive form a separate optional branch; successful theft never requires them.
The two smaller rooms have central exhibit islands and parallel doorways rather
than displays crowding their door approaches.

The four existing escapes are **MAIN, REAR, SIDE_A and SIDE_B**. Side exits use
the existing colonnade gaps and terrace stairs. Every route is bidirectional,
also allowing police interception. No new facade opening is proposed or cut.
Existing courtyard gallery doors are approximately 9 studs wide; new internal
doorways are 10 studs wide and 14 studs high. Main axial routes remain generous.

## Loot and future bag planning

18 independent exhibit markers have stable `VIC_LOOT_001`–`018` IDs. Their
attributes include GalleryId, LootCategory, ExhibitName, ProvisionalValue,
CapacityCost, CollectionSeconds, SecurityRisk, AvailabilityState and
AlertOnTheftStart. Exhibit names are fictional; they make no assertion about
the actual museum collection. The provisional individual bag capacity is 10.

| Category | Value units | Capacity | Collection seconds |
| --- | ---: | ---: | ---: |
| Common | 300 | 1 | 2 |
| Standard | 600 | 2 | 3 |
| Valuable | 1,100 | 3 | 4 |
| Rare | 1,800 | 4 | 6 |
| Premium | 2,800 | 5 | 8 |

These are planning numbers, not a working economy. Multiple players can approach
different pedestals simultaneously. Future gameplay must claim each shared item
atomically on the server, preventing duplicate collection while keeping other
items independent. Capacity, availability, timers and payouts are unimplemented.

## Security and alert contract

Nine non-colliding, labelled security reservations:

- 2 static laser grids: optional high-security side branch and archive north approach.
- 1 predictable moving-laser envelope: high-security south side, with retreat space.
- 1 electrical floor: short 8 × 8 central pad, with walk-around room.
- 2 terminals: intended short disable interactions, located off the main lanes.
- 3 protected case footprints: associated with loot 015, 016 and 017.

Orange footprints reserve hazard space, not active beams or damage. The archive
has a second approach through its south doorway. Future hazards need visible
telegraphs, predictable timing, forgiving touch traversal and safe retreat.
The present clearance inspection does not validate future moving hazard timing.

Two invisible `VIC_RESTRICTED_001/002` volumes cover the high-security room and
archive, including both routes into the restricted wing. Red entry strips mark
the vestibule and courtyard thresholds. Public hall/gallery entry causes no
alert. The future event must alert police on the first **unauthorized restricted
entry OR theft start**, and only once per robbery event across both sources.
Markers implement no detection. CCTV and motion sensors remain decorative only.

## Ownership, reuse and replacement

All original Victoria geometry was retained: Queen's Hall, figure/plinth,
radial floor, arcade and dome lining; four gallery floors/vaults and walls;
vestibules, courtyard floors and doors; both portals, side openings, stairs,
grounds, exterior, collision and road connection. Only two interior partition
assemblies were added. Existing eight Task 002 zones are preserved as historical
authoring metadata; use Task 007 room/restricted IDs for the future heist.

Inside HeistGreybox, `Structure` owns the new partitions. `LootMarkers`,
`SecurityMarkers` and `Wayfinding` own replaceable prototype presentation.
`RoomZones`, `RestrictedZoneMarkers` and `EntryExitMarkers` preserve spatial
definitions independently of final visuals. Final assets should keep these IDs
and connections. No whole-campus Atomic model was introduced.

`authoring/task007/BuildGreybox.luau` is a one-shot edit-only source, also stored
in `ServerStorage.WorldAuthoring.Task007`. It refuses to run over an existing
greybox. No automatic synchronization exists. Do not rerun the older landmark
integration or Blender assembly over the live Studio model.

## Focused inspection and images

One edit-mode layout inspection sampled floor support and a 3-stud-wide avatar
clearance envelope along five connected routes, followed by viewport review.
It allows the original 0.8-stud floor thresholds. Initial exhibit clearance
issues were corrected and the affected inspection rerun: **no remaining route
issues**. A visual emitter/display overlap was also separated. This is the
requested minimal equivalent inspection, not a character playtest, multiplayer,
mobile, economy, exploit or performance test.

The original-geometry comparison found all **920 original BaseParts unchanged**
in transforms, dimensions, colour, collision, transparency and mesh IDs. Details
are in [inspection.json](inspection.json). Five original Studio PNGs:

- [Top-down cutaway](../../artifacts/review/task007/top_down.png)
- [Queen's Hall](../../artifacts/review/task007/hall.png)
- [Public gallery](../../artifacts/review/task007/public_gallery.png)
- [High security](../../artifacts/review/task007/high_security.png)
- [Archive](../../artifacts/review/task007/archive.png)

For the top-down capture only, roofs/upper meshes were locally hidden and shell
walls made translucent. Original visibility was restored and temporary photo
helpers removed before saving. This screenshot is a cutaway, not missing roofs.

## Save and recovery

- Before structural edits: local, Git-ignored
  `artifacts/recovery/HoodTesting-pre-Task007.rbxm` (2,744,854 bytes).
- Final full-world recovery: local, Git-ignored
  `artifacts/recovery/HoodTesting-Task007.rbxm` (2,737,706 bytes).
- Final landmark-only package, tracked:
  `artifacts/VictoriaMemorial-Task007.rbxm` (231,929 bytes).
- [snapshot.json](snapshot.json) records final engine serialization/reopen checks
  and top-level service bindings; [pre-snapshot.json](pre-snapshot.json) records
  the pre-task package bindings. Scene properties are preserved in
  `ServerStorage.WorldAuthoring.Task007SceneSettings` in the final world package.

These are real engine `.rbxm` recovery packages, **not native `.rbxl` place
files**. The full package includes Terrain, city roots, stored asset masters,
scripts and lighting children. For recovery, use an empty Studio recovery
session and restore top-level objects to the services listed in snapshot.json;
apply the named scene settings. Inspect existing roots before inserting a
package into a populated world to avoid duplicates. The landmark-only package
contains Victoria at its original transform and includes the greybox/connector.

Native Save to File was unavailable: Computer Use access to Studio was rejected
as “not approved to use Roblox Studio.” MCP serialization succeeded instead.
HTTP was enabled temporarily for a loopback-only file transfer and restored to
its original disabled state. No public publishing occurred.

Remaining work belongs to later milestones: final interior art, upper-level
access if desired, gameplay, actual hazard balancing and multiplayer/device QA.
