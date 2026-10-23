"""Summaries/provenance and a static native-light installer; no Studio mutation."""
import hashlib
import json
from pathlib import Path

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
EXPORT=ROOT/'exports/kolkata_cultural'


def lua(value):
    if isinstance(value,str):return json.dumps(value)
    if isinstance(value,bool):return str(value).lower()
    if isinstance(value,(int,float)):return str(value)
    if isinstance(value,list):return '{'+','.join(lua(v) for v in value)+'}'
    return '{'+','.join('['+lua(k)+']='+lua(v) for k,v in value.items())+'}'


def package():
    rows=[];summary=[];lightdata={}
    for key,images in [('rajbari',range(9,12)),('jorasanko',range(1,9))]:
        folder=BASE/key;row=json.loads((folder/'asset.json').read_text(encoding='utf8'));rows.append(row)
        upper=38000 if key=='rajbari' else 34000
        ref=dict(origin='User-supplied reference photographs/drawing, mapping explicitly confirmed in chat',
            usage='Private visual study only. Photos kept locally and excluded from Git; redistribution rights not established.',
            mapping='9–10 brick/cream Rajbari courtyard; 11 domed Rajbari street exterior' if key=='rajbari' else '1 layout, 2–8 Jorasanko red/white galleries and green shutters',files=[])
        for i in images:
            path=folder/'references/photos'/f'image-{i}.png'
            ref['files'].append(dict(file='photos/'+path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        (folder/'references/manifest.json').write_text(json.dumps(ref,indent=2),encoding='utf8')
        summary.append({k:row[k] for k in ['assetId','name','dimensionsStuds','uniqueSourceTriangles','assembledTriangles','largestMeshTriangles'] }|
            dict(source=f'{key}/{row["source"]}',exports=row['exports'],nightLights=len(row['nightLights']),
                uniqueBudgetUpper=upper,budgetOveragePercent=round(max(0,row['uniqueSourceTriangles']-upper)/upper*100,2),
                headroomBelowUpperPercent=round((upper-row['uniqueSourceTriangles'])/upper*100,2)))
        lightdata[row['assetId']]=row['nightLights']
        (folder/'ASSEMBLY.md').write_text(f'''# {row['name']}

Editable source: `{row['source']}`. Source front is Blender +Y, exported Roblox -Z.
One neutral Blender unit = one Roblox stud. Align all section FBXs at the same
ground-center origin; import at Stud/1, retain separate meshes and material slots.
Files are together in `../../../../exports/kolkata_cultural/`.

{row['uniqueSourceTriangles']:,} unique source triangles; {row['assembledTriangles']:,} placed.
Source bays share mesh data. Exported section chunks bake placements; do not
mistake unique source counts for the assembled rendering cost. Largest export
mesh: {max(e['largestExportMeshTriangles'] for e in row['exports']):,} triangles.

Visible architecture, simple collision-box guides and lighting are separate
collections. Guides are excluded from FBX, and `asset.json` records their sizes.
Use simple shell/plinth/step collisions and non-colliding decorative rails,
windows and trim at integration. Preserve the courtyard voids and entry routes.
Set static content anchored, use automatic render fidelity, and stream the two
main houses/estate sections at practical distances. Small fixtures/ornament can
hide earlier than the shell. No mobile performance claim is made.

{len(row['nightLights'])} working Blender lights cover external elevations,
galleries, entrances and cultural focal zones. `CulturalLighting.luau` beside
the FBXs reproduces the authored light positions with native shadowless spots
after import. FBX contains meshes only. Its origin must be the common ground
origin, not an automatically recentered model bounding-box pivot. No global
Lighting properties or day/night runtime system are changed.

Original day, reverse, courtyard and night PNGs are saved here. `validation.json`
records source/FBX checks and clear court/entry samples; these are not Studio,
player collision, full navigation, gameplay or physical-device tests.
''',encoding='utf8')
    data=dict(assets=summary,totalUniqueSourceTriangles=sum(r['uniqueSourceTriangles'] for r in rows),
        totalPlacedTriangles=sum(r['assembledTriangles'] for r in rows),
        uniqueBudgetUpper=72000,uniqueSoftReviewThreshold=82000,
        budgetOveragePercent=round(max(0,sum(r['uniqueSourceTriangles'] for r in rows)-72000)/72000*100,2),
        robloxIndividualMeshLimit=20000,largestActualExportMeshTriangles=max(e['largestExportMeshTriangles'] for r in rows for e in r['exports']),
        specification='https://create.roblox.com/docs/art/modeling/specifications',specificationChecked='2026-10-24',
        scope='Original Blender exterior/compound assets. Studio integration excluded by task.')
    (BASE/'batch-manifest.json').write_text(json.dumps(data,indent=2),encoding='utf8')
    (EXPORT/'lighting-zones.json').write_text(json.dumps(lightdata,indent=2),encoding='utf8')
    module='''--!strict
-- Static authoring helper; install after importing FBXs at their shared origin.
-- Call install(model, "KOL_T1_RAJBARI" or "KOL_T1_JORASANKO", groundOriginCFrame).
-- Does not change global Lighting or start any runtime/day-night loops.
type LightZone = {
    name: string, positionStuds: {number}, targetStuds: {number}, rangeStuds: number,
    brightness: number, angleDegrees: number, colorRGB: {number}, blenderWatts: number, shadows: boolean,
}
local definitions: {[string]: {LightZone}} = '''+lua(lightdata)+'''

local LightingSetup = {}

function LightingSetup.install(model: Model, assetId: string, groundOrigin: CFrame): number
    assert(model:IsA("Model"), "Expected the imported compound Model")
    local zones = definitions[assetId]
    assert(zones ~= nil, "Unknown cultural asset identifier")
    assert(typeof(groundOrigin) == "CFrame", "Pass the FBX common ground-origin CFrame")
    local existing = model:FindFirstChild("CulturalNightLights")
    if existing then
        assert(existing:GetAttribute("CulturalLightingOwned") == true, "Light folder name is already in use")
    end
    local folder = Instance.new("Folder")
    folder.Name = "CulturalNightLights"
    folder:SetAttribute("CulturalLightingOwned", true)
    for _, zone in zones do
        local p = zone.positionStuds
        local t = zone.targetStuds
        local position = groundOrigin:PointToWorldSpace(Vector3.new(p[1], p[2], p[3]))
        local target = groundOrigin:PointToWorldSpace(Vector3.new(t[1], t[2], t[3]))
        local holder = Instance.new("Part")
        holder.Name = zone.name
        holder.Size = Vector3.new(0.2, 0.2, 0.2)
        holder.CFrame = CFrame.lookAt(position, target)
        holder.Anchored = true
        holder.Transparency = 1
        holder.CanCollide = false
        holder.CanTouch = false
        holder.CanQuery = false
        holder.CastShadow = false
        local light = Instance.new("SpotLight")
        light.Name = "ArchitecturalWash"
        light.Face = Enum.NormalId.Front
        light.Color = Color3.fromRGB(zone.colorRGB[1], zone.colorRGB[2], zone.colorRGB[3])
        light.Brightness = zone.brightness
        light.Angle = zone.angleDegrees
        light.Range = math.min(zone.rangeStuds, 60)
        light.Shadows = false
        light.Parent = holder
        holder.Parent = folder
    end
    if existing then existing:Destroy() end
    folder.Parent = model
    return #zones
end

return LightingSetup
'''
    (EXPORT/'CulturalLighting.luau').write_text(module,encoding='utf8')
    print(json.dumps(data,indent=2))


if __name__=='__main__':package()
