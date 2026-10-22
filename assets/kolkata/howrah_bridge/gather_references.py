"""Reference photos only; never incorporated as game textures."""
import json,io,urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
BASE=Path(__file__).resolve().parent
REF=BASE/'references';PHOTO=REF/'photos';PHOTO.mkdir(parents=True,exist_ok=True)

def fetch(row):
 path=PHOTO/(row['id']+'.jpg')
 try:
  if not path.exists():
   request=urllib.request.Request(row['image'],headers={'User-Agent':'Mozilla/5.0'})
   with urllib.request.urlopen(request,timeout=30) as response:data=response.read()
   with Image.open(io.BytesIO(data)) as im:
    im.thumbnail((1500,1200));im.convert('RGB').save(path,quality=91)
  return dict(**row,localPhoto=str(path.relative_to(BASE)).replace('\\','/'),examined=False,usage='Photographic inspiration only; source retains rights. Not game content.')
 except Exception as error:return dict(**row,error=str(error))

if __name__=='__main__':
 rows=json.loads((REF/'catalogue.json').read_text(encoding='utf8'))
 with ThreadPoolExecutor(max_workers=5) as pool:rows=list(pool.map(fetch,rows))
 (REF/'retrieved.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
 for family in ['side','road','ghat','props']:
  group=[r for r in rows if r['category']==family and 'localPhoto' in r]
  w,h=510,385;sheet=Image.new('RGB',(w*2,h*((len(group)+1)//2)),'#19282f');draw=ImageDraw.Draw(sheet)
  for i,row in enumerate(group):
   x,y=i%2*w,i//2*h
   with Image.open(BASE/row['localPhoto']) as im:
    thumb=ImageOps.contain(im,(w-12,h-40));sheet.paste(thumb,(x+(w-thumb.width)//2,y+35+(h-40-thumb.height)//2))
   draw.text((x+10,y+10),row['id']+' '+row['title'][:55],fill='white')
  sheet.save(PHOTO/(family+'-board.jpg'),quality=93)
 print(json.dumps([{'id':r['id'],'retrieved':'localPhoto' in r,'error':r.get('error')} for r in rows]))
