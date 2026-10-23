--!strict
-- Edit-time only. Call with snapshotPhase="pre" or "final" through execute_luau.
local Http = game:GetService("HttpService")
local Serialization = game:GetService("SerializationService")
local phase = snapshotPhase
assert(phase == "pre" or phase == "pre-integration" or phase == "final", "Explicit snapshot phase required")
local function send(route: string, data: buffer)
	local total = buffer.len(data)
	for offset = 0, total - 1, 240000 do
		local length = math.min(240000, total - offset)
		local ok, result = pcall(function()
			return Http:RequestAsync({Url = "http://127.0.0.1:8769/" .. route, Method = "POST",
				Headers = {["Content-Type"] = "application/octet-stream", ["X-Chunk-Index"] = tostring(offset / 240000), ["X-Final"] = if offset + length == total then "1" else "0"},
				Body = buffer.readstring(data, offset, length)})
		end)
		assert(ok and result.Success, tostring(result))
		task.wait()
	end
	return total
end
local roots: {Instance} = {}
local bindings = {}
for _, service in {"Workspace", "Lighting", "SoundService", "ReplicatedStorage", "ReplicatedFirst", "ServerScriptService", "ServerStorage", "StarterGui", "StarterPack", "StarterPlayer", "Teams", "MaterialService", "LocalizationService", "TextChatService"} do
	for _, child in game:GetService(service):GetChildren() do
		if child.Archivable and not child:IsA("Camera") then
			table.insert(roots, child)
			table.insert(bindings, {index = #roots, service = service, name = child.Name, class = child.ClassName})
		end
	end
end
local ok, data = pcall(function() return Serialization:SerializeInstancesAsync(roots) end)
assert(ok, tostring(data))
local bytes = send(phase .. ".rbxm", data)
local decodedOk, reopened = pcall(function() return Serialization:DeserializeInstancesAsync(data) end)
assert(decodedOk, tostring(reopened))
local checks = {roots = #reopened, hasWorld = false, hasTerrain = false, hasVictoria = false, lootCount = 0,securityCount=0,routes=0,activeMasters=0,retiredContentAbsent=true}
for _, root in reopened do
	if root.Name == "World" then
		checks.hasWorld = true
		local victoria = root:FindFirstChild("VictoriaMemorial", true)
		checks.hasVictoria = victoria ~= nil
		local greybox = victoria and victoria:FindFirstChild("HeistGreybox")
		if greybox then checks.lootCount = #greybox.LootMarkers:GetChildren() checks.securityCount=#greybox.SecurityMarkers:GetChildren() checks.routes=#greybox.EntryExitMarkers:GetChildren() end
	end
	if phase=="final" and root.Name=="WorldAuthoring" then
		for _,name in {"Task009Archive","Task009Baseline","VictoriaImportRecovery"} do if root:FindFirstChild(name) then checks.retiredContentAbsent=false end end
		for _,o in root.Task009Assets:GetDescendants() do if o:IsA("Model") and o:GetAttribute("ImportComplete") then checks.activeMasters+=1 end end
	end
	if root:IsA("Terrain") then checks.hasTerrain = true end
	-- Deserialized Terrain is unparented; the engine does not allow Destroy on it.
	if not root:IsA("Terrain") then root:Destroy() end
end
assert(checks.hasWorld and checks.hasTerrain and checks.hasVictoria, "Incomplete engine snapshot")
local report = {phase = phase, placeId = game.PlaceId, format = "Engine model package with service bindings; not native rbxl", bytes = bytes, bindings = bindings, reopen = checks}
if phase == "final" then
	assert(checks.lootCount == 28, "Two-floor layout absent from recovery")
	assert(checks.securityCount==16 and checks.routes==4 and checks.activeMasters==46 and checks.retiredContentAbsent,"Recovery content mismatch")
	local landmark = workspace.World.Cities.Kolkata.Districts.Maidan.VictoriaMemorial
	local modelOk, modelData = pcall(function() return Serialization:SerializeInstancesAsync({landmark}) end)
	assert(modelOk, tostring(modelData))
	report.landmarkBytes = send("victoria.rbxm", modelData)
	local landmarkReopened=Serialization:DeserializeInstancesAsync(modelData)
	assert(#landmarkReopened==1 and #landmarkReopened[1].HeistGreybox.LootMarkers:GetChildren()==28,"Landmark recovery incomplete")
	report.landmarkReopened=true
	landmarkReopened[1]:Destroy()
end
send(if phase == "pre" then "pre-snapshot.json" elseif phase == "pre-integration" then "pre-integration-snapshot.json" else "snapshot.json", buffer.fromstring(Http:JSONEncode(report)))
return Http:JSONEncode({phase = phase, bytes = bytes, reopen = checks})
