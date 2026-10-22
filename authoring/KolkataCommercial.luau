--!strict
-- Edit-only commercial street authoring. Large forms and walkable voids take priority.
local SS=game:GetService("ServerStorage")
local Geometry=game:GetService("GeometryService")
local History=game:GetService("ChangeHistoryService")
local Commercial={}
local IVORY=Color3.fromRGB(239,224,193)
local STONE=Color3.fromRGB(190,175,145)
local DARK=Color3.fromRGB(37,64,65)
local IRON=Color3.fromRGB(49,74,67)
local RED=Color3.fromRGB(153,67,49)
local COPPER=Color3.fromRGB(84,128,115)
local function model(name: string): Model
	local m=Instance.new("Model");m.Name=name;m.WorldPivot=CFrame.identity;m.ModelStreamingMode=Enum.ModelStreamingMode.Atomic;return m
end
local function part(m: Instance,name: string,size: Vector3,cf: CFrame,color: Color3,solid: boolean?,role: string?): Part
	local p=Instance.new("Part");p.Name=name;p.Size=size;p.CFrame=cf;p.Color=color
	p.Material=Enum.Material.SmoothPlastic;p.Anchored=true;p.CanTouch=false;p.CanCollide=solid==true;p.CanQuery=solid==true
	p.CastShadow=solid==true or size.Y>4;p.TopSurface=Enum.SurfaceType.Smooth;p.BottomSurface=Enum.SurfaceType.Smooth
	if role then p:SetAttribute("PaletteRole",role) end
	p.Parent=m;return p
end
local function box(m: Instance,name: string,x: number,y: number,z: number,w: number,h: number,d: number,c: Color3,solid: boolean?,role: string?): Part
	return part(m,name,Vector3.new(w,h,d),CFrame.new(x,y,z),c,solid,role)
end
local function line(m: Instance,a: Vector3,b: Vector3,width: number,color: Color3)
	part(m,"Moulding",Vector3.new(width,width,(b-a).Magnitude),CFrame.lookAt((a+b)/2,b),color,false)
end
local function component(name: string,m: Instance,cf: CFrame,scale: number?): Model
	local p=SS.WorldAuthoring.HeritageKit[name]:Clone() :: Model
	if scale then p:ScaleTo(scale) end
	p:PivotTo(cf);p.Parent=m;return p
end
local function sign(m: Instance,cf: CFrame,w: number,text: string,bg: Color3?)
	local p=part(m,"CommercialName",Vector3.new(w,2.4,0.22),cf,bg or DARK,false)
	local g=Instance.new("SurfaceGui");g.Face=Enum.NormalId.Front;g.CanvasSize=Vector2.new(w*32,90);g.LightInfluence=1;g.MaxDistance=180
	local t=Instance.new("TextLabel");t.Size=UDim2.fromScale(0.96,0.85);t.Position=UDim2.fromScale(0.02,0.075);t.BackgroundTransparency=1
	t.Font=Enum.Font.GothamBold;t.Text=text;t.TextColor3=IVORY;t.TextScaled=true;t.Parent=g;g.Parent=p
end
local function triangle(m: Instance,a: Vector3,b: Vector3,c: Vector3,thickness: number,color: Color3)
	local ab,ac,bc=b-a,c-a,c-b
	if ab:Dot(ab)>ac:Dot(ac) and ab:Dot(ab)>bc:Dot(bc) then c,a=a,c elseif ac:Dot(ac)>bc:Dot(bc) then a,b=b,a end
	ab,ac,bc=b-a,c-a,c-b
	local right=ac:Cross(ab).Unit;local back=bc.Unit;local up=bc:Cross(right).Unit;local h=math.abs(ab:Dot(up))
	for _,v in {{(a+b)/2,right,back,math.abs(ab:Dot(back))},{(a+c)/2,-right,-back,math.abs(ac:Dot(back))}} do
		if (v[4] :: number)>0.01 then
			local p=Instance.new("WedgePart");p.Size=Vector3.new(thickness,h,v[4] :: number);p.CFrame=CFrame.fromMatrix(v[1] :: Vector3,v[2] :: Vector3,up,v[3] :: Vector3)
			p.Anchored=true;p.CanCollide=false;p.CanTouch=false;p.CanQuery=false;p.Color=color;p.Parent=m
		end
	end
end
local function union(m: Model,parent: Instance,name: string,color: Color3,solid: boolean?): Model
	local pieces={}
	for _,v in m:GetChildren() do if v:IsA("BasePart") then table.insert(pieces,v) end end
	local first=table.remove(pieces,1)
	local ok,result=pcall(function()return Geometry:UnionAsync(first,pieces,{SplitApart=false,CollisionFidelity=Enum.CollisionFidelity.Hull})end)
	if not ok then m:Destroy();error(`Cannot author {name}: {result}`) end
	first:Destroy();for _,p in pieces do p:Destroy() end
	for _,p in result do
		p.Name=name;p.Anchored=true;p.CanCollide=solid==true;p.CanQuery=solid==true;p.CanTouch=false;p.Color=color;p.Material=Enum.Material.SmoothPlastic
		p.CastShadow=true;if p:IsA("UnionOperation") then p.UsePartColor=true end;p.Parent=m
	end
	m.Name=name;m.Parent=parent;return m
end
local function polygon(parent: Instance,name: string,x: number,bottom: number,z: number,r: number,h: number,color: Color3,solid: boolean?): Model
	local m=model(name)
	for i=0,7 do
		local a,b=(i+0.5)*math.pi/4,(i+1.5)*math.pi/4
		triangle(m,Vector3.new(x,bottom+h/2,z),Vector3.new(x+math.cos(a)*r,bottom+h/2,z+math.sin(a)*r),Vector3.new(x+math.cos(b)*r,bottom+h/2,z+math.sin(b)*r),h,color)
	end
	local result=union(m,parent,name,color,solid)
	result.WorldPivot=CFrame.new(x,bottom+h/2,z)
	return result
end
local function cupola(parent: Instance,x: number,bottom: number,z: number)
	local m=model("FacetedCopperCupola")
	local profile={{12,0},{11.3,4},{8,9},{3,13},{1,14}}
	for band=1,#profile-1 do for i=0,7 do
		local a,b=(i+0.5)*math.pi/4,(i+1.5)*math.pi/4
		local r1,y1=profile[band][1],bottom+profile[band][2]
		local r2,y2=profile[band+1][1],bottom+profile[band+1][2]
		local p1,p2=Vector3.new(x+math.cos(a)*r1,y1,z+math.sin(a)*r1),Vector3.new(x+math.cos(b)*r1,y1,z+math.sin(b)*r1)
		local p3,p4=Vector3.new(x+math.cos(a)*r2,y2,z+math.sin(a)*r2),Vector3.new(x+math.cos(b)*r2,y2,z+math.sin(b)*r2)
		triangle(m,p1,p2,p3,0.18,COPPER);triangle(m,p2,p4,p3,0.18,COPPER)
	end end
	local result=union(m,parent,"FacetedCopperCupola",COPPER,false)
	result.WorldPivot=CFrame.new(x,bottom,z)
	box(parent,"CupolaFinial",x,bottom+15,z,0.5,2,0.5,STONE,false)
end
local function column(m: Instance,x: number,y: number,z: number,h: number,width: number?)
	local w=width or 1
	local p=part(m,"ClassicalColumn",Vector3.new(h-1,w,w),CFrame.new(x,y+h/2,z)*CFrame.Angles(0,0,math.pi/2),IVORY,false)
	p.Shape=Enum.PartType.Cylinder
	box(m,"ColumnBase",x,y+0.3,z,w+0.6,0.6,w+0.6,IVORY,false)
	box(m,"Capital",x,y+h-0.35,z,w+0.9,0.7,w+0.9,IVORY,false)
end
local function glassWindow(m: Instance,cf: CFrame,w: number,h: number,arched: boolean?)
	local f=model("CommercialWindow")
	box(f,"WindowSurround",0,h/2,0,w+0.7,h+0.5,0.2,IVORY,false)
	box(f,"OpaqueGlazing",0,h/2,-0.18,w,h,0.15,DARK,false)
	box(f,"Mullion",0,h/2,-0.3,0.16,h,0.1,IVORY,false)
	box(f,"Transom",0,h*0.56,-0.3,w,0.16,0.1,IVORY,false)
	if arched then
		component("Fanlight",f,CFrame.new(0,h+0.1,-0.15),w/5.6)
		component("ArchRing",f,CFrame.new(0,h+0.1,-0.35),w/6)
	end
	f:PivotTo(cf);f.Parent=m
end
local function balcony(m: Instance,x: number,y: number,z: number,w: number,d: number)
	box(m,"GallerySlab",x,y,z,w,0.55,d,IVORY,true)
	local n=math.floor(w/5.2)
	for i=1,n do component("IronRailingPanel",m,CFrame.new(x-w/2+(i-0.5)*w/n,y+0.3,z-d/2+0.2),w/n/5.2) end
end
local function cornice(m: Instance,x: number,y: number,z: number,w: number,d: number)
	box(m,"CorniceLower",x,y-0.6,z,w+1,0.5,d+1,IVORY,false)
	box(m,"CorniceCap",x,y,z,w+2,0.7,d+2,IVORY,false)
end
local function sideWindows(m: Instance,x: number,zs: {number},ys: {number},direction: number)
	for _,z in zs do for _,y in ys do
		local pos=Vector3.new(x,y,z)
		glassWindow(m,CFrame.lookAt(pos,pos+Vector3.new(direction,0,0)),5.5,7,true)
	end end
end
local function mirrorX(m: Model)
	-- Components are symmetric around their own local X axis; reflection preserves readable signs.
	for _,p in m:GetChildren() do if p:IsA("PVInstance") then
		local cf=p:GetPivot();local pos,rt,up,bk=cf.Position,cf.RightVector,cf.UpVector,cf.ZVector
		p:PivotTo(CFrame.fromMatrix(Vector3.new(-pos.X,pos.Y,pos.Z),Vector3.new(rt.X,-rt.Y,-rt.Z),Vector3.new(-up.X,up.Y,up.Z),Vector3.new(-bk.X,bk.Y,bk.Z)))
	end end
end
local function pitchedRoof(m: Instance,x: number,y: number,z: number,w: number,d: number,rise: number,color: Color3)
	local half=w/2;local angle=math.atan(rise/half);local length=math.sqrt(half*half+rise*rise)
	for side=-1,1,2 do
		part(m,"PitchedRoofPlane",Vector3.new(length+0.6,0.5,d+1.5),CFrame.new(x+side*half/2,y+rise/2,z)*CFrame.Angles(0,0,-side*angle),color,false)
	end
	local g=model("Gable")
	for _,face in {-d/2,d/2} do triangle(g,Vector3.new(x-half,y,z+face),Vector3.new(x+half,y,z+face),Vector3.new(x,y+rise,z+face),0.25,IVORY) end
	local ends=union(g,m,"GableEnds",IVORY,false)
	ends.WorldPivot=CFrame.new(x,y,z)
	box(m,"Ridge",x,y+rise+0.2,z,0.5,0.5,d+2,color,false)
end
local function emporium(): Model
	local m=model("CornerEmporium")
	local wall=Color3.fromRGB(219,205,173)
	-- An offset long wing meets a polygonal corner pavilion; the arcade has real depth.
	box(m,"LongRearWing",-6,22.5,8,76,45,34,wall,true,"Wall")
	box(m,"UpperFrontWing",-6,30,-14,76,30,10,wall,true,"Wall")
	box(m,"ArcadeFloor",-6,0.22,-17,78,0.44,16,STONE,true)
	for _,x in {-38,-25,-12,1,14} do
		glassWindow(m,CFrame.new(x,0.9,-9.2),8,8,true)
		for _,y in {16,31} do glassWindow(m,CFrame.new(x,y,-19.2),6.5,8,true) end
	end
	for _,x in {-44,-31,-18,-5,8,21} do column(m,x,0.5,-24,8.9,1.2) end
	for _,x in {-37.5,-24.5,-11.5,1.5,14.5} do component("ArchRing",m,CFrame.new(x,9.1,-24),2) end
	for _,y in {15,30} do balcony(m,-6,y,-22,77,6) end
	for _,x in {-43,21} do column(m,x,15.5,-24,28.5,1.25) end
	cornice(m,-6,45.4,2,78,46)
	box(m,"SetbackRoofRoom",-14,48,12,38,5,19,wall,true,"Wall")
	cornice(m,-14,50.6,12,38,19)
	polygon(m,"OctagonalCornerPavilion",31,0,-11,13,53,wall,true)
	for _,y in {15,30,45,53} do polygon(m,"PavilionCornice",31,y,-11,14,0.65,IVORY,false) end
	for f=0,2 do for _,angle in {-math.pi/2,-math.pi/4,0} do
		local outward=Vector3.new(math.cos(angle),0,math.sin(angle))
		local pos=Vector3.new(31,f*15+1,-11)+outward*12.15
		glassWindow(m,CFrame.lookAt(pos,pos+outward),5.8,8,true)
	end end
	polygon(m,"CupolaDrum",31,53.5,-11,10,8,IVORY,false)
	for _,angle in {-math.pi/2,-math.pi/4,0} do
		local outward=Vector3.new(math.cos(angle),0,math.sin(angle))
		local pos=Vector3.new(31,54.3,-11)+outward*9.4
		glassWindow(m,CFrame.lookAt(pos,pos+outward),3.4,4,true)
	end
	cupola(m,31,61.5,-11)
	-- A smaller stepped pavilion balances the opposite roof, without duplicating the tower.
	box(m,"EndPavilion",-35,48,-8,15,6,18,wall,true,"Wall")
	pitchedRoof(m,-35,51,-8,17,20,5,COPPER)
	sign(m,CFrame.new(-9,13.8,-24.4),54,"BENGAL EMPORIUM")
	sideWindows(m,-44.2,{0,13,23},{1,16,31},-1)
	mirrorX(m)
	m:SetAttribute("WidthStuds",91);return m
end
local function exchange(): Model
	local m=model("CourtyardExchange")
	local wall=Color3.fromRGB(164,75,55)
	for _,x in {-39,39} do
		box(m,"OfficeWing",x,21,5,32,42,46,wall,true,"Wall")
		box(m,"ColonnadeFloor",x,0.2,-23,33,0.4,10,STONE,true)
		for _,offset in {-10,0,10} do for _,y in {1,15.5,29.5} do glassWindow(m,CFrame.new(x+offset,y,-18.2),5.8,7.5,true) end end
		for _,offset in {-14,-5,5,14} do column(m,x+offset,0.5,-27,11.5,1) end
		cornice(m,x,14,-22,33,11)
		cornice(m,x,42.5,5,33,46)
		box(m,"RoofShoulder",x,44,7,21,3,29,wall,true,"Wall")
	end
	box(m,"RearWing",0,21,19,46,42,18,wall,true,"Wall")
	box(m,"OpenCourtyardFloor",0,0.18,-7,46,0.36,34,Color3.fromRGB(193,172,139),true)
	for _,x in {-15,-5,5,15} do for _,y in {1,15.5,29.5} do glassWindow(m,CFrame.new(x,y,9.8),5.5,7.5,true) end end
	-- The entrance bridge encloses the upper floor, leaving a generous open gateway below.
	box(m,"EntranceBridge",0,33,-20,46,18,14,wall,true,"Wall")
	for _,x in {-16,16} do column(m,x,0.6,-27.3,23,1.7) end
	component("ArchRing",m,CFrame.new(0,13.5,-27.3),3.5)
	for _,x in {-13,0,13} do glassWindow(m,CFrame.new(x,27,-27.2),6,7.5,true) end
	cornice(m,0,42.6,-20,48,15)
	local pediment=model("CentralPediment")
	triangle(pediment,Vector3.new(-21,43,-27),Vector3.new(21,43,-27),Vector3.new(0,51,-27),0.65,IVORY)
	union(pediment,m,"CentralPediment",IVORY,false)
	line(m,Vector3.new(-22,43,-27.5),Vector3.new(0,51.5,-27.5),0.6,IVORY)
	line(m,Vector3.new(0,51.5,-27.5),Vector3.new(22,43,-27.5),0.6,IVORY)
	sign(m,CFrame.new(0,24.5,-27.6),31,"BENGAL EXCHANGE")
	box(m,"CourtyardPlanter",0,0.8,-2,8,1.5,8,RED,true)
	local tree=SS.WorldAuthoring.KolkataKit.ShadeTree:Clone() :: Model;tree:ScaleTo(0.65);tree:PivotTo(CFrame.new(0,1,-2));tree.Parent=m
	for side=-1,1,2 do
		sideWindows(m,side*55.2,{-7,6,19},{1,15.5,29.5},side)
		sideWindows(m,side*22.8,{-5,9},{1,15.5,29.5},-side)
		for _,y in {14.1,28.1} do cornice(m,side*39,y,5,32,46) end
		for _,offset in {-14.5,14.5} do column(m,side*39+offset,14.5,-18.7,27,1.2) end
		for x=-52,-26,3 do
			box(m,"TerraceBaluster",side*math.abs(x),44.2,-18.8,0.45,2.2,0.65,IVORY,false)
		end
		box(m,"TerraceRail",side*39,45.4,-18.8,33,0.4,1,IVORY,false)
	end
	m:SetAttribute("WidthStuds",112);return m
end
local function market(): Model
	local m=model("MarketHall")
	local wall=Color3.fromRGB(207,168,113)
	for _,x in {-33,33} do
		box(m,"MarketWing",x,13,4,34,26,46,wall,true,"Wall")
		box(m,"ArcadeFloor",x,0.2,-23,35,0.4,10,STONE,true)
		for _,offset in {-11,0,11} do
			glassWindow(m,CFrame.new(x+offset,1,-19.2),7.5,7.5,true)
			glassWindow(m,CFrame.new(x+offset,15,-19.2),5.5,6.3,false)
		end
		for _,offset in {-16,-5.5,5.5,16} do column(m,x+offset,0.5,-27,8.3,1) end
		for _,offset in {-10.7,0,10.7} do component("ArchRing",m,CFrame.new(x+offset,8.5,-27),1.6) end
		cornice(m,x,13.7,-23,35,10)
		pitchedRoof(m,x,26.4,4,36,48,9,RED)
	end
	-- Covered central lane is open at both ends, connecting the street to the residential lane.
	box(m,"ThroughPassage",0,0.2,0,24,0.4,61,Color3.fromRGB(182,170,145),true)
	for _,x in {-12,12} do for _,z in {-27,-9,9,27} do column(m,x,0.5,z,17,1.1) end end
	box(m,"PassageCanopy",0,17.5,0,26,0.5,61,IVORY,false)
	pitchedRoof(m,0,17.8,0,27,62,9,COPPER)
	component("ArchRing",m,CFrame.new(0,9.3,-31.4),2.4)
	sign(m,CFrame.new(0,19.3,-31.5),23,"PARA MARKET HALL")
	for side=-1,1,2 do sideWindows(m,side*50.2,{-8,8,21},{14.5},side) end
	m:SetAttribute("WidthStuds",104);return m
end
local function infill(name: string,w: number,style: number): Model
	local m=model(name)
	local wall=if style==1 then Color3.fromRGB(160,183,172) elseif style==2 then Color3.fromRGB(198,163,124) else Color3.fromRGB(178,188,187)
	local h=if style==1 then 27 else 36
	-- Offset wings, a recessed shopfront and a roof setback keep the smaller commercial plots varied.
	box(m,"RearCommercialWing",0,h/2,7,w,h,36,wall,true,"Wall")
	box(m,"LeftFrontReturn",-w/2+5,h/2,-15,10,h,9,wall,true,"Wall")
	box(m,"ShopWalkway",0,0.2,-20,w,0.4,17,STONE,true)
	local n=math.max(2,math.floor(w/15))
	for i=1,n do
		local x=-w/2+(i-0.5)*w/n
		glassWindow(m,CFrame.new(x,0.8,-11.2),w/n-3,8,false)
		for y=15,h-5,11 do glassWindow(m,CFrame.new(x,y,-11.2),w/n-4,6,false) end
		box(m,"CanopySupport",x-w/n/2+0.5,5.6,-26,0.4,11,0.4,IRON,false)
		local title=if i%3==1 then "BOOKS & STATIONERY" elseif i%3==2 then "BENGAL SWEETS" else "TEXTILES" 
		sign(m,CFrame.new(x,10.3,-25.8),w/n-0.5,title,if i%2==0 then RED else DARK)
	end
	box(m,"ContinuousCanopy",0,11.8,-20,w+1,0.5,13,IVORY,false)
	cornice(m,0,h+0.5,5,w+1,40)
	box(m,"SetbackOfficeFloor",w*0.12,h+3.8,10,w*0.65,6,24,wall,true,"Wall")
	for i=1,n-1 do glassWindow(m,CFrame.new(-w*0.25+i*w*0.5/n,h+1.4,-2.2),5,4,false) end
	if style==2 then pitchedRoof(m,-w*0.2,h+0.9,5,w*0.42,42,7,RED) end
	if style==3 then
		box(m,"StairPavilion",w/2-7,h+6,-9,13,11,15,wall,true,"Wall")
		cornice(m,w/2-7,h+11.8,-9,14,16)
	end
	m:SetAttribute("WidthStuds",w);return m
end
function Commercial.createKit()
	local a=SS.WorldAuthoring
	assert(not a:FindFirstChild("CommercialKit"),"Commercial kit exists")
	local kit=Instance.new("Folder");kit.Name="CommercialKit";kit.Parent=a
	for _,fn in {emporium,exchange,market} do
		local m=fn();m:SetAttribute("Use","Commercial");m:SetAttribute("ArchitectureType",m.Name);m:SetAttribute("AssetId","commercial."..m.Name)
		box(m,"CommercialForecourt",0,0.05,-28,(m:GetAttribute("WidthStuds") :: number)-1,0.3,10,STONE,true)
		m.Parent=kit;task.wait()
	end
	for _,v in {{"BookArcade",110,1},{"RetailCourt",88,3},{"TextileHouse",104,2},{"OfficeCorner",58,3},{"PrintHouse",58,2}} do
		local m=infill(v[1] :: string,v[2] :: number,v[3] :: number);m:SetAttribute("Use","Commercial");m:SetAttribute("ArchitectureType",v[1]);m:SetAttribute("AssetId","commercial."..(v[1] :: string))
		box(m,"CommercialForecourt",0,0.05,-28,(v[2] :: number)-1,0.3,10,STONE,true)
		m.Parent=kit;task.wait()
	end
	return "Three large heritage types and five commercial infill templates built"
end
function Commercial.placeStreet()
	local a=SS.WorldAuthoring
	local para=workspace.World.Cities.Kolkata.Districts.Para01
	local recording=History:TryBeginRecording("Kolkata - commercial main street")
	local archive=Instance.new("Folder");archive.Name="TownhouseStreetArchive";archive.Parent=a
	for _,b in para.Buildings:GetChildren() do
		local i=tonumber(b.Name:match("^Building_(%d+)_"))
		if i and i<=14 then
			b.Parent=archive
			local d=para.StreetFurniture:FindFirstChild(`BuildingDetails_{i}`);if d then d.Parent=archive end
		else b:SetAttribute("Use","Residential") end
	end
	local layout={{"CornerEmporium",-178,-63,180},{"BookArcade",-52,-63,180},{"MarketHall",94,-63,180},{"OfficeCorner",194,-63,180},{"RetailCourt",-178,63,0},{"CourtyardExchange",-52,63,0},{"TextileHouse",94,63,0},{"PrintHouse",194,63,0}}
	for _,v in layout do
		local m=a.CommercialKit[v[1] :: string]:Clone() :: Model
		m:SetAttribute("LocationId","kolkata.para01."..string.lower(v[1] :: string));m:SetAttribute("AuthoringVersion",3)
		m:PivotTo(CFrame.new(v[2] :: number,0.4,v[3] :: number)*CFrame.Angles(0,math.rad(v[4] :: number),0));m.Parent=para.Buildings;task.wait()
	end
	-- Keep the four Generic 1.0 heritage types available in the residential lanes.
	local architecture=require(a.KolkataArchitecture)
	for _,v in {{17,"RedGalleryHouse",Color3.fromRGB(166,85,62)},{18,"CornerTownhouse",Color3.fromRGB(213,179,130)}} do
		for _,b in para.Buildings:GetChildren() do
			if b.Name:match("^Building_"..string.format("%02d",v[1]).."_") then
				local replacement=architecture.place(v[2],para.Buildings,b:GetPivot(),{wall=v[3]},b:GetAttribute("LocationId"));replacement.Name=string.format("Building_%02d_%s",v[1],v[2]);replacement:SetAttribute("Use","Residential");b.Parent=archive
				local d=para.StreetFurniture:FindFirstChild(`BuildingDetails_{v[1]}`);if d then d.Parent=archive end
			end
		end
	end
	if recording then History:FinishRecording(recording,Enum.FinishRecordingOperation.Commit) end
	return "Main road commercial; residential heritage kit retained in lanes"
end
function Commercial.expandNeighbourhood()
	local para=workspace.World.Cities.Kolkata.Districts.Para01
	assert(not para.Streets:FindFirstChild("ResidentialLoop"),"Residential extension exists")
	local m=model("ResidentialLoop")
	local road=Color3.fromRGB(145,143,126)
	for _,z in {-207,195} do box(m,"BackLane",0,0.03,z,542,0.3,16,road,true) end
	for _,x in {-264,264} do box(m,"SideGully",x,0.03,-6,14,0.3,418,road,true) end
	box(m,"CrossStreetExtension",24,-0.13,-215,20,0.26,34,Color3.fromRGB(63,72,79),true)
	m.Parent=para.Streets
	local a=SS.WorldAuthoring
	local layout={{"MintResidence",-195,-239,180},{"CoralResidence",-146,-239,180},{"BlueResidence",-78,-239,180},{"OchreResidence",-35,-239,180},{"MintResidence",-195,227,0},{"CoralResidence",106,227,0}}
	for i,v in layout do
		local house=a.KolkataKit[v[1] :: string]:Clone() :: Model;house.Name=`ResidentialExtension_{i}`;house:SetAttribute("Use","Residential");house:SetAttribute("LocationId",`kolkata.para01.extension.{i}`)
		local cf=CFrame.new(v[2] :: number,0.4,v[3] :: number)*CFrame.Angles(0,math.rad(v[4] :: number),0)
		house:PivotTo(cf);house.Parent=para.Buildings
		local path=model(`FrontPath_{i}`);box(path,"StoopPath",0,0.03,-23,8,0.3,13,STONE,true);path:PivotTo(cf);path.Parent=para.Streets
		task.wait()
	end
	for _,v in {{-251,-185},{247,-177},{-248,176},{244,172},{-102,-207},{146,195}} do
		local t=a.KolkataKit.ShadeTree:Clone() :: Model;t:PivotTo(CFrame.new(v[1],0.4,v[2]));t.Parent=para.Vegetation
	end
	return "Residential loop expanded with six houses and connected side gullies"
end
return Commercial
