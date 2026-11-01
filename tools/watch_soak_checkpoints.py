"""OS-only checkpoint wall-time observer. No browser/GPU work or per-input claim."""
from pathlib import Path
import json,time,datetime,os
R=Path(__file__).resolve().parents[1];p=R/'docs/previews/webgl-running-soak-29/manifest.json';o=p.parent/'checkpoint-wall-times.jsonl';last=None
while True:
 try:
  st=p.stat()
  if st.st_mtime_ns!=last:
   s=json.loads(p.read_text());last=st.st_mtime_ns
   for phase in s['phases']:
    if not phase.get('startUTC')or not phase['checks']or phase.get('endUTC'):continue
    start=datetime.datetime.fromisoformat(phase['startUTC']).timestamp();c=phase['checks'][-1];row={'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phase':phase['phase'],'checkpointStartElapsed':c['elapsed'],'checkpointEndElapsed':st.st_mtime-start,'wallMs':max(0,(st.st_mtime-start-c['elapsed'])*1000),'includes':'all checkpoint inputs, UI/GPU waits, pixel checks and optional GC/actions; NOT individual input latency'}
    with o.open('a')as f:f.write(json.dumps(row)+'\n')
   if s.get('endUTC'):break
 except (FileNotFoundError,json.JSONDecodeError):pass
 time.sleep(1)
