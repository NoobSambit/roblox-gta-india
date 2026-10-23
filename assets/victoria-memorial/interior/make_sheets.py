"""Arrange original Blender PNGs into labelled contact sheets and an asset index."""
import collections
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
BASE=Path(__file__).resolve().parent

def main():
    rows=json.loads((BASE/'asset-manifest.json').read_text())['assets']
    placement=json.loads((BASE/'placement-manifest.json').read_text())
    usage={r['assetId']:r['instances'] for r in placement['usage']}
    review=BASE/'review';review.mkdir(exist_ok=True)
    font=ImageFont.load_default(size=17)
    title=ImageFont.load_default(size=27)
    small=ImageFont.load_default(size=14)
    for category in ['Architecture','Exhibition','Loot','Security']:
        group=[r for r in rows if r['category']==category]
        cols=min(5,len(group));cellW,cellH=300,344
        sheet=Image.new('RGB',(cols*cellW,84+math.ceil(len(group)/cols)*cellH),(232,233,229))
        draw=ImageDraw.Draw(sheet)
        draw.text((22,16),f'VICTORIA / {category.upper()}',font=title,fill=(29,51,56))
        draw.text((22,51),f"{len(group)} reusable assets | {sum(r['triangles'] for r in group):,} unique triangles | original Blender renders",font=small,fill=(68,81,84))
        for i,r in enumerate(group):
            x,y=(i%cols)*cellW,84+(i//cols)*cellH
            with Image.open(BASE/r['preview']) as preview:
                preview=preview.convert('RGB').resize((280,280),Image.Resampling.LANCZOS)
                sheet.paste(preview,(x+10,y+4))
            draw.text((x+12,y+290),r['assetId'].replace('VIC_',''),font=font,fill=(29,51,56))
            d=r['dimensionsStuds']
            draw.text((x+12,y+314),f"{r['triangles']} tris / cap {r['triangleCap']}  |  {d['width']:g} x {d['height']:g} x {d['depth']:g}",font=small,fill=(68,81,84))
        sheet.save(review/(category.lower()+'-sheet.png'))
    index=['# Victoria interior asset index','',
        f"{len(rows)} original reusable assets. Dimensions are width × height × depth in studs.",
        'Caps are design ceilings, not targets to fill. Below-range pieces retain simple readable silhouettes.',
        '“Pass uses” counts the offline placement plan, not objects installed in Studio.','',
        '| Asset | Category | Triangles / cap | Dimensions | Pass uses | Source / export / preview |',
        '| --- | --- | ---: | --- | ---: | --- |']
    for r in rows:
        d=r['dimensionsStuds']
        links=' / '.join(f"[{key}]({r[key]})" for key in ['source','export','preview'])
        index.append(f"| {r['assetId']} — {r['name']} | {r['category']} | {r['triangles']} / {r['triangleCap']} | {d['width']:g} × {d['height']:g} × {d['depth']:g} | {usage.get(r['assetId'],0)} | {links} |")
    index+=['','## Measured totals','',
        '| Category | Assets | Unique library triangles | Proposed pass triangles |',
        '| --- | ---: | ---: | ---: |']
    for category in ['Architecture','Exhibition','Loot','Security']:
        group=[r for r in rows if r['category']==category]
        index.append(f"| {category} | {len(group)} | {sum(r['triangles'] for r in group):,} | {placement['countSummary']['byCategory'][category]:,} |")
    index+=['',f"**Total: {sum(r['triangles'] for r in rows):,} unique triangles; {placement['countSummary']['proposedPassTriangles']:,} in the {placement['countSummary']['instances']}-instance proposed pass.**",'',
        f"{len(placement['optionalLibraryAssets'])} optional variants are excluded from that pass. Cases shared by loot/security markers are counted once. Original shell triangles, greybox structure and renderer-only context are excluded.",
        '', 'Four flat artwork images are assigned separately to the existing frame backing. They add no sculpted artwork geometry.']
    (BASE/'asset-index.md').write_text('\n'.join(index)+'\n',encoding='utf8')
    print('Saved four category sheets and asset-index.md')

if __name__=='__main__':main()
