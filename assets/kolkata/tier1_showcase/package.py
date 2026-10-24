"""Write portable package inventories and concise handoff notes; no asset changes."""
import json
import sys
from pathlib import Path

BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
from catalog import ROOT,EXPORT


def main():
    manifest=json.loads((BASE/'export-manifest.json').read_text(encoding='utf8'))
    validation=json.loads((BASE/'validation.json').read_text(encoding='utf8'))
    rows=[]
    for a in manifest['assets']:
        folder=EXPORT/a['packageKey'];original=json.loads((ROOT/a['metadata']).read_text(encoding='utf8'))
        local=lambda path:Path(path).relative_to(folder.relative_to(ROOT)).as_posix()
        packaged=[]
        for part in a['files']:
            packaged.append(dict(part,file=local(part['file'])))
        dependencies=[]
        for dep in a['textures']:
            dependencies.append(dict(dep,file='../shared/textures/'+Path(dep['file']).name))
        helpers=[]
        for dep in a['helpers']:
            path=ROOT/dep['file']
            file=local(dep['file']) if path.is_relative_to(folder) else '../shared/'+path.name
            helpers.append(dict(dep,file=file))
        package=dict(assetId=a['assetId'],name=a['name'],dimensionsStuds=a['dimensionsStuds'],
            units='Stud / 1; Blender +Y front, Z up; Roblox -Z front, Y up',
            origin='Original authored ground origin; no showcase-grid offset in these FBXs',
            assembledTriangles=a['assembledTriangles'],uniqueSourceTriangles=a['uniqueSourceTriangles'],
            files=packaged,textures=dependencies,helpers=helpers,
            provenance=dict(source=a['source'],sourceSha256=a['sourceSha256'],metadata=a['metadata'],metadataSha256=a['metadataSha256']),
            originalAuthoringMetadata=original,
            originalMetadataPathNote='Paths inside originalAuthoringMetadata refer to the canonical source folder in the repository; use files above for this portable export package.')
        (folder/'package-manifest.json').write_text(json.dumps(package,indent=2),encoding='utf8')
        default=[p for p in packaged if p['defaultImport']]
        dims=a['dimensionsStuds'];size=' × '.join(f'{dims[k]:g}' for k in ['width','height','depth'])
        text=f'''# {a['label']}

{len(default)} modular FBXs in this folder, including the finished foundation/grounds.
Dimensions **{size} studs (width × height × depth)**.
Geometry: **{a['uniqueSourceTriangles']:,} unique / {a['assembledTriangles']:,} placed triangles**.

Import all root-level FBXs together with **Stud / scale 1**, mesh merging off and
the common authored origin preserved. Keep each section's relative transform;
do not recenter the sections independently. Anchor the resulting scenery later.
These FBXs contain no staging-grid offset. The [package manifest](package-manifest.json)
lists each section, material/texture dependencies and original authoring metadata.

'''
        if a['assetId']=='KOL_T1_DAKSHINESHWAR':
            text+='''The default `10_Shiva_Temples.fbx` contains all twelve existing shrines.
`modules/` holds the optional single-shrine master, placements and original
assembly helper for reusing one set of MeshIds. Use either the complete row or
the master/clone workflow; importing both duplicates the shrines.
`InstallNightLights.luau` is the existing optional native-light installer.
Water remains native Terrain work for later integration: local Y=-5, river
towards -Z, ghat front Z=-133.8 and lowest tread Y=-7. No water mesh is missing.

'''
        text+='''Blender lights and collision guides are retained in the master, outside the
visible-geometry FBX exports. Configure native lights and simplified collision
during later Studio integration, using the preserved authoring metadata/helpers.
Source shader graphs remain exact in Blender; Studio uses imported supported
materials/textures rather than arbitrary Blender shader graphs. No Studio
import or world modification has been performed for this staging task.
'''
        (folder/'README.md').write_text(text,encoding='utf8')
        rows.append(f"| {a['index']:02} | [{a['label']}]({a['packageKey']}/README.md) | {size} | {len(default)} |")
    notes='''# Completed Tier 1 export staging

One master Blender scene contains **16 completed landmark packages** in a 4×4
inspection grid. This is an offline asset showcase, not Kolkata's city layout.
The original completed masters and exports are unchanged.

The master is `assets/kolkata/tier1_showcase/Kolkata_Tier1_Staging.blend` in the
repository. Its numbered landmark collections include source architecture,
linked repeated meshes, foundation/grounds, fixtures and original collision
guides where present. `PIVOT | <landmark>` moves the entire package: select it
and use Select Hierarchy for whole-landmark selection. Subcollections retain the
authored modular structure. The `00 | Staging presentation` collection holds
only the showcase camera and daylight. Original architectural lights are
retained with render visibility disabled for the daytime showcase.

## Import packages

Each named folder below is independently importable. Import its root FBXs
together with **Stud units, scale 1, Merge Meshes off**. Preserve their common
ground origin and relative transforms. FBX orientation is Roblox Y up, -Z front;
Blender authoring is Z up, +Y front. Staging pivots apply translation only; those
grid translations are absent from the packaged FBXs.

There are **131 default modular FBXs**, plus one optional single-shrine master
under `dakshineshwar/modules/`. No giant scene FBX is supplied. Dakshineshwar's
default row already includes twelve shrines; its master/placement helper offers
an alternative shared-MeshId workflow. Each asset's package manifest uses paths
relative to its own folder and includes the original material, collision,
socket/module and lighting metadata. Keep the sibling `shared/` folder with
the packages; it contains the five image dependencies and existing light helpers.
Images are also packed in the Blender master; completed FBXs were copied
unchanged, except for the existing assembled Shiva row exported at local origin.

| Collection | Landmark / package | Width × height × depth (studs) | Default FBXs |
|---|---|---|---:|
'''+ '\n'.join(rows)+f'''

## Verification and source ownership

The essential pass verified one scene, all 16 asset collections, unit scale,
source geometry/UV/material preservation, repeated linked meshes, unchanged
canonical file hashes, dependency availability and modular FBX geometry/normals.
The measured nearest footprint separation is **{validation['minimumGapStuds']:g} studs**.
All FBX meshes are below 15,000 triangles; the largest is **{validation['largestExportMeshTriangles']:,}**.
Totals: **298,998 unique source / 1,136,464 placed triangles** across the showcase.
The newly exported shrine row passed a Blender round trip with unit scale,
matching bounds, materials and original UV inventory. The overview was visually inspected.
See `validation.json` and `export-manifest.json` for the inventory and hashes.

Canonical per-landmark `.blend` files remain the editable source of truth.
Rebuild this staging copy using `build.py` after future canonical changes.
For deliberate edits to the staging copy, `reexport.py -- KOL_T1_ASSET_ID`
exports only that landmark's named sections into its separate `reexported/`
folder after stripping the grid pivot. Run it with Blender's `--background
--python` arguments; no whole-scene export action is provided.

Native lights, collision settings, streaming and water are later Studio work.
Blender node graphs are preserved in the master but are not executable Studio
materials. This task did not change Studio, place a city, run gameplay checks
or measure device performance. No new architecture, textures or external assets
were produced; provenance remains with the original landmark packages.
'''
    (EXPORT/'README.md').write_text(notes,encoding='utf8')
    master_notes='''# Tier 1 master showcase

Open [Kolkata_Tier1_Staging.blend](Kolkata_Tier1_Staging.blend) for the complete
16-landmark staging scene. Each numbered collection has its own ground-origin
pivot and original modular source hierarchy, with foundations and grounds.
Geometry, linked repeats, material graphs and UVs are preserved; all five
material images are packed. Move a `PIVOT | …` to reposition a whole landmark.

![All sixteen completed Tier 1 packages](preview-overview.png)

The [final export packages and import guidance](../../../exports/kolkata_tier1_staging/README.md)
contain 131 default modular FBXs and the optional Shiva master. The
[export manifest](export-manifest.json) records sources, hashes, local/staging
transforms, dimensions, dependencies and module counts; the
[essential check report](validation.json) records the verified result.

This is a 4×4 inspection grid with at least 218 studs between footprints.
It is not the final city. Source masters remain unchanged and authoritative;
Studio has not been modified. Presentation lights/camera are separate from exports.

Reproduce from the repo root with Blender 5.2:

```powershell
& 'C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe' --background --python-exit-code 1 --python assets/kolkata/tier1_showcase/build.py
& 'C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe' --background --python-exit-code 1 --python assets/kolkata/tier1_showcase/verify.py
python assets/kolkata/tier1_showcase/package.py
```

For one deliberately edited staging asset, run `reexport.py -- KOL_T1_ASSET_ID`
with Blender's `--python` argument. Output goes to that asset's `reexported/`
folder, at its original local origin; the completed packages are not overwritten.
'''
    (BASE/'README.md').write_text(master_notes,encoding='utf8')
    print('PACKAGES_DOCUMENTED',len(manifest['assets']))


if __name__=='__main__':main()
