--!strict
-- Edit-only authoring. No runtime script calls this module.
local ServerStorage = game:GetService("ServerStorage")
local Lighting = game:GetService("Lighting")
local ChangeHistoryService = game:GetService("ChangeHistoryService")
local Builder = {}
local C = {
	cream = Color3.fromRGB(240, 217, 175), ivory = Color3.fromRGB(248, 235, 204),
	green = Color3.fromRGB(42, 91, 77), dark = Color3.fromRGB(35, 49, 55),
	red = Color3.fromRGB(159, 66, 48), teal = Color3.fromRGB(76, 146, 143),
	road = Color3.fromRGB(63, 72, 79), paving = Color3.fromRGB(174, 168, 149),
	metal = Color3.fromRGB(64, 78, 77), wood = Color3.fromRGB(112, 72, 43),
	leaf = Color3.fromRGB(67, 113, 73), clay = Color3.fromRGB(190, 101, 61),
}
local function folder(parent: Instance, name: string): Folder
	local f = Instance.new("Folder")
	f.Name = name
	f.Parent = parent
	return f
end
local function model(name: string): Model
	local m = Instance.new("Model")
	m.Name = name
	m.ModelStreamingMode = Enum.ModelStreamingMode.Atomic
	m.WorldPivot = CFrame.identity
	return m
end
local function part(parent: Instance, name: string, size: Vector3, cf: CFrame, color: Color3, material: Enum.Material?, solid: boolean?): Part
	local p = Instance.new("Part")
	p.Name, p.Size, p.CFrame = name, size, cf
	p.Anchored, p.CanTouch = true, false
	p.CanCollide = solid == true
	p.CanQuery = solid == true
	p.CastShadow = solid == true or size.Y > 2
	p.Material, p.Color = material or Enum.Material.SmoothPlastic, color
	p.TopSurface, p.BottomSurface = Enum.SurfaceType.Smooth, Enum.SurfaceType.Smooth
	p.Parent = parent
	return p
end
local function box(parent: Instance, name: string, x: number, y: number, z: number, w: number, h: number, d: number, color: Color3, solid: boolean?, material: Enum.Material?): Part
	return part(parent, name, Vector3.new(w,h,d), CFrame.new(x,y,z), color, material, solid)
end
local function cylinder(parent: Instance, name: string, pos: Vector3, radius: number, height: number, color: Color3, solid: boolean?): Part
	local p = part(parent,name,Vector3.new(height,radius*2,radius*2),CFrame.new(pos)*CFrame.Angles(0,0,math.pi/2),color,Enum.Material.SmoothPlastic,solid)
	p.Shape = Enum.PartType.Cylinder
	return p
end
local function line(parent: Instance, name: string, a: Vector3, b: Vector3, width: number, color: Color3, solid: boolean?): Part
	return part(parent,name,Vector3.new(width,width,(b-a).Magnitude),CFrame.lookAt((a+b)/2,b),color,Enum.Material.SmoothPlastic,solid)
end
local function sign(parent: Instance, name: string, cf: CFrame, w: number, h: number, text: string, bg: Color3, fg: Color3): Part
	local p=part(parent,name,Vector3.new(w,h,0.28),cf,bg,nil,false)
	local gui=Instance.new("SurfaceGui")
	gui.Name="Lettering"
	gui.Face=Enum.NormalId.Front
	gui.CanvasSize=Vector2.new(math.floor(w*40),math.floor(h*40))
	gui.LightInfluence=1
	gui.MaxDistance=150
	local label=Instance.new("TextLabel")
	label.Size=UDim2.fromScale(0.94,0.88)
	label.Position=UDim2.fromScale(0.03,0.06)
	label.BackgroundTransparency=1
	label.Text=text
	label.TextColor3=fg
	label.Font=Enum.Font.GothamBold
	label.TextScaled=true
	label.Parent=gui
	gui.Parent=p
	return p
end
local function finish(m: Model, parent: Instance, cf: CFrame, id: string): Model
	m:SetAttribute("AssetId",id)
	m:SetAttribute("AuthoringVersion",1)
	m:PivotTo(cf)
	m.Parent=parent
	return m
end
local function district(): Folder
	return workspace.World.Cities.Kolkata.Districts.Para01 :: Folder
end
local function record(name: string, fn: () -> ()): ()
	local id=ChangeHistoryService:TryBeginRecording(name)
	local ok,err=xpcall(fn,debug.traceback)
	if id then ChangeHistoryService:FinishRecording(id,Enum.FinishRecordingOperation.Commit) end
	if not ok then error(err) end
end

function Builder.infrastructure()
	assert(not workspace:FindFirstChild("World"),"World exists; inspect before regenerating")
	record("Kolkata foundation - street network",function()
		local authoring=ServerStorage:FindFirstChild("WorldAuthoring") or folder(ServerStorage,"WorldAuthoring")
		local originals=folder(authoring,"OriginalTemplate")
		for _,name in {"Baseplate","SpawnLocation"} do
			local v=workspace:FindFirstChild(name)
			if v then v.Parent=originals end
		end
		local world=folder(workspace,"World")
		world:SetAttribute("WorldVersion",1)
		world:SetAttribute("StudsPerMetre",3.57)
		world:SetAttribute("SourceOfTruth","Studio authored; no automatic file sync")
		local cities=folder(world,"Cities")
		local city=folder(cities,"Kolkata")
		city:SetAttribute("CityId","kolkata")
		local districts=folder(city,"Districts")
		local para=folder(districts,"Para01")
		para:SetAttribute("DistrictId","kolkata.para01")
		para:SetAttribute("Design","Fictional North Kolkata-inspired neighbourhood")
		for _,name in {"Ground","Streets","Buildings","StreetFurniture","Vegetation","Utilities","Courtyard"} do folder(para,name) end
		local connections=folder(city,"ExpansionConnections")
		for _,v in {{"EastRoad",320,0},{"WestRoad",-320,0},{"NorthStreet",24,-230},{"SouthStreet",24,230}} do
			local marker=box(connections,v[1] :: string,v[2] :: number,2,v[3] :: number,2,2,2,C.cream,false)
			marker.Transparency=1
			marker:SetAttribute("ConnectionId","kolkata."..string.lower(v[1] :: string))
		end
		-- Ground tiles remain independent streaming units, rather than one city-sized atomic model.
		for ix=-2,2 do for iz=-2,2 do
			local m=model(`Ground_{ix}_{iz}`)
			box(m,"Earth",0,-3,0,180,5,180,Color3.fromRGB(126,143,101),true,Enum.Material.Grass)
			finish(m,para.Ground,CFrame.new(ix*180,0,iz*180),"ground.tile")
		end end
		local road=model("MainRoad")
		box(road,"Carriageway",0,-0.2,0,640,0.4,40,C.road,true,Enum.Material.Asphalt)
		for x=-300,300,24 do if math.abs(x-24)>25 then
			box(road,"CentreDash",x,0.025,0,10,0.035,0.22,C.ivory,false)
		end end
		finish(road,para.Streets,CFrame.identity,"road.main.40")
		local lanes=model("LaneNetwork")
		box(lanes,"CrossStreetNorth",24,-0.14,-126,20,0.28,212,C.road,true,Enum.Material.Asphalt)
		box(lanes,"CrossStreetSouth",24,-0.14,126,20,0.28,212,C.road,true,Enum.Material.Asphalt)
		box(lanes,"WestGullyNorth",-120,0.02,-65,14,0.3,90,C.paving,true,Enum.Material.Concrete)
		box(lanes,"WestGullySouth",-120,0.02,65,14,0.3,90,C.paving,true,Enum.Material.Concrete)
		box(lanes,"EastGullyNorth",156,0.02,-65,14,0.3,90,C.paving,true,Enum.Material.Concrete)
		box(lanes,"EastGullySouth",156,0.02,65,14,0.3,90,C.paving,true,Enum.Material.Concrete)
		box(lanes,"NorthBackLane",0,0.02,-105,450,0.3,16,C.paving,true,Enum.Material.Concrete)
		box(lanes,"SouthBackLane",0,0.02,105,450,0.3,16,C.paving,true,Enum.Material.Concrete)
		finish(lanes,para.Streets,CFrame.identity,"road.lanes")
		-- Pavements are interrupted at every gully and crossing; no hidden curb across entrances.
		local ranges={{-225,-127},{-113,10},{38,149},{163,225}}
		for side=-1,1,2 do for i,r in ranges do
			local m=model(`Pavement_{side}_{i}`)
			local mid,w=(r[1]+r[2])/2,r[2]-r[1]
			box(m,"Footpath",0,0.2,0,w,0.4,12,C.paving,true,Enum.Material.Concrete)
			for x=-w/2+3,w/2-2,6 do
				-- Project the painted face beyond the pavement to avoid coplanar flicker.
				box(m,"Curb",x,0.27,-side*5.78,5.9,0.54,0.6,if math.floor((x+w/2)/6)%2==0 then C.ivory else C.teal,true)
			end
			finish(m,para.Streets,CFrame.new(mid,0,side*26),"pavement.12")
		end end
		for _,x in {-2,50} do
			local crossing=model("PedestrianCrossing")
			for z=-17,17,5 do box(crossing,"Stripe",x,0.04,z,6,0.035,2.5,C.ivory,false) end
			finish(crossing,para.Streets,CFrame.identity,"road.crossing")
		end
		local court=model("AddaCourtyard")
		box(court,"Paving",92,0.13,-136,108,0.26,46,Color3.fromRGB(194,169,129),true,Enum.Material.Concrete)
		box(court,"RedOxideBorder",92,0.15,-160,108,0.3,2,C.red,true)
		finish(court,para.Courtyard,CFrame.identity,"courtyard.adda")
		local spawn=Instance.new("SpawnLocation")
		spawn.Name="ParaSpawn"
		spawn.Size=Vector3.new(6,0.2,6)
		spawn.CFrame=CFrame.new(60,0.5,-129)*CFrame.Angles(0,math.pi,0)
		spawn.Anchored=true
		spawn.Transparency=1
		spawn.CanCollide=false
		spawn.CanTouch=false
		spawn.CanQuery=false
		spawn.Neutral=true
		spawn.Duration=0
		spawn.Parent=para.Courtyard
	end)
	return "Street network built"
end

local function window(): Model
	local m=model("LouvredWindow")
	box(m,"Surround",0,0,0,5.4,7.7,0.35,C.ivory,false)
	box(m,"Recess",0,0,-0.22,4.65,6.9,0.15,C.dark,false)
	for side=-1,1,2 do
		box(m,"Shutter",side*1.16,0,-0.37,2.15,6.5,0.18,C.green,false)
		for y=-2.6,2.6,1.3 do box(m,"Louvre",side*1.16,y,-0.51,1.9,0.14,0.22,Color3.fromRGB(58,111,89),false) end
	end
	box(m,"Sill",0,-3.9,-0.3,6.1,0.4,0.9,C.ivory,false)
	box(m,"DripHood",0,4.05,-0.45,6.3,0.35,1.5,C.ivory,false)
	return m
end
local function balcony(m: Model, width: number, y: number, front: number)
	box(m,"BalconySlab",0,y,front-1.8,width,0.6,4.4,C.ivory,true)
	box(m,"BalconyRail",0,y+2.9,front-3.7,width,0.18,0.18,C.green,false)
	box(m,"BalconyLowerRail",0,y+0.65,front-3.7,width,0.16,0.18,C.green,false)
	for x=-width/2,width/2,2.6 do
		box(m,"Balustrade",x,y+1.7,front-3.7,0.14,2.5,0.14,C.green,false)
	end
	for _,x in {-width/2,width/2} do
		box(m,"BalconyEndRail",x,y+2.9,front-1.8,0.16,0.18,3.8,C.green,false)
	end
end
local function house(kit: Folder, name: string, width: number, floors: number, wall: Color3, shop: string?): Model
	local m=model(name)
	local depth,h=32,floors*12
	local front=-depth/2
	-- Shop arcades are real eight-stud-deep alcoves with clear pedestrian openings.
	box(m,"CollisionVolume",0,h/2,if shop then 4 else 0,width,h,if shop then 24 else depth,wall,true,Enum.Material.Concrete)
	if shop then
		box(m,"UpperFront",0,12+(h-12)/2,-12,width,h-12,8,wall,true,Enum.Material.Concrete)
		for _,x in {-width/2+0.65,0,width/2-0.65} do
			box(m,"ArcadePier",x,5.2,front+0.5,1.3,10.4,1.3,C.ivory,true)
		end
		box(m,"ShopFloor",0,0.3,-12,width,0.6,9,C.red,true)
		local shutter=box(m,"ClosedShopShutter",width/4,4.7,-15.2,width/2-2,8.5,0.4,C.teal,true,Enum.Material.Metal)
		for y=1,8,1 do box(m,"ShutterRib",width/4,y,-15.48,width/2-2,0.09,0.13,C.metal,false) end
		box(m,"DisplayCounter",-width/4,1.8,-10,width/2-3,3.2,2.3,C.wood,true)
		for j=1,4 do box(m,"Goods",-width/4-4+j*1.8,3.7,-10.1,1.2,0.6,1,if j%2==0 then C.cream else C.red,false) end
		sign(m,"ShopName",CFrame.new(0,10,-16.8),width-2,2.6,shop,C.green,C.ivory)
		for x=-width/2+1,width/2-1,3 do
			local aw=part(m,"AwningPanel",Vector3.new(2.95,0.18,5),CFrame.new(x,8.5,-18.7)*CFrame.Angles(math.rad(-9),0,0),if math.floor((x+width/2)/3)%2==0 then C.cream else C.red,Enum.Material.Fabric,false)
			box(m,"AwningValance",x,8.1,-21.1,2.95,0.75,0.18,aw.Color,false)
		end
	else
		box(m,"RedOxideStoop",0,0.35,front-1.3,width-1,0.7,3,C.red,true)
		box(m,"DoorFrame",0,5,front-0.2,6.5,10,0.4,C.ivory,false)
		box(m,"Door",0,4.65,front-0.48,5.3,9.3,0.2,C.green,false)
		box(m,"DoorSplit",0,4.65,front-0.64,0.1,8.5,0.1,C.ivory,false)
		cylinder(m,"DoorHandle",Vector3.new(0.7,4.6,front-0.8),0.14,0.18,C.cream,false)
	end
	for f=1,floors-1 do
		for _,x in {-width*0.3,0,width*0.3} do
			local w=kit.LouvredWindow:Clone() :: Model
			w:PivotTo(CFrame.new(x,f*12+5.3,front-0.18))
			w.Parent=m
		end
		box(m,"FloorCornice",0,f*12-0.1,0,width+0.8,0.5,depth+0.8,C.ivory,false)
	end
	if not shop then
		for _,x in {-width*0.3,width*0.3} do
			local w=kit.LouvredWindow:Clone() :: Model
			w:PivotTo(CFrame.new(x,5.3,front-0.18))
			w.Parent=m
		end
	end
	balcony(m,width*0.78,12,front)
	box(m,"RoofCornice",0,h+0.3,0,width+1.6,0.8,depth+1.6,C.ivory,false)
	box(m,"RoofTerrace",0,h+0.8,0,width,0.3,depth,C.red,true)
	for _,z in {-15.7,15.7} do box(m,"Parapet",0,h+1.7,z,width,1.8,0.6,wall,true) end
	for _,x in {-width/2+0.3,width/2-0.3} do box(m,"Parapet",x,h+1.7,0,0.6,1.8,32,wall,true) end
	for _,x in {-width/2+0.7,width/2-0.7} do box(m,"CornerPilaster",x,h/2,front-0.15,1.1,h,0.4,C.ivory,false) end
	cylinder(m,"WaterTank",Vector3.new(width/4,h+3.2,8),2.6,4.8,C.dark,false)
	cylinder(m,"TankLid",Vector3.new(width/4,h+5.7,8),2.7,0.3,C.metal,false)
	box(m,"RainwaterPipe",-width/2+2,h/2,front-0.55,0.24,h,0.24,C.metal,false)
	-- Side windows add readable detail at gully approaches without hidden geometry.
	for side=-1,1,2 do for f=1,floors-1 do
		local w=kit.LouvredWindow:Clone() :: Model
		w:PivotTo(CFrame.new(side*(width/2+0.18),f*12+5.3,3)*CFrame.Angles(0,-side*math.pi/2,0))
		w.Parent=m
	end end
	m:SetAttribute("WidthStuds",width)
	m:SetAttribute("FloorHeightStuds",12)
	return m
end

function Builder.buildings()
	record("Kolkata foundation - modular architecture",function()
		local para=district()
		assert(#para.Buildings:GetChildren()==0,"Buildings already exist")
		local kit=folder(ServerStorage.WorldAuthoring,"KolkataKit")
		window().Parent=kit
		local styles={
			{"OchreResidence",38,3,Color3.fromRGB(218,168,99),nil},
			{"MintResidence",34,2,Color3.fromRGB(139,180,154),nil},
			{"CoralResidence",36,3,Color3.fromRGB(199,126,106),nil},
			{"BlueResidence",32,2,Color3.fromRGB(128,169,177),nil},
			{"Bookshop",38,3,Color3.fromRGB(231,195,132),"PARA BOOK HOUSE"},
			{"Provisions",34,2,Color3.fromRGB(170,190,151),"PARA PROVISIONS"},
			{"SweetShop",36,2,Color3.fromRGB(224,158,128),"BENGAL SWEETS"},
		}
		for _,s in styles do
			local m=house(kit,s[1] :: string,s[2] :: number,s[3] :: number,s[4] :: Color3,s[5] :: string?)
			m.Parent=kit
			task.wait()
		end
		local layout={
			{"Bookshop",-197,-52,180},{"CoralResidence",-154,-52,180},
			{"MintResidence",-90,-52,180},{"OchreResidence",-48,-52,180},
			{"SweetShop",63,-52,180},{"BlueResidence",107,-52,180},{"OchreResidence",193,-52,180},
			{"MintResidence",-198,52,0},{"Provisions",-154,52,0},
			{"CoralResidence",-91,52,0},{"BlueResidence",-49,52,0},
			{"Bookshop",64,52,0},{"CoralResidence",107,52,0},{"SweetShop",194,52,0},
			{"BlueResidence",-190,-145,180},{"MintResidence",-145,-145,180},
			{"CoralResidence",-78,-145,180},{"OchreResidence",-36,-145,180},
			{"MintResidence",62,-180,180},{"CoralResidence",108,-180,180},
			{"OchreResidence",-170,145,0},{"MintResidence",-65,145,0},
			{"BlueResidence",84,145,0},{"MintResidence",195,145,0},
		}
		for i,item in layout do
			local m=kit[item[1] :: string]:Clone() :: Model
			m.Name=string.format("Building_%02d_%s",i,item[1])
			m:SetAttribute("LocationId",`kolkata.para01.building.{i}`)
			finish(m,para.Buildings,CFrame.new(item[2] :: number,0.4,item[3] :: number)*CFrame.Angles(0,math.rad(item[4] :: number),0),"building."..(item[1] :: string))
			task.wait()
		end
	end)
	return "24 modular buildings placed"
end

local function tree(): Model
	local m=model("CourtyardShadeTree")
	cylinder(m,"Trunk",Vector3.new(0,7,0),1.1,14,C.wood,true)
	for _,v in {{-4,13,0},{4,15,1},{0,16,-4}} do
		line(m,"Branch",Vector3.new(0,8,0),Vector3.new(v[1],v[2],v[3]),0.8,C.wood,false)
	end
	for i,v in {{0,19,0,14},{-7,17,0,12},{6,18,2,12},{0,18,-7,11},{-3,23,-2,11}} do
		local p=box(m,"Canopy",v[1],v[2],v[3],v[4],v[4]*0.8,v[4],if i%2==0 then Color3.fromRGB(84,132,79) else C.leaf,false)
		p.Shape=Enum.PartType.Ball
		p.CastShadow=true
	end
	return m
end
local function bench(): Model
	local m=model("AddaBench")
	for _,x in {-3,3} do
		box(m,"Leg",x,0.8,0,0.6,1.6,2,C.metal,true)
		box(m,"BackSupport",x,2.1,0.8,0.4,3,0.4,C.metal,false)
	end
	for z=-0.7,0.7,0.7 do box(m,"SeatSlat",0,1.6,z,8,0.25,0.6,C.wood,true) end
	for y=2.3,3.1,0.8 do box(m,"BackSlat",0,y,0.9,8,0.6,0.25,C.wood,false) end
	return m
end
local function lamp(): Model
	local m=model("Streetlight")
	cylinder(m,"Base",Vector3.new(0,0.5,0),0.75,1,C.green,true)
	cylinder(m,"Mast",Vector3.new(0,9,0),0.25,18,C.green,true)
	line(m,"Arm",Vector3.new(0,17.8,0),Vector3.new(0,18.4,-4),0.3,C.green,false)
	box(m,"Lantern",0,18.2,-4.1,1.4,0.55,2.8,C.dark,false)
	box(m,"Diffuser",0,17.9,-4.1,1.1,0.12,2.3,Color3.fromRGB(255,229,175),false,Enum.Material.Neon)
	local light=Instance.new("PointLight")
	light.Name="WarmLight"
	light.Color=Color3.fromRGB(255,224,171)
	light.Brightness=0.5
	light.Range=22
	light.Shadows=false
	light.Parent=m.Lantern
	return m
end
local function pole(): Model
	local m=model("ElectricalPole")
	cylinder(m,"ConcretePole",Vector3.new(0,13.5,0),0.42,27,Color3.fromRGB(152,149,132),true)
	box(m,"PaintedBase",0,2,0,0.86,4,0.86,C.ivory,true)
	box(m,"CrossArm",0,25,0,5.5,0.35,0.4,C.metal,false)
	for _,x in {-2,0,2} do
		cylinder(m,"Insulator",Vector3.new(x,25.6,0),0.26,0.8,C.cream,false)
	end
	box(m,"JunctionBox",0,6.4,0.55,1.3,2,0.65,C.metal,false)
	return m
end
local function pot(m: Model, x: number, y: number, z: number)
	cylinder(m,"TerracottaPlanter",Vector3.new(x,y+0.65,z),0.8,1.3,C.clay,true)
	cylinder(m,"PotRim",Vector3.new(x,y+1.3,z),0.9,0.2,C.clay,false)
	local p=box(m,"Plant",x,y+2,z,1.7,2,1.7,C.leaf,false)
	p.Shape=Enum.PartType.Ball
end
local function chai(): Model
	local m=model("ParaChaiStall")
	box(m,"RaisedFloor",0,0.3,0,18,0.6,10,C.red,true)
	box(m,"BackWall",0,4.3,4.5,18,8,0.5,C.green,true)
	box(m,"SidePanel",8.7,3,0,0.5,5.5,9,C.green,true)
	for _,x in {-8.4,8.4} do for _,z in {-4.5,4.5} do box(m,"BambooPost",x,5,z,0.3,10,0.3,C.wood,true) end end
	box(m,"Counter",-1,3.1,-3.4,14,0.6,2.5,C.wood,true)
	box(m,"CounterFront",-1,1.7,-3.6,14,2.2,0.5,C.teal,true)
	for x=-8.8,8.8,1.1 do
		part(m,"CorrugatedRoof",Vector3.new(1.08,0.25,12),CFrame.new(x,9.6,0)*CFrame.Angles(math.rad(-6),0,0),if math.floor(x*2)%3==0 then C.red else Color3.fromRGB(160,72,53),Enum.Material.Metal,false)
	end
	sign(m,"ChaiSign",CFrame.new(0,7.4,-5.1),16,2.6,"PARA CHA  |  TEA & ADDA",C.cream,C.green)
	sign(m,"Menu",CFrame.new(-4,5.6,4.1),5,3.2,"CHA\nBISCUITS\nFRESH DAILY",C.dark,C.ivory)
	box(m,"Shelf",3,5.1,3.8,7,0.25,1.5,C.wood,false)
	for _,x in {1,3,5} do
		cylinder(m,"BiscuitJar",Vector3.new(x,5.9,3.8),0.55,1.4,C.cream,false)
		cylinder(m,"JarLid",Vector3.new(x,6.65,3.8),0.58,0.14,C.red,false)
	end
	cylinder(m,"Stove",Vector3.new(3.8,3.7,-3.4),0.9,0.7,C.dark,false)
	local kettle=box(m,"Kettle",3.8,4.6,-3.4,1.7,1.5,1.7,Color3.fromRGB(162,176,175),false,Enum.Material.Metal)
	kettle.Shape=Enum.PartType.Ball
	cylinder(m,"KettleLid",Vector3.new(3.8,5.35,-3.4),0.5,0.12,C.metal,false)
	line(m,"Spout",Vector3.new(4.4,4.7,-3.4),Vector3.new(5.2,5,-3.4),0.4,C.metal,false)
	line(m,"HandleTop",Vector3.new(2.6,5,-3.4),Vector3.new(3.1,5.3,-3.4),0.14,C.dark,false)
	for _,x in {-5,-3.5,-2,-0.5} do
		cylinder(m,"BhanrClayCup",Vector3.new(x,3.8,-3.3),0.28,0.55,C.clay,false)
		cylinder(m,"TeaSurface",Vector3.new(x,4.08,-3.3),0.23,0.025,C.wood,false)
	end
	return m
end
function Builder.details()
	record("Kolkata foundation - streets and chai courtyard",function()
		local para=district()
		assert(#para.StreetFurniture:GetChildren()==0,"Details already exist")
		local kit=ServerStorage.WorldAuthoring.KolkataKit
		for name,m in {ShadeTree=tree(),AddaBench=bench(),Streetlight=lamp(),ElectricalPole=pole(),ChaiStall=chai()} do m.Name=name;m.Parent=kit end
		local function place(template: string, parent: Instance, x: number, z: number, yaw: number?, id: string?): Model
			local m=kit[template]:Clone() :: Model
			return finish(m,parent,CFrame.new(x,0.4,z)*CFrame.Angles(0,math.rad(yaw or 0),0),id or string.lower(template))
		end
		place("ChaiStall",para.Courtyard,117,-151,180,"kolkata.para01.chai")
		for _,v in {{60,-146},{-233,-42},{-230,67},{230,-75},{229,85},{-103,134},{138,143},{-211,-183},{177,-173}} do place("ShadeTree",para.Vegetation,v[1],v[2]) end
		for _,v in {{78,-153,180},{50,-138,-90},{82,-120,0},{132,-134,90},{-105,89,0}} do place("AddaBench",para.StreetFurniture,v[1],v[2],v[3]) end
		local planter=model("CourtyardTreeSeat")
		for _,v in {{60,-152,12,1.5},{60,-140,12,1.5},{54,-146,1.5,12},{66,-146,1.5,12}} do
			box(planter,"RedOxideSeat",v[1],1,v[2],v[3],1.6,v[4],C.red,true)
		end
		finish(planter,para.Courtyard,CFrame.identity,"courtyard.treeSeat")
		for side=-1,1,2 do
			for _,x in {-215,-105,-7,144,220} do place("Streetlight",para.StreetFurniture,x,side*24,if side==-1 then 180 else 0) end
		end
		place("Streetlight",para.StreetFurniture,40,-148,90)
		local poles={-217,-118,-11,153,224}
		for _,x in poles do place("ElectricalPole",para.Utilities,x,-30) end
		local wires=model("OverheadUtilityLines")
		for i=1,#poles-1 do
			local a,b=poles[i],poles[i+1]
			for _,offset in {-1.8,1.8} do
				local previous=Vector3.new(a+offset,26.4,-30)
				for step=1,6 do
					local t=step/6
					local nextPoint=Vector3.new(a+(b-a)*t+offset,26.4-2.3*4*t*(1-t),-30)
					line(wires,"SaggingWire",previous,nextPoint,0.07,C.dark,false)
					previous=nextPoint
				end
			end
		end
		finish(wires,para.Utilities,CFrame.identity,"utility.wires")
		for i,b in para.Buildings:GetChildren() do
			local cf=(b :: Model):GetPivot()
			local dressing=model(`BuildingDetails_{i}`)
			local width=b:GetAttribute("WidthStuds") :: number
			pot(dressing,-width/2+3,0,-18.6)
			if i%3==0 then
				box(dressing,"ACUnit",width/2-2,16,-16.7,3,1.9,1.3,C.ivory,false)
				for j=1,3 do box(dressing,"ACGrille",width/2-2,15.4+j*0.3,-17.4,2.5,0.09,0.1,C.metal,false) end
			end
			if i%4==0 then
				-- Height is read from the roof rather than assumed from style.
				local roof=b:FindFirstChild("RoofTerrace") :: BasePart
				local localHeight=cf:PointToObjectSpace(roof.Position).Y
				box(dressing,"RoofStairHead",-7,localHeight+3.5,5,9,7,9,Color3.fromRGB(191,158,116),true,Enum.Material.Concrete)
				box(dressing,"StairHeadRoof",-7,localHeight+7.1,5,10,0.4,10,C.ivory,false)
				line(dressing,"Clothesline",Vector3.new(-8,localHeight+4,-6),Vector3.new(8,localHeight+4,-6),0.06,C.metal,false)
				for j=1,4 do box(dressing,"DryingCloth",-8+j*3,localHeight+2.8,-6,2.4,2.6,0.08,if j%2==0 then C.cream else C.teal,false,Enum.Material.Fabric) end
			end
			if i%3==1 then
				for j=1,3 do box(dressing,"ExposedBrick",width/2-3+j*0.2,1+j*0.4,-16.08,3-j*0.4,0.32,0.08,C.red,false) end
			end
			finish(dressing,para.StreetFurniture,cf,"building.dressing")
			if i%6==0 then task.wait() end
		end
		local neighbourhood=model("NeighbourhoodSign")
		cylinder(neighbourhood,"Signpost",Vector3.new(0,4,0),0.16,8,C.green,true)
		sign(neighbourhood,"StreetName",CFrame.new(0,7,-0.1),10,2.2,"KOLKATA  /  PARA",C.green,C.ivory)
		finish(neighbourhood,para.StreetFurniture,CFrame.new(40,0.4,-28)*CFrame.Angles(0,math.pi,0),"sign.para")
		-- Familiar municipal details, deliberately sparse and outside clear walking routes.
		for _,v in {{-102,-30},{139,30},{211,-30}} do
			local detail=model("StreetBin")
			cylinder(detail,"Bin",Vector3.new(0,1.4,0),0.9,2.8,C.green,true)
			cylinder(detail,"Lid",Vector3.new(0,2.9,0),1,0.25,C.metal,false)
			finish(detail,para.StreetFurniture,CFrame.new(v[1],0.4,v[2]),"street.bin")
		end
		for _,v in {{-108,-21},{140,-21},{-108,21},{140,21}} do
			local drain=model("DrainGrate")
			box(drain,"Frame",0,0.01,0,3,0.04,1,C.dark,false)
			for x=-1.2,1.2,0.4 do box(drain,"Grate",x,0.04,0,0.15,0.04,0.9,C.metal,false) end
			finish(drain,para.StreetFurniture,CFrame.new(v[1],0,v[2]),"street.drain")
		end
		local washing=model("CourtyardWashPoint")
		box(washing,"Platform",0,0.25,0,6,0.5,5,C.paving,true)
		cylinder(washing,"HandPump",Vector3.new(0,2,0),0.3,3.5,C.green,true)
		line(washing,"PumpHandle",Vector3.new(0,3.5,0),Vector3.new(1.7,3.8,0),0.22,C.green,false)
		line(washing,"Spout",Vector3.new(0,2.7,0),Vector3.new(-1.1,2.6,0),0.22,C.green,false)
		finish(washing,para.Courtyard,CFrame.new(140,0.25,-151),"courtyard.washpoint")
	end)
	return "Reusable chai, tree, bench, lighting and utility assets placed"
end

function Builder.lighting()
	Lighting.LightingStyle=Enum.LightingStyle.Soft
	Lighting.PrioritizeLightingQuality=true
	Lighting.ClockTime=15.4
	Lighting.GeographicLatitude=22.57
	Lighting.Brightness=2.3
	Lighting.ExposureCompensation=0.12
	Lighting.Ambient=Color3.fromRGB(116,119,128)
	Lighting.OutdoorAmbient=Color3.fromRGB(147,150,154)
	Lighting.EnvironmentDiffuseScale=0.65
	Lighting.EnvironmentSpecularScale=0.35
	for _,v in Lighting:GetChildren() do
		if v:IsA("Atmosphere") then
			v.Density=0.22; v.Offset=0.18; v.Color=Color3.fromRGB(224,230,225); v.Decay=Color3.fromRGB(173,179,166); v.Glare=0.05; v.Haze=1.1
		elseif v:IsA("DepthOfFieldEffect") then v.Enabled=false
		elseif v:IsA("SunRaysEffect") then v.Intensity=0.025
		elseif v:IsA("BloomEffect") then v.Intensity=0.10; v.Size=20; v.Threshold=1.8
		end
	end
	return "Soft afternoon lighting set"
end

return Builder
