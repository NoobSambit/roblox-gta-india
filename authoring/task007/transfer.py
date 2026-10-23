"""Local-only edit-time transfer; never installed in the Roblox game."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = {
    "/pre.rbxm": ROOT / "artifacts/recovery/HoodTesting-pre-Task007.rbxm",
    "/final.rbxm": ROOT / "artifacts/recovery/HoodTesting-Task007.rbxm",
    "/victoria.rbxm": ROOT / "artifacts/VictoriaMemorial-Task007.rbxm",
    "/snapshot.json": ROOT / "docs/task007/snapshot.json",
    "/inspection.json": ROOT / "docs/task007/inspection.json",
}

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def reply(self, code, data):
        self.send_response(code)
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        paths = {f"/{p.name}": p for p in (ROOT / "authoring/task007").glob("*.luau")}
        path = paths.get(self.path)
        self.reply(200 if path else 404, path.read_bytes() if path else b"Unknown source")

    def do_POST(self):
        path = OUTPUTS.get(self.path)
        if not path:
            return self.reply(403, b"Unknown output")
        length = int(self.headers.get("Content-Length", "0"))
        if not 0 < length <= 500000:
            return self.reply(413, b"Invalid chunk")
        if self.path == "/pre.rbxm" and path.exists():
            return self.reply(409, b"Pre-task recovery already preserved")
        index = int(self.headers.get("X-Chunk-Index", "0"))
        final = self.headers.get("X-Final", "1") == "1"
        path.parent.mkdir(parents=True, exist_ok=True)
        partial = path.with_suffix(path.suffix + ".part")
        with partial.open("wb" if index == 0 else "ab") as stream:
            stream.write(self.rfile.read(length))
        if final:
            partial.replace(path)
        self.reply(200, json.dumps({"saved": final, "bytes": (path if final else partial).stat().st_size}).encode())

if __name__ == "__main__":
    print("Task007 local bridge: 127.0.0.1:8767", flush=True)
    ThreadingHTTPServer(("127.0.0.1", 8767), Handler).serve_forever()
