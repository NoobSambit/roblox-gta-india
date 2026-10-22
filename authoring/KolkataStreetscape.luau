--!strict
-- Static streetscape and lighting authoring. No runtime world-generation loop.
local SS=game:GetService("ServerStorage")
local Lighting=game:GetService("Lighting")
local Geometry=game:GetService("GeometryService")
local History=game:GetService("ChangeHistoryService")
local Streetscape={}
local IVORY=Color3.fromRGB(237,222,191)
local BLUE=Color3.fromRGB(65,121,154)
local RED=Color3.fromRGB(153,69,49)
local WOOD=Color3.fromRGB(114,77,47)
local GREEN=Color3.fromRGB(49,94,71)
local STONE=Color3.fromRGB(178,162,135)
local DARK=Color3.fromRGB(45,64,62)
local function model(name: string): Model
	local m=Instance.new("Model");m.Name=name;m.WorldPivot=CFrame.identity;m.ModelStreamingMode=Enum.ModelStreamingMode.Atomic;return m
end
local function box(m: Instance,name: string,x: number,y: number,z: number,w: number,h: number,d: number,c: Color3,solid: boolean?): Part
	local p=Instance.new("Part");p.Name=name;p.Size=Vector3.new(w,h,d);p.CFrame=CFrame.new(x,y,z);p.Color=c;p.Material=Enum.Material.SmoothPlastic
	p.Anchored=true;p.CanTouch=false;p.CanCollide=solid==true;p.CanQuery=solid==true;p.CastShadow=solid==true or h>4
	p.TopSurface=Enum.SurfaceType.Smooth;p.BottomSurface=Enum.SurfaceType.Smooth;p.Parent=m;return p
end
local function rod(m: Instance,name: string,a: Vector3,b: Vector3,width: number,c: Color3,solid: boolean?)
	local p=box(m,name,0,0,0,width,width,(b-a).Magnitude,c,solid);p.CFrame=CFrame.lookAt((a+b)/2,b);return p
end
local function cylinder(m: Instance,name: string,x: number,y: number,z: number,r: number,h: number,c: Color3,solid: boolean?)
	local p=box(m,name,x,y,z,h,r*2,r*2,c,solid);p.Shape=Enum.PartType.Cylinder;p.CFrame*=CFrame.Angles(0,0,math.pi/2);return p
end
local function sign(m: Instance,name: string,cf: CFrame,w: number,h: number,text: string,bg: Color3?,fg: Color3?)
	local p=box(m,name,0,0,0,w,h,0.18,bg or BLUE,false);p.CFrame=cf
	local g=Instance.new("SurfaceGui");g.Name="Lettering";g.Face=Enum.NormalId.Front;g.CanvasSize=Vector2.new(w*45,h*45);g.LightInfluence=1;g.MaxDistance=100
	local t=Instance.new("TextLabel");t.Size=UDim2.fromScale(0.94,0.88);t.Position=UDim2.fromScale(0.03,0.06);t.BackgroundTransparency=1;t.Font=Enum.Font.GothamBold
	t.Text=text;t.TextColor3=fg or IVORY;t.TextScaled=true;t.Parent=g;g.Parent=p
end
local function finish(m: Model,parent: Instance,cf: CFrame,id: string)
	m:SetAttribute("AssetId",id);m:SetAttribute("AuthoringVersion",6);m:PivotTo(cf);m.Parent=parent;return m
end
local function combine(m: Model)
	local list={};for _,p in m:GetChildren() do if p:IsA("BasePart") then table.insert(list,p) end end
	local first=table.remove(list,1)
	local ok,parts=pcall(function()return Geometry:UnionAsync(first,list,{SplitApart=false,CollisionFidelity=Enum.CollisionFidelity.Box})end)
	if not ok then error(parts) end
	first:Destroy();for _,p in list do p:Destroy() end
	for _,p in parts do p.Name="IronOrnament";p.Anchored=true;p.CanTouch=false;p.CanCollide=false;p.CanQuery=false;p.CastShadow=false;if p:IsA("UnionOperation") then p.UsePartColor=true end;p.Color=IVORY;p.Parent=m end
end
local function railing(): Model
	local m=model("KolkataFootpathRailing")
	for _,x in {-3,3} do
		box(m,"BluePost",x,1.7,0,0.28,3.4,0.28,BLUE,true)
		local cap=box(m,"WhiteFinial",x,3.5,0,0.45,0.45,0.45,IVORY,false);cap.Shape=Enum.PartType.Ball
	end
	for _,y in {0.45,3.1} do box(m,"WhiteRail",0,y,0,6,0.17,0.17,IVORY,true) end
	local ornament=model("RailingMedallion")
	for _,x in {-1.7,0,1.7} do box(ornament,"Upright",x,1.75,0,0.1,2.6,0.1,IVORY,false) end
	for i=0,7 do
		local a,b=i*math.pi/4,(i+1)*math.pi/4
		rod(ornament,"Hoop",Vector3.new(math.cos(a)*0.7,1.75+math.sin(a)*0.7,0),Vector3.new(math.cos(b)*0.7,1.75+math.sin(b)*0.7,0),0.1,IVORY,false)
	end
	combine(ornament);ornament.Parent=m;return m
end
local function lamp(): Model
	local m=model("GullyWallLamp")
	box(m,"WallBracket",0,0,0,0.45,1.1,0.3,DARK,false)
	rod(m,"LampArm",Vector3.new(0,0.1,-0.1),Vector3.new(0,0.6,-1.4),0.13,DARK,false)
	box(m,"LanternTop",0,0.5,-1.4,1,0.2,1,DARK,false)
	local glass=box(m,"WarmLantern",0,0.1,-1.4,0.7,0.7,0.7,Color3.fromRGB(255,210,139),false);glass.Material=Enum.Material.Neon
	box(m,"LanternBase",0,-0.3,-1.4,0.9,0.15,0.9,DARK,false)
	local light=Instance.new("PointLight");light.Name="PracticalLight";light.Color=Color3.fromRGB(255,207,143);light.Range=13;light.Brightness=0.75;light.Shadows=false;light.Parent=glass
	return m
end
local function planter(): Model
	local m=model("TerracottaGardenPot")
	cylinder(m,"Pot",0,0.7,0,0.95,1.4,Color3.fromRGB(179,94,54),true)
	cylinder(m,"Rim",0,1.4,0,1.05,0.2,Color3.fromRGB(196,112,67),false)
	box(m,"Stem",0,2.5,0,0.18,2.5,0.18,GREEN,false)
	for i=0,4 do
		local angle=i*math.pi*0.4
		local leaf=box(m,"BroadLeaf",0,0,0,0.18,1.2,3.8,if i%2==0 then GREEN else Color3.fromRGB(81,129,78),false)
		leaf.Shape=Enum.PartType.Ball;leaf.CFrame=CFrame.new(math.sin(angle)*0.8,3.2+i*0.12,math.cos(angle)*0.8)*CFrame.Angles(math.rad(-24),angle,math.rad(13))
	end
	return m
end
local function produce(): Model
	local m=model("FixedProduceCounter")
	box(m,"Counter",0,2.7,0,10,0.35,3.8,WOOD,true)
	for _,x in {-4,4} do box(m,"CounterLeg",x,1.3,0,0.5,2.6,3,WOOD,true) end
	for _,x in {-4.7,4.7} do box(m,"BambooPost",x,3.6,1,0.22,7.2,0.22,WOOD,true) end
	for i=0,4 do box(m,"StripedCanopy",-4+i*2,7.1,0,1.98,0.2,5,if i%2==0 then RED else IVORY,false) end
	for _,x in {-3.2,0,3.2} do
		box(m,"ProduceTray",x,2.95,0,2.7,0.3,3,Color3.fromRGB(126,88,50),false)
		for i=1,5 do
			local p=box(m,"Produce",x-0.8+(i%3)*0.8,3.4,-0.8+math.floor(i/3)*1.2,0.8,0.8,0.8,if x==0 then Color3.fromRGB(231,171,52) elseif x<0 then Color3.fromRGB(121,151,64) else Color3.fromRGB(189,72,49),false);p.Shape=Enum.PartType.Ball
		end
	end
	sign(m,"ProduceSign",CFrame.new(0,5.8,-2.5),8.5,1.3,"FRESH FRUIT  /  DAILY",GREEN)
	return m
end
local function utility(): Model
	local m=model("MunicipalUtilityCabinet")
	box(m,"ConcretePlinth",0,0.25,0,3.8,0.5,2.5,STONE,true)
	box(m,"Cabinet",0,2.1,0,3.1,3.7,1.8,Color3.fromRGB(104,127,117),true)
	box(m,"DoorSeam",0,2.1,-0.92,0.05,3.5,0.05,DARK,false)
	for _,x in {-0.8,0.8} do for y=2.4,3.3,0.3 do box(m,"Vent",x,y,-0.95,1.15,0.08,0.08,DARK,false) end end
	return m
end
local function shopDisplay(): Model
	local m=model("ArcadeBookDisplay")
	box(m,"ShelfBack",0,3.2,0,7,5.4,0.3,WOOD,false)
	for _,y in {0.6,2,3.4,4.8} do
		box(m,"Shelf",0,y,-0.7,7,0.2,1.7,WOOD,false)
		for i=1,6 do box(m,"BookStack",-3.6+i,y+0.5,-0.8,0.7,0.8,1,if i%3==0 then BLUE elseif i%3==1 then RED else IVORY,false) end
	end
	return m
end
function Streetscape.createKit()
	local a=SS.WorldAuthoring
	assert(not a:FindFirstChild("StreetscapeKit"),"Streetscape kit already exists")
	local kit=Instance.new("Folder");kit.Name="StreetscapeKit";kit.Parent=a
	for _,fn in {railing,lamp,planter,produce,utility,shopDisplay} do local m=fn();m.Parent=kit;task.wait() end
	return "Six original streetscape templates authored"
end
function Streetscape.gullies()
	local para=workspace.World.Cities.Kolkata.Districts.Para01
	local a=SS.WorldAuthoring
	local kit=a.StreetscapeKit
	local archive=Instance.new("Folder");archive.Name="ResidentialShopRevision";archive.Parent=a
	for _,v in {{16,"Provisions","PARA PROVISIONS"},{22,"SweetShop","SWEETS & SNACKS"},{24,"Bookshop","PARA TAILORS"}} do
		for _,b in para.Buildings:GetChildren() do if b.Name:match("^Building_"..string.format("%02d",v[1]).."_") then
			local m=a.KolkataKit[v[2]]:Clone() :: Model;m.Name=string.format("Building_%02d_LaneShop",v[1]);m:SetAttribute("Use","ResidentialWithShop");m:SetAttribute("LocationId",b:GetAttribute("LocationId"));m:SetAttribute("WidthStuds",m:GetAttribute("WidthStuds"))
			m.ShopName.Lettering.TextLabel.Text=v[3];m:PivotTo(b:GetPivot());m.Parent=para.Buildings;b.Parent=archive
			local d=para.StreetFurniture:FindFirstChild(`BuildingDetails_{v[1]}`);if d then d.Parent=archive end
		end end
	end
	for _,b in para.Buildings:GetChildren() do if b:GetAttribute("Use")~="Commercial" then
		local cf=(b :: Model):GetPivot()
		local width=(b:GetAttribute("WidthStuds") or 34) :: number
		local kind=b:GetAttribute("ArchitectureType")
		local front=if kind and kind~="ModernApartment" then -12 else -16
		local loc=cf.Position
		local isCourt=loc.Z< -165 and loc.Z> -195 and loc.X>30
		local extension=b.Name:match("^ResidentialExtension")~=nil
		local detail=model(b.Name.."_LaneLife")
		if not isCourt then
			local depth=if extension then 8 else 16
			box(detail,"BrickForecourt",0,0.03,-16-depth/2,width+1,0.3,depth,Color3.fromRGB(173,151,124),true)
			for _,x in {-width/2,width/2} do
				box(detail,"LowCompoundWall",x,1.15,-16-depth/2,0.6,2.3,depth-0.5,Color3.fromRGB(176,130,98),true)
				box(detail,"WallCoping",x,2.4,-16-depth/2,0.9,0.22,depth,RED,false)
			end
			if b:GetAttribute("Use")=="Residential" then
				box(detail,"RedOxideRoak",width/2-6,0.8,-19,8,1.2,2.5,RED,true)
			end
		end
		local lampClone=kit.GullyWallLamp:Clone() :: Model;lampClone:PivotTo(CFrame.new(-width/2+2.5,8.8,front-0.4));lampClone.Parent=detail
		local plant=kit.TerracottaGardenPot:Clone() :: Model;plant:ScaleTo(0.7);plant:PivotTo(CFrame.new(width/2-2,0.2,-18.5));plant.Parent=detail
		sign(detail,"HouseNumber",CFrame.new(-4,5.8,front-0.35),1.7,1.3,"P / "..(b.Name:match("%d+") or "1"),BLUE)
		for i=1,3 do box(detail,"PlasterPatch",width/2-2-i*0.3,0.7+i*0.35,front-0.08,2.8-i*0.5,0.3,0.06,Color3.fromRGB(183,144,110),false) end
		finish(detail,para.StreetFurniture,cf,"gully.frontage")
		task.wait()
	end end
	local function place(template: string,parent: Instance,cf: CFrame,id: string?)
		local m=kit[template]:Clone() :: Model;return finish(m,parent,cf,id or template)
	end
	place("FixedProduceCounter",para.StreetFurniture,CFrame.new(-180,0.5,-122)*CFrame.Angles(0,math.pi,0),"gully.produce.north")
	place("FixedProduceCounter",para.StreetFurniture,CFrame.new(-76,0.5,122),"gully.produce.south")
	for _,v in {{-227,-110},{168,118},{-102,-204},{205,194}} do place("MunicipalUtilityCabinet",para.Utilities,CFrame.new(v[1],0.4,v[2])) end
	for _,v in {{-104,-120,0},{-90,120,180},{53,-151,90},{-27,-224,0}} do
		local bench=a.KolkataKit.AddaBench:Clone() :: Model;finish(bench,para.StreetFurniture,CFrame.new(v[1],0.4,v[2])*CFrame.Angles(0,math.rad(v[3]),0),"gully.addaBench")
	end
	for _,v in {{-122,-87,90},{151,89,-90},{38,-204,90},{-259,35,90}} do
		local plaque=model("LaneName")
		cylinder(plaque,"SignPole",0,3.4,0,0.13,6.8,GREEN,true)
		sign(plaque,"LanePlate",CFrame.new(0,6,-0.1),8,1.7,"PARA LANE",BLUE)
		finish(plaque,para.StreetFurniture,CFrame.new(v[1],0.4,v[2])*CFrame.Angles(0,math.rad(v[3]),0),"gully.nameplate")
	end
	-- Back-lane electrical infrastructure stays out of clear walking and driving routes.
	for _,z in {-115,115} do
		local xs=if z<0 then {-225,-110,40,166,225} else {-225,10,166,225}
		local wire=model("BackLaneUtilitySpan")
		for _,x in xs do local p=a.KolkataKit.ElectricalPole:Clone() :: Model;finish(p,para.Utilities,CFrame.new(x,0.4,z),"gully.utilityPole") end
		for i=1,#xs-1 do
			local previous=Vector3.new(xs[i],25.8,z)
			for step=1,5 do local t=step/5;local nextPoint=Vector3.new(xs[i]+(xs[i+1]-xs[i])*t,25.8-1.8*4*t*(1-t),z);rod(wire,"Cable",previous,nextPoint,0.055,DARK,false);previous=nextPoint end
		end
		finish(wire,para.Utilities,CFrame.identity,"gully.utilitySpan")
	end
	-- Tiled neighbourhood corners, a community board and low courtyard boundaries.
	local court=model("CourtyardEdges")
	box(court,"BrickBoundary",147,1.4,-147,0.6,2.8,25,Color3.fromRGB(183,143,109),true)
	box(court,"RedCoping",147,2.9,-147,0.9,0.25,25.5,RED,false)
	box(court,"BrickBoundary",39,1.4,-147,0.6,2.8,25,Color3.fromRGB(183,143,109),true)
	box(court,"RedCoping",39,2.9,-147,0.9,0.25,25.5,RED,false)
	sign(court,"CommunityBoard",CFrame.new(132,6,-163.2),9,4,"PARA NOTICEBOARD\nKEEP OUR LANES CLEAN",GREEN)
	finish(court,para.Courtyard,CFrame.identity,"courtyard.boundaries")
	for _,v in {{-233,-185},{-102,-179},{162,-199},{232,150},{-226,178},{9,165},{141,-183},{-102,177}} do
		local t=a.KolkataKit.ShadeTree:Clone() :: Model;t:ScaleTo(0.75);finish(t,para.Vegetation,CFrame.new(v[1],0.4,v[2]),"gully.shadeTree")
	end
	return "Residential forecourts, three ground-floor shops and local street life built"
end
function Streetscape.mainStreet()
	local para=workspace.World.Cities.Kolkata.Districts.Para01
	local a=SS.WorldAuthoring
	local kit=a.StreetscapeKit
	-- Twenty-four-stud runs leave frequent six-stud openings; crosswalks and gullies stay open.
	for side=-1,1,2 do
		for _,start in {-221,-191,-161,-107,-77,-47,57,87,117,171,201} do
			for n=0,3 do
				local m=kit.KolkataFootpathRailing:Clone() :: Model
				finish(m,para.StreetFurniture,CFrame.new(start+n*6,0.4,side*21),"main.footpathRailing")
			end
		end
	end
	-- Populate the covered commercial walks, leaving the outer arcade aisle clear.
	for _,v in {{"BookArcade",-33,-13},{"BookArcade",5,-13},{"TextileHouse",-28,-13},{"PrintHouse",10,-13},{"RetailCourt",-15,-13}} do
		local b=para.Buildings[v[1]] :: Model
		local display=kit.ArcadeBookDisplay:Clone() :: Model
		finish(display,para.StreetFurniture,b:GetPivot()*CFrame.new(v[2],0.3,v[3]),"commercial.shopDisplay")
	end
	for _,v in {{"MarketHall",-33,-22},{"RetailCourt",23,-20}} do
		local b=para.Buildings[v[1]] :: Model
		local counter=kit.FixedProduceCounter:Clone() :: Model;counter:ScaleTo(0.8)
		finish(counter,para.StreetFurniture,b:GetPivot()*CFrame.new(v[2],0.4,v[3]),"commercial.marketCounter")
	end
	for _,name in {"CornerEmporium","CourtyardExchange","MarketHall","BookArcade","RetailCourt","TextileHouse","OfficeCorner","PrintHouse"} do
		local b=para.Buildings[name] :: Model
		for side=-1,1,2 do
			local p=kit.TerracottaGardenPot:Clone() :: Model
			finish(p,para.StreetFurniture,b:GetPivot()*CFrame.new(side*((b:GetAttribute("WidthStuds") :: number)/2-3),0.3,-29),"commercial.entrancePlanter")
		end
	end
	-- Curved pavilion gallery rails accent the three-dimensional street corner.
	for _,m in {a.CommercialKit.CornerEmporium,para.Buildings.CornerEmporium} do
		local detail=model("PavilionGalleryRails")
		for _,y in {15.5,30.5,45.5} do
			for i=0,5 do
				local a1,a2=-math.pi+i*math.pi/8,-math.pi+(i+1)*math.pi/8
				local p1,p2=Vector3.new(-31+math.cos(a1)*13.7,y+2.6,-11+math.sin(a1)*13.7),Vector3.new(-31+math.cos(a2)*13.7,y+2.6,-11+math.sin(a2)*13.7)
				rod(detail,"PavilionRail",p1,p2,0.13,IVORY,false)
				rod(detail,"PavilionBaluster",p1-Vector3.new(0,2.6,0),p1,0.12,IVORY,false)
			end
		end
		detail:PivotTo(m:GetPivot());detail.Parent=m
	end
	return "Kolkata footpath rails, commercial displays and pavilion galleries added"
end
function Streetscape.finalDetails()
	local para=workspace.World.Cities.Kolkata.Districts.Para01
	local a=SS.WorldAuthoring
	assert(not para.StreetFurniture:FindFirstChild("FinalStreetDetails"),"Final dressing already exists")
	local root=Instance.new("Folder");root.Name="FinalStreetDetails";root.Parent=para.StreetFurniture
	-- Service elevations matter because players can freely explore the back lanes.
	for _,v in {{"CornerEmporium",6,25.2,76,45},{"BookArcade",0,25.2,110,27},{"RetailCourt",0,25.2,88,36},{"TextileHouse",0,25.2,104,36},{"OfficeCorner",0,25.2,58,36},{"PrintHouse",0,25.2,58,36},{"CourtyardExchange",0,28.2,108,42}} do
		local b=para.Buildings[v[1]] :: Model
		local detail=model(v[1].."_ServiceElevation")
		local count=math.floor(v[4]/12)
		for i=1,count do
			local x=v[2]-v[4]/2+(i-0.5)*v[4]/count
			for y=15,v[5]-5,13 do
				box(detail,"RearWindowFrame",x,y,v[3],5.8,7,0.22,IVORY,false)
				box(detail,"RearWindow",x,y,v[3]+0.18,5.1,6.3,0.16,DARK,false)
				box(detail,"RearWindowMullion",x,y,v[3]+0.3,0.15,6.3,0.1,IVORY,false)
				box(detail,"RearWindowDrip",x,y+3.8,v[3]+0.5,6.4,0.3,1.4,IVORY,false)
			end
		end
		box(detail,"ServiceDoorFrame",v[2],4.7,v[3],6,9.4,0.25,IVORY,false)
		box(detail,"ServiceDoor",v[2],4.4,v[3]+0.2,5.2,8.8,0.18,GREEN,false)
		finish(detail,root,b:GetPivot(),"commercial.serviceElevation")
		local pad=model(v[1].."_UrbanPlot")
		box(pad,"PackedUrbanGround",0,-0.4,0,v[4]+2,0.2,62,Color3.fromRGB(143,137,118),true).Material=Enum.Material.Ground
		finish(pad,para.Ground,CFrame.new(b:GetPivot().Position.X,0,b:GetPivot().Position.Z),"urban.plotSurface")
		task.wait()
	end
	-- Each small shop gets a distinct product display rather than anonymous boxes.
	for _,v in {{16,"Groceries"},{22,"Sweets"},{24,"Cloth"}} do
		local b=para.Buildings[string.format("Building_%02d_LaneShop",v[1])] :: Model
		for _,old in b:GetChildren() do if old.Name=="Goods" then old:Destroy() end end
		local goods=model("LaneShop_"..v[2])
		local x=-(b:GetAttribute("WidthStuds") :: number)/4
		if v[2]=="Sweets" then
			for tray=1,3 do
				local px=x-5+tray*2.5
				box(goods,"SweetTray",px,3.55,-10,2.2,0.14,1.8,IVORY,false)
				for i=1,4 do
					local sweet=box(goods,"Sweets",px-0.6+(i%2)*1.1,3.85,-10.5+math.floor(i/2)*0.55,0.6,0.5,0.6,if tray==2 then Color3.fromRGB(198,132,57) else Color3.fromRGB(239,215,166),false);sweet.Shape=Enum.PartType.Ball
				end
			end
		elseif v[2]=="Cloth" then
			for pile=1,3 do for j=1,4 do box(goods,"FoldedTextile",x-5+pile*2.5,3.4+j*0.25,-10,2,0.23,1.6,if j%3==0 then BLUE elseif j%3==1 then RED else IVORY,false) end end
			rod(goods,"HangingRail",Vector3.new(x-5,6.7,-10),Vector3.new(x+5,6.7,-10),0.08,DARK,false)
			for i=1,4 do box(goods,"HangingFabric",x-5+i*2,5.5,-9.8,1.6,2.2,0.07,if i%2==0 then Color3.fromRGB(200,144,90) else Color3.fromRGB(84,133,126),false) end
		else
			for i=1,6 do box(goods,"ProvisionsTin",x-4+i*1.2,3.9,-10,0.8,1,0.8,if i%2==0 then IVORY else RED,false) end
			for i=1,3 do cylinder(goods,"RiceSack",x-5+i*2,1.5,-8,0.65,2.2,Color3.fromRGB(185,158,111),false) end
		end
		finish(goods,root,b:GetPivot(),"gully.shopDisplay."..v[2])
	end
	local shelter=model("KolkataBusShelter")
	for _,x in {-8,8} do
		box(shelter,"BlueShelterPost",x,4,1.5,0.25,8,0.25,BLUE,true)
		box(shelter,"WhitePostBase",x,0.8,1.5,0.3,1.6,0.3,IVORY,false)
	end
	box(shelter,"Canopy",0,8.1,0,19,0.5,6,BLUE,false)
	box(shelter,"CanopyTrim",0,7.75,-3,19,0.4,0.25,IVORY,false)
	box(shelter,"WindScreen",0,4.5,1.65,17,3.8,0.15,Color3.fromRGB(92,133,128),true)
	local bench=a.KolkataKit.AddaBench:Clone() :: Model;bench:PivotTo(CFrame.new(0,0,0.3));bench.Parent=shelter
	sign(shelter,"StopName",CFrame.new(0,6.8,-0.05),12,1.4,"BUS STOP  /  KOLKATA",BLUE)
	shelter.Parent=a.StreetscapeKit
	for side=-1,1,2 do for _,x in {-240.5,240.5} do
		local paving=model("FootpathExtension")
		box(paving,"Footpath",x,0.2,side*26,31,0.4,12,Color3.fromRGB(174,168,149),true).Material=Enum.Material.Pavement
		for px=-12,12,6 do box(paving,"Curb",x+px,0.27,side*20.22,5.9,0.54,0.6,if px%12==0 then IVORY else BLUE,true) end
		finish(paving,para.Streets,CFrame.identity,"main.footpathExtension")
	end end
	for _,v in {{-240,-28,180},{240,28,0}} do local m=shelter:Clone() :: Model;finish(m,root,CFrame.new(v[1],0.4,v[2])*CFrame.Angles(0,math.rad(v[3]),0),"main.busShelter") end
	for _,m in para.Streets:GetChildren() do
		for _,p in m:GetChildren() do if p:IsA("BasePart") and p.Name=="Footpath" then p.Material=Enum.Material.Pavement end end
	end
	return "Back-lane service facades, distinct shop displays and static bus shelters finished"
end
function Streetscape.atmosphere()
	local para=workspace.World.Cities.Kolkata.Districts.Para01
	Lighting.LightingStyle=Enum.LightingStyle.Soft
	Lighting.PrioritizeLightingQuality=true
	Lighting.ClockTime=16.65;Lighting.GeographicLatitude=22.57
	Lighting.Brightness=2.2;Lighting.ExposureCompensation=0.02
	Lighting.Ambient=Color3.fromRGB(121,111,105);Lighting.OutdoorAmbient=Color3.fromRGB(157,146,128)
	Lighting.ColorShift_Top=Color3.fromRGB(242,197,141);Lighting.ColorShift_Bottom=Color3.fromRGB(115,108,103)
	Lighting.EnvironmentDiffuseScale=0.65;Lighting.EnvironmentSpecularScale=0.24
	local atmosphere=Lighting:FindFirstChildOfClass("Atmosphere") or Instance.new("Atmosphere")
	atmosphere.Name="KolkataAfternoonHaze";atmosphere.Density=0.255;atmosphere.Offset=0.18
	atmosphere.Color=Color3.fromRGB(232,214,185);atmosphere.Decay=Color3.fromRGB(201,175,151)
	atmosphere.Glare=0.09;atmosphere.Haze=1.35;atmosphere.Parent=Lighting
	for _,v in Lighting:GetChildren() do
		if v:IsA("DepthOfFieldEffect") then v.Enabled=false
		elseif v:IsA("SunRaysEffect") then v.Intensity=0.018;v.Spread=0.8
		elseif v:IsA("BloomEffect") then v.Intensity=0.10;v.Size=18;v.Threshold=1.9 end
	end
	local grade=Lighting:FindFirstChild("KolkataWarmGrade") :: ColorCorrectionEffect?
	if not grade then grade=Instance.new("ColorCorrectionEffect");grade.Name="KolkataWarmGrade";grade.Parent=Lighting end
	grade.TintColor=Color3.fromRGB(255,244,225);grade.Contrast=0.055;grade.Saturation=-0.025;grade.Brightness=0.005
	local sky=Lighting:FindFirstChildOfClass("Sky")
	if sky then sky.SunAngularSize=6;sky.MoonAngularSize=9;sky.StarCount=400 end
	-- Warm practical lights and occasional lit displays, with no shadow-casting local lights.
	local windows=0
	for _,v in para:GetDescendants() do
		if v:IsA("Light") then v.Shadows=false;v.Color=Color3.fromRGB(255,209,147)
		elseif v:IsA("BasePart") and v.Name=="Diffuser" then v.Color=Color3.fromRGB(255,215,149)
		elseif v:IsA("BasePart") and v.Name=="OpaqueGlazing" then
			windows+=1
			v.Color=if windows%5==0 then Color3.fromRGB(142,121,86) else Color3.fromRGB(49,74,75)
		end
	end
	return "Curated warm afternoon sky, restrained grading and warm practical lights applied"
end
return Streetscape
