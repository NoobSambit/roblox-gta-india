import json,urllib.request,io
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from gather_references import ROOT,DEST,board
choices=json.loads((Path(__file__).parent/'alternate_references.json').read_text())
def fetch(entry):
 key,i,(url,page,angle)=entry
 path=DEST/key/f'alt-{i:02}.jpg';path.parent.mkdir(parents=True,exist_ok=True)
 try:
  if not path.exists():
   request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
   with urllib.request.urlopen(request,timeout=30) as r:data=r.read()
   with Image.open(io.BytesIO(data)) as image:
    image.thumbnail((1400,1100));image.convert('RGB').save(path,quality=91)
  return dict(building=key,index=f'alt-{i}',title='File:'+angle,url=url,page=page,path=str(path.relative_to(ROOT)),usage='Reference only; photographer/source retain rights. No photo is incorporated in exported assets.')
 except Exception as e:return dict(building=key,url=url,error=str(e))
work=[(key,i+1,row) for key,rows in choices.items() for i,row in enumerate(rows)]
with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(fetch,work))
# Preserve successfully cached Commons images, even when other requests throttled.
selected=json.loads((DEST/'selected.json').read_text())
for key,titles in selected.items():
 for i,title in enumerate(titles):
  path=DEST/key/f'{i+1:02}.jpg'
  if path.exists():rows.append(dict(building=key,index=i+1,title=title,page='https://commons.wikimedia.org/wiki/'+title.replace(' ','_'),path=str(path.relative_to(ROOT)),usage='Reference only; see source for photographer and licence. Not incorporated into game assets.'))
(DEST/'sources.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
for key in selected:board(key,[r for r in rows if r['building']==key and 'path' in r])
print(json.dumps({key:sum(r['building']==key and 'path' in r for r in rows) for key in selected}))
print(json.dumps([r for r in rows if 'error' in r]))
