"""Task009 loopback-only authoring/recovery bridge; never installed at runtime."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = {
    '/pre.rbxm': ROOT/'artifacts/recovery/HoodTesting-pre-Task009.rbxm',
    '/final.rbxm': ROOT/'artifacts/recovery/HoodTesting-Task009.rbxm',
    '/pre-integration.rbxm': ROOT/'artifacts/recovery/HoodTesting-Task009-pre-integration.rbxm',
    '/victoria.rbxm': ROOT/'artifacts/VictoriaMemorial-Task009.rbxm',
    **{f'/{name}.json':ROOT/f'docs/task009/{name}.json' for name in
       ['pre-snapshot','pre-integration-snapshot','snapshot','audit','inspection','integration','mesh-ids','correction-mesh-ids','lighting']},
}

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*_): pass
    def reply(self,code,data):
        self.send_response(code);self.end_headers();self.wfile.write(data)
    def do_GET(self):
        paths={f'/{p.name}':p for p in (ROOT/'authoring/task009').glob('*') if p.suffix in ['.luau','.json']}
        path=paths.get(self.path) or {k:p for k,p in OUTPUTS.items() if p.suffix=='.json'}.get(self.path)
        self.reply(200 if path else 404,path.read_bytes() if path else b'Unknown source')
    def do_POST(self):
        path=OUTPUTS.get(self.path)
        if not path:return self.reply(403,b'Unknown output')
        length=int(self.headers.get('Content-Length','0'))
        if not 0<length<=500000:return self.reply(413,b'Invalid chunk')
        if self.path=='/pre.rbxm' and path.exists():return self.reply(409,b'Pre-task recovery already preserved')
        index=int(self.headers.get('X-Chunk-Index','0'))
        final=self.headers.get('X-Final','1')=='1'
        path.parent.mkdir(parents=True,exist_ok=True)
        partial=path.with_suffix(path.suffix+'.part')
        with partial.open('wb' if index==0 else 'ab') as stream:stream.write(self.rfile.read(length))
        if final:partial.replace(path)
        self.reply(200,json.dumps({'saved':final,'bytes':(path if final else partial).stat().st_size}).encode())

if __name__=='__main__':
    print('Task009 bridge: 127.0.0.1:8769',flush=True)
    ThreadingHTTPServer(('127.0.0.1',8769),Handler).serve_forever()
