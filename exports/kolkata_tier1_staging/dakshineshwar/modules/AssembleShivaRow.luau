--!strict
-- Template must be imported at its authored origin, then stored outside Workspace.
local positions: { Vector3 } = {
	Vector3.new(-61, 3.4, 30),
	Vector3.new(-85, 3.4, 30),
	Vector3.new(-109, 3.4, 30),
	Vector3.new(-133, 3.4, 30),
	Vector3.new(-157, 3.4, 30),
	Vector3.new(-181, 3.4, 30),
	Vector3.new(61, 3.4, 30),
	Vector3.new(85, 3.4, 30),
	Vector3.new(109, 3.4, 30),
	Vector3.new(133, 3.4, 30),
	Vector3.new(157, 3.4, 30),
	Vector3.new(181, 3.4, 30),
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
