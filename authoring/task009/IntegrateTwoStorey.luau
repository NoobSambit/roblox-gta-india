--!strict
-- One-shot EDIT-ONLY integration of the finished original-source Blender interior.
local Http = game:GetService("HttpService")
local Storage = game:GetService("ServerStorage")
local v = workspace.World.Cities.Kolkata.Districts.Maidan.VictoriaMemorial
local site, grey, art = v:GetPivot(), v.HeistGreybox, v.InteriorArt
assert(not game:GetService("RunService"):IsRunning(), "Edit mode only")
assert(not art:FindFirstChild("TwoStoreyArchitecture"), "Already assembled; inspect edits before rerunning")
local plan = Http:JSONDecode(Http:GetAsync("http://127.0.0.1:8769/final-plan.json"))
local masters = Storage.WorldAuthoring.Task009Assets
for _, p in plan.instances do
	local master = masters:FindFirstChild(p.assetId, true)
	assert(master and master:IsA("Model") and master:GetAttribute("ImportComplete"), `Missing {p.assetId}`)
end
local function vec(t): Vector3 return Vector3.new(t[1],t[2],t[3]) end
local function folder(parent, name)
	local f=Instance.new("Folder") f.Name,f.Parent=name,parent return f
end
local archive = Storage.WorldAuthoring.Task009Archive
local interim = folder(archive,"SupersededTask009Finishing")
local original = archive.OriginalInteriorReplaced
local report = {replacedOriginalInterior={},archivedInterim={},instances={},nativeStructure=plan.nativeStructure,lights=plan.lights,
	groundMarkersPreserved=true,gameplayImplemented=false,sharedRobberyEvent="VIC_HEIST_007"}
local function retire(o, parent)
	local path=o:GetFullName() o:SetAttribute("Task009OriginalPath",path) o.Parent=parent
	table.insert(report.replacedOriginalInterior,path)
end
art.CorrectedArchitecture.Parent=interim
art.InteriorLighting.Parent=interim
for _, o in v.Interior:GetChildren() do
	local template=o:GetAttribute("TemplateId")
	if template=="RotundaArcade" or template=="RotundaInnerLining" or template=="QueensHallFigure" then retire(o,original) end
end
for _, p in v.Structure:GetDescendants() do
	if not p:IsA("BasePart") then continue end
	local localPos=site:PointToObjectSpace(p.Position)
	if p.Name=="EntryDoorLintel" or ((p.Name=="RotundaUpperWall" or p.Name=="AxialPassageLintel") and math.abs(localPos.Z)>30) then retire(p,original) end
end
local architecture=folder(art,"TwoStoreyArchitecture")
local lighting=folder(art,"MuseumLighting")
local structure=folder(architecture,"SourceMatchedNativeStructure")
local collision=folder(architecture,"SimpleCollision")
local courtyard=folder(art,"CourtyardPresentation")
local landscaping=folder(art,"VictoriaLandscaping")
local finalIds={} for _,p in plan.instances do finalIds[p.instanceId]=true end
local existing={}
for _,o in art:GetDescendants() do
	if o:IsA("Model") and o:GetAttribute("ArtInstanceId") then
		if finalIds[o.Name] then existing[o.Name]=o else o.Parent=interim end
	end
end
local MaterialService=game:GetService("MaterialService")
local warm=MaterialService:FindFirstChild("VIC009_WarmStone")
if not warm then
	warm=Instance.new("MaterialVariant") warm.Name="VIC009_WarmStone" warm.BaseMaterial=Enum.Material.Limestone
	warm.StudsPerTile=14 warm.ColorMapContent=Content.fromUri("rbxassetid://74587698959678") warm.Parent=MaterialService
end
local ivory=Color3.fromRGB(232,226,211)
local function finish(part,assetId)
	part.Anchored=true part.CanCollide=false part.CanTouch=false part.CanQuery=false
	local role,component=part:GetAttribute("PaletteRole"),part:GetAttribute("Component") or "Body"
	if role=="Ivory" or role=="Stone" then
		part.Material,part.MaterialVariant=Enum.Material.Limestone,"VIC009_WarmStone"
		part.Color=if role=="Ivory" or assetId=="VIC_A03_ARCH_10" then ivory else Color3.fromRGB(215,207,189)
	end
	if component:sub(1,5)=="Floor" then
		part.Material,part.MaterialVariant,part.Color=Enum.Material.Marble,"VIC009_PaleStoneFloor",Color3.fromRGB(247,245,239)
		part.CanCollide,part.CanQuery=true,true
		part.CollisionFidelity=if assetId=="VIC_B03_BALCONY" then Enum.CollisionFidelity.Hull else Enum.CollisionFidelity.Box
	elseif component=="Landing" then part.CanCollide,part.CanQuery=true,true part.CollisionFidelity=Enum.CollisionFidelity.Box
	elseif component=="Diffuser" then part.Material,part.Color,part.CastShadow=Enum.Material.Neon,Color3.fromRGB(255,235,196),false end
	if role=="Glass" then part.CastShadow=false end
	if assetId=="VIC_B14_COURTYARD_SPANDREL" then
		local source=v.Structure:FindFirstChild("WingCourtyardWall",true)
		if source and source:IsA("BasePart") then part.Color,part.Material,part.MaterialVariant=source.Color,source.Material,source.MaterialVariant end
	end
end
local placed={}
for i,p in plan.instances do
	local model=existing[p.instanceId]
	if model and model:GetAttribute("AssetId")~=p.assetId then model.Parent=interim model=nil end
	if not model then model=masters:FindFirstChild(p.assetId,true):Clone() end
	model.Name=p.instanceId
	model:SetAttribute("ArtInstanceId",p.instanceId) model:SetAttribute("SourceMarker",p.sourceMarker or "")
	model:SetAttribute("ArtRole",p.role) model:SetAttribute("RoomId",p.roomId or "") model:SetAttribute("ArtScale",p.scale)
	model.ModelStreamingMode=Enum.ModelStreamingMode.Atomic
	model:ScaleTo(p.scale)
	if p.stretch then
		local scale=vec(p.stretch)
		for _,part in model:GetDescendants() do if part:IsA("BasePart") then
			local cf=part.CFrame part.Size*=scale part.CFrame=CFrame.new(cf.Position*scale)*cf.Rotation
		end end
	end
	model:PivotTo(site*CFrame.new(vec(p.position))*CFrame.Angles(0,p.yaw,0)*CFrame.Angles(p.pitch or 0,0,0))
	for _,part in model:GetDescendants() do if part:IsA("MeshPart") then finish(part,p.assetId) end end
	if p.materialOverrides then for _,part in model:GetDescendants() do if part:IsA("BasePart") and p.materialOverrides[part:GetAttribute("PaletteRole")]=="Teal" then part.Color=Color3.fromRGB(36,93,99) end end end
	if p.role=="PremiumBanner" then for _,part in model:GetDescendants() do if part:IsA("BasePart") and part:GetAttribute("PaletteRole")=="Teal" then part.Color,part.Material=Color3.fromRGB(136,72,63),Enum.Material.Fabric end end end
	model.Parent=if p.role=="TwoStoreyArchitecture" or p.role=="UpperGalleryBacking" or p.role=="CourtyardRepair" then architecture elseif p.role=="CourtyardFurniture" or p.role=="CourtyardInterpretation" then courtyard elseif p.role=="LightFixture" then lighting
		elseif p.role=="Emitter" or p.role=="Housing" or p.role=="FloorInlay" or p.role=="Terminal" then art.SecurityVisuals
		elseif p.role=="ExhibitSupport" or p.role=="LootVisual" or p.role=="Frame" or p.role=="SecureArchiveDressing" or p.role=="PermanentCollection" or p.role=="WallArtwork" then art.ExhibitionVisuals else art.ArchitecturalEnhancements
	placed[p.instanceId]=model table.insert(report.instances,p)
	if i%25==0 then task.wait() end
end
local function native(name,size,cf,color,material,solid,parent,invisible)
	local p=Instance.new("Part") p.Name,p.Size,p.CFrame=name,size,cf
	p.Color,p.Material,p.Anchored=color,material,true p.CanCollide,p.CanTouch,p.CanQuery=solid,false,solid
	p.TopSurface,p.BottomSurface=Enum.SurfaceType.Smooth,Enum.SurfaceType.Smooth
	p:SetAttribute("Task009Native",true)
	if invisible then p.Transparency,p.CastShadow=1,false elseif material==Enum.Material.Limestone then p.MaterialVariant="VIC009_WarmStone" end
	p.Parent=parent return p
end
for _,r in plan.nativeStructure do
	local invisible=r.purpose=="InvisibleCollision"
	local color=if r.material=="Brass" then Color3.fromRGB(184,155,96) elseif r.material=="Charcoal" then Color3.fromRGB(52,63,69) elseif r.material=="Teal" then Color3.fromRGB(36,93,99) elseif r.material=="Oxblood" then Color3.fromRGB(136,72,63) elseif r.material=="Mushroom" then Color3.fromRGB(162,157,147) else ivory
	local material=if r.material=="Brass" or r.material=="Charcoal" then Enum.Material.Metal elseif r.purpose=="Carpet" then Enum.Material.Fabric else Enum.Material.Limestone
	local p=native(r.name,vec(r.size),site*CFrame.new(vec(r.position))*CFrame.Angles(0,r.yaw,0),color,material,r.solid,if invisible then collision else structure,invisible)
	if material~=Enum.Material.Limestone then p.MaterialVariant="" end
	p:SetAttribute("Purpose",r.purpose)
end
-- Continuous simple ramps over the visual stair treads; separate turn landings already have box collision.
for _,sign in {-1,1} do
	local stairSite=site*CFrame.new(-sign*11.5,6.8,sign*48)*CFrame.Angles(0,if sign<0 then 0 else math.pi,0)
	for i,ends in {{{5.25,0,1.5},{5.25,13.6,-27}},{{-5.25,13.6,-28.5},{-5.25,27.2,0}}} do
		local a,b=vec(ends[1]),vec(ends[2])
		local back=(a-b).Unit local right=Vector3.xAxis local up=back:Cross(right).Unit
		local cf=CFrame.fromMatrix((a+b)/2+up*.1,right,up,back)
		local p=native("StairRamp_"..sign.."_"..i,Vector3.new(8.5,.2,(b-a).Magnitude),stairSite*cf,ivory,Enum.Material.SmoothPlastic,true,collision,true)
		p:SetAttribute("SourceStair",if sign<0 then "VIC_STAIR_NORTH" else "VIC_STAIR_SOUTH")
	end
end
for _,p in grey.Structure:GetDescendants() do if p:IsA("BasePart") then p.Material,p.MaterialVariant,p.Color=Enum.Material.Limestone,"VIC009_WarmStone",ivory end end
-- Preserve all original eighteen loot models, nine security reservations and their transforms/attributes.
local function anchor(parent,position,name,size)
	return native(name or "InteractionAnchor",size or Vector3.new(.2,.2,.2),site*CFrame.new(vec(position)),ivory,Enum.Material.SmoothPlastic,false,parent,true)
end
for _,room in plan.upperLayout.upperRooms do
	local s=room.sizeXZ or {61.6,61.6}
	local p=anchor(grey.RoomZones,{room.centerXZ[1],40.5,room.centerXZ[2]},room.roomId,Vector3.new(s[1],13,s[2]))
	p:SetAttribute("RoomId",room.roomId) p:SetAttribute("RoomName",room.name) p:SetAttribute("RoomRole",room.role)
	p:SetAttribute("Floor",2) p:SetAttribute("HeistId","VIC_HEIST_007")
	if room.annulusRadii then p:SetAttribute("ZoneShape","Annulus") p:SetAttribute("InnerRadius",23) p:SetAttribute("OuterRadius",30.8) end
end
for _,item in plan.upperLayout.upperLoot do
	assert(not grey.LootMarkers:FindFirstChild(item.lootId),"Upper loot already exists")
	local m=Instance.new("Model") m.Name=item.lootId m.WorldPivot=site*CFrame.new(vec(item.rootPosition))
	for key,value in {LootId=item.lootId,GalleryId=item.roomId,LootCategory=item.category,ExhibitName=item.name,ProvisionalValue=item.provisionalValue,CapacityCost=item.capacityCost,CollectionSeconds=item.collectionSeconds,SecurityRisk="UpperOptional",AvailabilityState="Available",AlertOnTheftStart=true,Floor=2,HeistId="VIC_HEIST_007"} do m:SetAttribute(key,value) end
	anchor(m,item.placeholderCenter) m.Parent=grey.LootMarkers
	local ref=Instance.new("ObjectValue") ref.Name,ref.Value,ref.Parent="ExhibitVisual",placed[item.lootId.."_CASE"],m
end
for _,item in plan.upperLayout.upperSecurity do
	local m=Instance.new("Model") m.Name=item.securityId m.WorldPivot=site*CFrame.new(vec(item.position))
	for key,value in {SecurityId=item.securityId,SecurityType=item.securityType,DifficultyTier=item.difficultyTier,AssociatedGallery=item.roomId,Floor=2,HeistId="VIC_HEIST_007",Active=false} do m:SetAttribute(key,value) end
	local centre=table.clone(item.position) centre[2]+=item.size[2]/2
	anchor(m,centre,"ReservedFootprint",vec(item.size)) m.Parent=grey.SecurityMarkers
	local n=0
	for _,p in plan.instances do if p.sourceMarker==item.securityId then
		n+=1 local ref=Instance.new("ObjectValue") ref.Name,ref.Value,ref.Parent="Visual_"..n,placed[p.instanceId],m
	end end
	if item.securityType=="ProtectedCase" then local ref=Instance.new("ObjectValue") ref.Name,ref.Value,ref.Parent="Visual_1",placed.VIC_LOOT_024_CASE,m end
end
for _,item in plan.upperLayout.restrictedUpper do
	local p=anchor(grey.RestrictedZoneMarkers,item.center,item.id,vec(item.size))
	p:SetAttribute("RestrictedId",item.id) p:SetAttribute("GalleryId",item.roomId) p:SetAttribute("Floor",2)
	p:SetAttribute("HeistId","VIC_HEIST_007") p:SetAttribute("AlertOnUnauthorizedEntry",true)
end
-- Rebind original and revised exhibit supports; marker identities and metadata stay intact.
for _,b in plan.lootBindings do
	local marker=grey.LootMarkers:FindFirstChild(b.lootId)
	local ref=marker:FindFirstChild("ExhibitVisual") or Instance.new("ObjectValue")
	ref.Name,ref.Value,ref.Parent="ExhibitVisual",placed[b.instances[1]],marker
end
-- Apply the original four uploaded 3:2 images to every selected flat frame.
local images=Http:JSONDecode(Http:GetAsync("http://127.0.0.1:8769/artwork.json"))
local mappings={}
for _,b in plan.artworkBindings do mappings[b.frameInstance]=b.artworkId end
for _,p in plan.instances do if p.role=="WallArtwork" then mappings[p.instanceId]=p.artworkId end end
for instanceId,artworkId in mappings do
	local item=nil for _,candidate in images.artworks do if candidate.artworkId==artworkId then item=candidate break end end
	assert(item,"Unknown original artwork mapping")
	for _,canvas in placed[instanceId]:GetDescendants() do if canvas:IsA("BasePart") and canvas:GetAttribute("Component")=="Canvas" then
		local oldGui=canvas:FindFirstChild("OriginalArtwork") if oldGui then oldGui:Destroy() end
		local gui=Instance.new("SurfaceGui") gui.Name,gui.Face,gui.CanvasSize="OriginalArtwork",Enum.NormalId.Back,Vector2.new(480,320)
		gui.LightInfluence,gui.AlwaysOnTop=1,false
		local image=Instance.new("ImageLabel") image.Name,image.Image,image.Size,image.BackgroundTransparency="Painting",item.robloxImageId,UDim2.fromScale(1,1),1
		image.ScaleType,image.Parent=Enum.ScaleType.Fit,gui gui.Parent=canvas
	end end
	placed[instanceId]:SetAttribute("ArtworkId",item.artworkId)
end
-- Furniture proxies match the enlarged supports and permanent islands, without hidden prototype pedestals.
art.FurnitureCollision:ClearAllChildren()
for _,p in plan.instances do if p.role=="ExhibitSupport" or p.role=="CourtyardFurniture" or (p.role=="PermanentCollection" and not p.assetId:find("VIC_L")) then
	local cf,size=placed[p.instanceId]:GetBoundingBox()
	local proxy=native(p.instanceId.."_Collision",size,cf,ivory,Enum.Material.SmoothPlastic,true,art.FurnitureCollision,true)
	proxy:SetAttribute("SourceMarker",p.sourceMarker or "PermanentCollection")
end end
-- Latest explicitly authorized grounds revision: reuse uploaded original tree
-- meshes and retain all four established property-gate/escape gaps.
local treeSource=nil
for _,o in v.Grounds:GetDescendants() do if o:IsA("Model") and o:GetAttribute("TemplateId")=="GardenTree" then treeSource=o break end end
assert(treeSource,"Original Victoria GardenTree source absent")
-- Original assemblies have automatic bounding-box pivots. Re-establish the
-- authored tree-base pivot before scaling; otherwise the trunk sinks below ground.
local trunk=assert(treeSource:FindFirstChild("Bark",true),"Original tree trunk absent")
assert(trunk:IsA("BasePart"))
local trunkLocal=site:PointToObjectSpace(trunk.Position)
local treeBase=Vector3.new(trunkLocal.X,.1,trunkLocal.Z)
for _,row in plan.legacyInstances do
	local tree=treeSource:Clone() tree.Name=row.instanceId
	tree.WorldPivot=site*CFrame.new(treeBase)
	tree:ScaleTo(row.scale)
	tree:PivotTo(site*CFrame.new(vec(row.position))*CFrame.Angles(0,row.yaw,0))
	for _,p in tree:GetDescendants() do if p:IsA("BasePart") then
		p.Anchored,p.CanCollide,p.CanTouch=true,false,false
		if p.Name=="Leaf" then p.Color,p.Material=Color3.fromRGB(66,106,69),Enum.Material.Grass elseif p.Name=="LeafLight" then p.Color,p.Material=Color3.fromRGB(114,145,91),Enum.Material.Grass end
	end end
	tree:SetAttribute("SourceTemplateId","GardenTree") tree.Parent=landscaping
end
local groundsChanges={}
for _,p in v.Grounds:GetDescendants() do if p:IsA("BasePart") then
	local n=p.Name local factor=if n:match("^BoundaryPicket") or n:match("^BoundaryRail") or n:match("^BoundarySideRail") then 1.7 elseif n:match("^BoundaryBase") or n:match("^BoundarySide") then 1.35 else 1
	if factor~=1 then
		local localCF=site:ToObjectSpace(p.CFrame)
		table.insert(groundsChanges,{path=p:GetFullName(),oldSize={p.Size.X,p.Size.Y,p.Size.Z},heightScale=factor})
		p.Size=Vector3.new(p.Size.X,p.Size.Y*factor,p.Size.Z)
		p.CFrame=site*CFrame.new(localCF.X,localCF.Y*factor,localCF.Z)*localCF.Rotation
	end
	if n:match("^CampusGround") then p.Color,p.Material=Color3.fromRGB(120,149,108),Enum.Material.Grass
	elseif n:find("Promenade") or n=="SideGatePath" or n:match("^PerimeterFootpath") then p.Color,p.Material=Color3.fromRGB(180,173,153),Enum.Material.Sandstone
	elseif n:match("^BoundaryPicket") or n:match("^BoundaryRail") or n:match("^BoundarySideRail") then p.Color,p.Material=Color3.fromRGB(62,80,75),Enum.Material.Metal end
	if p.Parent:IsA("Model") and p.Parent:GetAttribute("TemplateId")=="GardenTree" then
		if n=="Leaf" then p.Color,p.Material=Color3.fromRGB(66,106,69),Enum.Material.Grass elseif n=="LeafLight" then p.Color,p.Material=Color3.fromRGB(114,145,91),Enum.Material.Grass end
	end
end end
for _,o in v.Interior:GetChildren() do if o:IsA("Model") and o:GetAttribute("TemplateId")=="CourtyardInlay" then
	for _,p in o:GetDescendants() do if p:IsA("BasePart") and p.Name=="FloorDark" then p.Color,p.Material=Color3.fromRGB(80,93,93),Enum.Material.Slate end end
end end
report.authorizedGroundsChanges=groundsChanges report.reusedTreeInstances=#plan.legacyInstances
for _,row in plan.lights do
	local model=placed[row.fixtureId or row.id] local diffuser=nil
	for _,p in model:GetDescendants() do if p:IsA("BasePart") and p:GetAttribute("Component")=="Diffuser" then diffuser=p end end
	assert(diffuser,"Fixture diffuser absent")
	local light=Instance.new(if row.kind=="Spot" then "SpotLight" else "PointLight")
	light.Name,light.Color,light.Range,light.Brightness,light.Shadows="MuseumIllumination",Color3.fromRGB(255,239,211),row.range,row.brightness,row.shadows==true
	if light:IsA("SpotLight") then light.Face,light.Angle=Enum.NormalId.Bottom,row.angle end
	if row.target then
		local mount=Instance.new("Attachment") mount.Name,mount.Parent="ArchitecturalWashAim",diffuser
		local clearance=if row.target[2]>=row.position[2] then .35 else -.35
		mount.WorldCFrame=site*CFrame.lookAt(vec(row.position)+Vector3.new(0,clearance,0),vec(row.target))
		light.Face=Enum.NormalId.Front light.Parent=mount
	else light.Parent=diffuser end
end
grey:SetAttribute("HeistId","VIC_HEIST_007") grey:SetAttribute("FloorCount",2)
grey:SetAttribute("SharedEventPolicy",plan.upperLayout.sharedEvent.alert)
grey:SetAttribute("SharedTimerEconomyCooldown",true)
art:SetAttribute("ArtInstanceCount",#plan.instances) art:SetAttribute("InteriorFloorCount",2)
art:SetAttribute("PlacedMeshTriangles",plan.statistics.importedPlacedTriangles)
report.statistics=plan.statistics
Http:PostAsync("http://127.0.0.1:8769/integration.json",Http:JSONEncode(report),Enum.HttpContentType.ApplicationJson)
game:GetService("Selection"):Set({})
return Http:JSONEncode({instances=#plan.instances,loot=#grey.LootMarkers:GetChildren(),security=#grey.SecurityMarkers:GetChildren(),rooms=#grey.RoomZones:GetChildren(),lights=#plan.lights})
