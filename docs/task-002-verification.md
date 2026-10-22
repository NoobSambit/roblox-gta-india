# Task 002 — Victoria Memorial integration

## Completed integration — 22 October 2026

Integrated in Hood Testing, place 96105551033653:
`Workspace/World/Cities/Kolkata/Districts/Maidan/VictoriaMemorial`.

The landmark faces west at (820, 0, 0), with formal grounds, perimeter drive and a connection to Para01's east road endpoint. Existing Para01, spawn and global lighting were preserved. Blender created the original modular exterior, Queen's Hall and gallery shell, grounds and vegetation. Eight zones mark entrances, exits and future objective spaces; no robbery mechanics exist.

## Import and optimization

Studio confirmed all 858 imported objects and campus bounds 600 × 144.6 × 620 studs. Visual inspection showed the complete exterior and grounds.

The edit-only builder reconstructed the site as **350 MeshParts sharing 54 mesh IDs**, with native simple structures/grounds/collision. Including zones and connector: **928 BaseParts, 214 colliders**, all anchored and CanTouch disabled. Decorative meshes have physical collision disabled and simple box collision fidelity; architectural surfaces retain useful queries. Native floors, walls, stairs and extra boxes provide traversal collision.

Streaming is enabled. The campus root uses Default streaming, with individual architectural assemblies Atomic. Plain materials have no image textures. No runtime generator or polling script was installed.

Studio owns the integrated world. Blender owns editable mesh source; there is no automatic sync. Edit-only builder/manifest modules are under ServerStorage.WorldAuthoring. The original import is retained in WorldAuthoring.VictoriaImportRecovery.

## Focused validation only

| Studio environment, one player, approach view | Triangles | Draw calls | Desktop host FPS |
| --- | ---: | ---: | ---: |
| Desktop client, 3-second sample | 81,244 | 65 | 60.37 |
| iPhone 17 Pro landscape emulation, 2-second sample | 98,716 | 70 | 60.30 |

The phone preset reports 874 × 402; the measured client viewport was 750 × 381. Phone-sized visual inspection showed the intact landmark. Studio rejected graphics-quality writes due to missing RobloxScript capability, so that sample remained **Automatic**. These measurements do not establish physical phone FPS. Play mode was stopped and the default viewport restored.

The character climbed the front approach and entered the central hall. The first waypoint ended 3.37 studs from its target, outside the diagnostic's 3-stud threshold; the subsequent interior target was reached. Only this entry route was checked, not every exit.

A whole-client Studio memory reading was 3358 MB, including the existing map/editor session. It does not isolate landmark memory. No physical phone/tablet, multiplayer stress, vehicle pursuit or exhaustive streaming tests were run. A short physical-device check remains appropriate before release.

## Recovery and records

- Editable source and corrected FBX: assets/victoria-memorial.
- Local binary recovery: artifacts/VictoriaMemorial-Task002.rbxm, **217,269 bytes**, containing the integrated landmark/connection and both authoring modules. It does not contain all Para01 or the original import archive.
- Mesh IDs and measurements: assets/victoria-memorial/studio-integration.json.
- Changes are in the open Studio edit session. No public publish operation was performed.

## Resolved defects and limits

The initial handoff mistakenly used the overlapping component library, and default FBX scaling baked in a 28× multiplier. Corrected to neutral units / scale 1 with FBX Unit Scale, then imported the full assembled campus successfully. Historical Blender roundtrip checks did not prove Roblox compatibility.

Floating corner-tower oculi were fixed in Blender with missing attic masonry and joined cornices. Approved geometry was preserved in integration.

Interior remains a first-pass shell; detailed exhibits, upper-level circulation and robbery mechanics are future work. This campus connects to the prototype; the wider Maidan district is not built. Eighteen exterior/interior reference photos are recorded under artifacts/references/victoria/sources.json, used only as reference. All game geometry is original.

## Surface overlap fix
Adjusted 148 Para01 curb fronts 0.08 studs towards the road, and lowered the four campus ground tiles plus connector ground by 0.08 studs. Updated live Studio authoring modules and local sources. Implemented directly from supplied screenshots; no tests were run. The earlier Task002 recovery binary predates this surface fix.
