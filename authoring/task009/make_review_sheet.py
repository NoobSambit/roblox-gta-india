"""Assemble original Blender previews with host Pillow; no source image editing."""
import json,math
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'assets/victoria-memorial/interior/task009'
manifest=json.loads((BASE/'two-storey-manifest.json').read_text())
sheet=Image.new('RGB',(5*320,math.ceil(len(manifest['assets'])/5)*360),(27,31,36))
draw=ImageDraw.Draw(sheet)
for i,row in enumerate(manifest['assets']):
    im=Image.open(BASE/row['preview']).convert('RGB');im.thumbnail((312,312))
    x=(i%5)*320;y=(i//5)*360
    sheet.paste(im,(x+(320-im.width)//2,y))
    draw.text((x+8,y+315),row['assetId'],fill=(240,231,211))
    draw.text((x+8,y+335),str(row['triangles'])+' triangles',fill=(179,186,190))
dest=ROOT/'artifacts/review/task009/blender/new_asset_contact_sheet.png'
sheet.save(dest)
print(str(dest))
