"""Retrieve real photographic inspiration; no reference photo is a game texture."""
import json,re,html,io,urllib.request,urllib.error
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from PIL import Image,ImageOps,ImageDraw
ROOT=Path(__file__).resolve().parents[3]
DEST=ROOT/'artifacts/references/tier3';DEST.mkdir(parents=True,exist_ok=True)
CANDIDATES=json.loads((DEST/'candidates.json').read_text(encoding='utf8'))
BLOG='https://kolkatacurry.blogspot.com/2018/04/balconies-and-terraces-of-kolkata-2.html'

def request(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=30) as r:return r.read()

def blog_images():
 page=request(BLOG).decode('utf8','replace')
 urls=[]
 for url in re.findall(r'https://[1-4]\.bp\.blogspot\.com/[^\s<>"\']+',page):
  url=html.unescape(url)
  if re.search(r'\.(jpg|jpeg|png)$',url,re.I) and url not in urls:
   url=re.sub(r'/s\d+/', '/s1200/',url)
   if url not in urls:urls.append(url)
 return [dict(image=u,page=BLOG,title='Kolkata balcony photographic study '+str(i+1)) for i,u in enumerate(urls[:14])]

def download(entry):
 family,index,row=entry
 path=DEST/family/f'{index:02}.jpg';path.parent.mkdir(exist_ok=True)
 try:
  if not path.exists():
   data=request(row['image'])
   with Image.open(io.BytesIO(data)) as img:
    img.thumbnail((1100,1000));img.convert('RGB').save(path,quality=90)
  with Image.open(path) as img:dimensions=img.size
  return dict(**row,family=family,index=index,path=str(path.relative_to(ROOT)),dimensions=dimensions,examined=False,usage='Photographic reference only. Source retains image rights. No photo pixels are used in game assets.')
 except Exception as error:return dict(**row,family=family,index=index,error=str(error))

def board(family,rows):
 good=[r for r in rows if r['family']==family and 'path' in r]
 w,h=420,330;sheet=Image.new('RGB',(w*3,h*((len(good)+2)//3)),'#17252b');draw=ImageDraw.Draw(sheet)
 for i,row in enumerate(good):
  x,y=i%3*w,i//3*h
  with Image.open(ROOT/row['path']) as image:
   thumb=ImageOps.contain(image,(w-14,h-52));sheet.paste(thumb,(x+(w-thumb.width)//2,y+44+(h-52-thumb.height)//2))
  draw.text((x+8,y+8),str(row['index'])+' '+str(row.get('title','Kolkata building'))[:48],fill='white')
 sheet.save(DEST/(family+'-candidates.jpg'),quality=92)

if __name__=='__main__':
 # Multiple photographs from the Kolkata balcony study are individual references,
 # not a single image assigned to many designs.
 try:CANDIDATES['balconyStudy']=blog_images()
 except Exception as error:print('Blog retrieval:',error)
 work=[(family,i+1,row) for family,rows in CANDIDATES.items() for i,row in enumerate(rows)]
 with ThreadPoolExecutor(max_workers=5) as pool:rows=list(pool.map(download,work))
 (DEST/'retrieved.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
 for family in CANDIDATES:
  if any(r['family']==family and 'path' in r for r in rows):board(family,rows)
 print(json.dumps({f:sum(r['family']==f and 'path' in r for r in rows) for f in CANDIDATES}))
 print(json.dumps([{'family':r['family'],'index':r['index'],'error':r['error']} for r in rows if 'error' in r]))
