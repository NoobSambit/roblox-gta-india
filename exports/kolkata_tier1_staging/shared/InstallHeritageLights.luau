--!strict
-- Offline authoring helper. Geometry FBX does not contain native Roblox lights.
type Spec = { name: string, position: Vector3, target: Vector3, range: number, brightness: number }
local plans: { [string]: { Spec } } = {
	["KOL_T1_WRITERS"] = {
		{ name = "Front_0", position = Vector3.new(-137, 3, -53), target = Vector3.new(-137, 40, -35), range = 60, brightness = 2 },
		{ name = "Front_1", position = Vector3.new(-94, 3, -53), target = Vector3.new(-94, 40, -35), range = 60, brightness = 2 },
		{ name = "Front_2", position = Vector3.new(-48, 3, -53), target = Vector3.new(-48, 40, -35), range = 60, brightness = 2 },
		{ name = "Front_3", position = Vector3.new(0, 3, -53), target = Vector3.new(0, 40, -35), range = 60, brightness = 2 },
		{ name = "Front_4", position = Vector3.new(48, 3, -53), target = Vector3.new(48, 40, -35), range = 60, brightness = 2 },
		{ name = "Front_5", position = Vector3.new(94, 3, -53), target = Vector3.new(94, 40, -35), range = 60, brightness = 2 },
		{ name = "Front_6", position = Vector3.new(137, 3, -53), target = Vector3.new(137, 40, -35), range = 60, brightness = 2 },
		{ name = "Rear_0", position = Vector3.new(-137, 3, 41), target = Vector3.new(-137, 38, 32), range = 60, brightness = 2 },
		{ name = "Rear_1", position = Vector3.new(-70, 3, 41), target = Vector3.new(-70, 38, 32), range = 60, brightness = 2 },
		{ name = "Rear_2", position = Vector3.new(0, 3, 41), target = Vector3.new(0, 38, 32), range = 60, brightness = 2 },
		{ name = "Rear_3", position = Vector3.new(70, 3, 41), target = Vector3.new(70, 38, 32), range = 60, brightness = 2 },
		{ name = "Rear_4", position = Vector3.new(137, 3, 41), target = Vector3.new(137, 38, 32), range = 60, brightness = 2 },
		{ name = "Side_-1_-17", position = Vector3.new(-161, 3, -17), target = Vector3.new(-156, 37, -17), range = 60, brightness = 2 },
		{ name = "Side_-1_20", position = Vector3.new(-161, 3, 20), target = Vector3.new(-156, 37, 20), range = 60, brightness = 2 },
		{ name = "Side_1_-17", position = Vector3.new(161, 3, -17), target = Vector3.new(156, 37, -17), range = 60, brightness = 2 },
		{ name = "Side_1_20", position = Vector3.new(161, 3, 20), target = Vector3.new(156, 37, 20), range = 60, brightness = 2 },
		{ name = "Crown_0", position = Vector3.new(-137, 64, -36), target = Vector3.new(-137, 80, -25), range = 40, brightness = 2 },
		{ name = "Crown_1", position = Vector3.new(0, 64, -36), target = Vector3.new(0, 80, -25), range = 40, brightness = 2 },
		{ name = "Crown_2", position = Vector3.new(137, 64, -36), target = Vector3.new(137, 80, -25), range = 40, brightness = 2 },
	},
	["KOL_T1_METROPOLITAN"] = {
		{ name = "Front_0", position = Vector3.new(-60, 3, -60), target = Vector3.new(-60, 38, -47), range = 60, brightness = 2 },
		{ name = "Front_1", position = Vector3.new(-25, 3, -60), target = Vector3.new(-25, 38, -47), range = 60, brightness = 2 },
		{ name = "Front_2", position = Vector3.new(15, 3, -60), target = Vector3.new(15, 38, -47), range = 60, brightness = 2 },
		{ name = "Front_3", position = Vector3.new(55, 3, -60), target = Vector3.new(55, 38, -47), range = 60, brightness = 2 },
		{ name = "Rear_0", position = Vector3.new(-58, 3, 51), target = Vector3.new(-58, 38, 47), range = 60, brightness = 2 },
		{ name = "Rear_1", position = Vector3.new(-18, 3, 51), target = Vector3.new(-18, 38, 47), range = 60, brightness = 2 },
		{ name = "Rear_2", position = Vector3.new(22, 3, 51), target = Vector3.new(22, 38, 47), range = 60, brightness = 2 },
		{ name = "Rear_3", position = Vector3.new(62, 3, 51), target = Vector3.new(62, 38, 47), range = 60, brightness = 2 },
		{ name = "Side_-1_-14", position = Vector3.new(-78, 3, -14), target = Vector3.new(-74, 36, -14), range = 60, brightness = 2 },
		{ name = "Side_-1_26", position = Vector3.new(-78, 3, 26), target = Vector3.new(-74, 36, 26), range = 60, brightness = 2 },
		{ name = "Side_1_-14", position = Vector3.new(78, 3, -14), target = Vector3.new(74, 36, -14), range = 60, brightness = 2 },
		{ name = "Side_1_26", position = Vector3.new(78, 3, 26), target = Vector3.new(74, 36, 26), range = 60, brightness = 2 },
		{ name = "Clock_crown", position = Vector3.new(61, 60, -45), target = Vector3.new(61, 82, -34), range = 42, brightness = 2 },
		{ name = "Satellite_crown", position = Vector3.new(-65, 59, -42), target = Vector3.new(-65, 71, -38), range = 30, brightness = 2 },
	},
	["KOL_T1_GPO"] = {
		{ name = "Front_0", position = Vector3.new(-52, 3, -66), target = Vector3.new(-52, 29, -51), range = 60, brightness = 2 },
		{ name = "Front_1", position = Vector3.new(-20, 3, -66), target = Vector3.new(-20, 29, -51), range = 60, brightness = 2 },
		{ name = "Front_2", position = Vector3.new(16, 3, -66), target = Vector3.new(16, 29, -51), range = 60, brightness = 2 },
		{ name = "Front_3", position = Vector3.new(54, 3, -66), target = Vector3.new(54, 29, -51), range = 60, brightness = 2 },
		{ name = "Rear_return_0", position = Vector3.new(-48, 3, 77), target = Vector3.new(-48, 33, 74), range = 60, brightness = 2 },
		{ name = "Rear_return_1", position = Vector3.new(-24, 3, 77), target = Vector3.new(-24, 33, 74), range = 60, brightness = 2 },
		{ name = "Rear_east_0", position = Vector3.new(5, 3, 7), target = Vector3.new(5, 30, 3), range = 60, brightness = 2 },
		{ name = "Rear_east_1", position = Vector3.new(44, 3, 7), target = Vector3.new(44, 30, 3), range = 60, brightness = 2 },
		{ name = "Rear_east_2", position = Vector3.new(74, 3, 7), target = Vector3.new(74, 30, 3), range = 60, brightness = 2 },
		{ name = "West_0", position = Vector3.new(-73, 3, -15), target = Vector3.new(-61, 30, -15), range = 60, brightness = 2 },
		{ name = "West_1", position = Vector3.new(-73, 3, 26), target = Vector3.new(-61, 30, 26), range = 60, brightness = 2 },
		{ name = "West_2", position = Vector3.new(-73, 3, 62), target = Vector3.new(-61, 30, 62), range = 60, brightness = 2 },
		{ name = "Inner_return_0", position = Vector3.new(-12, 3, 23), target = Vector3.new(-17, 30, 23), range = 60, brightness = 2 },
		{ name = "Inner_return_1", position = Vector3.new(-12, 3, 59), target = Vector3.new(-17, 30, 59), range = 60, brightness = 2 },
		{ name = "Dome_front", position = Vector3.new(-50, 46, -56), target = Vector3.new(-39, 87, -30), range = 60, brightness = 2 },
		{ name = "Dome_back", position = Vector3.new(-27, 46, -17), target = Vector3.new(-39, 87, -30), range = 60, brightness = 2 },
	},
	["KOL_T1_TOWN_HALL"] = {
		{ name = "Portico_0", position = Vector3.new(-32, 3, -65), target = Vector3.new(-32, 32, -40), range = 60, brightness = 2 },
		{ name = "Portico_1", position = Vector3.new(0, 3, -65), target = Vector3.new(0, 32, -40), range = 60, brightness = 2 },
		{ name = "Portico_2", position = Vector3.new(32, 3, -65), target = Vector3.new(32, 32, -40), range = 60, brightness = 2 },
		{ name = "Rear_0", position = Vector3.new(-39, 3, 39), target = Vector3.new(-39, 30, 36), range = 60, brightness = 2 },
		{ name = "Rear_1", position = Vector3.new(0, 3, 39), target = Vector3.new(0, 30, 36), range = 60, brightness = 2 },
		{ name = "Rear_2", position = Vector3.new(39, 3, 39), target = Vector3.new(39, 30, 36), range = 60, brightness = 2 },
		{ name = "Side_-1_-14", position = Vector3.new(-60, 3, -14), target = Vector3.new(-56, 30, -14), range = 60, brightness = 2 },
		{ name = "Side_-1_20", position = Vector3.new(-60, 3, 20), target = Vector3.new(-56, 30, 20), range = 60, brightness = 2 },
		{ name = "Side_1_-14", position = Vector3.new(60, 3, -14), target = Vector3.new(56, 30, -14), range = 60, brightness = 2 },
		{ name = "Side_1_20", position = Vector3.new(60, 3, 20), target = Vector3.new(56, 30, 20), range = 60, brightness = 2 },
	},
}

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
