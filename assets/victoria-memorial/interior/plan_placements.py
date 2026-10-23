"""Offline art assignment only. Does not write to Roblox Studio."""
import collections
import json
import math
from pathlib import Path
BASE=Path(__file__).resolve().parent

def main():
    locked=json.loads((BASE/'layout-lock.json').read_text())
    assets={r['assetId']:r for r in json.loads((BASE/'asset-manifest.json').read_text())['assets']}
    instances=[];bindings=[];security_bindings=[];artwork_bindings=[]
    def put(asset,position,room,owner,role,yaw=0):
        row=dict(instanceId=f"VIC_ART_{len(instances)+1:03}",assetId='VIC_'+asset,position=position,yaw=yaw,roomId=room,sourceMarker=owner,role=role)
        instances.append(row)
        return row['instanceId']
    choices=[
        ('E06_DOCUMENT_DESK','L02_LETTER',2.31),
        ('A10_FEATURE_PANEL','ART_01_RIVER_DAWN',0),
        ('E06_DOCUMENT_DESK','L01_FOLIO',2.31),
        ('E01_CASE_SMALL','L12_MINIATURE',1.72),
        ('E02_CASE_MEDIUM','L05_TRADE_COLLECTION',1.72),
        ('A07_PLINTH_OCTAGON','L09_KEEPSAKE',1.6),
        ('E02_CASE_MEDIUM','L07_PRESENTATION_SET',1.72),
        ('A10_FEATURE_PANEL','ART_02_MONSOON_STREET',0),
        ('A10_FEATURE_PANEL','ART_04_HERITAGE_SKYLINE',0),
        ('A10_FEATURE_PANEL','ART_03_GARDEN_STUDY',0),
        ('E06_DOCUMENT_DESK','L14_RIVER_PORTFOLIO',2.31),
        ('A07_PLINTH_OCTAGON','L06_ABSTRACT_BRONZE',1.6),
        ('E02_CASE_MEDIUM','L08_CEREMONIAL_VESSEL',1.72),
        ('A06_PLINTH_SQUARE','L05_TRADE_COLLECTION',1.6),
        ('E03_CASE_PREMIUM','L10_PREMIUM_INSIGNIA',1.72),
        ('E03_CASE_PREMIUM','L08_CEREMONIAL_VESSEL',1.72),
        ('E03_CASE_PREMIUM','L11_RARE_ARCHIVE_FOLIO',1.72),
        ('E01_CASE_SMALL','L07_PRESENTATION_SET',1.72),
    ]
    for marker,(support,loot,mount_y) in zip(locked['loot'],choices):
        x,y,z=marker['rootPosition'];room=marker['roomId'];owner=marker['lootId']
        center=next(r for r in locked['rooms'] if r['roomId']==room)['centerXZ']
        yaw=math.pi if z<center[1] or room=='VIC_ROOM_ARCHIVE' else 0
        ids=[put(support,[x,y,z],room,owner,'ExhibitSupport',yaw)]
        if support=='A10_FEATURE_PANEL':
            # Reuse the physical frame/backing; artwork is an image binding only.
            def mount(offset):
                dx,dy,dz=offset;c,s=math.cos(yaw),math.sin(yaw)
                return [x+c*dx+s*dz,y+dy,z-s*dx+c*dz]
            frame_id=put('E04_FRAME_LANDSCAPE',mount([0,2.15,-.04]),room,owner,'Frame',yaw)
            ids.append(frame_id)
            artwork_bindings.append(dict(lootId=owner,artworkId=loot,frameInstance=frame_id,
                targetComponent='Canvas',targetFace='Front (-Z)',aspectRatio=1.5,
                implementation='Reuse uploaded image ID on existing frame backing; no sculpted art mesh'))
        else:
            ids.append(put(loot,[x,y+mount_y,z],room,owner,'LootVisual',yaw))
        bindings.append(dict(lootId=owner,sourceRootPosition=marker['rootPosition'],sourcePlaceholderCenter=marker['placeholderCenter'],
            supportAsset='VIC_'+support,lootAsset=None if loot.startswith('ART_') else 'VIC_'+loot,artworkId=loot if loot.startswith('ART_') else None,instances=ids,
            allowedFootprintXZ=[6,6] if owner in ['VIC_LOOT_015','VIC_LOOT_016','VIC_LOOT_017'] else [4,4]))
    for marker in locked['security']:
        owner=marker['securityId'];x,_,z=marker['padCenter'];room=marker['roomId'];ids=[]
        if marker['type']=='StaticLaserGrid':
            for sign in [-1,1]:
                ids.append(put('S01_STATIC_EMITTER',[x,6.8,z+sign*marker['footprintXZ'][1]/2],room,owner,'Emitter',math.pi if sign<0 else 0))
        elif marker['type']=='MovingLaser':ids.append(put('S02_MOVING_HOUSING',[x,6.8,z],room,owner,'Housing'))
        elif marker['type']=='ElectricalFloor':ids.append(put('S03_ELECTRIC_FLOOR',[x,6.8,z],room,owner,'FloorInlay'))
        elif marker['type']=='SecurityTerminal':ids.append(put('S04_TERMINAL',[x,6.8,z],room,owner,'Terminal'))
        else:
            # Cases are already the loot support: never instantiate a second case.
            loot_id='VIC_LOOT_'+{'VIC_SECURITY_CASE_001':'015','VIC_SECURITY_CASE_002':'016','VIC_SECURITY_CASE_003':'017'}[owner]
            ids=[next(b for b in bindings if b['lootId']==loot_id)['instances'][0]]
        security_bindings.append(dict(securityId=owner,sourcePadCenter=marker['padCenter'],reservedFootprintXZ=marker['footprintXZ'],instances=ids))
    # Repeated short trims on existing gallery wall surfaces, leaving courtyard gaps.
    def wing_room(x,z):
        if z>0:return 'VIC_ROOM_GALLERY_A' if x<0 else 'VIC_ROOM_GALLERY_B'
        if x<0:return 'VIC_ROOM_GALLERY_C' if x<-66 else 'VIC_ROOM_PUBLIC'
        return 'VIC_ROOM_ARCHIVE' if x>69 else 'VIC_ROOM_HIGH_SECURITY'
    for side in [-1,1]:
        for wing in [-1,1]:
            for z,xs in [(side*93.10,[36.5+i*8 for i in range(7)]),(side*58.90,[40,48,68.5,76.5,84.5])]:
                for xx in xs:
                    x=wing*xx;room=wing_room(x,z)
                    put('A04_DADO_8',[x,6.8,z],room,'ExistingWall','WallDado')
                    put('A05_CORNICE_8',[x,21.6,z],room,'ExistingWall','WallCornice')
    for x in [-65.3,68.3]:
        for z in [-84,-66]:
            room='VIC_ROOM_PUBLIC' if x<0 else 'VIC_ROOM_HIGH_SECURITY'
            yaw=-math.pi/2 if x<0 else math.pi/2
            put('A03_ARCH_10',[x,6.8,z],room,'ExistingPartitionDoor','ArchOverlay',yaw)
            if x>0:put('A09_RESTRICTED_PORTAL',[x-.20,6.8,z],room,'ExistingPartitionDoor','RestrictedOverlay',yaw)
    for x,z in [(-18,-17),(18,17)]:put('E08_INFO_STAND',[x,7.04,z],'VIC_ROOM_MAIN_HALL','HallWayfinding','InformationStand')
    # Known solid partition piers provide vertical colour without covering windows.
    for x,room,yaw in [(-65.3,'VIC_ROOM_PUBLIC',-math.pi/2),(-66.7,'VIC_ROOM_GALLERY_C',math.pi/2),(68.3,'VIC_ROOM_HIGH_SECURITY',math.pi/2),(69.7,'VIC_ROOM_ARCHIVE',-math.pi/2)]:
        put('A11_MUSEUM_BANNER',[x,14.0,-75],room,'ExistingPartitionPier','MuseumBanner',yaw)
    # The archive benefits from one functional wall anchor, outside both return lanes.
    put('E07_ARCHIVE_CABINET',[79.5,6.8,-92.35],'VIC_ROOM_ARCHIVE','ArchiveWall','SecureArchiveDressing',math.pi)
    # Floor colour gives the intentionally open gallery space a clear composition.
    # Keep the optional high-security pad and archive loop free of runner graphics.
    for room,xs,z in [
        ('VIC_ROOM_PUBLIC',[-56,-48,-40],-76),
        ('VIC_ROOM_GALLERY_A',[-40,-48,-56,-64,-72,-80],76),
        ('VIC_ROOM_GALLERY_B',[40,48,56,64,72,80],76),
    ]:
        for x in xs:put('A12_FLOOR_RUNNER_8',[x,6.805,z],room,'ExistingFloor','FlatRunner')
    counts=collections.Counter(p['assetId'] for p in instances)
    report=dict(task='008',status='Offline integration plan; no Studio edits',units=locked['units'],
        rooms=locked['rooms'],lootBindings=bindings,securityBindings=security_bindings,artworkBindings=artwork_bindings,instances=instances,
        countSummary=dict(assetsCreated=len(assets),assetsUsed=len(counts),instances=len(instances),
            uniqueCreatedTriangles=sum(r['triangles'] for r in assets.values()),
            uniqueUsedTriangles=sum(assets[k]['triangles'] for k in counts),
            proposedPassTriangles=sum(assets[k]['triangles']*v for k,v in counts.items()),
            byCategory={c:sum(assets[k]['triangles']*v for k,v in counts.items() if assets[k]['category']==c) for c in ['Architecture','Exhibition','Loot','Security']}),
        usage=[dict(assetId=k,instances=v,trianglesPerAsset=assets[k]['triangles'],placedTriangles=assets[k]['triangles']*v) for k,v in sorted(counts.items())],
        optionalLibraryAssets=[k for k in assets if k not in counts],
        collisionPolicy='Decoration stays non-colliding; retain authored floor/wall and simple exhibit collision. No asset enables damage/touch logic.',
        upperFloor='Unchanged and unused',sourceHashes=locked['sourceHashes'])
    # Required marker coverage and support footprint checks only, not a flow test.
    assert len(bindings)==18 and len(security_bindings)==9
    assert len(artwork_bindings)==4
    for b in bindings:
        d=assets[b['supportAsset']]['dimensionsStuds']
        assert d['width']<=b['allowedFootprintXZ'][0]+1e-5 and d['depth']<=b['allowedFootprintXZ'][1]+1e-5,(b['lootId'],d)
    (BASE/'placement-manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report['countSummary']))

if __name__=='__main__':main()
