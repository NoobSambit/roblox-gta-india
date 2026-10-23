--!strict
-- Edit-only. Normalize existing imports using the actual saved Blender geometry.
local Http = game:GetService("HttpService")
local Storage = game:GetService("ServerStorage")
local RunService = game:GetService("RunService")
local Prep = {}
local URL = "http://127.0.0.1:8766/"

type SourceObject = {name:string, meshKey:string, position:{number}, yaw:number, centre:{number}, color:{number}, role:string, group:string, triangles:number}
type Collider = {name:string,position:{number},size:{number},yaw:number,shape:string?}
type Spec = {assetId:string,name:string,category:string,importName:string,objects:{SourceObject},dimensions:{number},triangles:number,collisionBoxes:{Collider},bodySize:{number}?,boundsMinStuds:{number},boundsMaxStuds:{number}}
local function vec(t:{number}):Vector3 return Vector3.new(t[1],t[2],t[3]) end
local function editOnly() assert(RunService:IsStudio() and not RunService:IsRunning(),"Edit-time authoring only") end
local function folder(parent:Instance,name:string):Folder
	local existing=parent:FindFirstChild(name)
	if existing then assert(existing:IsA("Folder"));return existing end
	local f=Instance.new("Folder");f.Name=name;f.Parent=parent;return f
end
local function library():Folder return folder(folder(Storage,"WorldAuthoring"),"AssetLibrary") end
local function masterFolder():Folder return folder(library(),"Masters") end
local function catalog():{Spec}
	local decoded=Http:JSONDecode(Http:GetAsync(URL.."authoring/task006/asset-catalog.json",true))
	assert(typeof(decoded)=="table" and #decoded==63,"Expected 58 existing assets and five commercial shells")
	return decoded :: {Spec}
end
local function proxy(parent:Instance,c:Collider)
	local p=Instance.new("Part");p.Name=c.name;p.Size=vec(c.size)
	p.CFrame=CFrame.new(vec(c.position))*CFrame.Angles(0,c.yaw or 0,0)
	p.Anchored=true;p.Transparency=1;p.CanTouch=false;p.CanCollide=true;p.CanQuery=true;p.CastShadow=false
	p:SetAttribute("CollisionProxy",true);p.Parent=parent;return p
end

function Prep.prepare(first:number?,last:number?)
	editOnly();local rows=catalog();local output={}
	for index=first or 1,last or #rows do
		local spec=rows[index];local destination=masterFolder()
		local existing=destination:FindFirstChild(spec.importName)
		if existing then assert(existing:GetAttribute("Task006Owned"));existing:Destroy() end
		local original=assert(workspace:FindFirstChild(spec.importName),"Missing raw import "..spec.importName)
		assert(original:IsA("Model"));local partIndex:{[string]:MeshPart}={}
		for _,p in original:GetDescendants() do if p:IsA("MeshPart") then partIndex[p.Name]=p end end
		-- Studio bakes the FBX root axis conversion into each uploaded mesh.
		-- Infer it from two actual object centres, then remove it once per template.
		local rootRotation=CFrame.Angles(0,math.pi,0)
		local firstObject=spec.objects[1]
		local firstPart=assert(partIndex[firstObject.name] or partIndex[firstObject.name.."_RBX"])
		for _,o in spec.objects do
			local raw=partIndex[o.name] or partIndex[o.name.."_RBX"]
			if raw then
				local sourceDelta=vec(o.centre)-vec(firstObject.centre)
				local rawDelta=raw.Position-firstPart.Position
				if Vector2.new(sourceDelta.X,sourceDelta.Z).Magnitude>4 and Vector2.new(rawDelta.X,rawDelta.Z).Magnitude>4 then
					local yaw=math.atan2(sourceDelta.Z,sourceDelta.X)-math.atan2(rawDelta.Z,rawDelta.X)
					rootRotation=CFrame.Angles(0,yaw,0);break
				end
			end
		end
		local model=Instance.new("Model");model.Name=spec.importName
		model:SetAttribute("AssetId",spec.assetId);model:SetAttribute("Task006Owned",true)
		model:SetAttribute("AssetCategory",spec.category);model:SetAttribute("SourceTriangles",spec.triangles)
		model.ModelStreamingMode=if spec.category=="tier2" or spec.category=="bridge" then Enum.ModelStreamingMode.Default else Enum.ModelStreamingMode.Atomic
		local geometry=Instance.new("Folder");geometry.Name="Geometry";geometry.Parent=model
		local groups:{[string]:Model}={};local templates:{[string]:{part:MeshPart,source:SourceObject}}={}
		for i,o in spec.objects do
			local pair=templates[o.meshKey]
			if not pair then
				local raw=partIndex[o.name] or partIndex[o.name.."_RBX"]
				assert(raw,"Missing object "..spec.importName.." / "..o.name)
				pair={part=raw,source=o};templates[o.meshKey]=pair
			end
			local clone=pair.part:Clone();clone.Name=o.name
			local ref=pair.source
			local referenceSource=CFrame.new(vec(ref.position))*CFrame.Angles(0,ref.yaw,0)
			local currentSource=CFrame.new(vec(o.position))*CFrame.Angles(0,o.yaw,0)
			local referenceMesh=CFrame.new(vec(ref.centre))*rootRotation:Inverse()*pair.part.CFrame.Rotation
			clone.CFrame=currentSource*referenceSource:Inverse()*referenceMesh
			clone.Color=Color3.new(o.color[1],o.color[2],o.color[3]);clone.Material=Enum.Material.SmoothPlastic
			clone.TextureID="";clone.Anchored=true;clone.CanCollide=false;clone.CanTouch=false;clone.CanQuery=true
			clone.Transparency=0;clone.DoubleSided=false;clone.RenderFidelity=Enum.RenderFidelity.Automatic
			clone.CastShadow=o.role~="Glass" and o.role~="Dark" and o.role~="Shadow"
			clone:SetAttribute("MeshKey",o.meshKey);clone:SetAttribute("PaletteRole",o.role);clone:SetAttribute("SourceTriangles",o.triangles)
			for _,child in clone:GetChildren() do if child:IsA("SurfaceAppearance") or child:IsA("BaseScript") then child:Destroy() end end
			local groupName=o.group
			if spec.category=="bridge" then groupName="Section"..tostring(math.clamp(math.floor((o.centre[3]+448)/128)+1,1,7)) end
			local group=groups[groupName]
			if not group then group=Instance.new("Model");group.Name=groupName;group.ModelStreamingMode=Enum.ModelStreamingMode.Atomic;group.Parent=geometry;groups[groupName]=group end
			clone.Parent=group
			if i%150==0 then task.wait() end
		end
		local collision=Instance.new("Folder");collision.Name="Collision";collision.Parent=model
		for _,c in spec.collisionBoxes do proxy(collision,c) end
		if spec.category=="tier3" then
			local size=assert(spec.bodySize);proxy(collision,{name="ClosedBuildingBounds",position={0,size[2]/2,0},size=size,yaw=0})
		elseif spec.category=="context" then
			local lo,hi=spec.boundsMinStuds,spec.boundsMaxStuds
			proxy(collision,{name="ClosedBackgroundShell",position={(lo[1]+hi[1])/2,(lo[2]+hi[2])/2,(lo[3]+hi[3])/2},size=spec.dimensions,yaw=0})
		end
		model.WorldPivot=CFrame.identity
		-- Validate render geometry only: collision boxes can deliberately extend below it.
		local temp=Instance.new("Model");geometry.Parent=temp
		local _,size=temp:GetBoundingBox();geometry.Parent=model;temp:Destroy()
		local errorSize=(size-vec(spec.dimensions)).Magnitude
		assert(errorSize<.35,`{spec.importName} assembled bounds differ by {errorSize}`)
		model.Parent=destination
		local unique=0;for _ in templates do unique+=1 end
		table.insert(output,{assetId=spec.assetId,parts=#spec.objects,uniqueMeshes=unique,boundsError=errorSize})
		task.wait()
	end
	return output
end

function Prep.archiveImports()
	editOnly();local archive=folder(folder(Storage.WorldAuthoring,"Task006Archive"),"ImportedOriginals")
	local count=0
	for _,spec in catalog() do
		assert(masterFolder():FindFirstChild(spec.importName),"Prepare every master before moving raw imports")
		local raw=workspace:FindFirstChild(spec.importName)
		if raw then raw.Parent=archive;count+=1;task.wait() end
	end
	return {archivedImports=count,masterCount=#masterFolder():GetChildren()}
end

-- New FBX uploads use Studio's 3D Importer; CreateAssetAsync is unavailable in this Studio build.

function Prep.report()
	local rows={};local ids={};local instances=0
	for _,model in masterFolder():GetChildren() do
		local meshRows={};local triangles=0
		for _,p in model:GetDescendants() do if p:IsA("MeshPart") then
			ids[p.MeshId]=true;instances+=1;triangles+=(p:GetAttribute("SourceTriangles") or 0)
			table.insert(meshRows,{name=p.Name,meshKey=p:GetAttribute("MeshKey"),meshId=p.MeshId,size={p.Size.X,p.Size.Y,p.Size.Z}})
		end end
		table.insert(rows,{assetId=model:GetAttribute("AssetId"),master=model:GetFullName(),triangles=triangles,meshes=meshRows})
	end
	local unique=0;for _ in ids do unique+=1 end
	local result={masters=#rows,meshInstances=instances,uniqueMeshIds=unique,assets=rows}
	local response=Http:RequestAsync({Url=URL.."report/asset-mapping.json",Method="POST",Headers={["Content-Type"]="application/json"},Body=Http:JSONEncode(result)})
	assert(response.Success,response.Body);return {masters=#rows,meshInstances=instances,uniqueMeshIds=unique}
end

return Prep
