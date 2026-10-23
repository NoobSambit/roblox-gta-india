# Original flat museum paintings

Four original ImageGen illustrations share a restrained Kolkata/heritage palette.
They are fictional artwork, not reproductions or claims about the real museum's
collection. Each image is front-facing and unframed, with no room background.

Release textures are **480 × 320 px, 3:2**, resized without cropping or stretching.
The four PNGs total 816,656 compressed bytes. Larger 1536 × 1024 originals remain
in `source/` for editing, not runtime use. [Prompts](prompts.json) and the
[manifest](manifest.json) retain provenance, hashes, sizes and marker assignments.

| Artwork | Release PNG | Roblox image ID | Exhibit |
| --- | --- | --- | --- |
| River at dawn | [ART_01](textures/ART_01_RIVER_DAWN_480x320.png) | `rbxassetid://114887892688456` | VIC_LOOT_002 |
| Monsoon boulevard | [ART_02](textures/ART_02_MONSOON_STREET_480x320.png) | `rbxassetid://129141760977791` | VIC_LOOT_008 |
| Maidan garden study | [ART_03](textures/ART_03_GARDEN_STUDY_480x320.png) | `rbxassetid://104257714526099` | VIC_LOOT_010 |
| Heritage rooflines at dusk | [ART_04](textures/ART_04_HERITAGE_SKYLINE_480x320.png) | `rbxassetid://134263422572535` | VIC_LOOT_009 |

The uploads returned these IDs through Studio MCP. Moderation and runtime image
availability were not tested. Reuse the same IDs for repeat displays.

`VIC_E04_FRAME_LANDSCAPE` has a 3.1 × 2.066667-stud image backing with planar UVs.
Apply the image to its `Canvas` component, front local -Z. The frame is 72
triangles, already included in the kit/pass totals. The artwork adds **no 3D
geometry**. Keep the image's 3:2 ratio during later Studio placement. The portrait
frame is an optional physical variant and is not assigned these landscape images.
