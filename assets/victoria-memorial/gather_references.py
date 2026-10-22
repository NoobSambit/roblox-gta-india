"""Reference-only downloads. These images are never exported as game assets."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json
import urllib.request
import hashlib
from urllib.parse import quote
from PIL import Image, ImageOps, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "artifacts/references/victoria"
REFS = [
    ("01-north-elevation", "https://victoriamemorial-cal.org/media/2024/04/Victoria-Memorial-Hall-Kolkata.jpg", "Official Memorial; broad portal elevation, cornice and tower proportions"),
    ("02-side-elevation", "https://s7ap1.scene7.com/is/image/incredibleindia/victoria-memorial-kolkata-west-bengal-tri-hero?qlt=82", "Incredible India tourism; curved colonnade and corner pavilion"),
    ("03-south-approach", "https://upload.wikimedia.org/wikipedia/commons/6/65/A_view_of_Victoria_memorial_hall_from_South_gate%2C_Kolkata_04.jpg", "Commons; photographed south approach, lawns and water"),
    ("04-rear-elevation", "https://upload.wikimedia.org/wikipedia/commons/a/ad/Kolkata_Victoria_Memorial_Garden_IMG_20181214_100636.jpg", "Commons; rear elevation and accessible terrace"),
    ("05-west-colonnade", "https://www.free-photos.biz/images/architecture/memorials/victoria_memorial__kolkata_-_west_facade_02.jpg", "Photograph labelled west facade; curved colonnade"),
    ("06-east-quadrangle", "https://victoriamemorial-cal.org/media/2024/05/IMG_7597-1.jpg", "Official Memorial; Eastern Quadrangle"),
    ("07-dome-detail", "https://victoriamemorial-cal.org/media/2024/05/DSC_9942.jpg", "Official Memorial; drum, chhatris, dome and Angel of Victory"),
    ("08-aerial-massing", "https://mxp-media.ilnmedia.com/media/content/2016/Feb/waking-up-with-kolkata-aerial-view-video980-1454999682.jpg", "Sandip De aerial, reproduced in MensXP; roof and campus massing"),
    ("09-queens-hall", "https://victoriamemorial-cal.org/media/2024/05/IMG_7658.png", "Official Memorial; Queen's Hall column and arch arrangement"),
    ("10-inner-dome", "https://victoriamemorial-cal.org/media/2024/05/IMG_7656.jpg", "Official Memorial; interior dome, clerestory and radial ceiling"),
    ("11-entrance-hall", "https://victoriamemorial-cal.org/media/2024/05/IMG_7662.png", "Official Memorial; Entrance Hall vaults and circulation"),
    ("12-prince-hall", "https://victoriamemorial-cal.org/media/2024/05/IMG_7649.png", "Official Memorial; Prince Hall gallery spatial proportions"),
    ("13-rotunda-floor", "https://victoriamemorial-cal.org/media/2024/05/IMG_7657.jpg", "Official Memorial; radial floor pattern and statue setting"),
    ("14-rotunda-gallery", "https://victoriamemorial-cal.org/media/2024/05/IMG_7659.jpg", "Official Memorial; upper gallery and rotunda detail"),
]

for key, filename, description in [
    ("15-north-cardinal", "Back side facade of Victoria Memorial Hall ,Kolkata.JPG", "Commons North-side category; photographer Winniekapoor123V; CC BY-SA 3.0"),
    ("16-south-cardinal", "Victoria Memorial, Kolkata India Facade from the Southern End.jpg", "Commons; Anupam Roy Bardhan, processed by PawelMM; CC BY-SA 3.0 option"),
    ("17-east-cardinal", "Looking into the Mirror.jpg", "Commons East-side category; see original file page for attribution and licence"),
    ("18-west-cardinal", "Victoria Memorial, Kolkata - West facade 02.jpg", "Commons West-side category; see original file page for attribution and licence"),
]:
    filename=filename.replace(" ","_")
    digest=hashlib.md5(filename.encode("utf-8")).hexdigest()
    REFS.append((key,"https://upload.wikimedia.org/wikipedia/commons/"+digest[0]+"/"+digest[:2]+"/"+quote(filename),description))

def download(ref):
    key, url, description = ref
    target = DEST / (key + ".jpg")
    try:
        if not target.exists():
            request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (architectural reference study)"})
            with urllib.request.urlopen(request, timeout=45) as response:
                data = response.read()
            with target.open("wb") as file:
                file.write(data)
        with Image.open(target) as img:
            dimensions = list(img.size)
        return dict(id=key, url=url, description=description, path=str(target.relative_to(ROOT)), dimensions=dimensions, status="downloaded", usage="Reference only; not a game texture or distributed asset. Rights remain with source.")
    except Exception as error:
        return dict(id=key, url=url, description=description, status="unavailable", error=str(error))

def contact_sheet(rows, name):
    width, height = 470, 340
    sheet = Image.new("RGB", (width * 2, height * ((len(rows) + 1) // 2)), "#162026")
    draw = ImageDraw.Draw(sheet)
    for index, row in enumerate(rows):
        x, y = index % 2 * width, index // 2 * height
        if row["status"] == "downloaded":
            with Image.open(ROOT / row["path"]) as img:
                preview = ImageOps.contain(img.convert("RGB"), (width - 16, height - 46))
            sheet.paste(preview, (x + (width - preview.width) // 2, y + 30 + (height - 46 - preview.height) // 2))
        draw.text((x + 10, y + 9), row["id"], fill="white")
    sheet.save(DEST / name)

if __name__ == "__main__":
    DEST.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(download, REFS))
    (DEST / "sources.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    contact_sheet(rows[:8], "exterior-reference-board.jpg")
    contact_sheet(rows[8:14], "interior-reference-board.jpg")
    contact_sheet(rows[14:], "cardinal-reference-board.jpg")
    print(json.dumps([{r["id"]: r["status"]} for r in rows]))
