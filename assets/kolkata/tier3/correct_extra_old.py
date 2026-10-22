"""Replace the misclassified supplementary batch; assigned references stay intact."""
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from gather_references import download, board

ROOT=Path(__file__).resolve().parents[3]
DEST=ROOT/'artifacts/references/tier3'
source=json.loads((DEST/'extraOld-replacement.json').read_text(encoding='utf8'))
wrong=DEST/'extraOld'
archive=DEST/'rejected_modern_supplement'
assert wrong.resolve().is_relative_to(DEST.resolve())
if wrong.exists() and not archive.exists():wrong.rename(archive)
candidates=json.loads((DEST/'candidates.json').read_text(encoding='utf8'))
candidates.pop('extraOld',None)
candidates['extraOld']=source
(DEST/'candidates.json').write_text(json.dumps(candidates,indent=2),encoding='utf8')
with ThreadPoolExecutor(max_workers=5) as pool:
 rows=list(pool.map(download,[('extraOld',i+1,r) for i,r in enumerate(source)]))
retrieved=json.loads((DEST/'retrieved.json').read_text(encoding='utf8'))
retrieved=[r for r in retrieved if r['family']!='extraOld']+rows
(DEST/'retrieved.json').write_text(json.dumps(retrieved,indent=2),encoding='utf8')
board('extraOld',rows)
print(json.dumps([{'index':r['index'],'path':r.get('path'),'error':r.get('error')} for r in rows]))
