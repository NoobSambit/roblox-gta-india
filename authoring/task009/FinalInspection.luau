--!strict
-- One focused metadata/import/light checkpoint; no gameplay or benchmark suite.
local H=game:GetService("HttpService")
local v=workspace.World.Cities.Kolkata.Districts.Maidan.VictoriaMemorial
local old=H:JSONDecode(H:GetAsync("http://127.0.0.1:8769/audit.json"))
local plan=H:JSONDecode(H:GetAsync("http://127.0.0.1:8769/final-plan.json"))
local report={scope="Focused edit-time metadata, exterior, import and lighting check; no gameplay/device test",issues={},originalMarkers=0,exteriorParts=0,lights=0,shadowLights=0,images={},statistics=plan.statistics}
local function issue(text) table.insert(report.issues,text) end
for group,rows in old.markers do
 for _,row in rows do
  local o=v.HeistGreybox[group]:FindFirstChild(row.name)
  if not o then issue("Missing marker "..row.name) continue end
  local cf=if o:IsA("Model") then o:GetPivot() else o.CFrame
  local a,b={cf:GetComponents()},row.cframe
  for i=1,12 do if math.abs(a[i]-b[i])>.001 then issue("Moved original marker "..row.name) break end end
  for k,val in row.attributes do if o:GetAttribute(k)~=val then issue("Changed original attribute "..row.name.."."..k) end end
  report.originalMarkers+=1
 end
end
local matchedExterior={}
for _,row in old.parts do if row.path:find(".Exterior.",1,true) then
 -- Original marble courses share sibling names. Match each baseline transform
 -- once instead of resolving every repeated name to the first sibling.
 local names=string.split(row.path,".")
 local parent=game
 for i=1,#names-1 do parent=parent and parent:FindFirstChild(names[i]) end
 local p=nil
 if parent then for _,candidate in parent:GetChildren() do
  if candidate.Name~=names[#names] or not candidate:IsA("BasePart") or matchedExterior[candidate] then continue end
  local exact=(candidate.Size-Vector3.new(unpack(row.size))).Magnitude<.001
  local a={candidate.CFrame:GetComponents()}
  for i=1,12 do if math.abs(a[i]-row.cframe[i])>.001 then exact=false break end end
  if candidate:IsA("MeshPart") and candidate.MeshId~=row.meshId then exact=false end
  if exact then p=candidate break end
 end end
 if not p or not p:IsDescendantOf(v.Exterior) then issue("Missing exterior "..row.path) continue end
 matchedExterior[p]=true
 if (p.Size-Vector3.new(unpack(row.size))).Magnitude>.001 then issue("Exterior size "..row.path) end
 local a={p.CFrame:GetComponents()} for i=1,12 do if math.abs(a[i]-row.cframe[i])>.001 then issue("Exterior transform "..row.path) break end end
 if p:IsA("MeshPart") and p.MeshId~=row.meshId then issue("Exterior mesh "..row.path) end
 report.exteriorParts+=1
end end
local ids={}
for _,p in plan.instances do
 local m=v.InteriorArt:FindFirstChild(p.instanceId,true)
 if not m or m:GetAttribute("AssetId")~=p.assetId then issue("Missing final art "..p.instanceId) end
 if ids[p.instanceId] then issue("Duplicate art ID "..p.instanceId) end ids[p.instanceId]=true
end
for _,o in v:GetDescendants() do
 if o:IsA("Light") then report.lights+=1 if o.Shadows then report.shadowLights+=1 end end
 if o:IsA("ImageLabel") and o.Name=="Painting" then table.insert(report.images,{image=o.Image,loaded=o.IsLoaded}) end
end
report.loot=#v.HeistGreybox.LootMarkers:GetChildren()
report.security=#v.HeistGreybox.SecurityMarkers:GetChildren()
report.rooms=#v.HeistGreybox.RoomZones:GetChildren()
report.routes=#v.HeistGreybox.EntryExitMarkers:GetChildren()
assert(report.loot==28 and report.security==16 and report.routes==4)
assert(report.lights==52 and report.shadowLights==2)
H:PostAsync("http://127.0.0.1:8769/inspection.json",H:JSONEncode(report),Enum.HttpContentType.ApplicationJson)
return H:JSONEncode(report)
