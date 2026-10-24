"""Read-only catalog of the finished Tier 1 packages requested for staging."""
import hashlib
import json
from pathlib import Path

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
EXPORT=ROOT/'exports/kolkata_tier1_staging'
MASTER=BASE/'Kolkata_Tier1_Staging.blend'
# Display order: near-to-far rows from the inspection camera, never city positions.
SOURCES=[
    ('landmarks_batch4/new_market','New Market','Batch 4'),
    ('landmarks_batch4/indian_museum','Indian Museum','Batch 4'),
    ('landmarks_batch4/st_pauls',"St Pauls Cathedral",'Batch 4'),
    ('dakshineshwar','Dakshineshwar','Temple'),
    ('heritage_batch2/writers','Writers Building','Heritage'),
    ('heritage_batch2/metropolitan','Metropolitan Building','Heritage'),
    ('heritage_batch2/gpo','General Post Office','Heritage'),
    ('heritage_batch2/town_hall','Town Hall','Heritage'),
    ('cultural_batch/rajbari','Rajbari Estate','Cultural'),
    ('cultural_batch/jorasanko','Jorasanko Thakurbari','Cultural'),
    ('tier1/sonar','ITC Sonar','Skyline'),
    ('tier1/royal','ITC Royal Bengal','Skyline'),
    ('tier1/atmosphere','Atmosphere and Deya','Skyline'),
    ('tier1/trump','Trump Tower Kolkata','Skyline'),
    ('tier1/urbana','Urbana Seven Towers','Skyline'),
    ('tier1/jw','JW Marriott Kolkata','Skyline'),
]


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(path):return Path(path).resolve().relative_to(ROOT).as_posix()


def catalog():
    rows=[]
    for index,(path,label,batch) in enumerate(SOURCES):
        folder=BASE.parent/path
        row=json.loads((folder/'asset.json').read_text(encoding='utf8'))
        verification=json.loads((folder/'validation.json').read_text(encoding='utf8'))
        assert verification['status']=='passed',(label,'source was not approved by its validation')
        source=folder/row['source'];assert source.is_file(),source
        files=[]
        for part in row['exports']:
            file=(folder/part['file']).resolve();assert file.is_file(),file
            files.append(dict(part,canonicalFile=relative(file),sha256=sha(file)))
        rows.append(dict(index=index+1,label=label,batch=batch,folder=relative(folder),
            metadata=relative(folder/'asset.json'),metadataSha256=sha(folder/'asset.json'),
            source=relative(source),sourceSha256=sha(source),row=row,exports=files,
            packageKey=row['assetId'].removeprefix('KOL_T1_').lower()))
    return rows
