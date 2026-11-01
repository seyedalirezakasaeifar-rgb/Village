"""Run legacy file-URL browser tests on an isolated localhost HTTP origin."""
from pathlib import Path
import functools,http.server,threading,sys
ROOT=Path(__file__).resolve().parents[1]
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 for name in sys.argv[1:]:
  path=ROOT/'tests'/name
  if path.parent!=ROOT/'tests' or not path.is_file():raise ValueError('Expected a repository test filename')
  text=path.read_text();old="(ROOT/'assets/index.html').as_uri()"
  if old not in text:raise ValueError('No supported file-URL navigation in '+name)
  text=text.replace(old,repr('http://127.0.0.1:'+str(server.server_port)+'/assets/index.html'))
  exec(compile(text,str(path),'exec'),{'__file__':str(path),'__name__':'__main__'})
finally:server.shutdown()
