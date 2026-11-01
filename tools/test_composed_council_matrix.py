"""Reuse paid owner's unchanged 60-choice assertions with normalized day owner hooks."""
from pathlib import Path
import subprocess,re,os
ROOT=Path(__file__).resolve().parents[1];PAID='455a12f1d01943bc9a8846b437146612e5f9bfd2'
def published(path):return subprocess.check_output(['git','show',PAID+':'+path],cwd=ROOT,text=True)
script=published('tools/test_root_transactions.py')
start=script.index('bootstrap=');end=script.index("probe=r'''",start)
script=script[:start]+'''for name in ['70-interaction.js','80-civic.js','98-project-opportunities.js']:
 source=re.sub(r'// SOURCE: '+re.escape(name)+r'\\n.*?(?=// SOURCE: |\\Z)',lambda m:'// SOURCE: '+name+'\\n'+published('src/'+name)+'\\n',source,flags=re.S)
bootstrap=(ROOT/'experiments/root-capacity-api.js').read_text()+'\\n'+(ROOT/'experiments/automatic-day-admission.js').read_text()+'\\n'+published('experiments/paid-command-root.js')+"\\n__automaticDayAdmission.install();const rootAdmission=__installPaidCommandLayer(__automaticDayAdmission);\\n"
'''+script[end:]
script=re.sub(r'^out=.*$',"out={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'automatic_adapter_sha256':hashlib.sha256((ROOT/'experiments/automatic-day-admission.js').read_bytes()).hexdigest(),'paid_dependency':PAID,'oracleOnly':False,'hostChromium':True,'physicalAndroid':False,'productionDefaultEnabled':False}",script,flags=re.M)
os.environ['ROOT_COUNCIL_MATRIX_ONLY']='1'
exec(compile(script,'immutable-paid-council-matrix','exec'))
