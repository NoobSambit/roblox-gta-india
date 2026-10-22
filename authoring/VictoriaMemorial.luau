--!strict
-- Edit-only assembly. Blender owns meshes; Studio owns the integrated world.
-- No runtime script calls this module. Import VictoriaMemorial_Roblox.fbx first.
local ServerStorage = game:GetService("ServerStorage")
local ChangeHistoryService = game:GetService("ChangeHistoryService")
local CollectionService = game:GetService("CollectionService")

type Triple = {number}
type Placement = {template: string, name: string, position: Triple, yaw: number, group: string}
type Primitive = {name: string, position: Triple, size: Triple, material: string, solid: boolean, group: string, yaw: number, shape: string, invisible: boolean?}
type Marker = {name: string, position: Triple, size: Triple, role: string, id: string}
type MeshInfo = {template: string, material: string, vertices: number, triangles: number}
export type Manifest = {assetId: string, palette: {[string]: Triple}, instances: {Placement}, primitives: {Primitive}, markers: {Marker}, library: {[string]: MeshInfo}}

local Builder = {}
local ASSET_ID = "landmark.kolkata.victoria-memorial"

local function vector(v: Triple): Vector3
	return Vector3.new(v[1], v[2], v[3])
end

local function pose(position: Triple, yaw: number): CFrame
	return CFrame.new(vector(position)) * CFrame.Angles(0, yaw, 0)
end

local function folder(parent: Instance, name: string): Folder
	local existing = parent:FindFirstChild(name)
	if existing then
		assert(existing:IsA("Folder"), `Expected folder {existing:GetFullName()}`)
		return existing
	end
	local result = Instance.new("Folder")
	result.Name, result.Parent = name, parent
	return result
end

local function model(parent: Instance, name: string, atomic: boolean): Model
	local result = Instance.new("Model")
	result.Name = name
	result.ModelStreamingMode = if atomic then Enum.ModelStreamingMode.Atomic else Enum.ModelStreamingMode.Default
	result.Parent = parent
	return result
end

local function normalized(name: string): string
	return (name:gsub("_Export$", ""):gsub("%.", "_"))
end

local function sourceIndex(source: Model): {[string]: MeshPart}
	local index: {[string]: MeshPart} = {}
	for _, item in source:GetDescendants() do
		if item:IsA("MeshPart") then
			local key = normalized(item.Name)
			assert(index[key] == nil, `Duplicate imported component: {key}`)
			index[key] = item
		end
	end
	return index
end

local function importedSceneFrame(index: {[string]: MeshPart}): CFrame
	-- The four centred ground tiles identify scene translation and orientation,
	-- even when Studio inserts at the camera instead of the FBX scene origin.
	local a = assert(index.CampusGround, "Full assembled FBX required; component library has no grounds")
	local b = assert(index.CampusGround_001, "Missing second ground tile")
	local c = assert(index.CampusGround_002, "Missing third ground tile")
	local x, z = (c.Position - a.Position) / 300, (b.Position - a.Position) / 310
	assert(math.abs(x.Magnitude - 1) < 0.003 and math.abs(z.Magnitude - 1) < 0.003,
		`Import scale is incorrect ({x.Magnitude}, {z.Magnitude}); expected Stud / 1`)
	x, z = x.Unit, z.Unit
	assert(math.abs(x:Dot(z)) < 0.003, "Import axes are not perpendicular")
	local y = z:Cross(x).Unit
	assert(y:Dot(Vector3.yAxis) > 0.99, "Imported landmark is not upright")
	return CFrame.fromMatrix(a.Position + x * 150 + y * 1.08 + z * 155, x, y, z)
end

local function configure(part: BasePart, solid: boolean, query: boolean, shadow: boolean)
	part.Anchored, part.CanCollide, part.CanTouch, part.CanQuery = true, solid, false, query
	part.CastShadow = shadow
	part.TopSurface, part.BottomSurface = Enum.SurfaceType.Smooth, Enum.SurfaceType.Smooth
end

local function material(role: string): Enum.Material
	if role == "Asphalt" then return Enum.Material.Asphalt end
	if role == "Path" then return Enum.Material.Concrete end
	return Enum.Material.SmoothPlastic
end

local function color(palette: {[string]: Triple}, role: string): Color3
	local rgb = assert(palette[role], `Unknown material role: {role}`)
	return Color3.new(rgb[1], rgb[2], rgb[3])
end

function Builder.integrate(source: Model, manifest: Manifest, site: CFrame): Model
	assert(manifest.assetId == ASSET_ID, "Wrong landmark manifest")
	local world = assert(workspace:FindFirstChild("World"), "Open the existing Kolkata place")
	local cities = assert(world:FindFirstChild("Cities"), "Missing Cities")
	local city = assert(cities:FindFirstChild("Kolkata"), "Missing Kolkata")
	local districts = assert(city:FindFirstChild("Districts"), "Missing Districts")
	local maidan = districts:FindFirstChild("Maidan")
	assert(not maidan or not maidan:FindFirstChild("VictoriaMemorial"), "Landmark exists; inspect before replacing")
	local index = sourceIndex(source)
	local importedFrame = importedSceneFrame(index)
	local templates: {[string]: {part: MeshPart, offset: CFrame}} = {}
	-- Recover each template's exact imported local axes and mesh-centre offset.
	-- Cloning these references guarantees repeated components share mesh IDs.
	for _, entry in manifest.instances do
		for key, info in manifest.library do
			if info.template ~= entry.template or templates[key] then continue end
			local rawName = normalized(entry.name .. "__" .. info.material)
			-- Blender suffixes instances that share their library template's name.
			local imported = assert(index[rawName] or index[rawName .. "_001"], `Missing imported mesh: {rawName}`)
			assert(imported.MeshId ~= "", `Mesh upload incomplete: {rawName}`)
			templates[key] = {part = imported, offset = pose(entry.position, entry.yaw):Inverse() * importedFrame:ToObjectSpace(imported.CFrame)}
		end
	end
	for key in manifest.library do assert(templates[key], `No imported instance of {key}`) end
	local root = Instance.new("Model")
	root.Name = "VictoriaMemorial"
	root.ModelStreamingMode = Enum.ModelStreamingMode.Default
	root.WorldPivot = site
	root:SetAttribute("AssetId", ASSET_ID)
	root:SetAttribute("CityId", "kolkata")
	root:SetAttribute("AuthoringVersion", 2)
	root:SetAttribute("Source", "assets/victoria-memorial/VictoriaMemorial.blend")
	root:SetAttribute("GameplayStatus", "Interior shell and authored zones; no robbery mechanics")
	local groups: {[string]: Folder} = {
		Exterior = folder(root, "Exterior"), Interior = folder(root, "Interior"),
		Grounds = folder(root, "Grounds"), Structure = folder(root, "Structure"),
		Collision = folder(root, "Collision"), Metadata = folder(root, "GameplayZones"),
	}
	local cells: {[string]: Model} = {}
	local function cell(group: string, position: Triple): Model
		local key = `{group}_{math.floor(position[1] / 64)}_{math.floor(position[3] / 64)}`
		local existing = cells[key]
		if existing then return existing end
		local created = model(groups[group] or groups.Structure, key, false)
		cells[key] = created
		return created
	end
	local ok, issue = xpcall(function()
		for _, entry in manifest.instances do
			local assembly = model(groups[entry.group] or groups.Exterior, entry.name, true)
			assembly:SetAttribute("TemplateId", entry.template)
			for key, info in manifest.library do
				if info.template ~= entry.template then continue end
				local template = templates[key]
				local mesh = template.part:Clone()
				mesh.Name = info.material
				mesh.CFrame = site * pose(entry.position, entry.yaw) * template.offset
				mesh.Color, mesh.Material = color(manifest.palette, info.material), material(info.material)
				mesh.TextureID = ""
				for _, child in mesh:GetChildren() do child:Destroy() end
				mesh.RenderFidelity = Enum.RenderFidelity.Automatic
				mesh.CollisionFidelity = Enum.CollisionFidelity.Box
				local query = info.material == "Marble" or info.material == "StoneShadow" or info.material == "Bark"
				local shadow = info.material ~= "Glazing" and info.material ~= "FloorDark" and info.material ~= "Gilt"
				configure(mesh, false, query, shadow)
				mesh:SetAttribute("MeshKey", key)
				mesh.Parent = assembly
			end
		end
		for _, entry in manifest.primitives do
			local part = Instance.new("Part")
			part.Name, part.Size = entry.name, vector(entry.size)
			part.CFrame = site * pose(entry.position, entry.yaw)
			if entry.shape == "Cylinder" then
				part.Shape = Enum.PartType.Cylinder
				part.Size = Vector3.new(entry.size[2], entry.size[1], entry.size[3])
				part.CFrame *= CFrame.Angles(0, 0, math.pi / 2)
			end
			part.Color, part.Material = color(manifest.palette, entry.material), material(entry.material)
			part.Transparency = if entry.invisible then 1 else 0
			configure(part, entry.solid, entry.solid, not entry.invisible and entry.size[2] > 2)
			part.Parent = cell(entry.group, entry.position)
		end
		for _, entry in manifest.markers do
			local zone = Instance.new("Part")
			zone.Name, zone.Size, zone.CFrame = entry.name, vector(entry.size), site * CFrame.new(vector(entry.position))
			zone.Transparency = 1
			configure(zone, false, false, false)
			zone:SetAttribute("ZoneId", entry.id)
			zone:SetAttribute("Role", entry.role)
			CollectionService:AddTag(zone, "LandmarkZone")
			zone.Parent = groups.Metadata
		end
	end, debug.traceback)
	if not ok then root:Destroy(); error(issue) end
	local recording = ChangeHistoryService:TryBeginRecording("Integrate Victoria Memorial")
	local district = maidan or folder(districts, "Maidan")
	district:SetAttribute("DistrictId", "kolkata.maidan")
	root.Parent = district
	local authoring = folder(ServerStorage, "WorldAuthoring")
	local imports = folder(authoring, "VictoriaImportRecovery")
	source.Parent = imports
	CollectionService:AddTag(root, "Landmark")
	if recording then ChangeHistoryService:FinishRecording(recording, Enum.FinishRecordingOperation.Commit) end
	return root
end

function Builder.connectPara01(landmark: Model): Model
	-- Authored against Task 001's east endpoint x=320 and the compressed campus
	-- west perimeter road at x=533. Keep the approved landmark site unchanged.
	local site = landmark:GetPivot()
	assert((site.Position - Vector3.new(820, 0, 0)).Magnitude < 0.01, "Connector requires the planned east Maidan site")
	assert(site.LookVector:Dot(Vector3.new(-1, 0, 0)) > 0.99, "Campus front must face west")
	assert(not landmark:FindFirstChild("Para01Connection"), "Connector already exists")
	local connection = model(landmark, "Para01Connection", false)
	local function slab(name: string, position: Vector3, size: Vector3, tint: Color3, surface: Enum.Material)
		local p = Instance.new("Part")
		p.Name, p.Size, p.Position = name, size, position
		p.Color, p.Material = tint, surface
		configure(p, true, true, size.Y > 1)
		p.Parent = connection
	end
	slab("GroundConnection", Vector3.new(480, -1.08, 0), Vector3.new(60, 2, 140), Color3.fromRGB(67, 110, 62), Enum.Material.SmoothPlastic)
	slab("MaidanApproachRoad", Vector3.new(416.5, -0.12, 0), Vector3.new(193, 0.24, 40), Color3.fromRGB(63, 72, 79), Enum.Material.Asphalt)
	for _, side in {-1, 1} do
		slab("ApproachPavement", Vector3.new(416.5, 0.2, side * 26), Vector3.new(193, 0.4, 12), Color3.fromRGB(174, 168, 149), Enum.Material.Concrete)
	end
	return connection
end

return Builder
