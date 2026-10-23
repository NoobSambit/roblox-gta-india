--!strict
-- Invoked through Studio MCP in Client; never installed as a runtime script.
local Players=game:GetService("Players")
local Run=game:GetService("RunService")
local player=Players.LocalPlayer
local character=assert(player.Character)
local humanoid=character:FindFirstChildWhichIsA("Humanoid")
local root=character:FindFirstChild("HumanoidRootPart")
assert(humanoid and root)
local Q={}
local function stream(pos)
	player:RequestStreamAroundAsync(pos,5)
end
local function begin(pos,speed)
	stream(pos);character:PivotTo(CFrame.new(pos));root.AssemblyLinearVelocity=Vector3.zero;humanoid.WalkSpeed=speed;task.wait(.35)
end
local function walk(pos,timeout)
	humanoid:MoveTo(pos);local started=os.clock();local refreshed=started
	while os.clock()-started<timeout do
		local delta=root.Position-pos
		if Vector2.new(delta.X,delta.Z).Magnitude<2.8 then return {reached=true,seconds=os.clock()-started,position={root.Position.X,root.Position.Y,root.Position.Z}}end
		-- Humanoid MoveTo expires after eight seconds even on a clear route.
		if os.clock()-refreshed>4 then humanoid:MoveTo(pos);refreshed=os.clock()end
		task.wait(.1)
	end
	return {reached=false,seconds=os.clock()-started,position={root.Position.X,root.Position.Y,root.Position.Z},state=humanoid:GetState().Name}
end
function Q.commercial()
	local rows={};local old=humanoid.WalkSpeed
	for _,b in workspace.World.Cities.Kolkata.Districts.Commercial.Buildings:GetChildren()do
		if b:GetAttribute("SourceAssetId") and b:GetAttribute("SourceAssetId"):match("^KOL_T25")then
			local f=b:GetPivot();begin(f:PointToWorldSpace(Vector3.new(0,3.5,-41)),32)
			local r=walk(f:PointToWorldSpace(Vector3.new(0,3.5,35)),4);r.assetId=b:GetAttribute("SourceAssetId");table.insert(rows,r)
		end
	end
	humanoid.WalkSpeed=old;return rows
end
function Q.jorasanko()
	local old=humanoid.WalkSpeed;local pos=Vector3.new(-230,3.5,-580)
	begin(pos,24);local r=walk(Vector3.new(-230,3.5,-650),6);humanoid.WalkSpeed=old;return r
end
function Q.bridge()
	local old=humanoid.WalkSpeed;local rows={};begin(Vector3.new(-495,3.5,-180),96)
	for _,pos in {Vector3.new(-650,22,-180),Vector3.new(-1500,22,-180),Vector3.new(-1680,3.5,-180)}do
		table.insert(rows,walk(pos,12));if not rows[#rows].reached then break end
	end
	humanoid.WalkSpeed=old;return rows
end
function Q.riverfront()
	local old=humanoid.WalkSpeed;local bridge=Q.bridge();local rows={}
	local f=workspace.World.Cities.Kolkata.Districts.HooghlyRiverfront.Buildings.KolkataGrandGhat:GetPivot()
	begin(f:PointToWorldSpace(Vector3.new(0,17,75)),24);rows={}
	for _,pos in {Vector3.new(0,17,55),Vector3.new(0,18.2,32),Vector3.new(0,17,9),Vector3.new(0,4.5,-56)}do
		table.insert(rows,walk(f:PointToWorldSpace(pos),5));if not rows[#rows].reached then break end
	end
	humanoid.WalkSpeed=old;return {bridge=bridge,ghat=rows}
end
function Q.performance()
	local cam=workspace.CurrentCamera;local oldType=cam.CameraType;local oldCF=cam.CFrame;cam.CameraType=Enum.CameraType.Scriptable
	local rows={};local stats=game:GetService("Stats")
	for _,view in {
		{name="NorthKolkata",position=Vector3.new(-280,12,-530),look=Vector3.new(-130,26,-450)},
		{name="Civic",position=Vector3.new(10,12,-160),look=Vector3.new(-140,28,-280)},
		{name="VictoriaMemorial",position=Vector3.new(445,12,0),look=Vector3.new(820,40,0)},
		{name="HowrahBridge",position=Vector3.new(-660,35,-230),look=Vector3.new(-1060,60,-180)}
	}do
		stream(view.position);character:PivotTo(CFrame.new(view.position));cam.CFrame=CFrame.lookAt(view.position,view.look);task.wait(.6)
		local frames={};for _=1,120 do table.insert(frames,Run.RenderStepped:Wait()*1000)end;table.sort(frames)
		local ok,data=pcall(function()return game:GetService("SceneAnalysisService"):GetTriangleCompositionAsync()end)
		local quality="unknown";pcall(function()quality=tostring(settings().Rendering.QualityLevel)end)
		table.insert(rows,{scene=view.name,frames=#frames,medianFrameMs=frames[60],p95FrameMs=frames[114],medianFPS=1000/frames[60],memoryMB=stats:GetTotalMemoryUsageMb(),renderComposition=if ok then data else tostring(data),quality=quality})
	end
	cam.CameraType=oldType;cam.CFrame=oldCF;return {environment="Roblox Studio desktop host, one local client, no device emulation",sampleFramesPerView=120,views=rows}
end
