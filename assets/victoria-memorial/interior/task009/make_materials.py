"""Two original periodic low-noise stone colour tiles; no baked lighting or PBR sets."""
import math,json,hashlib
from pathlib import Path
from PIL import Image
BASE=Path(__file__).resolve().parent
folder=BASE/'materials';folder.mkdir(exist_ok=True)
n=512;image=Image.new('RGB',(n,n));pixels=image.load()
for y in range(n):
    for x in range(n):
        u,v=x/n,y/n
        broad=1.2*math.sin(math.tau*(u+v))+.8*math.cos(math.tau*(3*u-2*v))
        vein=max(0,math.cos(math.tau*(3*u+2*v)+.65*math.sin(math.tau*(u-v))))**12
        seam=5 if min(x%256,255-x%256,y%256,255-y%256)<1 else 0
        delta=broad-2.2*vein-seam
        pixels[x,y]=tuple(round(c+delta) for c in (226,222,213))
path=folder/'VIC009_PaleStoneFloor_512.png';image.save(path)
row=dict(name='VIC009_PaleStoneFloor',source='Original procedural colour texture',resolution=[512,512],
    baseMaterial='Marble',studsPerTile=12,tileGrid=[2,2],uniqueRuntimeTextures=1,
    maps=['ColorMap'],bakedLighting=False,periodic=True,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
row.update({k:v for k,v in (json.loads((folder/'material.json').read_text()) if (folder/'material.json').exists() else {}).items() if k in ['robloxImageId','uploadStatus']})
(folder/'material.json').write_text(json.dumps(row,indent=2)+'\n')
print(json.dumps(row))

# Repeated broad walls benefit from a quiet finish instead of the built-in
# limestone's conspicuous cloudy mottling at this monumental scale.
wall=Image.new('RGB',(256,256));pixels=wall.load()
for y in range(256):
    for x in range(256):
        u,v=x/256,y/256
        c=round(250+.9*math.sin(math.tau*(u+v))+.5*math.cos(math.tau*(3*u-v)))
        pixels[x,y]=(c,c,c)
path=folder/'VIC009_WarmStone_256.png';wall.save(path)
row=dict(name='VIC009_WarmStone',source='Original procedural colour texture',resolution=[256,256],
    baseMaterial='Limestone',studsPerTile=14,uniqueRuntimeTextures=1,maps=['ColorMap'],
    bakedLighting=False,periodic=True,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
row.update({k:v for k,v in (json.loads((folder/'wall-material.json').read_text()) if (folder/'wall-material.json').exists() else {}).items() if k in ['robloxImageId','uploadStatus']})
(folder/'wall-material.json').write_text(json.dumps(row,indent=2)+'\n')
print(json.dumps(row))
