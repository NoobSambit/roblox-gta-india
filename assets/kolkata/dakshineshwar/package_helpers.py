"""Generate the small offline Studio assembly helpers from authored metadata."""
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
OUT=HERE.parents[2]/'exports/dakshineshwar'


def vec(values):return 'Vector3.new('+', '.join(f'{v:g}' for v in values)+')'


def write_helpers():
    plan=json.loads((HERE/'night-lights.json').read_text(encoding='utf8'))
    rows=[]
    for spec in plan['lights']:
        rows.append('\t{ name = "'+spec['name']+'", position = '+vec(spec['positionStuds'])+
            ', target = '+(vec(spec['targetStuds']) if spec['targetStuds'] else 'nil')+
            f', range = {spec["rangeStuds"]}, brightness = {spec["brightness"]}, shadows = '+str(spec['shadows']).lower()+' },')
    lights='''--!strict
-- Authoring helper: paste into a ModuleScript; does not alter global Lighting.
type LightSpec = {
	name: string, position: Vector3, target: Vector3?,
	range: number, brightness: number, shadows: boolean,
}
local specs: { LightSpec } = {
'''+ '\n'.join(rows)+'''
}

return function(model: Model, origin: CFrame): Folder
	local folder = Instance.new("Folder")
	folder.Name = "DakshineshwarNightLights"
	folder:SetAttribute("DakshineshwarAuthoredLights", true)
	for _, spec in specs do
		local holder = Instance.new("Part")
		holder.Name = spec.name
		holder.Size = Vector3.new(0.2, 0.2, 0.2)
		holder.Anchored = true
		holder.Transparency = 1
		holder.CastShadow = false
		holder.CanCollide = false
		holder.CanTouch = false
		holder.CanQuery = false
		local target = spec.target
		local light: PointLight | SpotLight
		if target then
			holder.CFrame = origin * CFrame.lookAt(spec.position, target)
			local spot = Instance.new("SpotLight")
			spot.Face = Enum.NormalId.Front
			spot.Angle = 75
			light = spot
		else
			holder.CFrame = origin * CFrame.new(spec.position)
			light = Instance.new("PointLight")
		end
		light.Color = Color3.fromRGB(255, 209, 147)
		light.Brightness = spec.brightness
		light.Range = spec.range
		light.Shadows = spec.shadows
		light.Enabled = true
		light.Parent = holder
		holder.Parent = folder
	end
	-- Replace only content installed by this helper, after construction succeeds.
	for _, child in model:GetChildren() do
		if child:GetAttribute("DakshineshwarAuthoredLights") == true then
			child:Destroy()
		end
	end
	folder.Parent = model
	return folder
end
'''
    (OUT/'InstallNightLights.luau').write_text(lights,encoding='utf8')
    module=json.loads((OUT/'shiva-placements.json').read_text(encoding='utf8'))
    placements='\n'.join('\t'+vec(p['positionStuds'])+',' for p in module['placements'])
    assembly='''--!strict
-- Template must be imported at its authored origin, then stored outside Workspace.
local positions: { Vector3 } = {
'''+placements+'''
}

return function(template: Model, complex: Model, origin: CFrame): Folder
	local folder = Instance.new("Folder")
	folder.Name = "ShivaTemples"
	folder:SetAttribute("DakshineshwarAuthoredShivaRow", true)
	local templatePivot = template:GetPivot()
	for index, position in positions do
		local shrine = template:Clone()
		shrine.Name = `ShivaTemple_{index}`
		shrine:SetAttribute("ShrineIndex", index)
		-- Preserve the imported pivot offset. Clone retains shared MeshIds.
		shrine:PivotTo(origin * CFrame.new(position) * templatePivot)
		for _, descendant in shrine:GetDescendants() do
			if descendant:IsA("BasePart") then
				descendant.Anchored = true
			end
		end
		shrine.Parent = folder
	end
	for _, child in complex:GetChildren() do
		if child:GetAttribute("DakshineshwarAuthoredShivaRow") == true then
			child:Destroy()
		end
	end
	folder.Parent = complex
	return folder
end
'''
    (OUT/'AssembleShivaRow.luau').write_text(assembly,encoding='utf8')


if __name__=='__main__':write_helpers()
