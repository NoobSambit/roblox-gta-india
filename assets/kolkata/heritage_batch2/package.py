"""Batch manifests, local photographic provenance and concise import notes."""
import hashlib
import json
import shutil
from pathlib import Path

BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2]
OUT=ROOT/'exports/kolkata_heritage_batch2'
ATTACH=Path(r'C:\Users\Sambit Pradhan\.codex\attachments\f67a113b-34ff-421c-850d-841df98f88f4')
GROUPS={'writers':list(range(1,7)),'metropolitan':[10,11,12],'gpo':[7,8,9],'town_hall':[13,14,15]}
NOTES={
    'writers':'Long red three-register facade, six giant columns, central pediment, raised mansard pavilions, dormers, roof ironwork and original simplified allegorical figures.',
    'metropolitan':'Two commercial street elevations, clipped rounded corner, wraparound balconies, tall clock cupola and two lower satellite cupolas. Carved ornament is simplified.',
    'gpo':'Connected L-shaped colonnades, rounded street corner, tall windowed drum, ribbed white dome and projecting clock. The footprint is deliberately compressed.',
    'town_hall':'Six-column Doric frontage, side return columns, broad entry steps, rosette frieze and flat balustraded entablature following the photos. A small doorway crown supplies classical pediment detail.'}


def prepare_references():
    for key,indices in GROUPS.items():
        folder=BASE/key;folder.mkdir(parents=True,exist_ok=True)
        local=ROOT/'artifacts/references/heritage_batch2'/key;local.mkdir(parents=True,exist_ok=True)
        entries=[]
        for i in indices:
            src=ATTACH/f'image-{i}.png';dest=local/src.name;shutil.copy2(src,dest)
            entries.append(dict(userReference=i,localFile=dest.relative_to(ROOT).as_posix(),
                sha256=hashlib.sha256(src.read_bytes()).hexdigest(),source='User-supplied photograph; visible credit/watermark retained locally',
                use='Visual modeling reference only; no image texture or copied asset geometry'))
        (folder/'references.json').write_text(json.dumps(dict(primarySource='User supplied reference images',
            design=NOTES[key],imagegenUsed=False,reason='References sufficiently define the adapted facade and massing',
            references=entries),indent=2),encoding='utf8')


def package():
    rows=[]
    for key in GROUPS:
        folder=BASE/key;row=json.loads((folder/'asset.json').read_text(encoding='utf8'));rows.append(row)
        (folder/'README.md').write_text(f'''# {row['name']} — Tier 1 heritage exterior

{NOTES[key]}

Editable source: `{row['source']}`. Original review PNGs: `preview-day.png`,
`preview-rear.png`, `preview-night.png`, `preview-night-rear.png`. Repeated bays/columns retain linked
mesh data. `asset.json` contains section exports, assembly transforms, material
roles, collision boxes and recommended night-lighting zones.

Geometry: **{row['uniqueSourceTriangles']:,} unique source / {row['assembledTriangles']:,}
assembled triangles**. Largest exported mesh: **{max(p['largestExportMeshTriangles'] for p in row['exports']):,}**.
Bounds in studs: {row['dimensionsStuds']}. Unique source counts measure editable
mesh reuse; material/section export batching bakes the assembled geometry.

All FBXs are together in `../../../../exports/kolkata_heritage_batch2/`.
Import files with this asset prefix together at **Stud / scale 1 / Merge Meshes
off / Anchored on**, retaining their common ground origin. Blender front +Y
maps to Roblox -Z. Opaque flat-color materials; no photographic textures.

Night zones: {'; '.join(row['nightLightingZones'])}. **{len(row['nightLights'])} installed Blender
lights** cover front, sides, rear and crowns. The plan is included in `asset.json`.
Lights/camera are excluded from FBX. `InstallHeritageLights.luau` in the export
folder creates the matching native lights later; Studio execution is untested.

The source contains hidden empty-box collision guides, mirrored by
`collisionBoxes` metadata. Rebuild these as simple native collisions later;
keep decorative facade meshes noncolliding. The exterior shell intentionally
has no full room network. `validation.json` records geometry, winding, mesh
limits, one FBX round trip and column-bearing checks. Actual Studio import,
gameplay, collisions and mobile performance were not tested in this asset task.

Reference provenance: `references.json`. Photographs remain local in
`artifacts/references/heritage_batch2/{key}/`; they are not redistributed.
Rebuild with the corresponding `{key}.py` module through `build.py` in the parent
folder. The older Tier 2 asset is preserved separately.
''',encoding='utf8')
    inventory=[dict(assetId=r['assetId'],name=r['name'],metadata=f'{key}/asset.json',source=f'{key}/{r["source"]}',
        uniqueSourceTriangles=r['uniqueSourceTriangles'],assembledTriangles=r['assembledTriangles'],exportCount=len(r['exports']))
        for key,r in zip(GROUPS,rows)]
    summary=dict(assets=inventory,uniqueSourceTriangles=sum(r['uniqueSourceTriangles'] for r in rows),
        assembledTriangles=sum(r['assembledTriangles'] for r in rows),uniqueTarget=[47000,76000],
        uniqueSoftReview=85000,imagegenUsed=False,scope='Blender exterior assets only; no Studio integration')
    assert summary['uniqueSourceTriangles']<=85000
    (BASE/'batch-manifest.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
    lines=['# Kolkata Tier 1 heritage batch 2','',
        'Four exterior landmarks, each with its own editable blend, reference notes,',
        'original front/rear day/night PNGs, counts, collision guides and modular exports.',
        'The supplied photos define the architecture. ImageGen was unnecessary.',
        '', '| Asset | Unique source tris | Assembled tris | FBXs |', '|---|---:|---:|---:|']
    for r in rows:lines.append(f"| {r['name']} | {r['uniqueSourceTriangles']:,} | {r['assembledTriangles']:,} | {len(r['exports'])} |")
    lines.extend(['',f"Total: **{summary['uniqueSourceTriangles']:,} unique / {summary['assembledTriangles']:,} placed triangles**.",
        'The unique total is within the 47k–76k batch target and below the 85k soft threshold.',
        'Source reuse and assembled export cost are reported separately; these are not device benchmarks.',
        '', 'Open `Heritage_Batch2_Live.blend` and choose a KOL_T1 scene from the scene selector.',
        'It contains only this four-building asset library, not a district layout.',
        'All FBXs are in `../../../exports/kolkata_heritage_batch2/`.',
        'Keep each building’s section files aligned at their common ground origin.',
        'Import at Stud/1, meshes separate, anchored. Source front +Y becomes Roblox -Z.',
        'Every exported mesh is capped at 5,500 triangles. Preserve the opaque material slots.',
        '', 'Working Blender lights cover every elevation and the major crowns, with a native',
        'Studio light installer supplied beside the FBXs. Lights and review rigs are excluded',
        'from mesh exports. No day/night gameplay system, Studio integration, full interiors',
        'or gameplay was built. Actual Studio collision/appearance and device performance remain',
        'unverified. The source files/generation modules own these assets; there is no automatic',
        'Studio synchronization. Older Tier 2 versions are preserved.',
        '', 'Build with Blender `--python-exit-code 1 --python build.py`; review with',
        '`--python-exit-code 1 --python review.py`. Run `python package.py` for notes/manifests.',
        'One focused source/FBX and bearing check plus front/rear day/night review per building is the',
        'validation scope. Original geometry/materials only; no external model/texture dependency.'])
    (BASE/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    (OUT/'README.md').write_text('''# Kolkata heritage batch 2 — FBX imports

Import all sections with the same building prefix together: WRITERS,
METROPOLITAN, GPO or TOWN_HALL. Each section contains material-separated mesh
chunks; it is not a separate building to recenter. **Stud / scale 1 / Merge
Meshes off / Anchored on**, common origin preserved. Meshes are at most 5,500
triangles and use opaque flat colors. No textures, preview rigs or water meshes.

Sources, previews, geometry validation and per-building assembly/collision
metadata are in `../../assets/kolkata/heritage_batch2/`. Simple native collision,
distance visibility and light quality scaling belong to later Studio integration.
`InstallHeritageLights.luau` returns a function `(model, assetId, originCFrame)`.
Use the assetId from its `asset.json`, for example `KOL_T1_WRITERS`; origin is
the authored ground-center transform, `CFrame.identity` for an unmoved import.
It creates the same front/side/rear/crown spot-light plan as the Blender source,
without changing global Lighting or adding a day/night controller. Light ranges
are no greater than 60 studs; shadow casting is disabled to control cost.
The helper only replaces its own prior lighting folder. Its Studio execution
and visual parity are untested. No Studio import or device benchmark is claimed.
''',encoding='utf8')
    write_lights(rows)
    expected={Path(p['file']).name for row in rows for p in row['exports']}
    for path in OUT.glob('KOL_T1_*.fbx'):
        if path.name not in expected:
            assert path.resolve().parent==OUT.resolve();path.unlink()
    obsolete=BASE/'metropolitan/KOL_T1_METROPOLITAN.001.blend'
    if obsolete.is_file():obsolete.unlink()
    print('PACKAGED',summary['uniqueSourceTriangles'],summary['assembledTriangles'],sum(len(r['exports']) for r in rows))


def write_lights(rows):
    def vec(values):return 'Vector3.new('+', '.join(f'{x:g}' for x in values)+')'
    lines=['--!strict','-- Offline authoring helper. Geometry FBX does not contain native Roblox lights.',
        'type Spec = { name: string, position: Vector3, target: Vector3, range: number, brightness: number }',
        'local plans: { [string]: { Spec } } = {']
    for row in rows:
        lines.append('\t["'+row['assetId']+'"] = {')
        for s in row['nightLights']:
            lines.append('\t\t{ name = "'+s['name']+'", position = '+vec(s['positionStuds'])+', target = '+vec(s['targetStuds'])+f', range = {s["rangeStuds"]}, brightness = {s["brightness"]}'+' },')
        lines.append('\t},')
    lines.extend(['}', '''
return function(model: Model, assetId: string, origin: CFrame): Folder
	local specs = plans[assetId]
	assert(specs, "Unknown heritage assetId: " .. assetId)
	local folder = Instance.new("Folder")
	folder.Name = "HeritageNightLights"
	folder:SetAttribute("AuthoredHeritageLights", true)
	for _, spec in specs do
		local holder = Instance.new("Part")
		holder.Name = spec.name
		holder.Size = Vector3.new(0.2, 0.2, 0.2)
		holder.Transparency = 1
		holder.Anchored = true
		holder.CastShadow = false
		holder.CanCollide = false
		holder.CanTouch = false
		holder.CanQuery = false
		holder.CFrame = origin * CFrame.lookAt(spec.position, spec.target)
		local light = Instance.new("SpotLight")
		light.Face = Enum.NormalId.Front
		light.Angle = 100
		light.Range = spec.range
		light.Brightness = spec.brightness
		light.Color = Color3.fromRGB(255, 218, 167)
		light.Shadows = false
		light.Enabled = true
		light.Parent = holder
		holder.Parent = folder
	end
	for _, child in model:GetChildren() do
		if child:GetAttribute("AuthoredHeritageLights") == true then child:Destroy() end
	end
	folder.Parent = model
	return folder
end
'''])
    (OUT/'InstallHeritageLights.luau').write_text('\n'.join(lines),encoding='utf8')


if __name__=='__main__':
    import sys
    prepare_references()
    if '--references-only' not in sys.argv:package()
