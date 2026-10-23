--!strict
-- EDIT-ONLY: validate native FBX imports, retain raw imports and build shared-ID masters.
local Http = game:GetService("HttpService")
local Storage = game:GetService("ServerStorage")
local Importer = {}
local function vector(v): Vector3 return Vector3.new(v[1], v[2], v[3]) end
local function folder(parent: Instance, name: string): Folder
	local found = parent:FindFirstChild(name)
	if found then return found :: Folder end
	local value = Instance.new("Folder") value.Name, value.Parent = name, parent return value
end
local materials = {Ivory = "Limestone", Stone = "Limestone", Charcoal = "Metal", Brass = "Metal", Bronze = "Metal",
	Teal = "Metal", Amber = "Metal", Oxblood = "Fabric", Paper = "Fabric", Glass = "Glass", Gem = "Glass",
	Sky = "Metal", River = "Metal", Leaf = "Metal", Ink = "Fabric"}

function Importer.run(onlyAssets)
	assert(not game:GetService("RunService"):IsRunning(), "Edit-only import")
	local data = Http:JSONDecode(Http:GetAsync("http://127.0.0.1:8769/two-storey-meshes.json"))
	local masters = folder(Storage.WorldAuthoring, "Task009Assets")
	local rawImports = folder(masters, "RawImports")
	local report = {assets = {}, meshCount = 0, uniqueTriangles = 0, maximumScaleError = 0,
		method = "Native individual FBX import; original imported models retained; no ephemeral meshes"}
	for _, asset in data.assets do
		if onlyAssets and not table.find(onlyAssets,asset.assetId) then continue end
		local category = folder(masters, asset.category)
		local old = category:FindFirstChild(asset.assetId)
		if old then
			assert(not old:GetAttribute("ImportComplete") and #old:GetChildren() == 0, "Master already populated; inspect before adopting again")
			old:Destroy()
		end
		local sourceName = asset.assetId .. "_Roblox"
		local source = workspace:FindFirstChild(sourceName)
		assert(source and source:IsA("Model"), `Missing native import {sourceName}`)
		local index = {}
		for _, object in source:GetDescendants() do if object:IsA("MeshPart") then
			assert(not index[object.Name], `Duplicate source mesh {object.Name}`) index[object.Name] = object
		end end
		local model = Instance.new("Model") model.Name = asset.assetId model.WorldPivot = CFrame.identity
		model:SetAttribute("AssetId", asset.assetId) model:SetAttribute("SourceFbx", asset.sourceFbx)
		model:SetAttribute("SourceSha256", asset.fbxSha256) model:SetAttribute("Triangles", asset.triangles)
		local row = {assetId = asset.assetId, sourceFbx = asset.sourceFbx, pieces = {}}
		for _, piece in asset.pieces do
			local imported = assert(index[piece.name], `Missing imported component {piece.name}`)
			assert(imported.MeshId ~= "", `Mesh upload incomplete {piece.name}`)
			local error = (imported.Size - vector(piece.size)).Magnitude
			assert(error < 0.003, `FBX scale mismatch {piece.name}: {imported.Size}`)
			assert(imported.CFrame.RightVector:Dot(Vector3.xAxis) > 0.999 and imported.CFrame.UpVector:Dot(Vector3.yAxis) > 0.999, `FBX axes mismatch {piece.name}`)
			report.maximumScaleError = math.max(report.maximumScaleError, error)
			local part = imported:Clone()
			for _, child in part:GetChildren() do child:Destroy() end
			part.Name, part.Anchored, part.CanCollide, part.CanTouch, part.CanQuery = piece.name, true, false, false, false
			-- The native FBX importer bakes a half-turn into mesh-local X/Z.
			-- Recover the author's -Z front while retaining the exact mesh centre.
			part.Size, part.CFrame = vector(piece.size), CFrame.new(vector(piece.center)) * CFrame.Angles(0, math.pi, 0)
			part.TextureID = ""
			part.Color = Color3.fromHex(data.palette[piece.material])
			part.Material = if asset.assetId == "VIC_A12_FLOOR_RUNNER_8" and piece.material == "Teal" then Enum.Material.Fabric else Enum.Material[materials[piece.material] or "Limestone"]
			part.Reflectance = if piece.material == "Brass" or piece.material == "Bronze" then 0.035 else 0
			part.Transparency = if piece.material == "Glass" then 0.84 else 0
			part.CastShadow = piece.material ~= "Glass"
			part.CollisionFidelity = Enum.CollisionFidelity.Box
			part:SetAttribute("AssetId", asset.assetId) part:SetAttribute("PaletteRole", piece.material)
			part:SetAttribute("Component", piece.component) part:SetAttribute("Triangles", piece.triangles)
			local pivot = asset.componentPivots[piece.component]
			if pivot then part.PivotOffset = part.CFrame:ToObjectSpace(CFrame.new(vector(pivot))) end
			part:SetAttribute("CanonicalMeshRotationY", 180)
			part.Parent = model
			table.insert(row.pieces, {name = piece.name, meshId = part.MeshId, triangles = piece.triangles, scaleError = error})
			report.meshCount += 1
		end
		model:SetAttribute("ImportComplete", true) model.Parent = category
		source.Parent = rawImports
		table.insert(report.assets, row) report.uniqueTriangles += asset.triangles
		task.wait()
	end
	local route=if onlyAssets then "correction-mesh-ids.json" else "mesh-ids.json"
	local ok, result = pcall(function() return Http:PostAsync("http://127.0.0.1:8769/"..route, Http:JSONEncode(report), Enum.HttpContentType.ApplicationJson) end)
	assert(ok, tostring(result))
	return Http:JSONEncode({assets = #report.assets, meshes = report.meshCount, uniqueUsedTriangles = report.uniqueTriangles, maximumScaleError = report.maximumScaleError})
end
return Importer
