--!strict
-- Authoring helper: paste into a ModuleScript; does not alter global Lighting.
type LightSpec = {
	name: string, position: Vector3, target: Vector3?,
	range: number, brightness: number, shadows: boolean,
}
local specs: { LightSpec } = {
	{ name = "Courtyard_01", position = Vector3.new(-151, 10, -66), target = nil, range = 22, brightness = 1.2, shadows = false },
	{ name = "Courtyard_02", position = Vector3.new(-51, 10, -66), target = nil, range = 22, brightness = 1.2, shadows = false },
	{ name = "Courtyard_03", position = Vector3.new(51, 10, -66), target = nil, range = 22, brightness = 1.2, shadows = false },
	{ name = "Courtyard_04", position = Vector3.new(151, 10, -66), target = nil, range = 22, brightness = 1.2, shadows = false },
	{ name = "Courtyard_05", position = Vector3.new(-48, 10, 70), target = nil, range = 22, brightness = 1.2, shadows = false },
	{ name = "Courtyard_06", position = Vector3.new(48, 10, 70), target = nil, range = 22, brightness = 1.2, shadows = false },
	{ name = "Ghat_01", position = Vector3.new(-95, 7.2, -102), target = nil, range = 38, brightness = 1.5, shadows = false },
	{ name = "Ghat_02", position = Vector3.new(95, 7.2, -102), target = nil, range = 38, brightness = 1.5, shadows = false },
	{ name = "Kali_face", position = Vector3.new(0, 24, 18), target = nil, range = 26, brightness = 2.2, shadows = true },
	{ name = "Shrine_fill", position = Vector3.new(0, 16, 23), target = nil, range = 18, brightness = 1.1, shadows = false },
	{ name = "Shiva_row_01", position = Vector3.new(-157, 14.7, 15), target = nil, range = 36, brightness = 1.1, shadows = false },
	{ name = "Shiva_row_02", position = Vector3.new(-85, 14.7, 15), target = nil, range = 36, brightness = 1.1, shadows = false },
	{ name = "Shiva_row_03", position = Vector3.new(85, 14.7, 15), target = nil, range = 36, brightness = 1.1, shadows = false },
	{ name = "Shiva_row_04", position = Vector3.new(157, 14.7, 15), target = nil, range = 36, brightness = 1.1, shadows = false },
	{ name = "Temple_wash_01", position = Vector3.new(-28, 12, -28), target = Vector3.new(-20, 42, -10), range = 60, brightness = 2.4, shadows = false },
	{ name = "Temple_wash_02", position = Vector3.new(28, 12, -28), target = Vector3.new(20, 42, -10), range = 60, brightness = 2.4, shadows = false },
	{ name = "Temple_wash_03", position = Vector3.new(-23, 57, -3), target = Vector3.new(-18, 101, 10), range = 60, brightness = 2.4, shadows = false },
	{ name = "Temple_wash_04", position = Vector3.new(23, 57, -3), target = Vector3.new(18, 101, 10), range = 60, brightness = 2.4, shadows = false },
	{ name = "Temple_wash_05", position = Vector3.new(-12, 93, 17), target = Vector3.new(0, 137, 22), range = 60, brightness = 2.4, shadows = false },
	{ name = "Temple_wash_06", position = Vector3.new(12, 93, 17), target = Vector3.new(0, 137, 22), range = 60, brightness = 2.4, shadows = false },
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
