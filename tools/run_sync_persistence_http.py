"""Run original persistence cases on supported localhost HTTP; browser policy unchanged."""
from pathlib import Path
import argparse,functools,http.server,threading,sys
R=Path(__file__).resolve().parents[1];(R/'reports/final').mkdir(parents=True,exist_ok=True);p=argparse.ArgumentParser();p.add_argument('test',choices=['test_save_storage.py','test_save_chronology.py','test_save_queue.py']);a=p.parse_args()
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(R/'assets')));threading.Thread(target=server.serve_forever,daemon=True).start();path=R/'tests'/a.test;source=path.read_text();url=f'http://127.0.0.1:{server.server_port}/index.html';source=source.replace("(R/'assets/index.html').as_uri()",repr(url)).replace("(ROOT/'assets/index.html').as_uri()",repr(url));sys.path.insert(0,str(R/'tests'))
try:exec(compile(source,str(path),'exec'),{'__name__':'__main__','__file__':str(path)})
finally:server.shutdown()
