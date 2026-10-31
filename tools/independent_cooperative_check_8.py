"""Independent matched-source check; prototype code remains unchanged."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];runner=ROOT/'tools/profile_cooperative_breakdown.py';code=runner.read_text()
code=code.replace("[('synchronous',False,source),('cooperative-copy-raf',True,raf_source),('cooperative-json',True,json_source),('cooperative-copy-admission',True,admit_source)]", "[('synchronous',False,source),('cooperative-copy-raf',True,raf_source)]")
code=code.replace('if(now-start<12000)', 'if(!window.__independentActionsDone||now-start<12000)')
code=code.replace("p.evaluate('()=>{window.__cooperativeProfileRun=__cooperativeProfile.run();}')", "p.evaluate('()=>{window.__independentActionsDone=false;window.__cooperativeProfileRun=__cooperativeProfile.run();}')")
code=code.replace("r=p.evaluate('window.__cooperativeProfileRun');", "p.wait_for_timeout(1000);p.evaluate('window.__independentActionsDone=true');r=p.evaluate('window.__cooperativeProfileRun');")
code=code.replace("reports/cooperative-breakdown-8.json", "reports/cooperative-independent-8.json")
exec(compile(code,str(runner),'exec'),{'__name__':'__main__','__file__':str(runner)})
