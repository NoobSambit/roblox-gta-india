--!strict
-- One-shot EDIT-TIME authoring; kept in ServerStorage, never run at runtime.
local Http=game:GetService("HttpService")
local Storage=game:GetService("ServerStorage")
local Run=game:GetService("RunService")
local History=game:GetService("ChangeHistoryService")
local B={}
local URL="http://127.0.0.1:8766/"
local K=workspace.World.Cities.Kolkata
local WA=Storage.WorldAuthoring
local Masters=WA.AssetLibrary.Masters
local plan=Http:JSONDecode(Http:GetAsync(URL.."authoring/task006/world-plan.json",true))
local specs={}
for _,s in Http:JSONDecode(Http:GetAsync(URL.."authoring/task006/asset-catalog.json",true)) do specs[s.assetId]=s end
local function v(a) return Vector3.new(a[1],a[2],a[3]) end
local function folder(p,name)
	local f=p:FindFirstChild(name);if f then return f end
	f=Instance.new("Folder");f.Name=name;f.Parent=p;return f
end
local function edit() assert(Run:IsStudio() and not Run:IsRunning(),"Edit-only authoring") end
local function cf(a,yaw) return CFrame.new(v(a))*CFrame.Angles(0,math.rad(yaw or 0),0) end
local function part(p,name,size,frame,color,material,transparent)
	local a=Instance.new("Part");a.Name=name;a.Size=size;a.CFrame=frame
	a.Anchored=true;a.CanTouch=false;a.CanQuery=true;a.CanCollide=true
	a.TopSurface=Enum.SurfaceType.Smooth;a.BottomSurface=Enum.SurfaceType.Smooth
	a.Material=material or Enum.Material.Concrete;a.Color=color or Color3.fromRGB(185,183,166)
	a.CastShadow=false
	if transparent then a.Transparency=1;a:SetAttribute("CollisionProxy",true) end
	a.Parent=p;return a
end
local function model(p,name,id)
	local m=Instance.new("Model");m.Name=name;m.WorldPivot=CFrame.identity
	m.ModelStreamingMode=Enum.ModelStreamingMode.Atomic;m:SetAttribute("Task006Owned",true)
	if id then m:SetAttribute("StableId",id) end;m.Parent=p;return m
end
local function master(id)
	for _,m in Masters:GetChildren() do if m:GetAttribute("AssetId")==id then return m end end
	error("Missing master "..id)
end
local function cloneAsset(id,p,frame,name,stable)
	local m=master(id):Clone();m.Name=name or id;m:SetAttribute("PlacementId",stable or name)
	m:PivotTo(frame);m.Parent=p;return m
end
local function post(name,data)
	local r=Http:RequestAsync({Url=URL.."report/"..name..".json",Method="POST",Headers={["Content-Type"]="application/json"},Body=Http:JSONEncode(data)})
	assert(r.Success,r.Body)
end
local function fingerprint(m)
	local rows={};for _,p in m:GetDescendants() do if p:IsA("BasePart") then table.insert(rows,p:GetFullName()..":"..tostring(p.CFrame)..":"..tostring(p.Size)) end end
	table.sort(rows);return table.concat(rows,"\n")
end
local victoriaBefore=fingerprint(K.Districts.Maidan.VictoriaMemorial)

function B.archive()
	edit();assert(not K:GetAttribute("Task006LegacyArchived"),"Already archived")
	local record=History:TryBeginRecording("Task006Archive","Archive prototype; preserve Victoria")
	local old=K.Districts.Para01
	local archive=folder(WA.Task006Archive,"LegacyPara01")
	local roadFolder=folder(K,"RoadNetwork")
	local retained=model(roadFolder,"RetainedMainBoulevard","KOL_RD_MAIN_RETAINED")
	old.Streets.MainRoad.Parent=retained
	-- Existing line paint cannot cross the new central street.
	for _,p in retained.MainRoad:GetChildren() do
		if p:IsA("BasePart") and p.Name~="Carriageway" and math.abs(p.Position.X-80)<24 then p.Parent=archive end
	end
	local ground=folder(K,"Ground")
	for _,m in old.Ground:GetChildren() do if m.Name:match("^Ground_") then m.Parent=ground else m.Parent=archive end end
	local civic=folder(K.Districts,"Civic");civic:SetAttribute("DistrictId","kolkata.civic")
	local court=old.Courtyard;court.Name="RetainedAddaCourtyard";court.Parent=folder(civic,"PublicSpaces")
	for _,m in court:GetChildren() do
		if m:IsA("Model") then m:PivotTo(CFrame.new(70,0,0)*m:GetPivot())
		elseif m:IsA("BasePart") then m.CFrame+=Vector3.new(70,0,0) end
	end
	-- Move bounded subtrees individually so Studio never inserts a huge subtree.
	for _,f in old:GetChildren() do
		local target=folder(archive,f.Name)
		for _,m in f:GetChildren() do m.Parent=target;task.wait() end
		f:Destroy()
	end
	old.Parent=archive
	local retired=folder(WA.Task006Archive,"LegacyGenerators")
	for _,name in {"KolkataFoundation","KolkataArchitecture","KolkataCommercial","KolkataStreetscape"} do
		local m=WA:FindFirstChild(name)
		if m then
			m:SetAttribute("Retired",true);m.Source='error("Retired Task001 authoring module: use Task006 authored world")\n'..m.Source;m.Parent=retired
		end
	end
	for _,name in {"Civic","NorthKolkata","ModernResidential","Commercial","InformalResidential","HooghlyRiverfront"} do
		local d=folder(K.Districts,name);d:SetAttribute("DistrictId","kolkata."..name)
		for _,n in {"Buildings","PlotInfrastructure","Environment"} do folder(d,n) end
	end
	K:SetAttribute("Task006LegacyArchived",true);K:SetAttribute("AuthoringVersion",6)
	if record then History:FinishRecording(record,Enum.FinishRecordingOperation.Commit) end
	assert(fingerprint(K.Districts.Maidan.VictoriaMemorial)==victoriaBefore,"Victoria changed")
	return {archivedBuildings=#archive.Buildings:GetChildren(),retainedGroundTiles=#ground:GetChildren(),victoriaUnchanged=true}
end

function B.roads()
	edit();assert(K:GetAttribute("Task006LegacyArchived"));local parent=K.RoadNetwork
	assert(not parent:FindFirstChild("NewSurfaces"),"Roads already authored")
	local surfaces=folder(parent,"NewSurfaces");local count=0
	for _,row in plan.roadSurfaces do
		local r=row.rect;local nx=math.ceil((r[3]-r[1])/128);local nz=math.ceil((r[4]-r[2])/128)
		for i=0,nx-1 do for j=0,nz-1 do
			local dx=(r[3]-r[1])/nx;local dz=(r[4]-r[2])/nz
			local x=r[1]+(i+.5)*dx;local z=r[2]+(j+.5)*dz
			local m=model(surfaces,row.kind.."_"..count,"KOL_SURFACE_"..count)
			local pavement=row.kind=="Pavement"
			part(m,row.kind,Vector3.new(dx,if pavement then .54 else .4,dz),CFrame.new(x,if pavement then .27 else -.2,z),if pavement then Color3.fromRGB(192,187,168) else Color3.fromRGB(63,72,79),if pavement then Enum.Material.Concrete else Enum.Material.Asphalt)
			count+=1
		end end
		task.wait()
	end
	local definitions=folder(parent,"Connections")
	for _,r in plan.roads do
		local d=Instance.new("Configuration");d.Name=r.id;d:SetAttribute("RoadId",r.id);d:SetAttribute("Width",r.width)
		d:SetAttribute("Start",Vector3.new(r.ends[1][1],0,r.ends[1][2]));d:SetAttribute("Finish",Vector3.new(r.ends[2][1],0,r.ends[2][2]));d.Parent=definitions
		local paint=model(parent,r.id.."_Paint");local a,b=r.ends[1],r.ends[2]
		local length=math.abs(b[1]-a[1])+math.abs(b[2]-a[2]);local dx=(b[1]-a[1])/length;local dz=(b[2]-a[2])/length
		for s=16,length-12,28 do
			local x=a[1]+dx*s;local z=a[2]+dz*s;local skip=(r.id=="KOL_RD_MAIN" and x>=-320 and x<=320)
			for _,other in plan.roads do if other~=r then local q=other.rect;if x>q[1]-14 and x<q[3]+14 and z>q[2]-14 and z<q[4]+14 then skip=true;break end end end
			if not skip and r.width>=24 then
				local p=part(paint,"CentreDash",Vector3.new(if dx~=0 then 10 else .24,.025,if dz~=0 then 10 else .24),CFrame.new(x,.025,z),Color3.fromRGB(242,225,184),Enum.Material.SmoothPlastic);p.CanCollide=false;p.CanQuery=false
			end
		end
	end
	-- Road paint only at the civic and commercial pedestrian crossings.
	for _,pos in {{-280,0},{240,0},{-130,-180},{270,-180},{-150,400},{10,400}} do
		local m=model(parent,"PedestrianCrossing")
		for z=-15,15,5 do local p=part(m,"Stripe",Vector3.new(8,.025,2.3),CFrame.new(pos[1],.03,pos[2]+z),Color3.fromRGB(228,225,204),Enum.Material.SmoothPlastic);p.CanCollide=false;p.CanQuery=false end
	end
	local expansion=K.ExpansionConnections
	for _,r in plan.expansionConnections do
		local p=part(expansion,r.id,Vector3.new(1,1,1),CFrame.new(v(r.position)),nil,nil,true);p.CanCollide=false;p.CanQuery=false
		p:SetAttribute("ConnectorId",r.id);p:SetAttribute("Direction",v(r.direction));p:SetAttribute("PreparedForExpansion",true)
	end
	return {surfaceChunks=count,roads=#plan.roads}
end

function B.ground()
	edit();local parent=folder(K.Ground,"Task006Extensions");assert(#parent:GetChildren()==0)
	local function rect(x0,z0,x1,z1,top,bottom,name)
		local nx=math.ceil((x1-x0)/180);local nz=math.ceil((z1-z0)/180)
		for i=0,nx-1 do for j=0,nz-1 do
			local dx=(x1-x0)/nx;local dz=(z1-z0)/nz
			part(parent,name,Vector3.new(dx,top-bottom,dz),CFrame.new(x0+(i+.5)*dx,(top+bottom)/2,z0+(j+.5)*dz),Color3.fromRGB(126,143,101),Enum.Material.Grass)
		end end;task.wait()
	end
	-- Reuse original 900x900 surface; extend north, south and river bank.
	rect(-450,-800,450,-450,-.5,-36,"NorthLand")
	rect(-450,450,450,700,-.5,-36,"SouthLand")
	rect(-620,-800,-450,305.5,-.5,-36,"RiverBankNorth")
	rect(-620,454.5,-450,700,-.5,-36,"RiverBankSouth")
	-- Ghat foundations own the notch and its descending steps.
	rect(-572,305.5,-450,454.5,-.5,-36,"GhatStreetBank")
	rect(-450,-450,450,450,-5.51,-36,"UnderExistingGround")
	rect(-1720,-275,-1524,-85,-.5,-36,"FarBridgeLanding")
	return {parts=#parent:GetChildren(),ghatNotchPreserved=true}
end

local function approachPath(parent,origin,yaw,spec,width)
	local frame=cf(origin,yaw);local start=frame:PointToWorldSpace(Vector3.new(0,0,spec.boundsMinStuds[3]))
	local dir=frame.LookVector;local nearest=nil;local best=math.huge
	for _,r in plan.roads do
		local q=r.rect
		if math.abs(dir.X)>.5 and start.Z>=q[2] and start.Z<=q[4] then
			local edge=if dir.X<0 then q[3] else q[1];local dist=(edge-start.X)/dir.X
			if dist>=0 and dist<best then best=dist;nearest=Vector3.new(edge,0,start.Z) end
		elseif math.abs(dir.Z)>.5 and start.X>=q[1] and start.X<=q[3] then
			local edge=if dir.Z<0 then q[4] else q[2];local dist=(edge-start.Z)/dir.Z
			if dist>=0 and dist<best then best=dist;nearest=Vector3.new(start.X,0,edge) end
		end
	end
	if nearest and best>.1 and best<160 then
		local centre=(start+nearest)/2;centre=Vector3.new(centre.X,.13,centre.Z)
		part(parent,"EntranceConnection",Vector3.new(if math.abs(dir.X)>.5 then best else width,.3,if math.abs(dir.Z)>.5 then best else width),CFrame.new(centre),Color3.fromRGB(189,184,164))
	end
end

function B.place(first,last)
	edit();local output={}
	for index=first,last do
		local row=plan.placements[index];local spec=specs[row.assetId];local district=K.Districts[row.district]
		assert(not district.Buildings:FindFirstChild(row.id),"Placement already exists "..row.id)
		local building=cloneAsset(row.assetId,district.Buildings,cf(row.position,row.yaw),row.id,row.id)
		building:SetAttribute("DistrictId",district:GetAttribute("DistrictId"));building:SetAttribute("SourceAssetId",row.assetId)
		local plot=model(district.PlotInfrastructure,row.id.."_Plot",row.plotId or row.id.."_PLOT")
		local frame=cf(row.position,row.yaw)
		local groundSize=Vector3.new(spec.dimensions[1]+6,.4,spec.dimensions[3]+8)
		local centre=Vector3.new((spec.boundsMinStuds[1]+spec.boundsMaxStuds[1])/2,-.24,(spec.boundsMinStuds[3]+spec.boundsMaxStuds[3])/2)
		part(plot,"FoundationSurround",groundSize,frame*CFrame.new(centre),Color3.fromRGB(164,161,138),Enum.Material.Concrete)
		approachPath(plot,row.position,row.yaw,spec,if row.kind=="landmark" then 18 elseif row.kind=="commercial" then 14 else 7)
		if row.kind=="commercial" then
			local data=nil;for _,r in plan.commercialPlots do if r.id==row.plotId then data=r;break end end
			assert(data);plot:SetAttribute("PlotId",data.id);plot:SetAttribute("Origin",v(data.origin));plot:SetAttribute("Yaw",data.yaw)
			plot:SetAttribute("Footprint",Vector3.new(data.footprint[1],0,data.footprint[2]));plot:SetAttribute("GroundElevation",0)
			plot:SetAttribute("RoadId",data.road);building:SetAttribute("PlotId",data.id)
			local anchor=part(plot,"PlotOrigin",Vector3.one,frame,nil,nil,true);anchor.CanCollide=false;anchor.CanQuery=false
			for name,pos in {Entrance=data.entrance,RearExit=data.rearExit,Objective=data.objectiveAttachment} do
				local a=Instance.new("Attachment");a.Name=name;a.Position=v(pos);a:SetAttribute("AttachmentId",data.id.."."..name);a.Parent=anchor
			end
			-- Blank future-signage surface remains in the asset; no invented text.
			local frontDepth=28
			part(plot,"PublicForecourt",Vector3.new(data.footprint[1],.32,frontDepth),frame*CFrame.new(0,-.2,spec.boundsMinStuds[3]-frontDepth/2),Color3.fromRGB(191,185,163))
			-- A clear side/rear route remains when the building is replaced.
			part(plot,"SideServicePath",Vector3.new(7,.32,spec.dimensions[3]+8),frame*CFrame.new(spec.boundsMaxStuds[1]+5,-.2,0),Color3.fromRGB(180,177,160))
		end
		table.insert(output,{id=row.id,assetId=row.assetId});task.wait()
	end
	return {placed=#output,first=first,last=last}
end

local function proxy(p,name,size,frame) return part(p,name,size,frame,nil,nil,true) end
local function ramp(p,name,width,z0,z1,y0,y1,x)
	local angle=-math.atan2(y1-y0,z1-z0);local thick=.65
	return proxy(p,name,Vector3.new(width,thick,math.sqrt((z1-z0)^2+(y1-y0)^2)),CFrame.new(x or 0,(y0+y1)/2-thick/(2*math.cos(angle)),(z0+z1)/2)*CFrame.Angles(angle,0,0))
end
function B.riverfront()
	edit();local district=K.Districts.HooghlyRiverfront;assert(#district.Buildings:GetChildren()==0,"Riverfront already authored")
	local bridgeMaster=master("KOL_HBR_HOWRAH")
	assert(#bridgeMaster.Collision:GetChildren()==0)
	for i=1,7 do
		local z=-448+(i-.5)*128;local section=model(bridgeMaster.Collision,"Section"..i)
		proxy(section,"Road",Vector3.new(60,1,128),CFrame.new(0,31.5,z))
		for _,x in {-39,39} do proxy(section,"Footway",Vector3.new(10,1,128),CFrame.new(x,32.5,z)) end
		for _,x in {-45.6,45.6} do proxy(section,"OuterSafetyRail",Vector3.new(.7,4,128),CFrame.new(x,34.5,z)) end
	end
	local bridge=cloneAsset("KOL_HBR_HOWRAH",district.Buildings,cf(plan.riverfront.bridge,90),"HowrahBridge","KOL_LANDMARK_HOWRAH")
	bridge:SetAttribute("LandmarkId","kolkata.howrah-bridge")
	local approachMaster=master("KOL_HBR_RF_01")
	ramp(approachMaster.Collision,"Road",62,-64,64,32,13.5)
	for _,x in {-40,40} do ramp(approachMaster.Collision,"Footway",10,-64,64,33,14.5,x) end
	for _,x in {-46,46} do ramp(approachMaster.Collision,"SafetyRail",.7,-64,64,37,18.5,x) end
	cloneAsset("KOL_HBR_RF_01",district.Buildings,cf({-580,-13.5,-180},90),"KolkataBridgeApproach","KOL_APPROACH_EAST")
	cloneAsset("KOL_HBR_RF_01",district.Buildings,cf({-1604,-13.5,-180},-90),"FarBridgeApproach","KOL_APPROACH_WEST")
	local farRoad=model(K.RoadNetwork,"FarBridgeConnector","KOL_RD_HOWRAH_FUTURE")
	part(farRoad,"Road",Vector3.new(68,.4,60),CFrame.new(-1686,-.2,-180),Color3.fromRGB(63,72,79),Enum.Material.Asphalt)
	-- The wider approach fans into the riverfront junction, keeping pedestrians.
	local neck=model(K.RoadNetwork,"HowrahApproachJunction","KOL_RD_BRIDGE_JUNCTION")
	for _,z in {-220,-140} do part(neck,"PavementWing",Vector3.new(16,.54,10),CFrame.new(-524,.27,z)) end
	local gm=master("KOL_HBR_GHAT");local c=gm.Collision
	proxy(c,"RiverLanding",Vector3.new(148,2.6,12),CFrame.new(0,-.3,-56))
	proxy(c,"UpperBank",Vector3.new(148,14.5,41.7),CFrame.new(0,6.25,27.15))
	proxy(c,"StreetApron",Vector3.new(149,.8,18),CFrame.new(0,13.1,57))
	for i,flight in {{-50,1,.6},{-29.9,5.2,.6},{-9.8,9.4,4.1/7}} do
		-- Three smooth collision ramps over the stepped render mesh.
		ramp(c,"StairFlight"..i,128,flight[1],flight[1]+16.1,flight[2]+flight[3],flight[2]+7*flight[3])
	end
	for _,q in {{-31.9,5.2},{-11.8,9.4}} do proxy(c,"IntermediateLanding",Vector3.new(128,1,4),CFrame.new(0,q[2]-.5,q[1])) end
	proxy(c,"PublicPavilionFloor",Vector3.new(142,1.2,32),CFrame.new(0,14.1,33))
	ramp(c,"PavilionFrontSteps",116,14.4,17,13.5,14.7)
	ramp(c,"PavilionRearSteps",116,49,51.6,14.7,13.5)
	for _,z in {18,46} do for _,x in {-54,-18,18,54} do proxy(c,"PavilionColumn",Vector3.new(1.7,13.8,1.7),CFrame.new(x,21.6,z)) end end
	for _,x in {-49.5,-16.5,16.5,49.5} do proxy(c,"GatewayPier",Vector3.new(4.4,10.3,4.8),CFrame.new(x,18.65,60.5)) end
	proxy(c,"GatewayLintel",Vector3.new(104,1.4,6),CFrame.new(0,24.5,60.5))
	for _,x in {-73,73} do proxy(c,"PromenadeBoundary",Vector3.new(.8,3.7,48),CFrame.new(x,15.35,28)) end
	local ghat=cloneAsset("KOL_HBR_GHAT",district.Buildings,cf(plan.riverfront.ghat,90),"KolkataGrandGhat","KOL_LANDMARK_GHAT")
	ghat:SetAttribute("LandmarkId","kolkata.grand-ghat");ghat:SetAttribute("WaterDatum",-13.5)
	-- Supporting modules receive shared simple collision in their masters.
	for _,id in {"02","03","04","05","06","07"} do
		local m=master("KOL_HBR_RF_"..id);local p=m.Collision
		if id=="02" then proxy(p,"WallAndWalk",Vector3.new(64,15.5,18),CFrame.new(0,5.75,1));proxy(p,"EdgeRail",Vector3.new(64,3.7,.8),CFrame.new(0,15.35,-7.4))
		elseif id=="03" then
			proxy(p,"CornerArmA",Vector3.new(48,15.5,16),CFrame.new(0,5.75,-16));proxy(p,"CornerArmB",Vector3.new(16,15.5,32),CFrame.new(16,5.75,8))
		elseif id=="04" then proxy(p,"WalkSlab",Vector3.new(64,.8,16),CFrame.new(0,13.1,0));proxy(p,"EdgeRail",Vector3.new(64,3.7,.8),CFrame.new(0,15.35,-7.4))
		elseif id=="05" then proxy(p,"ArrivalApron",Vector3.new(64,.8,40),CFrame.new(0,13.1,0))
		elseif id=="06" then proxy(p,"ReturnWall",Vector3.new(32,15.5,6),CFrame.new(0,5.75,0));proxy(p,"EdgeRail",Vector3.new(32,3.7,.8),CFrame.new(0,15.35,0))
		else proxy(p,"LandingDeck",Vector3.new(32,1.2,16),CFrame.new(0,1.6,0)) end
	end
	local pieces=folder(district,"RiverbankModules")
	local index=0
	for z=-768,640,64 do
		if math.abs(z+180)<90 or (z+32>305.5 and z-32<454.5) then continue end
		index+=1;cloneAsset("KOL_HBR_RF_02",pieces,cf({-620,-13.5,z},90),"Embankment_"..index,"KOL_EMBANKMENT_"..index);task.wait()
	end
	cloneAsset("KOL_HBR_RF_05",pieces,cf({-536,-13.5,380},90),"GhatArrivalApron","KOL_GHAT_APRON")
	-- A paved forecourt joins all three road-facing archways to the drive.
	local public=model(district.PlotInfrastructure,"GhatForecourt","KOL_GHAT_FORECOURT")
	part(public,"OpenArrivalSquare",Vector3.new(56,.4,132),CFrame.new(-544,-.2,380),Color3.fromRGB(191,185,166))
	cloneAsset("KOL_HBR_RF_04",pieces,cf({-584,-13.5,292},90),"NorthGhatPromenade","KOL_PROMENADE_01")
	cloneAsset("KOL_HBR_RF_03",pieces,cf({-592,-13.5,244},90),"PromenadeCorner","KOL_PROMENADE_CORNER")
	cloneAsset("KOL_HBR_RF_06",pieces,cf({-606,-13.5,478},90),"GhatRetainingReturn","KOL_GHAT_RETURN")
	cloneAsset("KOL_HBR_RF_07",pieces,cf({-694,-13.5,380},90),"RiverLanding","KOL_RIVER_LANDING")
	-- Native bounded terrain water. No Blender water or runtime animation.
	local t=workspace.Terrain;t.WaterColor=Color3.fromRGB(75,98,76);t.WaterReflectance=.12;t.WaterTransparency=.28;t.WaterWaveSize=.12;t.WaterWaveSpeed=5
	for z=-830,749,160 do
		local endZ=math.min(z+160,750)
		t:FillBlock(CFrame.new(-1094,(-36-13.5)/2,(z+endZ)/2),Vector3.new(932,22.5,endZ-z),Enum.Material.Water);task.wait()
	end
	return {bridgeSections=7,approaches=2,ghats=1,embankments=index,waterDatum=-13.5}
end

local function legacyProp(name,p,x,z,yaw,ground)
	local source=WA.Task006Archive.LegacyPara01:FindFirstChild(name,true);assert(source and source:IsA("Model"),"Missing original prop "..name)
	local m=source:Clone();local frame=m:GetPivot();local box,size=m:GetBoundingBox()
	local bottom=box.Position.Y-size.Y/2;local dy=frame.Y-bottom
	m:PivotTo(cf({x,(ground or .54)+dy,z},yaw or 0));m.ModelStreamingMode=Enum.ModelStreamingMode.Atomic
	for _,a in m:GetDescendants() do if a:IsA("BasePart") then a.Anchored=true;a.CanTouch=false;if name=="ShadeTree" then a.CastShadow=true end elseif a:IsA("Light") then a.Enabled=false end end
	m.Parent=p;return m
end

function B.environment()
	edit();local civic=K.Districts.Civic.Environment
	assert(#civic:GetChildren()==0,"Environment already placed")
	local count=0
	-- Reuse the approved streetscape rather than introduce unrelated props.
	for _,z in {-400,-180,0,400} do
		for x=-430,350,130 do
			if math.abs(x-80)<30 then continue end
			for _,side in {-1,1} do legacyProp("Streetlight",civic,x,z+side*27,if side==1 then 0 else 180);count+=1 end
		end
	end
	for _,q in {{-267,-250},{-20,-240},{210,-225},{320,-225},{-440,100},{-430,220},{150,230},{335,265},{280,360},{-205,-590},{-280,-590},{110,-145},{240,-145},{-180,430},{30,430},{155,-670},{340,-490},{-450,520}} do
		legacyProp("ShadeTree",civic,q[1],q[2],0,-.35);count+=1
	end
	for _,q in {{-180,-215},{-70,-215},{255,-220},{-447,180},{165,230},{300,360},{-278,-570},{-185,-570},{-165,435},{20,435}} do legacyProp("AddaBench",civic,q[1],q[2],0,.1);count+=1 end
	for _,q in {{-310,-26},{-60,26},{220,-26},{-260,-426},{-220,426},{120,426}} do legacyProp("DrainGrate",civic,q[1],q[2],0,.50);count+=1 end
	for _,q in {{-440,-550},{-335,-550},{-195,-550},{-35,-550}} do legacyProp("ElectricalPole",K.Districts.NorthKolkata.Environment,q[1],q[2]+13,0,.1);count+=1 end
	for _,q in {{-210,-94},{-370,-94},{-95,365}} do legacyProp("FixedProduceCounter",K.Districts.Commercial.Environment,q[1],q[2],180,.1);count+=1 end
	for _,q in {{-80,55},{230,55},{-190,365},{45,365},{-420,-65}} do legacyProp("StreetBin",civic,q[1],q[2],0,.1);count+=1 end
	local river=K.Districts.HooghlyRiverfront.Environment
	for z=-690,590,128 do
		if math.abs(z+180)<72 or math.abs(z-380)<90 then continue end
		cloneAsset("KOL_HBR_PROP_01",river,cf({-530,.54,z},90),"RiverfrontStreetlight");count+=1
	end
	for _,q in {{-566,315},{-566,445},{-576,265}} do cloneAsset("KOL_HBR_PROP_02",river,cf({q[1],0,q[2]},90),"GhatPedestrianLight");count+=1 end
	for _,q in {{-538,330},{-538,430},{-588,280}} do cloneAsset("KOL_HBR_PROP_08",river,cf({q[1],0,q[2]},90),"RiverBench");count+=1 end
	for _,q in {{-530,330},{-530,430}} do cloneAsset("KOL_HBR_PROP_09",river,cf({q[1],0,q[2]},90),"RiverBin");count+=1 end
	cloneAsset("KOL_HBR_PROP_03",river,cf({-535,0,245},0),"RiverUtilityPole")
	cloneAsset("KOL_HBR_PROP_10",river,cf({-541,0,444},90),"GhatSignFrame")
	cloneAsset("KOL_HBR_PROP_11",river,cf({-542,0,495},90),"RiverVendorCanopy")
	cloneAsset("KOL_HBR_PROP_12",river,cf({-541,0,510},90),"RiverUtilityBox")
	cloneAsset("KOL_HBR_PROP_13",river,cf({-545,0,523},90),"RiverTap")
	for _,q in {{-699,369},{-699,391}} do cloneAsset("KOL_HBR_PROP_06",river,cf({q[1],-11.14,q[2]},90),"MooringPost") end
	for _,z in {330,346,414,430} do cloneAsset("KOL_HBR_PROP_07",river,cf({-552,0,z},0),"ArrivalBollard") end
	cloneAsset("KOL_HBR_PROP_04",river,cf({-571,0,310},0),"GhatBlueWhiteRailing")
	cloneAsset("KOL_HBR_PROP_05",river,cf({-571,0,450},0),"GhatSteelRailing")
	cloneAsset("KOL_HBR_PROP_14",river,cf({-725,-14.4,365},95),"DecorativeBoat01")
	cloneAsset("KOL_HBR_PROP_15",river,cf({-749,-14.4,421},80),"DecorativeBoat02")
	cloneAsset("KOL_HBR_CTX_01",K.Districts.HooghlyRiverfront.Buildings,cf({-560,0,575},90),"RiverServiceShed","KOL_CONTEXT_01")
	cloneAsset("KOL_HBR_CTX_02",K.Districts.HooghlyRiverfront.Buildings,cf({-555,0,-520},90),"RiverStoreShell","KOL_CONTEXT_02")
	return {reusedStreetProps=count,riverPropTypes=15}
end

function B.report()
	local used={};local rows={};local residential=0;local meshIds={};local meshInstances=0;local triangles=0;local parts=0
	for _,r in plan.placements do
		local m=K.Districts[r.district].Buildings:FindFirstChild(r.id)
		assert(m,"Missing placement "..r.id)
		if r.kind=="residential" then residential+=1;used[r.assetId]=true end
		table.insert(rows,{placementId=r.id,assetId=r.assetId,district=r.district,position=r.position,yaw=r.yaw,plotId=r.plotId})
	end
	for _,p in K:GetDescendants() do
		if p:IsA("BasePart") then parts+=1 end
		if p:IsA("MeshPart") then meshInstances+=1;meshIds[p.MeshId]=true;triangles+=(p:GetAttribute("SourceTriangles") or 0) end
	end
	local n=0;for _ in used do n+=1 end
	local unique=0;for _ in meshIds do unique+=1 end
	local result={residentialPlacements=residential,uniqueTier3Designs=n,tier2=5,tier25=5,placements=rows,commercialPlots=plan.commercialPlots,roads=plan.roads,expansionConnections=plan.expansionConnections,meshInstances=meshInstances,uniqueMeshIds=unique,sourceTrianglesExcludingUnlabelledVictoria=triangles,baseParts=parts,victoriaUnchanged=fingerprint(K.Districts.Maidan.VictoriaMemorial)==victoriaBefore}
	post("audit",result);return {residential=residential,uniqueTier3=n,parts=parts,meshInstances=meshInstances,uniqueMeshIds=unique,victoriaUnchanged=result.victoriaUnchanged}
end
return B
