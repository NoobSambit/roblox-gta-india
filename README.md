# Indian Hood — Kolkata foundation

Git remote: [roblox-gta-india](https://github.com/NoobSambit/roblox-gta-india). See [repository workflow](docs/repository-workflow.md) for source ownership, commits and asset tracking.

**Task 006 is in progress.** The rebuilt city was assembled and received focused
Studio checks. Studio disconnected before the final recovery save; persistence
of that authored session is not yet confirmed. See [current status and recovery
next steps](docs/task006/status.md). The older milestone descriptions below are
historical, not the current integration status.

For the current bulk import, [exports/roblox_import](exports/roblox_import/README.md)
contains **61 FBX files in one flat folder**: all five Tier 2 buildings, all 27
Tier 3 buildings, five Tier 2.5 commercial shells and 24 riverfront support/prop/context assets. Howrah Bridge
and the main ghat remain in their own asset folders. These are convenience
copies; canonical sources and exports remain under `assets/kolkata/`.

Task 005's **Howrah Bridge and riverfront library** contains the modular bridge,
one upgraded open Kolkata Ganga ghat, seven support/approach modules, fifteen
props and two minimal context shells. Editable Blender sources, individual FBX
exports, final PNGs and manifests are saved. See the [library and import notes](assets/kolkata/howrah_bridge/README.md)
and [asset index](assets/kolkata/howrah_bridge/asset-index.md). No river water or
Studio placement is included in this milestone.

Task 004's **27 Tier 3 buildings** are saved as individual Blender sources and assembled FBX exports: 10 Old North Kolkata, 9 modern, 5 mixed-use and 3 informal residential. See the [library and import notes](assets/kolkata/tier3/README.md) and [asset index](assets/kolkata/tier3/asset-index.md). They have not been placed in Studio.

Task 003's five **Tier 2 Kolkata buildings** are saved as an editable Blender library and assembled FBX exports. See the [asset library](assets/kolkata/tier2/README.md), [preview sheet](artifacts/review/tier2/library-review.jpg), and [Task 003 notes](docs/task-003-tier2.md). They have not been placed in Studio.

Task 002's **Victoria Memorial is integrated in Studio**, with an interior shell, formal grounds and a road connection east of Para01. Source assets are in [assets/victoria-memorial](assets/victoria-memorial/README.md); the local recovery model is [VictoriaMemorial-Task002.rbxm](artifacts/VictoriaMemorial-Task002.rbxm). See [focused validation and limitations](docs/task-002-verification.md).

The current authored scene is in **Hood Testing**, place **96105551033653**. This is one continuous Roblox place. Only Kolkata exists.

The prototype contains eight commercial main-road blocks, including three original heritage anchors (Bengal Emporium, Bengal Exchange and Para Market Hall), and sixteen residential buildings behind them. Three residential buildings contain open ground-floor shop alcoves. Four reusable heritage townhouse types form the Generic 1.0 residential kit; simpler houses and apartments provide contrast.

The streetscape includes a chai courtyard, produce counters, book/textile/sweet displays, blue-and-white footpath railings, static bus shelters, red-oxide community seats, boundary walls, planters, street and wall lamps, electrical infrastructure, drains, bins and neighbourhood signs. Everything is anchored. There are no vehicles or gameplay systems.

The warm afternoon look uses Soft lighting, an Atmosphere, restrained colour correction and bloom, and unshadowed practical lights. No imported textures or Toolbox models are used.

## Ownership and authoring

**Studio owns the authored world. No Rojo or automatic file synchronisation is configured.**

- Scene: `Workspace/World/Cities/Kolkata/Districts/Para01`
- Expansion metadata: `Workspace/World/Cities/Kolkata/ExpansionConnections`
- Kits and edit-only modules: `ServerStorage/WorldAuthoring`
- Original default baseplate/spawn: `ServerStorage/WorldAuthoring/OriginalTemplate`
- Reproducible sources: [authoring](authoring/)

The builders bake geometry into Studio and do not run during gameplay. Do not rerun them over manual edits. Creation order in a fresh template:

1. `KolkataFoundation.infrastructure()`, `.buildings()`, `.details()`
2. `KolkataArchitecture.apply()`
3. `KolkataCommercial.createKit()`, `.placeStreet()`, `.expandNeighbourhood()`
4. `KolkataStreetscape.createKit()`, `.gullies()`, `.mainStreet()`, `.finalDetails()`, `.atmosphere()`

`KolkataArchitecture.place(kind, parent, cframe, palette, locationId)` clones a residential heritage type with wall, trim and shutter colour options. Building LocationId values are unique. AssetId, ArchitectureType, Use and PaletteRole relate instances to the kits. Models use local pivots and asset-sized streaming boundaries.

## Scale

Main road: 40 studs. Pavements: 12. Cross street: 20. Gullies: 14–16. Residential storeys: 12–14. The tallest pavilion is approximately 76 studs. The expanded lane loop spans approximately 540 × 500 studs inside a 900 × 900-stud ground foundation. Open road ends reserve growth.

## Verification and recovery

See [Task 001 verification](docs/task-001-verification.md) for checks and limitations. [WalkRoutes.client.luau](authoring/WalkRoutes.client.luau) is an optional manual Studio QA command, not a game script.

The local `artifacts/Kolkata-Task001.rbxm` recovery package, when present, contains the World, authoring kits/modules and lighting settings. It is a recovery model package, not a published place version. Future work should also use Studio's Save to File workflow.

Reference photos remain the property of their photographers. They were inspected for architectural vocabulary and are not included in the Roblox world. No third-party assets or dependencies were adopted. Links and scope are in [the design](docs/task-001-design.md).
