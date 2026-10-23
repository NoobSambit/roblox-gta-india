--!strict
-- One-shot EDIT-ONLY authoring. Studio owns subsequent manual edits.
-- Does not replace, resize, move or remove any original Victoria geometry.
local ChangeHistory = game:GetService("ChangeHistoryService")
local Builder = {}
type Triple = {number}
local function vector(v: Triple): Vector3 return Vector3.new(v[1], v[2], v[3]) end
local colors = {
	Public = Color3.fromRGB(77, 161, 184), Medium = Color3.fromRGB(199, 164, 93),
	High = Color3.fromRGB(204, 105, 88), Archive = Color3.fromRGB(153, 127, 182),
	Wall = Color3.fromRGB(165, 167, 168), Escape = Color3.fromRGB(76, 174, 140),
	Security = Color3.fromRGB(239, 130, 72), Pedestal = Color3.fromRGB(115, 123, 130),
}

function Builder.build(): Model
	assert(not game:GetService("RunService"):IsRunning(), "Edit-only builder")
	local victoria = workspace.World.Cities.Kolkata.Districts.Maidan.VictoriaMemorial
	assert(not victoria:FindFirstChild("HeistGreybox"), "Greybox exists: inspect manual edits before rebuilding")
	assert(game:GetService("ServerStorage").WorldAuthoring:FindFirstChild("Task007Baseline"), "Save pre-task recovery and record baseline first")
	local site = victoria:GetPivot()
	local root = Instance.new("Model")
	root.Name = "HeistGreybox"
	root.WorldPivot = site
	root:SetAttribute("LayoutId", "VIC_HEIST_007")
	root:SetAttribute("Milestone", "Task007 greybox; no gameplay")
	root:SetAttribute("DesignOccupancy", "4-8 criminals; unverified design target")
	root:SetAttribute("ProvisionalBagCapacity", 10)
	root:SetAttribute("AlertRule", "First unauthorized restricted entry OR theft start; once per robbery event")
	root:SetAttribute("CCTVAndMotionSensors", "Decorative only; no detection planned")
	local folders: {[string]: Folder} = {}
	for _, name in {"Structure", "RoomZones", "LootMarkers", "SecurityMarkers", "RestrictedZoneMarkers", "EntryExitMarkers", "Wayfinding"} do
		local f = Instance.new("Folder") f.Name = name f.Parent = root folders[name] = f
	end
	local function part(parent: Instance, name: string, pos: Triple, size: Triple, color: Color3, solid: boolean, transparency: number?): Part
		local p = Instance.new("Part")
		p.Name, p.Size, p.CFrame = name, vector(size), site * CFrame.new(vector(pos))
		p.Anchored, p.CanCollide, p.CanTouch, p.CanQuery = true, solid, false, solid
		p.Material, p.Color, p.Transparency = Enum.Material.SmoothPlastic, color, transparency or 0
		p.TopSurface, p.BottomSurface, p.CastShadow = Enum.SurfaceType.Smooth, Enum.SurfaceType.Smooth, solid
		p.Parent = parent
		return p
	end
	local function floorText(parent: Instance, name: string, text: string, x: number, z: number, width: number, color: Color3)
		local p = part(parent, name, {x, 7.12, z}, {width, 0.06, 3.3}, color, false)
		local gui = Instance.new("SurfaceGui")
		gui.Name, gui.Face, gui.CanvasSize, gui.LightInfluence = "Label", Enum.NormalId.Top, Vector2.new(850, 180), 0
		local label = Instance.new("TextLabel")
		label.Size, label.BackgroundTransparency = UDim2.fromScale(1, 1), 1
		label.Text, label.TextColor3, label.TextScaled = text, Color3.fromRGB(245, 246, 243), true
		label.Font = Enum.Font.GothamBold label.Parent = gui gui.Parent = p
		return p
	end
	local function billboard(p: BasePart, text: string)
		local gui = Instance.new("BillboardGui")
		gui.Name, gui.Size, gui.StudsOffset, gui.MaxDistance = "Label", UDim2.fromOffset(148, 44), Vector3.new(0, 3, 0), 65
		gui.AlwaysOnTop = false
		local label = Instance.new("TextLabel")
		label.Size, label.BackgroundColor3, label.BackgroundTransparency = UDim2.fromScale(1, 1), Color3.fromRGB(28, 35, 42), 0.15
		label.Text, label.TextColor3, label.TextSize, label.TextWrapped = text, Color3.new(1, 1, 1), 12, true
		label.Font = Enum.Font.GothamBold label.Parent = gui gui.Parent = p
	end
	local rooms = {
		{"MAIN_HALL", "A  QUEEN'S HALL", 0, 0, 54, 54, "Orientation", colors.Public},
		{"PUBLIC", "B  PUBLIC EXHIBITION", -48.5, -76, 33, 34, "Public", colors.Public},
		{"GALLERY_C", "C3  COLLECTIONS", -78, -76, 22, 34, "Medium", colors.Medium},
		{"GALLERY_A", "C1  PAINTING GALLERY", -60.5, 76, 57, 34, "Medium", colors.Medium},
		{"GALLERY_B", "C2  SCULPTURE GALLERY", 60.5, 76, 57, 34, "Medium", colors.Medium},
		{"HIGH_SECURITY", "D  HIGH SECURITY", 50, -76, 36, 34, "High", colors.High},
		{"ARCHIVE", "E  RESTRICTED ARCHIVE", 79.5, -76, 19, 34, "Restricted", colors.Archive},
	}
	for _, r in rooms do
		local zone = part(folders.RoomZones, "VIC_ROOM_" .. r[1], {r[3], 16, r[4]}, {r[5], 18, r[6]}, r[8], false, 1)
		zone:SetAttribute("RoomId", zone.Name) zone:SetAttribute("DisplayName", r[2]) zone:SetAttribute("RiskTier", r[7])
		zone:SetAttribute("AlertOnEntry", r[7] == "High" or r[7] == "Restricted")
		if r[1] ~= "MAIN_HALL" then
			part(folders.Wayfinding, r[1] .. "_FloorTint", {r[3], 6.86, r[4]}, {r[5] - 0.4, 0.08, r[6] - 0.4}, r[8], false, 0.8)
		end
		floorText(folders.Wayfinding, r[1] .. "_Sign", r[2], r[3], if r[1] == "MAIN_HALL" then -18 else r[4] + 0.5, math.min(26, r[5] - 2), r[8])
	end
	-- Two ten-stud doorways per partition allow a local loop, without new facade cuts.
	for _, x in {-66, 69} do
		local wall = Instance.new("Model") wall.Name = if x < 0 then "PublicCollectionsPartition" else "ArchivePartition"
		for _, span in {{-93, -89}, {-79, -71}, {-61, -59}} do
			part(wall, "Wall", {x, 17, (span[1] + span[2]) / 2}, {1, 20.4, span[2] - span[1]}, colors.Wall, true)
		end
		for _, z in {-84, -66} do part(wall, "DoorLintel_10StudClear", {x, 24, z}, {1, 6.4, 10}, colors.Wall, true) end
		wall:SetAttribute("DoorClearWidth", 10) wall:SetAttribute("DoorClearHeight", 14)
		wall.Parent = folders.Structure
	end
	local rates = {
		Common = {300, 1, 2}, Standard = {600, 2, 3}, Valuable = {1100, 3, 4}, Rare = {1800, 4, 6}, Premium = {2800, 5, 8},
	}
	-- Fictional exhibit names: no claim about the real museum's collection.
	local loot = {
		{"PUBLIC", -39, -87, "Common", "Reproduction-era correspondence"},
		{"PUBLIC", -56, -87, "Standard", "Imagined river study"},
		{"PUBLIC", -39, -64, "Common", "Historic print folio"},
		{"PUBLIC", -56, -64, "Standard", "Decorative miniature"},
		{"GALLERY_C", -72, -76, "Valuable", "Fictional trade collection"},
		{"GALLERY_C", -84, -76, "Rare", "Ceremonial keepsake"},
		{"GALLERY_C", -78, -76, "Valuable", "Engraved presentation set"},
		{"GALLERY_A", -40, 65, "Standard", "Monsoon street study"},
		{"GALLERY_A", -58, 87, "Valuable", "Fictional city panorama"},
		{"GALLERY_A", -78, 87, "Standard", "Imagined garden painting"},
		{"GALLERY_A", -78, 64, "Valuable", "River-trade portfolio"},
		{"GALLERY_B", 41, 65, "Valuable", "Small abstract bronze"},
		{"GALLERY_B", 60, 87, "Rare", "Fictional ceremonial vessel"},
		{"GALLERY_B", 80, 65, "Valuable", "Decorative sculpture set"},
		{"HIGH_SECURITY", 60, -87, "Premium", "Fictional jewelled insignia"},
		{"HIGH_SECURITY", 51, -87, "Rare", "Protected presentation artefact"},
		{"ARCHIVE", 85, -76, "Premium", "Fictional rare archive folio"},
		{"ARCHIVE", 76, -76, "Rare", "Restricted ceremonial collection"},
	}
	for index, item in loot do
		local id = string.format("VIC_LOOT_%03d", index)
		local model = Instance.new("Model") model.Name = id
		local rate = rates[item[4]]
		for key, value in {LootId = id, GalleryId = "VIC_ROOM_" .. item[1], LootCategory = item[4], ExhibitName = item[5], ProvisionalValue = rate[1], CapacityCost = rate[2], CollectionSeconds = rate[3], SecurityRisk = if index >= 15 then "Restricted" else item[4], AvailabilityState = "Placeholder", AlertOnTheftStart = true} do model:SetAttribute(key, value) end
		part(model, "TemporaryPedestal", {item[2], 7.6, item[3]}, {4, 1.6, 4}, colors.Pedestal, true)
		local block = part(model, "LootPlaceholder", {item[2], 9.6, item[3]}, {2.8, 2.4, 2.8}, if index >= 15 then colors.High else colors.Medium, false)
		billboard(block, string.format("%02d  %s\n$%d | BAG %d | %ds", index, item[4], rate[1], rate[2], rate[3]))
		local top = Instance.new("SurfaceGui") top.Name, top.Face, top.CanvasSize, top.LightInfluence = "PlanNumber", Enum.NormalId.Top, Vector2.new(160, 160), 0
		local number = Instance.new("TextLabel") number.Size, number.BackgroundTransparency, number.TextScaled = UDim2.fromScale(1, 1), 1, true
		number.Text, number.TextColor3, number.Font = string.format("%02d", index), Color3.new(1, 1, 1), Enum.Font.GothamBold
		number.Parent = top top.Parent = block
		model.WorldPivot = site * CFrame.new(item[2], 6.8, item[3]) model.Parent = folders.LootMarkers
	end
	local security = {
		{"LASER_001", "StaticLaserGrid", "HIGH_SECURITY", 2, 42, -85, 5, 10, "Side branch; clear central retreat lane"},
		{"LASER_002", "StaticLaserGrid", "ARCHIVE", 3, 72, -84, 5, 10, "Archive north approach; alternate south door"},
		{"MOVING_001", "MovingLaser", "HIGH_SECURITY", 3, 49, -65, 8, 10, "Predictable sweep only within marked envelope"},
		{"ELECTRIC_001", "ElectricalFloor", "HIGH_SECURITY", 3, 55, -76, 8, 8, "Telegraphed short crossing; walk around either side"},
		{"TERMINAL_001", "SecurityTerminal", "HIGH_SECURITY", 2, 36, -62, 3, 3, "Future short disable for LASER_001 and MOVING_001"},
		{"TERMINAL_002", "SecurityTerminal", "ARCHIVE", 3, 73, -62, 3, 3, "Future short disable for LASER_002"},
		{"CASE_001", "ProtectedCase", "HIGH_SECURITY", 3, 60, -87, 6, 6, "Associated loot VIC_LOOT_015"},
		{"CASE_002", "ProtectedCase", "HIGH_SECURITY", 2, 51, -87, 6, 6, "Associated loot VIC_LOOT_016"},
		{"CASE_003", "ProtectedCase", "ARCHIVE", 3, 85, -76, 6, 6, "Associated loot VIC_LOOT_017"},
	}
	for _, s in security do
		local marker = Instance.new("Model") marker.Name = "VIC_SECURITY_" .. s[1]
		for key, value in {SecurityId = marker.Name, SecurityType = s[2], DifficultyTier = s[4], AssociatedGallery = "VIC_ROOM_" .. s[3], DesignNote = s[9], Functional = false} do marker:SetAttribute(key, value) end
		local pad = part(marker, "ReservedFootprint", {s[5], 6.98, s[6]}, {s[7], 0.12, s[8]}, colors.Security, false, 0.35)
		if s[2] == "StaticLaserGrid" then
			for _, dz in {-s[8] / 2, s[8] / 2} do part(marker, "FutureEmitter", {s[5], 10.3, s[6] + dz}, {0.7, 7, 0.7}, colors.Security, false) end
		elseif s[2] == "SecurityTerminal" then
			part(marker, "TerminalBlock", {s[5], 9, s[6]}, {3, 4.4, 2}, colors.Security, false)
		end
		billboard(pad, s[1] .. "\n" .. s[2] .. " [INACTIVE]")
		marker.Parent = folders.SecurityMarkers
	end
	for index, room in {{"HIGH_SECURITY", 50, 36}, {"ARCHIVE", 79.5, 19}} do
		local id = string.format("VIC_RESTRICTED_%03d", index)
		local volume = part(folders.RestrictedZoneMarkers, id, {room[2], 17, -76}, {room[3], 20.4, 34}, colors.High, false, 1)
		volume:SetAttribute("RestrictedId", id) volume:SetAttribute("GalleryId", "VIC_ROOM_" .. room[1])
		volume:SetAttribute("PoliceAlertOnUnauthorizedEntry", true) volume:SetAttribute("AlertScope", "Once per robbery event; shared with theft-start trigger")
		volume:SetAttribute("Functional", false)
	end
	-- The high-security wing already has two public approaches. Mark both clearly.
	floorText(folders.Wayfinding, "RestrictedEntry_Hall", "RESTRICTED >  ALERT ON ENTRY", 38, -75, 12, colors.High)
	floorText(folders.Wayfinding, "RestrictedEntry_Court", "RESTRICTED  /  ALERT ON ENTRY", 60, -60.5, 16, colors.High)
	local exits = {
		{"MAIN", 0, -102, "Main portal / approach stairs", 28, 10},
		{"REAR", 0, 102, "Opposite portal / approach stairs", 28, 10},
		{"SIDE_A", -130, 0, "Open quadrangle / existing side stairs", 10, 18},
		{"SIDE_B", 130, 0, "Open quadrangle / existing side stairs", 10, 18},
	}
	for _, e in exits do
		local marker = part(folders.EntryExitMarkers, "VIC_EXIT_" .. e[1], {e[2], 6.12, e[3]}, {e[5], 0.12, e[6]}, colors.Escape, false, 0.25)
		marker:SetAttribute("RouteId", marker.Name) marker:SetAttribute("RouteRole", "Bidirectional entry and escape; police interception")
		marker:SetAttribute("ExistingOpening", true) marker:SetAttribute("DesignNote", e[4])
		billboard(marker, "EXIT " .. e[1] .. "\n" .. e[4])
	end
	for _, x in {-60, 60} do
		for _, z in {-45, 0, 45} do floorText(folders.Wayfinding, "CourtyardRoute", "< SIDE EXIT / GALLERIES >", x, z, 18, colors.Escape) end
	end
	floorText(folders.Wayfinding, "MainHall_NoAlert", "PUBLIC HALL  /  NO ENTRY ALERT", 0, 18, 24, colors.Public)
	local recording = ChangeHistory:TryBeginRecording("Task007 Victoria heist greybox")
	root.Parent = victoria
	if recording then ChangeHistory:FinishRecording(recording, Enum.FinishRecordingOperation.Commit) end
	return root
end

return Builder
