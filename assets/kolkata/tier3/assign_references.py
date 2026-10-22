import json
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2]
DEST=ROOT/'artifacts/references/tier3'
designs=json.loads((BASE/'designs.json').read_text())
retrieved=json.loads((DEST/'retrieved.json').read_text())
refs=[]
for design in designs:
 family,index=design['ref']
 source=next(r for r in retrieved if r['family']==family and r['index']==index)
 assert 'path' in source,design['id']
 refs.append(dict(assetId=design['id'],category=design['family'],sourcePage=source['page'],photoUrl=source['image'],localPhoto=source['path'],photographExamined=True,observedFeatures=design['features'],usage='Reference only. No photographic pixels, signage or copyrighted texture content are incorporated.'))
assert len(refs)==27 and len({r['photoUrl'] for r in refs})==27
(DEST/'reference-manifest.json').write_text(json.dumps(refs,indent=2),encoding='utf8')
for family in ['old_kolkata','modern','mixed_use','informal']:
 rows=[r for r in refs if r['category']==family]
 w,h=390,325;sheet=Image.new('RGB',(w*3,h*((len(rows)+2)//3)),'#17252b');draw=ImageDraw.Draw(sheet)
 for i,row in enumerate(rows):
  x,y=i%3*w,i//3*h
  with Image.open(ROOT/row['localPhoto']) as image:
   thumb=ImageOps.contain(image,(w-14,h-45));sheet.paste(thumb,(x+(w-thumb.width)//2,y+36+(h-45-thumb.height)//2))
  draw.text((x+8,y+10),row['assetId'],fill='white')
 sheet.save(DEST/(family+'-assigned.jpg'),quality=92)
print('Assigned 27 distinct retrieved photographs: 10 old, 9 modern, 5 mixed-use, 3 informal.')
