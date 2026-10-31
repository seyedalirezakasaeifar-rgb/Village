"""Opt-in loopback asset origin for QA environments that prohibit file URLs."""
import os
if os.environ.get('TOWNLEDGER_USE_HTTP')=='1':
 import atexit,http.server,threading
 from pathlib import Path
 from urllib.parse import unquote,urlsplit,quote
 root=Path(__file__).resolve().parents[2]
 class Handler(http.server.SimpleHTTPRequestHandler):
  def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(root),**kwargs)
  def log_message(self,*args):pass
  def do_GET(self):
   try:
    path=(root/unquote(urlsplit(self.path).path).lstrip('/')).resolve();relative=path.relative_to(root);parts=relative.parts
    allowed=parts and (parts[0]=='assets' or parts[0]=='reference' and 'assets' in parts)
    if not allowed or not path.is_file():self.send_error(404);return
   except (ValueError,OSError):self.send_error(404);return
   super().do_GET()
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
 threading.Thread(target=lambda:server.serve_forever(poll_interval=.05),daemon=True).start()
 def close():server.shutdown();server.server_close()
 atexit.register(close)
 original=Path.as_uri
 def asset_uri(path):
  try:
   relative=path.resolve().relative_to(root);parts=relative.parts
   if parts and (parts[0]=='assets' or parts[0]=='reference' and 'assets' in parts):return f'http://127.0.0.1:{server.server_port}/'+quote(relative.as_posix())
  except (ValueError,OSError):pass
  return original(path)
 Path.as_uri=asset_uri
