--!strict
-- Engine-authored recovery package, including native Terrain, with service bindings.
-- This is .rbxm, NOT a substitute renamed to .rbxl and NOT a publish operation.
local Http=game:GetService("HttpService")
local Serialization=game:GetService("SerializationService")
local WA=game:GetService("ServerStorage").WorldAuthoring
local cfg=WA:FindFirstChild("Task006EnvironmentSettings")
if cfg then cfg:Destroy()end
cfg=Instance.new("Configuration");cfg.Name="Task006EnvironmentSettings"
for service,properties in {
	Lighting={"Brightness","ClockTime","GeographicLatitude","Ambient","OutdoorAmbient","ExposureCompensation","EnvironmentDiffuseScale","EnvironmentSpecularScale","GlobalShadows","LightingStyle","PrioritizeLightingQuality"},
	Workspace={"Gravity","StreamingEnabled"},
	Terrain={"WaterColor","WaterReflectance","WaterTransparency","WaterWaveSize","WaterWaveSpeed"},
}do
	local obj=if service=="Terrain" then workspace.Terrain else game:GetService(service)
	for _,key in properties do
		local ok,value=pcall(function()return obj[key]end)
		if ok then cfg:SetAttribute(service.."_"..key,if typeof(value)=="EnumItem" then tostring(value)else value)end
	end
end
cfg:SetAttribute("PlaceId",game.PlaceId);cfg:SetAttribute("SnapshotFormat","Engine .rbxm with service bindings")
cfg.Parent=WA
local roots={};local bindings={}
for _,service in {"Workspace","Lighting","SoundService","ReplicatedStorage","ReplicatedFirst","ServerScriptService","ServerStorage","StarterGui","StarterPack","StarterPlayer","Teams","MaterialService","LocalizationService","TextChatService"}do
	for _,child in game:GetService(service):GetChildren()do
		if child.Archivable and not child:IsA("Camera")then
			table.insert(roots,child);table.insert(bindings,{index=#roots,service=service,name=child.Name,class=child.ClassName,descendants=#child:GetDescendants()})
		end
	end
end
local data=Serialization:SerializeInstancesAsync(roots)
local total=buffer.len(data);local chunk=240000
for offset=0,total-1,chunk do
	local length=math.min(chunk,total-offset)
	local r=Http:RequestAsync({Url="http://127.0.0.1:8766/snapshot/final.rbxm",Method="POST",Headers={["Content-Type"]="application/octet-stream",["X-Chunk-Index"]=tostring(offset/chunk),["X-Final"]=if offset+length==total then "1"else "0"},Body=buffer.readstring(data,offset,length)})
	assert(r.Success,r.Body);task.wait()
end
-- Reopen with the same engine parser, without inserting duplicates into the world.
local reopened=Serialization:DeserializeInstancesAsync(data)
local checks={roots=#reopened,hasWorld=false,hasTerrain=false,hasMasters=false}
for _,root in reopened do
	if root.Name=="World"then checks.hasWorld=root:FindFirstChild("Kolkata",true)~=nil end
	if root:IsA("Terrain")then checks.hasTerrain=true end
	if root.Name=="WorldAuthoring"then checks.hasMasters=root:FindFirstChild("Masters",true)~=nil end
	root:Destroy()
end
assert(checks.hasWorld and checks.hasTerrain and checks.hasMasters,"Incomplete recovery package")
local report={type="Engine model recovery, not a full place file",placeId=game.PlaceId,path="artifacts/HoodTesting-Task006.rbxm",bytes=total,bindings=bindings,engineReopen=checks,nativeTerrainIncluded=true,environmentSettings="ServerStorage.WorldAuthoring.Task006EnvironmentSettings",preSnapshot="artifacts/recovery/HoodTesting-pre-Task006.rbxm",fullPlacePreSaveWaivedByUser=true,nativePlaceFileSaved=false}
local r=Http:RequestAsync({Url="http://127.0.0.1:8766/report/snapshot.json",Method="POST",Headers={["Content-Type"]="application/json"},Body=Http:JSONEncode(report)})
assert(r.Success,r.Body)
return Http:JSONEncode({bytes=total,bindings=#bindings,engineReopen=checks,nativeTerrainIncluded=true})
