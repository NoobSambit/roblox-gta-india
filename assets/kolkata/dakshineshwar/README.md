# Dakshineshwar Kali temple complex

Original, reference-led Kolkata Tier 1 asset: nine-spire main temple, limited
accessible Kali chamber, twelve linked Shiva shrines, rectangular courtyard
and attached three-flight ghat. Front is Roblox -Z / Blender +Y. One neutral
Blender unit is one Roblox stud; common origin is the campus ground center.

Editable source: `KOL_T1_DAKSHINESHWAR.blend`. Rebuild with Blender Python
`build.py`; `review.py` performs the focused source/FBX check and saves the
four original `preview-*.png` images. `concepts/` contains the four requested
ImageGen concepts; prompts are retained in `concept-prompts.json`.

| Geometry | Actual triangles | Revised allowance |
|---|---:|---:|
| Unique authoring geometry | 40,772 | 40,000–55,000 |
| Assembled visible complex | 75,580 | 65,000–95,000 |
| Placed soft review threshold | — | 110,000 |
| Largest exported mesh | 5,500 | Roblox individual limit: 20,000 |

The Shiva master is 1,516 triangles, shared across all twelve authoring
placements and exported once. Export section batching duplicates some other
architectural modules; unique source triangles are not uploaded-memory counts.
The render envelope is 418 × 219.853 studs, 159.6 studs from lowest foundation
to highest finial. Campus paving is Y=0.8; main shrine platform is Y=6.05.

All fourteen FBXs, the Shiva placement manifest and offline Studio assembly
helpers are together in `../../../exports/dakshineshwar/`. See that folder's
README before importing the master module. Meshes are opaque shared-color
materials, without photo textures. `asset.json` retains sections, transforms,
collision roles, sockets, exact counts and revised budget.

Ground repairs remove coplanar cap layers. Curved friezes have continuous
backing and red faces projecting 0.45 studs; ghat tread solids overlap their
separator edges. Paving joints are intentional recessed gaps. Temple openings
remain open rather than having transparent door planes.

Twenty actual Blender lights cover the main temple, Shiva rows, shrine,
courtyard and ghat; only the shrine key casts shadows. `night-lights.json`
records the equivalent native-light plan. The export helper installs those
lights after import; FBX geometry does not carry Roblox light instances.
Preview sky/sun/camera live in a separate collection and are not exported.

Use native Roblox water at local Y=-5, toward negative Z from the attached
ghat. The lowest tread is Y=-7; its front is Z=-133.8. There is no final water
mesh. Apply any landmark translation/rotation to the water datum as well.

At integration, keep decoration noncolliding and use simple authored box/step
colliders for courtyard, platforms, shrine walls and ghat. Do not use a convex
hull around a whole material batch: that can seal doorways. Keep the small
murti/interior and porch details scoped to close viewing; stream the landmark
and reduce lights with the game's distance/quality policy. This asset task
does not establish device performance or implement that runtime policy.

`validation.json` records closed triangles, finite vertices, winding, FBX mesh
limits, one scale/material round trip, nine spires, twelve reused shrines,
entry clearance and the reported surface repairs. Studio import, collision
behaviour, the native helper scripts and mobile performance remain untested;
Studio integration was explicitly excluded from this task.

Eight supplied photos remain local under
`artifacts/references/dakshineshwar/`; `references.json` tracks their provenance.
They are modeling references, not redistributed game textures. All geometry,
preview renders and generated concept assets in this folder are original.
