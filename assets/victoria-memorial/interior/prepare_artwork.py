"""Create compact release images without cropping or changing artwork aspect."""
import hashlib
import json
from pathlib import Path
from PIL import Image
BASE=Path(__file__).resolve().parent

def main():
    folder=BASE/'artwork';(folder/'textures').mkdir(exist_ok=True)
    prompts=json.loads((folder/'prompts.json').read_text())['artworks']
    prior=json.loads((folder/'manifest.json').read_text()) if (folder/'manifest.json').exists() else {'artworks':[]}
    rows=[]
    for prompt in prompts:
        aid=prompt['id'];source=folder/'source'/(aid+'.png')
        with Image.open(source) as original:
            image=original.convert('RGB');width,height=image.size
            scale=min(480/width,480/height,1)
            output_size=(round(width*scale),round(height*scale))
            image=image.resize(output_size,Image.Resampling.LANCZOS)
            filename=aid+f'_{output_size[0]}x{output_size[1]}.png'
            target=folder/'textures'/filename
            image.save(target,optimize=True)
        assert max(output_size)<=512 and abs(output_size[0]/output_size[1]-width/height)<.003
        row=dict(artworkId=aid,name=prompt['name'],source=str(source.relative_to(BASE)).replace('\\','/'),
            texture=str(target.relative_to(BASE)).replace('\\','/'),sourcePixels=[width,height],releasePixels=list(output_size),
            aspectRatio=width/height,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),bytes=target.stat().st_size,
            generator='Built-in ImageGen',originalArt=True,frameBakedIntoImage=False,perspectiveDistortion=False,
            geometry='None; apply image to reusable physical frame backing',robloxImageId=None,uploadStatus='Not uploaded')
        old=next((r for r in prior['artworks'] if r['artworkId']==aid and r['sha256']==row['sha256']),None)
        if old:
            for k in ['robloxImageId','uploadStatus']:row[k]=old[k]
        rows.append(row)
    report=dict(uniqueImages=len(rows),releasePixelCount=sum(r['releasePixels'][0]*r['releasePixels'][1] for r in rows),
        paintingMarkerAssignments={'VIC_LOOT_002':'ART_01_RIVER_DAWN','VIC_LOOT_008':'ART_02_MONSOON_STREET','VIC_LOOT_009':'ART_04_HERITAGE_SKYLINE','VIC_LOOT_010':'ART_03_GARDEN_STUDY'},artworks=rows)
    (folder/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(uniqueImages=len(rows),releasePixels=[r['releasePixels'] for r in rows],totalBytes=sum(r['bytes'] for r in rows))))

if __name__=='__main__':main()
