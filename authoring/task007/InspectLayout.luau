--!strict
-- One focused edit-mode spatial inspection, not a gameplay or multiplayer test.
local Http = game:GetService("HttpService")
local v = workspace.World.Cities.Kolkata.Districts.Maidan.VictoriaMemorial
local site = v:GetPivot()
local root = v.HeistGreybox
local baseline = game:GetService("ServerStorage").WorldAuthoring.Task007Baseline
local report = {mode = "Edit-mode clearance/floor inspection plus viewport review", preserved = {}, routes = {}, issues = {}, rooms = #root.RoomZones:GetChildren(), loot = #root.LootMarkers:GetChildren(), security = {}}
for _, ref in baseline:GetChildren() do
	local records = {}
	for _, p in v[ref.Name]:GetDescendants() do
		if p:IsA("BasePart") then table.insert(records, {path = p:GetFullName(), cf = {p.CFrame:GetComponents()}, size = {p.Size.X, p.Size.Y, p.Size.Z}, color = {p.Color.R, p.Color.G, p.Color.B}, collide = p.CanCollide, transparency = p.Transparency, mesh = if p:IsA("MeshPart") then p.MeshId else ""}) end
	end
	table.sort(records, function(a, b) return a.path .. tostring(a.cf[1]) .. tostring(a.cf[3]) < b.path .. tostring(b.cf[1]) .. tostring(b.cf[3]) end)
	local unchanged = Http:JSONEncode(records) == ref.Value
	report.preserved[ref.Name] = {unchanged = unchanged, parts = #records}
	if not unchanged then table.insert(report.issues, "Original geometry changed: " .. ref.Name) end
end
local overlap = OverlapParams.new()
overlap.FilterType, overlap.FilterDescendantsInstances, overlap.RespectCanCollide = Enum.RaycastFilterType.Include, {v}, true
local ray = RaycastParams.new()
ray.FilterType, ray.FilterDescendantsInstances, ray.RespectCanCollide = Enum.RaycastFilterType.Include, {v}, true
local routes = {
	MainPortals = {{0,-105},{0,-75},{0,-40},{12,-15},{12,15},{0,40},{0,75},{0,105}},
	PublicCollectionsSideA = {{0,-75},{-42,-75},{-60,-84},{-74,-84},{-84,-84},{-84,-66},{-74,-66},{-60,-66},{-60,-50},{-60,0},{-130,0}},
	PaintingLoop = {{0,75},{-42,75},{-60,75},{-60,50},{-60,0}},
	SculptureSideB = {{0,75},{45,75},{60,75},{60,50},{60,0},{130,0}},
	RestrictedArchiveLoop = {{0,-75},{34,-75},{45,-75},{55,-75},{63,-75},{64,-84},{74,-84},{86,-84},{86,-66},{74,-66},{63,-66},{60,-50},{60,0}},
}
for name, points in routes do
	local checked, failures = 0, 0
	for i = 1, #points - 1 do
		local a, b = Vector3.new(points[i][1], 0, points[i][2]), Vector3.new(points[i+1][1], 0, points[i+1][2])
		local steps = math.ceil((b-a).Magnitude / 3)
		for j = 0, steps do
			local p = a:Lerp(b, j / steps)
			local floor = workspace:Raycast(site:PointToWorldSpace(p + Vector3.new(0, 13, 0)), Vector3.new(0,-12,0), ray)
			checked += 1
			if not floor then
				failures += 1 table.insert(report.issues, {route = name, x = p.X, z = p.Z, issue = "Missing floor"})
			else
				-- Existing wing floors rise 0.8 studs above the terrace: allow that step.
				local box = CFrame.new(floor.Position + Vector3.new(0, 3.3, 0)) * site.Rotation
				local blockers = workspace:GetPartBoundsInBox(box, Vector3.new(3, 4.5, 3), overlap)
				if #blockers > 0 then
					failures += 1 table.insert(report.issues, {route = name, x = p.X, z = p.Z, issue = blockers[1]:GetFullName()})
				end
			end
		end
	end
	report.routes[name] = {samples = checked, failures = failures}
end
for _, marker in root.SecurityMarkers:GetChildren() do
	local key = marker:GetAttribute("SecurityType")
	report.security[key] = (report.security[key] or 0) + 1
end
local response = Http:RequestAsync({Url = "http://127.0.0.1:8767/inspection.json", Method = "POST", Body = Http:JSONEncode(report)})
assert(response.Success, response.Body)
return Http:JSONEncode(report)
