--!strict
-- Edit-only lighting pass. Never creates/rebuilds architecture or gameplay.
local H=game:GetService("HttpService")
local v=workspace.World.Cities.Kolkata.Districts.Maidan.VictoriaMemorial
local site=v:GetPivot()
local plan=H:JSONDecode(H:GetAsync("http://127.0.0.1:8769/final-plan.json"))
local function vec(t):Vector3 return Vector3.new(t[1],t[2],t[3]) end
local before={}
for _,p in v:GetDescendants() do if p:IsA("BasePart") and p:GetAttribute("AssetId")~="VIC_B12_LIGHT" then before[p]={p.CFrame,p.Size} end end
local report={scope="Lighting only; approved architecture unchanged",lights={},fixtures=0,shadowLights=0,globalLightingChanged=false}
for _,row in plan.lights do
 local model=assert(v.InteriorArt:FindFirstChild(row.fixtureId or row.id,true),row.id)
 if not row.fixtureId then model:PivotTo(site*CFrame.new(vec(row.position))*CFrame.Angles(0,row.fixtureYaw or 0,0)*CFrame.Angles(row.fixturePitch or 0,0,0)) end
 local diffuser=nil
 for _,p in model:GetDescendants() do if p:IsA("BasePart") and p:GetAttribute("Component")=="Diffuser" then diffuser=p break end end
 assert(diffuser,"No physical fixture for "..row.id)
 for _,o in model:GetDescendants() do if o:IsA("Light") then o:Destroy() end end
 local old=diffuser:FindFirstChild("ArchitecturalWashAim") if old then old:Destroy() end
 diffuser.Material,diffuser.Color,diffuser.CastShadow=Enum.Material.SmoothPlastic,Color3.fromRGB(248,243,227),false
 local light=Instance.new(if row.kind=="Spot" then "SpotLight" else "PointLight")
 light.Name,light.Color,light.Range,light.Brightness,light.Shadows="MuseumIllumination",Color3.fromRGB(unpack(row.color)),row.range,row.brightness,row.shadows
 if light:IsA("SpotLight") then light.Face,light.Angle=Enum.NormalId.Bottom,row.angle end
 if row.target then
  local mount=Instance.new("Attachment") mount.Name,mount.Parent="ArchitecturalWashAim",diffuser
  local clearance=if row.target[2]>=row.position[2] then .35 else -.35
  mount.WorldCFrame=site*CFrame.lookAt(vec(row.position)+Vector3.new(0,clearance,0),vec(row.target))
  light.Face,light.Parent=Enum.NormalId.Front,mount
 else light.Parent=diffuser end
 report.fixtures+=1
 if row.shadows then report.shadowLights+=1 end
 table.insert(report.lights,row)
end
for p,state in before do assert(p.Parent and p.CFrame==state[1] and p.Size==state[2],"Architecture moved during lighting pass: "..p.Name) end
report.architectureUnchanged=true
H:PostAsync("http://127.0.0.1:8769/lighting.json",H:JSONEncode(report),Enum.HttpContentType.ApplicationJson)
return {lights=#report.lights,fixtures=report.fixtures,shadows=report.shadowLights,architectureUnchanged=true}
