"""Small original tile maps and reference provenance; no photographs redistributed."""
from pathlib import Path
from PIL import Image, ImageDraw
import hashlib
import json
import random

BASE=Path(__file__).resolve().parent
ATTACHMENTS=Path(r'C:\Users\Sambit Pradhan\.codex\attachments\67008d13-5e6d-447f-8b84-f8c188aeb329')


def textures():
    folder=BASE/'textures';folder.mkdir(exist_ok=True)
    rng=random.Random(414)
    for role,base,brick in [('B4_Brick',(167,70,52),True),('B4_Stone',(210,208,190),False),('B4_Plaster',(226,220,203),False),('B4_MuseumWall',(205,190,159),False)]:
        im=Image.new('RGB',(512,512));px=im.load()
        for y in range(512):
            for x in range(512):
                v=rng.randint(-4,4);px[x,y]=tuple(max(0,min(255,c+v)) for c in base)
        d=ImageDraw.Draw(im)
        if brick:
            for row in range(16):
                yy=row*32
                for xx in range(-64,576,128):
                    x=xx+(64 if row%2 else 0);v=rng.randint(-9,8)
                    col=tuple(c+v for c in base)
                    d.rectangle((x+2,yy+2,x+125,yy+29),fill=col)
                    d.line((x,yy,x+128,yy),fill=(139,98,77),width=2)
                    d.line((x,yy,x,yy+32),fill=(139,98,77),width=2)
                    d.line((x+3,yy+3,x+124,yy+3),fill=tuple(c+7 for c in col),width=1)
        elif role=='B4_Stone':
            for row in range(4):
                yy=row*128;d.line((0,yy,512,yy),fill=(191,191,176),width=1)
                for x in range((64 if row%2 else 0),512,256):d.line((x,yy,x,yy+128),fill=(193,193,178),width=1)
        im.save(folder/(role+'.png'),optimize=True)


def references():
    groups=dict(new_market=[7,8,9,10,12],indian_museum=[4,5,6],st_pauls=[1,2,3])
    if not (ATTACHMENTS/'image-1.png').is_file():
        if not all((BASE/key/'references.json').is_file() for key in groups):
            raise FileNotFoundError('Original photo attachments or tracked reference manifests are required.')
        print('Photo attachments unavailable; retaining tracked reference hashes and notes.')
        return
    for key,indices in groups.items():
        folder=BASE/key;folder.mkdir(exist_ok=True)
        refs=[]
        for i in indices:
            p=ATTACHMENTS/f'image-{i}.png'
            refs.append(dict(attachment=f'image-{i}.png',sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                use='Architectural observation only; no photographic pixels enter model textures',rights='User supplied; photographer retains rights; not committed'))
        (folder/'references.json').write_text(json.dumps(dict(primarySources=refs,
            additionalReference=('Cathedral facade photograph supplied in later user feedback; used for tower/buttress/porch detailing. No local attachment path was exposed for this image.' if key=='st_pauls' else None),
            excludedImage11='Different long retail/colonnaded elevation, inconsistent with the museum entry/court in images 4–6; not used for museum geometry.',
            modelProvenance='Original procedural mesh/texture work; no external meshes, photo textures, AI generation or proprietary game assets'),indent=2),encoding='utf8')


if __name__=='__main__':textures();references();print('Prepared 4 original 512px maps and 11 primary photo hashes; image 11 excluded.')
