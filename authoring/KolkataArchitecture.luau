--!strict
-- Edit-only heritage kit. Reference vocabulary, original geometry; no copied textures.
local ServerStorage = game:GetService("ServerStorage")
local GeometryService = game:GetService("GeometryService")
local ChangeHistoryService = game:GetService("ChangeHistoryService")
local Architecture = {}
local IVORY=Color3.fromRGB(241,223,188)
local GREEN=Color3.fromRGB(39,83,67)
local IRON=Color3.fromRGB(41,62,58)
local DARK=Color3.fromRGB(31,49,46)
local RED=Color3.fromRGB(153,62,45)
local function model(name: string): Model
	local m=Instance.new("Model")
	m.Name=name
	m.WorldPivot=CFrame.identity
	m.ModelStreamingMode=Enum.ModelStreamingMode.Atomic
	return m
end
local function part(m: Instance, name: string, size: Vector3, cf: CFrame, color: Color3, solid: boolean?, role: string?): Part
	local p=Instance.new("Part")
	p.Name=name;p.Size=size;p.CFrame=cf;p.Color=color
	p.Material=Enum.Material.SmoothPlastic
	p.Anchored=true;p.CanTouch=false;p.CanCollide=solid==true;p.CanQuery=solid==true
	p.CastShadow=solid==true or size.Y>3
	p.TopSurface=Enum.SurfaceType.Smooth;p.BottomSurface=Enum.SurfaceType.Smooth
	if role then p:SetAttribute("PaletteRole",role) end
	p.Parent=m
	return p
end
local function box(m: Instance, name: string,x: number,y: number,z: number,w: number,h: number,d: number,color: Color3,solid: boolean?,role: string?): Part
	return part(m,name,Vector3.new(w,h,d),CFrame.new(x,y,z),color,solid,role)
end
local function rod(m: Instance,name: string,a: Vector3,b: Vector3,width: number,color: Color3,role: string?)
	return part(m,name,Vector3.new(width,width,(b-a).Magnitude),CFrame.lookAt((a+b)/2,b),color,false,role)
end
local function column(m: Instance,x: number,bottom: number,z: number,h: number,paired: boolean?)
	local offsets=if paired then {-0.55,0.55} else {0}
	for _,offset in offsets do
		local shaft=part(m,"ColumnShaft",Vector3.new(h-1.1,0.62,0.62),CFrame.new(x+offset,bottom+h/2,z)*CFrame.Angles(0,0,math.pi/2),IVORY,false,"Trim")
		shaft.Shape=Enum.PartType.Cylinder
		box(m,"ColumnBase",x+offset,bottom+0.3,z,1,0.6,1,IVORY,false,"Trim")
		box(m,"ColumnCapital",x+offset,bottom+h-0.3,z,1.25,0.6,1.2,IVORY,false,"Trim")
	end
end
local function triangle(m: Instance,a: Vector3,b: Vector3,c: Vector3,color: Color3)
	local ab,ac,bc=b-a,c-a,c-b
	if ab:Dot(ab)>ac:Dot(ac) and ab:Dot(ab)>bc:Dot(bc) then c,a=a,c
	elseif ac:Dot(ac)>bc:Dot(bc) then a,b=b,a end
	ab,ac,bc=b-a,c-a,c-b
	local right=ac:Cross(ab).Unit
	local back=bc.Unit
	local up=bc:Cross(right).Unit
	local height=math.abs(ab:Dot(up))
	for _,v in {{(a+b)/2,right,back,math.abs(ab:Dot(back))},{(a+c)/2,-right,-back,math.abs(ac:Dot(back))}} do
		if (v[4] :: number)>0.01 then
			local p=Instance.new("WedgePart")
			p.Size=Vector3.new(0.15,height,v[4] :: number)
			p.CFrame=CFrame.fromMatrix(v[1] :: Vector3,v[2] :: Vector3,up,v[3] :: Vector3)
			p.Color=color;p.Material=Enum.Material.SmoothPlastic
			p.Anchored=true;p.CanCollide=false;p.CanTouch=false;p.CanQuery=false;p.CastShadow=false;p.Parent=m
		end
	end
end
local function consolidate(m: Model,name: string,color: Color3,role: string)
	local parts={}
	for _,p in m:GetChildren() do if p:IsA("BasePart") then table.insert(parts,p) end end
	assert(#parts>1,"Consolidation requires geometry")
	local first=table.remove(parts,1)
	local ok,result=pcall(function()
		return GeometryService:UnionAsync(first,parts,{SplitApart=false,CollisionFidelity=Enum.CollisionFidelity.Box})
	end)
	if not ok then error(`Cannot create reusable {name}: {result}`) end
	for _,p in result do
		p.Name=name;p.Anchored=true;p.CanCollide=false;p.CanTouch=false;p.CanQuery=false;p.CastShadow=false
		p.Color=color;p.Material=Enum.Material.SmoothPlastic;p:SetAttribute("PaletteRole",role)
		if p:IsA("UnionOperation") then p.UsePartColor=true end
		p.Parent=m
	end
	first:Destroy()
	for _,p in parts do p:Destroy() end
	return m
end
local function kitPart(kit: Folder,name: string,parent: Instance,cf: CFrame,scale: number?): Model
	local m=kit[name]:Clone() :: Model
	if scale then m:ScaleTo(scale) end
	m:PivotTo(cf);m.Parent=parent
	return m
end
local function makeComponents(kit: Folder)
	local arc=model("ArchRing")
	for i=0,9 do
		local a,b=i*math.pi/10,(i+1)*math.pi/10
		rod(arc,"ArchSegment",Vector3.new(math.cos(a)*3,math.sin(a)*3,0),Vector3.new(math.cos(b)*3,math.sin(b)*3,0),0.4,IVORY)
	end
	consolidate(arc,"ArchMoulding",IVORY,"Trim").Parent=kit
	local fan=model("Fanlight")
	for i=0,9 do
		local a,b=i*math.pi/10,(i+1)*math.pi/10
		triangle(fan,Vector3.zero,Vector3.new(math.cos(a)*2.8,math.sin(a)*2.8,0),Vector3.new(math.cos(b)*2.8,math.sin(b)*2.8,0),DARK)
	end
	consolidate(fan,"ArchedRecess",DARK,"Recess").Parent=kit
	local rail=model("IronRailingPanel")
	for _,y in {0.1,2.6} do box(rail,"Rail",0,y,0,5.2,0.14,0.14,IRON) end
	for _,x in {-2.5,-1.25,0,1.25,2.5} do
		rod(rail,"Diagonal",Vector3.new(x-0.5,0.3,0),Vector3.new(x+0.5,2.4,0),0.095,IRON)
		rod(rail,"Diagonal",Vector3.new(x+0.5,0.3,0),Vector3.new(x-0.5,2.4,0),0.095,IRON)
	end
	consolidate(rail,"Ironwork",IRON,"Iron").Parent=kit
	local win=model("ArchedShutterWindow")
	box(win,"DarkOpening",0,3.5,0,5.5,7,0.18,DARK,false,"Recess")
	kitPart(kit,"Fanlight",win,CFrame.new(0,7,-0.08))
	kitPart(kit,"ArchRing",win,CFrame.new(0,7,-0.25))
	for _,x in {-2.95,2.95} do box(win,"Jamb",x,3.5,-0.2,0.4,7,0.45,IVORY,false,"Trim") end
	for _,x in {-1.35,1.35} do
		box(win,"Shutter",x,3.4,-0.3,2.55,6.7,0.18,GREEN,false,"Shutter")
		for y=0.7,6.1,1.1 do box(win,"ShutterLouvre",x,y,-0.43,2.3,0.13,0.2,Color3.fromRGB(57,103,77),false,"Louvre") end
	end
	for i=1,5 do
		local theta=i*math.pi/6
		rod(win,"FanlightSpoke",Vector3.new(0,7,-0.32),Vector3.new(math.cos(theta)*2.6,7+math.sin(theta)*2.6,-0.32),0.10,IVORY,"Trim")
	end
	box(win,"Sill",0,-0.1,-0.2,6.5,0.4,1,IVORY,false,"Trim")
	win.Parent=kit
	task.wait()
end
local function railRun(kit: Folder,m: Model,width: number,y: number,z: number,color: Color3?)
	local n=math.floor(width/5)
	for i=1,n do
		local p=kitPart(kit,"IronRailingPanel",m,CFrame.new(-width/2+(i-0.5)*width/n,y,z),width/n/5.2)
		if color then for _,v in p:GetDescendants() do if v:IsA("BasePart") then v.Color=color end end end
	end
end
local function shell(m: Model,width: number,height: number,wall: Color3)
	box(m,"BuildingShell",0,height/2,2,width,height,28,wall,true,"Wall")
	box(m,"Stoop",0,0.35,-15.55,width+0.2,0.7,7.1,RED,true,"Plinth")
	box(m,"RoofTerrace",0,height+0.3,1,width+0.8,0.6,31,RED,true,"Plinth")
	for _,x in {-width/2+0.3,width/2-0.3} do box(m,"SideParapet",x,height+1.7,1,0.6,2.2,30,wall,true,"Wall") end
	box(m,"RearParapet",0,height+1.7,15.7,width,2.2,0.6,wall,true,"Wall")
	box(m,"LayeredCornice",0,height-0.4,-0.3,width+2,0.7,34,IVORY,false,"Trim")
	box(m,"LayeredCornice",0,height-1.1,-16,width+0.9,0.45,1.5,IVORY,false,"Trim")
	for x=-width/2+1,width/2-1,2.7 do box(m,"CorniceDentil",x,height-1.7,-16.2,0.8,0.5,0.9,IVORY,false,"Trim") end
	-- Repeated side openings face gullies; the rear stays deliberately simple.
	for side=-1,1,2 do for y=17,height-5,14 do
		box(m,"SideRecess",side*(width/2+0.05),y,4,0.15,7,4,DARK,false,"Recess")
		box(m,"SideShutter",side*(width/2+0.16),y,4,0.18,6.7,3.7,GREEN,false,"Shutter")
	end end
	m:SetAttribute("WidthStuds",width)
	m:SetAttribute("FloorHeightStuds",14)
end
local function crest(kit: Folder,m: Model,y: number,width: number)
	box(m,"RoofBalustradeBase",0,y,-15.5,width,0.5,0.7,IVORY,false,"Trim")
	box(m,"RoofBalustradeTop",0,y+2,-15.5,width,0.4,0.7,IVORY,false,"Trim")
	for x=-width/2,width/2,3 do box(m,"RoofBaluster",x,y+1,-15.5,0.4,1.8,0.5,IVORY,false,"Trim") end
	box(m,"CrestTablet",0,y+1.8,-15.5,7,3.4,0.65,IVORY,false,"Trim")
	local infill=kitPart(kit,"Fanlight",m,CFrame.new(0,y+3.4,-15.45),1.05)
	for _,p in infill:GetDescendants() do if p:IsA("BasePart") then p.Color=IVORY;p:SetAttribute("PaletteRole","Trim") end end
	kitPart(kit,"ArchRing",m,CFrame.new(0,y+3.4,-15.5),1.05)
	for _,x in {-width/2,width/2} do
		box(m,"FinialBase",x,y+2.6,-15.5,1,0.9,1,IVORY,false,"Trim")
		local p=box(m,"Finial",x,y+3.4,-15.5,1.1,1.1,1.1,IVORY,false,"Trim");p.Shape=Enum.PartType.Ball
	end
end
local function heritage(kit: Folder,kind: string): Model
	local m=model(kind)
	local width=36
	local floors=if kind=="VerandahTownhouse" or kind=="CornerTownhouse" then 3 else 2
	local height=floors*14
	local wall=if kind=="RedGalleryHouse" then RED else Color3.fromRGB(209,160,125)
	shell(m,width,height,wall)
	for f=0,floors-1 do
		local y=f*14
		for _,x in {-10,0,10} do kitPart(kit,"ArchedShutterWindow",m,CFrame.new(x,y+0.8,-12.15)) end
		if f>0 then
			box(m,"DeepVerandah",0,y,-14.2,width+0.6,0.65,7.8,IVORY,true,"Trim")
			box(m,"VerandahRedFloor",0,y+0.36,-14.5,width-0.7,0.08,6.9,RED,false,"Plinth")
		end
	end
	if kind=="VerandahTownhouse" then
		for f=1,2 do
			local y=f*14
			railRun(kit,m,33,y+0.4,-18)
			for _,x in {-17.3,17.3} do column(m,x,y+0.5,-17,12.2,true) end
			-- Ventilated louvred transom screen gives the characteristic shaded hanging gallery.
			for yOffset=10.9,12.4,0.5 do box(m,"VerandahTransom",0,y+yOffset,-17.4,32,0.22,0.3,GREEN,false,"Shutter") end
			for _,x in {-6,6} do box(m,"VerandahMullion",x,y+11.5,-17.45,0.2,2.6,0.4,IVORY,false,"Trim") end
		end
		for _,x in {-17.5,17.5} do
			box(m,"GiantPilaster",x,21,-16.8,1.3,40,1.1,IVORY,false,"Trim")
			box(m,"PilasterCapital",x,40.9,-16.8,2.4,1.1,1.8,IVORY,false,"Trim")
		end
		crest(kit,m,height+0.8,35)
	elseif kind=="ArcadedHouse" then
		for f=0,1 do
			local y=f*14
			for _,x in {-15,-5,5,15} do column(m,x,y+0.8,-17,8.9,false) end
			for _,x in {-10,0,10} do kitPart(kit,"ArchRing",m,CFrame.new(x,y+9.3,-17),1.53) end
			box(m,"ArcadeEntablature",0,y+13,-16.7,36.8,0.8,1.6,IVORY,false,"Trim")
		end
		railRun(kit,m,30,14.4,-17.7)
		crest(kit,m,height+0.8,35)
	elseif kind=="RedGalleryHouse" then
		for f=0,1 do
			local y=f*14
			for _,x in {-16,-5.5,5.5,16} do column(m,x,y+0.8,-17,12.4,true) end
			box(m,"GalleryBeam",0,y+13.4,-17,37.5,0.6,1.4,IVORY,false,"Trim")
		end
		railRun(kit,m,33,14.4,-18,IVORY)
		for x=-17,17,3 do
			box(m,"RoofParapetPier",x,height+1.5,-15.7,0.7,2.4,0.8,IVORY,false,"Trim")
		end
		box(m,"RoofParapetRail",0,height+2.6,-15.7,36.8,0.4,1,IVORY,false,"Trim")
	else
		-- A faceted central bay creates a distinct corner silhouette with few surfaces.
		for f=1,2 do
			local y=f*14
			box(m,"BayBalcony",0,y,-15.7,12,0.7,9,IVORY,true,"Trim")
			for _,x in {-5.5,5.5} do column(m,x,y+0.4,-19,12,false) end
			railRun(kit,m,11,y+0.4,-20)
			for _,side in {-1,1} do
				local p=kitPart(kit,"IronRailingPanel",m,CFrame.new(side*6,y+0.4,-17)*CFrame.Angles(0,side*math.pi/2,0))
			end
		end
		for _,x in {-17,17} do box(m,"RusticatedPier",x,21,-16.4,1.8,42,0.9,IVORY,false,"Trim") end
		for y=2,39,3 do for _,x in {-17,17} do box(m,"RusticationBand",x,y,-16.95,2,0.12,0.15,Color3.fromRGB(191,172,139),false,"Mortar") end end
		crest(kit,m,height+0.8,17)
		for _,x in {-13,13} do
			box(m,"RoofShoulder",x,height+1.4,-15.7,8,2.2,0.7,wall,false,"Wall")
		end
	end
	m:SetAttribute("ArchitectureType",kind)
	m:SetAttribute("ReferenceUse","Original interpretation of North Kolkata heritage vocabulary")
	return m
end
local function apartment(): Model
	local m=model("ModernApartment")
	local wall=Color3.fromRGB(204,208,185)
	box(m,"ApartmentBody",0,22,0,32,44,32,wall,true,"Wall")
	box(m,"StairwellStrip",-8,23,-16.25,6,42,0.5,Color3.fromRGB(100,141,140),false,"Accent")
	for f=0,3 do
		local y=f*11
		for _,x in {-8,5} do
			box(m,"WindowFrame",x,y+5.8,-16.5,5.5,5.4,0.3,IVORY,false,"Trim")
			box(m,"OpaqueGlazing",x,y+5.8,-16.7,4.9,4.8,0.2,Color3.fromRGB(58,87,94),false,"Recess")
			box(m,"Sunshade",x,y+8.8,-17,6.5,0.25,2,IVORY,false,"Trim")
		end
		if f>0 then
			box(m,"BoxBalcony",7,y+1,-18,15,0.5,4,IVORY,true,"Trim")
			box(m,"SolidBalconyFront",7,y+2.7,-20,15,2.9,0.45,wall,false,"Wall")
			for _,x in {-0.5,14.5} do box(m,"BalconyEnd",x,y+2.7,-18,0.4,2.9,4,wall,false,"Wall") end
		end
	end
	box(m,"Entrance",6,4.5,-16.5,5,9,0.4,GREEN,false,"Shutter")
	box(m,"RoofTerrace",0,44.4,0,33,0.8,33,IVORY,true,"Trim")
	box(m,"RoofRoom",-8,47,5,10,5,10,wall,true,"Wall")
	m:SetAttribute("WidthStuds",32);m:SetAttribute("FloorHeightStuds",11);m:SetAttribute("ArchitectureType","ModernApartment")
	return m
end
export type Palette = { wall: Color3, trim: Color3?, shutter: Color3? }
function Architecture.place(kind: string,parent: Instance,cf: CFrame,palette: Palette,locationId: string): Model
	local kit=ServerStorage.WorldAuthoring.HeritageKit
	local template=kit:FindFirstChild(kind)
	assert(template and template:IsA("Model"),"Unknown architecture template")
	local m=template:Clone() :: Model
	for _,p in m:GetDescendants() do if p:IsA("BasePart") then
		local role=p:GetAttribute("PaletteRole")
		if role=="Wall" then p.Color=palette.wall
		elseif role=="Trim" and palette.trim then p.Color=palette.trim
		elseif role=="Shutter" and palette.shutter then p.Color=palette.shutter end
	end end
	m:SetAttribute("WallColor",palette.wall)
	m:SetAttribute("LocationId",locationId)
	m:SetAttribute("AssetId","architecture."..kind)
	m:SetAttribute("AuthoringVersion",2)
	m:PivotTo(cf);m.Parent=parent
	return m
end
function Architecture.apply()
	local authoring=ServerStorage.WorldAuthoring
	assert(not authoring:FindFirstChild("HeritageKit"),"Heritage kit already exists; inspect before replacing")
	local history=ChangeHistoryService:TryBeginRecording("Kolkata - heritage street architecture")
	local ok,result=xpcall(function()
		local kit=Instance.new("Folder");kit.Name="HeritageKit";kit.Parent=authoring
		makeComponents(kit)
		for _,kind in {"VerandahTownhouse","ArcadedHouse","RedGalleryHouse","CornerTownhouse"} do
			local m=heritage(kit,kind);m.Parent=kit;task.wait()
		end
		apartment().Parent=kit
		local old=Instance.new("Folder");old.Name="OriginalArchitecture";old.Parent=authoring
		local para=workspace.World.Cities.Kolkata.Districts.Para01
		local variants={
			{2,"VerandahTownhouse",Color3.fromRGB(201,144,133)},
			{3,"RedGalleryHouse",Color3.fromRGB(159,69,49)},
			{4,"ArcadedHouse",Color3.fromRGB(220,176,99)},
			{7,"CornerTownhouse",Color3.fromRGB(161,183,153)},
			{8,"ArcadedHouse",Color3.fromRGB(206,155,128)},
			{10,"CornerTownhouse",Color3.fromRGB(218,180,109)},
			{11,"VerandahTownhouse",Color3.fromRGB(161,187,165)},
			{13,"RedGalleryHouse",Color3.fromRGB(188,107,79)},
			{19,"ArcadedHouse",Color3.fromRGB(223,188,127)},
			{20,"VerandahTownhouse",Color3.fromRGB(202,151,138)},
			{6,"ModernApartment",Color3.fromRGB(204,208,185)},
			{23,"ModernApartment",Color3.fromRGB(188,202,195)},
		}
		for _,v in variants do
			local index,kind,color=v[1] :: number,v[2] :: string,v[3] :: Color3
			local source: Model?=nil
			for _,b in para.Buildings:GetChildren() do if b.Name:match("^Building_"..string.format("%02d",index).."_") then source=b :: Model;break end end
			assert(source,"Replacement location missing")
			local replacement=Architecture.place(kind,para.Buildings,source:GetPivot(),{wall=color},source:GetAttribute("LocationId") :: string)
			replacement.Name=string.format("Building_%02d_%s",index,kind)
			source.Parent=old
			local details=para.StreetFurniture:FindFirstChild(`BuildingDetails_{index}`)
			if details then details.Parent=old end
			task.wait()
		end
		return "Four heritage types placed in ten colour variants; two apartments; original models preserved"
	end,debug.traceback)
	if history then ChangeHistoryService:FinishRecording(history,Enum.FinishRecordingOperation.Commit) end
	if not ok then error(result) end
	return result
end
return Architecture
