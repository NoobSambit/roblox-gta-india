"""Local-only edit-time bridge for Task 006 sources, reports and place snapshots.
Run from the repository root. Never installed in the game.
"""
import json
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote,urlparse

ROOT=Path(__file__).resolve().parents[2]
POSTS={
 '/snapshot/pre.rbxl':ROOT/'artifacts/recovery/HoodTesting-pre-Task006.rbxl',
 '/snapshot/pre.rbxm':ROOT/'artifacts/recovery/HoodTesting-pre-Task006.rbxm',
 '/snapshot/final.rbxm':ROOT/'artifacts/HoodTesting-Task006.rbxm',
 '/snapshot/final.rbxl':ROOT/'artifacts/HoodTesting-Task006.rbxl',
 **{f'/report/{name}.json':ROOT/f'docs/task006/{name}.json' for name in ['audit','asset-mapping','validation','performance','snapshot']},
}
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def reply(self,code,data):
  self.send_response(code);self.end_headers();self.wfile.write(data)
 def do_GET(self):
  route=unquote(urlparse(self.path).path).lstrip('/')
  if route=='health':return self.reply(200,b'IH Task006 local authoring')
  path=(ROOT/route).resolve()
  if not any(path.is_relative_to(ROOT/p) for p in ['authoring/task006','assets/kolkata','docs/task006']):return self.reply(403,b'Outside task sources')
  if not path.is_file():return self.reply(404,b'Not found')
  self.reply(200,path.read_bytes())
 def do_POST(self):
  path=POSTS.get(urlparse(self.path).path)
  if not path:return self.reply(403,b'Unknown output')
  length=int(self.headers.get('Content-Length','0'))
  if not 0<length<=500000:return self.reply(413,b'Invalid chunk size')
  index=int(self.headers.get('X-Chunk-Index','0'));final=self.headers.get('X-Final','1')=='1'
  if path.name.startswith('HoodTesting-pre') and path.exists():return self.reply(409,b'Pre-rebuild snapshot already preserved')
  path.parent.mkdir(parents=True,exist_ok=True);partial=path.with_suffix(path.suffix+'.part')
  with partial.open('wb' if index==0 else 'ab') as f:f.write(self.rfile.read(length))
  if final:partial.replace(path)
  self.reply(200,json.dumps({'saved':final,'bytes':(path if final else partial).stat().st_size}).encode())

if __name__=='__main__':
 print('Task006 authoring bridge: 127.0.0.1:8766',flush=True)
 ThreadingHTTPServer(('127.0.0.1',8766),Handler).serve_forever()
