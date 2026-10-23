--!strict
-- Focused edit-time checks for this integration, not a gameplay test suite.
local Http=game:GetService("HttpService")
local K=workspace.World.Cities.Kolkata
local plan=Http:JSONDecode(Http:GetAsync("http://127.0.0.1:8766/authoring/task006/world-plan.json",true))
local result={scope="Task006 integration",structural={},entranceClearance={},surfaceChecks={},issues={}}
local rp=RaycastParams.new();rp.RespectCanCollide=true;rp.IgnoreWater=true
local function issue(s) table.insert(result.issues,s) end
local count,unanchored,decorCollision,touches=0,0,0,0
for _,p in K:GetDescendants()do
	if p:IsA("BasePart")then count+=1;if not p.Anchored then unanchored+=1 end end
	if p:IsA("MeshPart")and not p:IsDescendantOf(K.Districts.Maidan)then if p.CanCollide then decorCollision+=1 end;if p.CanTouch then touches+=1 end end
end
result.structural={baseParts=count,unanchored=unanchored,newDecorativeMeshCollisions=decorCollision,newDecorativeMeshTouch=touches,streamingEnabled=workspace.StreamingEnabled,oldPara01Absent=K.Districts:FindFirstChild("Para01")==nil}
if unanchored>0 or decorCollision>0 or touches>0 then issue("Unexpected static mesh physics")end
local used={};local residential=0;local tier2=0;local tier25=0
for _,row in plan.placements do
	local b=K.Districts[row.district].Buildings:FindFirstChild(row.id);assert(b,"Missing "..row.id)
	if row.kind=="residential"then used[row.assetId]=true;residential+=1 elseif row.kind=="landmark"then tier2+=1 elseif row.kind=="commercial"then
		tier25+=1;local frame=b:GetPivot();local hit=workspace:Blockcast(frame*CFrame.new(0,3.4,-41),Vector3.new(3,5,2),frame:VectorToWorldSpace(Vector3.new(0,0,77)),rp)
		table.insert(result.entranceClearance,{assetId=row.assetId,frontToRearClear=hit==nil,obstacle=if hit then hit.Instance:GetFullName()else nil})
		if hit then issue(row.assetId.." entrance obstructed")end
	end
end
local n=0;for _ in used do n+=1 end
result.structural.tier2=tier2;result.structural.tier25=tier25;result.structural.uniqueTier3=n;result.structural.residentialPlacements=residential
assert(tier2==5 and tier25==5 and n==27)
local jora=K.Districts.NorthKolkata.Buildings[plan.placements[5].id]
local jf=jora:GetPivot();local jh=workspace:Blockcast(jf*CFrame.new(0,3.3,-70),Vector3.new(3,5,2),jf:VectorToWorldSpace(Vector3.new(0,0,70)),rp)
result.structural.jorasankoEntranceClear=jh==nil;if jh then issue("Jorasanko entrance obstruction "..jh.Instance:GetFullName())end
local ghat=K.Districts.HooghlyRiverfront.Buildings.KolkataGrandGhat
for _,x in {-33,0,33}do
	local hit=workspace:Blockcast(ghat:GetPivot()*CFrame.new(x,16.5,75),Vector3.new(3,5,2),ghat:GetPivot():VectorToWorldSpace(Vector3.new(0,0,-22)),rp)
	table.insert(result.entranceClearance,{ghatArch=x,clear=hit==nil});if hit then issue("Ghat arch blocked "..x.." "..hit.Instance:GetFullName())end
end
local function surface(label,points,expected,rayOffset)
	local missed=0;local minY=math.huge;local maxY=-math.huge;local jumps=0;local previous=nil
	for _,point in points do
		local h=workspace:Raycast(point+Vector3.new(0,rayOffset or 35,0),Vector3.new(0,-85,0),rp)
		if not h then missed+=1 else minY=math.min(minY,h.Position.Y);maxY=math.max(maxY,h.Position.Y);if previous and math.abs(h.Position.Y-previous)>3 then jumps+=1 end;previous=h.Position.Y end
	end
	table.insert(result.surfaceChecks,{label=label,samples=#points,missing=missed,minY=minY,maxY=maxY,heightJumpsOver3=jumps})
	if missed>0 or (expected and (math.abs(minY-expected)>.75 or math.abs(maxY-expected)>.75))then issue(label.." floor mismatch")end
end
for _,r in plan.roads do
	local a,b=r.ends[1],r.ends[2];local length=math.abs(b[1]-a[1])+math.abs(b[2]-a[2]);local points={}
	for i=0,math.ceil(length/24)do local t=i/math.ceil(length/24);table.insert(points,Vector3.new(a[1]+(b[1]-a[1])*t,0,a[2]+(b[2]-a[2])*t))end
	surface(r.id,points,0)
end
local points={};for x=-1710,-502,12 do table.insert(points,Vector3.new(x,0,-180))end;surface("BridgeAndApproaches",points,nil)
points={};for z=-61,74,2 do
	local y=13.5
	if z< -50 then y=1 elseif z< -33.9 then y=1.6+(z+50)/16.1*3.6 elseif z< -29.9 then y=5.2
	elseif z< -13.8 then y=5.8+(z+29.9)/16.1*3.6 elseif z< -9.8 then y=9.4
	elseif z<6.3 then y=9.4+4.1/7+(z+9.8)/16.1*(4.1*6/7)
	elseif z>=17 and z<49 then y=14.7 end
	table.insert(points,ghat:GetPivot():PointToWorldSpace(Vector3.new(0,y,z)))
end;surface("GhatCentreline",points,nil,3)
local water=RaycastParams.new();water.FilterType=Enum.RaycastFilterType.Include;water.FilterDescendantsInstances={workspace.Terrain};water.IgnoreWater=false
local hit=workspace:Raycast(Vector3.new(-1000,5,0),Vector3.new(0,-50,0),water)
result.structural.nativeWater={material=if hit then hit.Material.Name else "missing",surfaceY=if hit then hit.Position.Y else nil,roadY=0}
if not hit or hit.Material~=Enum.Material.Water or hit.Position.Y>=-5 then issue("Water datum conflict")end
local res=Http:RequestAsync({Url="http://127.0.0.1:8766/report/validation.json",Method="POST",Headers={["Content-Type"]="application/json"},Body=Http:JSONEncode(result)})
assert(res.Success,res.Body)
return Http:JSONEncode(result)
