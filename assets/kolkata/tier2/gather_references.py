"""Download photographic architectural references only, never game textures."""
import json
import hashlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageOps, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
DEST = ROOT / "artifacts/references/tier2"
CATEGORIES = {
    "writers_building": "Writers' Building",
    "gpo": "General Post Office, Kolkata",
    "metropolitan_building": "Metropolitan Building (Kolkata)",
    "town_hall": "Kolkata Town Hall",
    "jorasanko_thakur_bari": "Maharshi Bhawan, Jorasanko Thakur Bari",
}

def api(params):
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(dict(action="query",format="json",**params))
    req = urllib.request.Request(url,headers={"User-Agent":"IndianHoodArchitecturalReference/1.0"})
    for delay in [0,3,9]:
        if delay:time.sleep(delay)
        try:
            with urllib.request.urlopen(req,timeout=35) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code!=429 or delay==9:raise

def catalogue(item):
    key,category = item
    result = api(dict(list="categorymembers",cmtitle="Category:"+category,cmtype="file",cmlimit=100))
    return key,[r["title"] for r in result["query"]["categorymembers"]]

def download(item):
    key,index,title = item
    filename=title[5:].replace(' ','_')
    digest=hashlib.md5(filename.encode('utf8')).hexdigest()
    quoted=urllib.parse.quote(filename)
    original=f'https://upload.wikimedia.org/wikipedia/commons/{digest[0]}/{digest[:2]}/{quoted}'
    info=dict(url=original,thumburl=f'https://upload.wikimedia.org/wikipedia/commons/thumb/{digest[0]}/{digest[:2]}/{quoted}/960px-{quoted}',descriptionurl='https://commons.wikimedia.org/wiki/'+urllib.parse.quote(title.replace(' ','_')))
    url = info.get("thumburl",info["url"])
    path = DEST/key/f"{index:02d}.jpg"
    path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists():
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=35) as response:
                data=response.read()
        except urllib.error.HTTPError:
            url=original
            with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=45) as response:
                data=response.read()
        with Image.open(__import__('io').BytesIO(data)) as image:
            image.thumbnail((1400,1100));image.convert("RGB").save(path,quality=91)
    meta=info.get("extmetadata",{})
    plain=lambda name:re.sub('<[^>]+>','',meta.get(name,{}).get("value",""))
    return dict(building=key,index=index,title=title,url=url,page=info["descriptionurl"],artist=plain("Artist") or "See linked file page",license=plain("LicenseShortName") or "See linked file page; no photograph incorporated in game assets",description=plain("ImageDescription"),path=str(path.relative_to(ROOT)),usage="Reference only; not used as texture, mesh or incorporated game content")

def board(key,rows):
    width,height=550,390
    sheet=Image.new("RGB",(width*2,height*((len(rows)+1)//2)),"#17252b")
    draw=ImageDraw.Draw(sheet)
    for i,row in enumerate(rows):
        x,y=i%2*width,i//2*height
        with Image.open(ROOT/row["path"]) as img:
            thumb=ImageOps.contain(img,(width-16,height-55))
            sheet.paste(thumb,(x+(width-thumb.width)//2,y+45+(height-55-thumb.height)//2))
        draw.text((x+8,y+8),str(row["index"])+" "+row["title"][5:65],fill="white")
    sheet.save(DEST/key/"reference-board.jpg",quality=92)

if __name__ == "__main__":
    DEST.mkdir(parents=True,exist_ok=True)
    if len(sys.argv)==1:
        with ThreadPoolExecutor(max_workers=3) as pool:
            catalog=dict(pool.map(catalogue,CATEGORIES.items()))
        (DEST/"catalogue.json").write_text(json.dumps(catalog,indent=2),encoding="utf8")
        print(json.dumps(catalog,indent=1))
    else:
        choices=json.loads((DEST/"selected.json").read_text(encoding="utf8"))
        work=[(key,i+1,title) for key,titles in choices.items() for i,title in enumerate(titles)]
        with ThreadPoolExecutor(max_workers=5) as pool:
            rows=list(pool.map(download,work))
        (DEST/"sources.json").write_text(json.dumps(rows,indent=2),encoding="utf8")
        for key in choices:board(key,[r for r in rows if r["building"]==key])
        print(json.dumps({key:sum(r["building"]==key for r in rows) for key in choices}))
