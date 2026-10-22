-- Manual QA only: execute in a Studio MCP Client context during Play.
-- This file is never installed in StarterPlayer or run in the shipped world.
local player=game:GetService("Players").LocalPlayer
local character=player.Character
assert(character,"Start Play and allow the character to spawn before running this check")
local humanoid=character:FindFirstChildOfClass("Humanoid")
local root=character:FindFirstChild("HumanoidRootPart")
assert(humanoid and root,"Character is incomplete")
local run=game:GetService("RunService")
workspace:SetAttribute("FinalWalkStatus","Running")
task.spawn(function()
	local targetPoint: Vector3?=nil
	run:BindToRenderStep("KolkataFinalWalkQA",Enum.RenderPriority.Last.Value+10,function()
		local delta=if targetPoint then Vector3.new(targetPoint.X-root.Position.X,0,targetPoint.Z-root.Position.Z) else Vector3.zero
		humanoid:Move(if delta.Magnitude>0.3 then delta.Unit else Vector3.zero,false)
	end)
	local results={}
	local ok,err=xpcall(function()
		for _,target in {
			{"MarketPassageNorth",94,-98},{"MarketPassageStreet",94,-24},
			{"WestGully",-120,0},{"EmporiumArcade",-175,-40},
			{"NorthBackLane",-120,-105},{"ProvisionsAlcove",-135,-131},
			{"NorthResidentialLoop",-146,-207},{"WestOuterNorth",-264,-207},
			{"WestOuterSouth",-264,195},{"SouthOuterLane",106,195},
			{"SweetShopAisle",-74,131},{"EastGully",156,0},
			{"ZebraCrossing",50,25},{"ExchangeCourtyard",-52,55},
		} do
			local path=game:GetService("PathfindingService"):CreatePath({AgentRadius=2,AgentHeight=5,AgentCanJump=false,WaypointSpacing=10})
			local computed=pcall(function()path:ComputeAsync(root.Position,Vector3.new(target[2],3,target[3]))end)
			local passed=computed and path.Status==Enum.PathStatus.Success
			local begin=os.clock()
			local reason=if passed then "" else "No walkable path"
			if passed then
				for _,waypoint in path:GetWaypoints() do
					targetPoint=waypoint.Position
					local start=os.clock()
					repeat task.wait(0.1) until (Vector3.new(root.Position.X,0,root.Position.Z)-Vector3.new(waypoint.Position.X,0,waypoint.Position.Z)).Magnitude<2 or os.clock()-start>6 or humanoid.Health<=0
					if os.clock()-start>6 or os.clock()-begin>65 or humanoid.Health<=0 then passed=false;reason="Walking timeout";break end
				end
			end
			path:Destroy()
			table.insert(results,{route=target[1],passed=passed,reason=reason,seconds=math.round((os.clock()-begin)*10)/10,position=tostring(root.Position)})
			workspace:SetAttribute("FinalWalkResults",game:GetService("HttpService"):JSONEncode(results))
			if not passed then break end
		end
	end,debug.traceback)
	run:UnbindFromRenderStep("KolkataFinalWalkQA")
	humanoid:Move(Vector3.zero,false)
	workspace:SetAttribute("FinalWalkStatus",if ok then "Finished" else tostring(err))
end)
return {started=true,spawn=tostring(root.Position),health=humanoid.Health}
