# Kolkata Tier 1 cultural compounds

Two separate editable assets/scenes: **Rajbari Estate** and **Jorasanko Thakurbari**.
Open `Cultural_Batch_Live.blend` and choose the compound in the scene selector.
The file is an asset library, not a district placement/map.

Rajbari combines the supplied brick-columned courtyard references with a domed
street pavilion, warm ivory/ochre plaster, a projecting Corinthian entrance,
broad grounded stairs and a finished Bengali-roofed Puja mandap space. The stage
is clear for a later ceremonial installation. The three original ImageGen
concepts/prompts are in `rajbari/concepts/`; later user feedback defines the final
warm plaster palette and more distinctive entrance.

Jorasanko keeps **two main houses**, Bahir Mahal around the southern private
garden court and Andar Mahal around the northern public court, with the central
white Thakur Dalan and finished side links. The supplied plan's west entrance,
south portico and northeast rear access remain open. Its southern garden/front
elevation includes green shuttered doors, paired red columns, white floral
frieze, ironwork entrance balcony and a shallow open upper gallery/green eaves.
This last gallery is an exterior silhouette feature, not a full third interior.

| Asset | Unique source triangles | Unique budget upper end | Placed triangles |
|---|---:|---:|---:|
| Rajbari | 27,458 | 38,000 | 123,800 |
| Jorasanko | 30,094 | 34,000 | 156,664 |
| Batch | 57,552 | 72,000 | 280,464 |

Neither exceeds its unique budget: Rajbari is 27.7% below its upper target,
Jorasanko 11.5% below, and the batch 20.1% below. The batch is also below the
82,000 unique soft review threshold. Placed totals include reused modules;
the brief specifies no numeric placed-triangle ceiling for this batch.
These are asset counts, not a mobile performance benchmark.

All **10 modular FBXs** are together in `../../../exports/kolkata_cultural/`.
Every exported mesh is at most **5,500 triangles**, below Roblox's documented
[20,000-triangle individual mesh limit](https://create.roblox.com/docs/art/modeling/specifications)
(checked 2026-10-24). Keep **Merge Meshes disabled** in the
[Studio importer](https://create.roblox.com/docs/studio/importer).
Import at Stud/1, preserve section alignment at the common ground-center origin,
anchor static meshes, retain opaque material slots and use simple authored
collision guides. Do not merge a whole compound into a single mesh.

Working Blender night lights cover both houses/estate elevations, courts,
galleries and entrances, plus Rajbari's mandap/dome. The shadowless native spot
setup in `CulturalLighting.luau` is supplied beside the FBXs, since mesh exports
do not contain lights. Pass the shared ground-origin CFrame when installing;
no global Lighting settings or runtime lighting loops are created.

Original day, reverse, court and night PNGs are saved inside each asset folder;
Jorasanko also has a front-facade view. Source/FBX closed geometry, finite data,
triangle caps, winding, material/scale round trip, courtyard sky and sampled
entry routes are checked in `validation.json`. Actual Studio import/appearance,
player collisions and device performance are outside this Blender-only task.

Build with Blender `--python-exit-code 1 --python build.py`; review with
`--python-exit-code 1 --python review.py`; pack the reviewed scenes with
`--python-exit-code 1 --python library.py`. Run `python package.py` for manifests,
assembly notes and the static native light helper. Generation scripts/source
files own these assets; there is no automatic Studio synchronization.

All geometry and flat palettes are original. User photos stay locally in each
`references/photos/` folder, excluded from Git; tracked manifests record mapping
and hashes. No photographic texture, external model or full interior is included.
Older Tier 2 Jorasanko assets remain separate.
