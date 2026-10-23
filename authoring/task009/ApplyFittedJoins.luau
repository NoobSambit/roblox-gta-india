--!strict
-- Edit-only update from the corrected Blender plan; no runtime installation.
local H=game:GetService("HttpService")
local S=game:GetService("ServerStorage")
local v=workspace.World.Cities.Kolkata.Districts.Maidan.VictoriaMemorial
local art,site=v.InteriorArt,v:GetPivot()
local plan=H:JSONDecode(H:GetAsync("http://127.0.0.1:8769/final-plan.json"))
local masters=S.WorldAuthoring.Task009Assets
for _,id in {"VIC_B15_DRUM_TRANSITION","VIC_B16_PORTAL_SPANDREL"} do assert(masters:FindFirstChild(id,true),"Import the two Blender correction meshes first") end
local archive=Instance.new("Folder") archive.Name="SupersededJoinAssembly" archive.Parent=S.WorldAuthoring.Task009Archive
local function vec(t):Vector3 return Vector3.new(t[1],t[2],t[3]) end
local function finish(p)
 p.Anchored,p.CanCollide,p.CanTouch,p.CanQuery=true,false,false,false
 p.Color,p.Material,p.MaterialVariant=Color3.fromRGB(232,226,211),Enum.Material.Limestone,"VIC009_WarmStone"
end
for _,r in plan.instances do
 if r.assetId=="VIC_B04_UPPER_LINING" or r.assetId=="VIC_B15_DRUM_TRANSITION" or r.assetId=="VIC_B16_PORTAL_SPANDREL" then
  local old=art.TwoStoreyArchitecture:FindFirstChild(r.instanceId)
  if old then old.Parent=archive end
  local m=masters:FindFirstChild(r.assetId,true):Clone() m.Name=r.instanceId
  m:SetAttribute("ArtInstanceId",r.instanceId) m:SetAttribute("ArtRole",r.role) m:SetAttribute("RoomId",r.roomId)
  m:SetAttribute("ArtScale",r.scale) m:SetAttribute("SourceMarker",r.sourceMarker or "")
  m:ScaleTo(r.scale)
  for _,p in m:GetDescendants() do if p:IsA("BasePart") then
   if r.stretch then local cf=p.CFrame local s=vec(r.stretch) p.Size*=s p.CFrame=CFrame.new(cf.Position*s)*cf.Rotation end
   finish(p)
  end end
  m:PivotTo(site*CFrame.new(vec(r.position))*CFrame.Angles(0,r.yaw,0))
  m.Parent=art.TwoStoreyArchitecture
 end
end
-- Reassemble only our source-matched visible Parts, retaining their old version.
art.TwoStoreyArchitecture.SourceMatchedNativeStructure.Parent=archive
local native=Instance.new("Folder") native.Name="SourceMatchedNativeStructure" native.Parent=art.TwoStoreyArchitecture
for _,r in plan.nativeStructure do if r.purpose~="InvisibleCollision" then
 local p=Instance.new("Part") p.Name,p.Size,p.CFrame=r.name,vec(r.size),site*CFrame.new(vec(r.position))*CFrame.Angles(0,r.yaw,0)
 p.Anchored,p.CanCollide,p.CanTouch,p.CanQuery=true,r.solid,false,r.solid
 p.TopSurface,p.BottomSurface=Enum.SurfaceType.Smooth,Enum.SurfaceType.Smooth
 p:SetAttribute("Task009Native",true) p:SetAttribute("Purpose",r.purpose)
 p.Color=if r.material=="Brass" then Color3.fromRGB(184,155,96) elseif r.material=="Charcoal" then Color3.fromRGB(52,63,69) elseif r.material=="Teal" then Color3.fromRGB(36,93,99) elseif r.material=="Oxblood" then Color3.fromRGB(136,72,63) elseif r.material=="Mushroom" then Color3.fromRGB(162,157,147) else Color3.fromRGB(232,226,211)
 p.Material=if r.material=="Brass" or r.material=="Charcoal" then Enum.Material.Metal elseif r.purpose=="Carpet" then Enum.Material.Fabric else Enum.Material.Limestone
 if p.Material==Enum.Material.Limestone then p.MaterialVariant="VIC009_WarmStone" end
 p.Parent=native
end end
for _,r in plan.lights do
 local m=art:FindFirstChild(r.fixtureId or r.id,true)
 if not r.fixtureId then m:PivotTo(site*CFrame.new(vec(r.position))*CFrame.Angles(0,r.fixtureYaw or 0,0)*CFrame.Angles(r.fixturePitch or 0,0,0)) end
 for _,l in m:GetDescendants() do if l:IsA("Light") then
  l.Brightness,l.Range=r.brightness,r.range
  if r.target then local a=l.Parent assert(a:IsA("Attachment")) local clearance=if r.target[2]>=r.position[2] then .35 else -.35 a.WorldCFrame=site*CFrame.lookAt(vec(r.position)+Vector3.new(0,clearance,0),vec(r.target)) end
 end end
end
art:SetAttribute("ArtInstanceCount",#plan.instances)
art:SetAttribute("PlacedMeshTriangles",plan.statistics.importedPlacedTriangles)
local report=H:JSONDecode(H:GetAsync("http://127.0.0.1:8769/integration.json"))
report.instances,report.nativeStructure,report.lights,report.statistics=plan.instances,plan.nativeStructure,plan.lights,plan.statistics
report.fittedBlenderCorrections=true
H:PostAsync("http://127.0.0.1:8769/integration.json",H:JSONEncode(report),Enum.HttpContentType.ApplicationJson)
return {artInstances=#plan.instances,lights=#plan.lights,fittedJoins=true}
