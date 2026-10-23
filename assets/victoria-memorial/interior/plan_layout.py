"""Read-only extraction of Task 007's approved layout for the art handoff."""
import csv
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
SOURCE = ROOT / "authoring/task007/BuildGreybox.luau"

def rows(source, start, end):
    block = source.split(start, 1)[1].split(end, 1)[0]
    result = []
    for line in block.splitlines():
        line = line.strip().rstrip(",")
        if line.startswith("{") and line.endswith("}"):
            result.append(next(csv.reader([line[1:-1]], skipinitialspace=True)))
    return result

def lock_layout():
    source = SOURCE.read_text(encoding="utf8")
    rooms = rows(source, "local rooms = {", "\n\t}\n\tfor _, r")
    loot = rows(source, "local loot = {", "\n\t}\n\tfor index")
    security = rows(source, "local security = {", "\n\t}\n\tfor _, s")
    exits = rows(source, "local exits = {", "\n\t}\n\tfor _, e")
    locked = {
        "source": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "units": "Roblox studs, landmark-local Y-up; Blender maps (x,-z,y)",
        "rooms": [dict(roomId="VIC_ROOM_"+r[0], name=r[1], centerXZ=[float(r[2]),float(r[3])], sizeXZ=[float(r[4]),float(r[5])], risk=r[6]) for r in rooms],
        "loot": [dict(lootId=f"VIC_LOOT_{i:03}", roomId="VIC_ROOM_"+r[0], rootPosition=[float(r[1]),6.8,float(r[2])], placeholderCenter=[float(r[1]),9.6,float(r[2])], footprintXZ=[4,4], category=r[3], name=r[4]) for i,r in enumerate(loot,1)],
        "security": [dict(securityId="VIC_SECURITY_"+r[0], type=r[1], roomId="VIC_ROOM_"+r[2], tier=int(r[3]), padCenter=[float(r[4]),6.98,float(r[5])], footprintXZ=[float(r[6]),float(r[7])], note=r[8]) for r in security],
        "exits": [dict(routeId="VIC_EXIT_"+r[0], position=[float(r[1]),6.12,float(r[2])], note=r[3], footprintXZ=[float(r[4]),float(r[5])]) for r in exits],
        "restricted": [dict(id="VIC_RESTRICTED_001",roomId="VIC_ROOM_HIGH_SECURITY",center=[50,17,-76],size=[36,20.4,34]),dict(id="VIC_RESTRICTED_002",roomId="VIC_ROOM_ARCHIVE",center=[79.5,17,-76],size=[19,20.4,34])],
        "partitionDoorways": dict(partitionX=[-66,69], doorwayZ=[-84,-66], clearWidth=10, clearHeight=14),
        "sourceHashes": {},
    }
    for rel in ["authoring/task007/BuildGreybox.luau","docs/task007/inspection.json","docs/task007/snapshot.json","artifacts/VictoriaMemorial-Task007.rbxm","assets/victoria-memorial/VictoriaMemorial.blend","assets/victoria-memorial/assembly-manifest.json"]:
        locked["sourceHashes"][rel] = hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
    assert (len(rooms),len(loot),len(security),len(exits)) == (7,18,9,4)
    (BASE/"layout-lock.json").write_text(json.dumps(locked,indent=2)+"\n")
    return locked

if __name__ == "__main__":
    result=lock_layout()
    print("Locked Task007: 7 rooms, 18 loot, 9 security, 4 exits; originals read-only")
