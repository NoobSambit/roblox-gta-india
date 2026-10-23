--!strict
-- Focused edit-time finishing pass; never required by runtime code.
local Http=game:GetService("HttpService")
local WA=game:GetService("ServerStorage").WorldAuthoring
local K=workspace.World.Cities.Kolkata
local P={}
local function v(a) return Vector3.new(a[1],a[2],a[3]) end
local function model(parent,name)
	local m=Instance.new("Model");m.Name=name;m:SetAttribute("Task006Owned",true);m.ModelStreamingMode=Enum.ModelStreamingMode.Atomic;m.Parent=parent;return m
end
local function slab(parent,name,x,z,w,d,top,color)
	local p=Instance.new("Part");p.Name=name;p.Size=Vector3.new(w,.3,d);p.Position=Vector3.new(x,top-.15,z)
	p.Color=color or Color3.fromRGB(188,183,163);p.Material=Enum.Material.Concrete;p.Anchored=true;p.CanTouch=false;p.CastShadow=false;p.Parent=parent;return p
end
local function sourceProp(name,parent,x,z,yaw)
	local source=assert(WA.Task006Archive.LegacyPara01:FindFirstChild(name,true));local m=source:Clone()
	local c,s=m:GetBoundingBox();local pivot=m:GetPivot();local y=pivot.Y-c.Y+s.Y/2
	m:PivotTo(CFrame.new(x,y+.05,z)*CFrame.Angles(0,math.rad(yaw or 0),0));m.ModelStreamingMode=Enum.ModelStreamingMode.Atomic
	for _,p in m:GetDescendants()do if p:IsA("BasePart")then p.Anchored=true;p.CanTouch=false end end
	m.Parent=parent;return m
end
function P.apply()
	assert(not game:GetService("RunService"):IsRunning());assert(not K:GetAttribute("Task006Polished"))
	local spaces=K.Districts.Civic:FindFirstChild("PublicSpaces")
	local civic=model(spaces,"CivicForecourts")
	slab(civic,"WritersPublicSquare",-130,-225,210,29,.05)
	slab(civic,"TownHallForecourt",270,-213,108,23,.05)
	slab(civic,"GPOPublicSquare",-433,151,68,132,.05)
	slab(civic,"MetropolitanForecourt",240,230,148,23,.05)
	-- Mark parking-ready bays in the permanent plots, leaving central entry clear.
	local plan=Http:JSONDecode(Http:GetAsync("http://127.0.0.1:8766/authoring/task006/world-plan.json",true))
	for _,row in plan.commercialPlots do
		local b=nil;for _,p in K.Districts.Commercial.PlotInfrastructure:GetChildren()do if p:GetAttribute("PlotId")==row.id then b=p;break end end
		assert(b);local spec=nil;for _,s in Http:JSONDecode(Http:GetAsync("http://127.0.0.1:8766/authoring/task006/asset-catalog.json",true))do if s.assetId==row.assetId then spec=s;break end end
		local frame=CFrame.new(v(row.origin))*CFrame.Angles(0,math.rad(row.yaw),0)
		for _,x in {-20,20}do
			for _,dx in {-4.5,4.5}do
				local line=slab(b,"ParkingBayLine",0,0,.14,15,.01,Color3.fromRGB(224,222,201));line.CFrame=frame*CFrame.new(x+dx,.018,spec.boundsMinStuds[3]-13);line.Size=Vector3.new(.14,.02,15);line.CanCollide=false;line.CanQuery=false
			end
		end
	end
	local river=K.Districts.HooghlyRiverfront
	local paths=model(river.PlotInfrastructure,"RiverParkPromenade")
	for _,q in {{-768,-235},{-125,305.5},{454.5,690}}do
		for z=q[1],q[2]-1,128 do local finish=math.min(z+128,q[2]);slab(paths,"PromenadePath",-590,(z+finish)/2,12,finish-z,.05)end
	end
	for _,z in {-650,-460,-20,180,520,650}do slab(paths,"RiverStreetConnection",-569,z,82,10,.05)end
	for _,z in {-700,-580,-360,-40,150,620}do sourceProp("ShadeTree",river.Environment,-550,z,0)end
	for _,z in {-650,-460,-20,180,520}do sourceProp("AddaBench",river.Environment,-603,z+14,90)end
	local returnMaster=WA.AssetLibrary.Masters.KOL_HBR_RF_06
	for _,z in {296,466}do
		local m=returnMaster:Clone();m.Name="GhatEmbankmentClosure_"..z;m:SetAttribute("PlacementId","KOL_GHAT_EDGE_"..z)
		m:PivotTo(CFrame.new(-620,-13.5,z)*CFrame.Angles(0,math.pi/2,0));m.Parent=river.RiverbankModules
	end
	river.RiverbankModules.RiverLanding:PivotTo(CFrame.new(-690,-13.5,380)*CFrame.Angles(0,math.pi/2,0))
	for _,p in river.Environment:GetChildren()do if p.Name=="MooringPost" then p:PivotTo(CFrame.new(4,0,0)*p:GetPivot())end end
	-- Keep environment ownership local to its district as the world expands.
	for _,m in K.Districts.Civic.Environment:GetChildren()do
		if m:IsA("Model")then
			local p=m:GetPivot().Position;local district=nil
			if p.Z < -400 then district=if p.X<80 then K.Districts.NorthKolkata else K.Districts.ModernResidential
			elseif p.Z>30 then district=K.Districts.Commercial end
			if district then m.Parent=district.Environment end
		end
	end
	local sky=game:GetService("Lighting"):FindFirstChildWhichIsA("Sky")
	if sky then sky.MoonAngularSize=3 end
	game:GetService("Selection"):Set({})
	K:SetAttribute("Task006Polished",true)
	return {commercialParkingBays=10,civicForecourts=4,riverParkPaths=true,ghatLandingConnected=true}
end
return P
