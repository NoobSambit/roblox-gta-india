"""Index original asset previews and make compact review contact sheets."""
import json,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps

BASE=Path(__file__).resolve().parent

def finish():
 rows=json.loads((BASE/'asset-manifest.json').read_text(encoding='utf8'))
 for row in rows:
  folder=(BASE/row['source']).parent
  row['previews']=[str(p.relative_to(BASE)).replace('\\','/') for p in sorted(folder.glob('preview*.png'))]
  assert row['previews'],row['assetId']
  (folder/'asset.json').write_text(json.dumps(row,indent=2),encoding='utf8')
 (BASE/'asset-manifest.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
 review=BASE/'review';review.mkdir(exist_ok=True)
 font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',15)
 def board(items,name,cols,tile):
  width,height=tile;sheet=Image.new('RGB',(cols*width,math.ceil(len(items)/cols)*height),(36,45,50));draw=ImageDraw.Draw(sheet)
  for i,row in enumerate(items):
   x=(i%cols)*width;y=(i//cols)*height
   source=Image.open(BASE/row['previews'][0]).convert('RGB')
   thumb=ImageOps.contain(source,(width-12,height-60))
   sheet.paste(thumb,(x+(width-thumb.width)//2,y+6+(height-60-thumb.height)//2))
   draw.text((x+10,y+height-51),row['assetId'],font=font,fill='white')
   draw.text((x+10,y+height-29),str(row['assembledTriangles'])+' tris',font=font,fill=(188,213,222))
  sheet.save(review/name,optimize=True)
 board([r for r in rows if r['category']=='props'],'props-library.png',5,(250,270))
 board([r for r in rows if r['category'] in ['riverfront_structures','context']],'riverfront-and-context.png',3,(340,300))
 lines=['# Task 005 asset index','','Full assembled triangles include every repeated mesh instance. Unique geometry counts each shared source mesh once per asset. All dimensions are studs.','','| Asset | Name | W x H x D | Assembled / unique tris | Mesh instances / unique | Files |','|---|---|---:|---:|---:|---|']
 for r in rows:
  d=r['dimensionsStuds'];dim=' x '.join(str(d[k]) for k in ['width','height','depth'])
  files='[source]('+r['source']+') · [FBX]('+r['export']+') · [PNG]('+r['previews'][0]+')'
  lines.append('| '+r['assetId']+' | '+r['name']+' | '+dim+' | '+str(r['assembledTriangles'])+' / '+str(r['uniqueGeometryTriangles'])+' | '+str(r['meshInstances'])+' / '+str(r['uniqueMeshes'])+' | '+files+' |')
 lines+=['','Per-asset reference IDs, materials, collision recommendations, connection sockets and mesh assembly transforms are in [asset-manifest.json](asset-manifest.json). Reference sources are in [the catalogue](references/catalogue.json); locally retrieved and examined photos are recorded in [retrieved.json](references/retrieved.json).']
 (BASE/'asset-index.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
 print(json.dumps(dict(assets=len(rows),individualPreviewPNGs=sum(len(r['previews']) for r in rows),reviewBoards=2)))

if __name__=='__main__':finish()
