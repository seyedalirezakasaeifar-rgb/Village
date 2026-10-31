"""Actual bank resolution, repayment and historical regional-creditor compaction."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import ast,hashlib,json,os
source=(ROOT/'assets/game.js').read_text();tree=ast.parse((ROOT/'tests/test_loan_history_limit.py').read_text());probe=next(ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='probe'for t in n.targets));needle="if(!loan)throw Error('Initial real loan refused');";assert needle in probe;probe=probe.replace(needle,needle+"liquidateBank(G.banks[loan.bankId],'Controlled creditor-transfer regression');if(loan.bankId!==-1)throw Error('No regional creditor transfer');")
probe+=r'''
window.__regionalSummaryFaults=()=>{const saved=archivePayload(),changes=[g=>g.settledLoanHistory.count++,g=>g.settledLoanHistory.banks['-1'].original++,g=>{g.settledLoanHistory.banks['-2']=g.settledLoanHistory.banks['-1'];delete g.settledLoanHistory.banks['-1'];},g=>delete g.nextLoanId];for(const change of changes){const g=JSON.parse(saved);change(g);if(hydrateSave(g)||archivePayload()!==saved)throw Error('Malformed summary adopted or changed town');}return changes.length;};
'''
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();
 try:
  r=p.evaluate('__loanLimit()')
  if os.environ.get('LOAN_EXPECT_NEGATIVE')!='1':r['malformedSummaryAtomicRejections']=p.evaluate('__regionalSummaryFaults()')
 except Exception as error:
  if os.environ.get('LOAN_EXPECT_NEGATIVE')!='1' or 'Historical boundary rejected' not in str(error):raise
  r={'newArchiveImportable':False,'historicalImportRejectedBeforeCompaction':True,'reason':'Regional creditor bankId=-1 rejected'}
 b.close()
negative=os.environ.get('LOAN_EXPECT_NEGATIVE')=='1';assert r['newArchiveImportable']!=negative,r;out=ROOT/'reports/regional-loan-summary';out.mkdir(exist_ok=True);(out/('before.json'if negative else 'after.json')).write_text(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'actualBankResolutionAndRepayment':True,'syntheticHistoricalReceiptCount':10000,'result':r},indent=2)+'\n');print('PASS expected negative'if negative else 'PASS regional creditor summary',r['newArchiveImportable'])
