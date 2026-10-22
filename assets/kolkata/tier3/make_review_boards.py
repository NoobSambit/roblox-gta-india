"""Small review contact sheets and a compact readable asset index."""
import json
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont

BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2];OUT=ROOT/'artifacts/review/tier3'
rows=json.loads((BASE/'asset-manifest.json').read_text(encoding='utf8'))
fontpath=Path('C:/Windows/Fonts/segoeui.ttf')
font=ImageFont.truetype(str(fontpath),19);small=ImageFont.truetype(str(fontpath),16)
for family in ['old_kolkata','modern','mixed_use','informal']:
    group=[r for r in rows if r['family']==family]
    if not group or not all((OUT/(r['id']+'.png')).exists() for r in group):continue
    w,h=430,470;header=55
    sheet=Image.new('RGB',(w*3,h*((len(group)+2)//3)+header),'#18282f');draw=ImageDraw.Draw(sheet)
    draw.text((18,14),family.replace('_',' ').upper()+' | TIER 3',font=font,fill='#e6e3d4')
    for i,row in enumerate(group):
        x,y=i%3*w,i//3*h+header
        with Image.open(OUT/(row['id']+'.png')) as im:sheet.paste(im.resize((w-12,w-12)),(x+6,y))
        draw.text((x+12,y+w-8),row['id']+'  |  '+str(row['triangles'])+' tris',font=small,fill='white')
        draw.text((x+12,y+w+13),row['name'],font=small,fill='#aec6ca')
    sheet.save(OUT/(family+'-review.jpg'),quality=94)
print('Updated available family contact sheets.')
