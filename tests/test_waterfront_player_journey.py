"""A mayor builds a southern waterfront through actual controls and live RAF."""
from test_mobile_rendering import ROOT
from playwright.sync_api import sync_playwright
import json,hashlib,time,threading
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT/'assets')));threading.Thread(target=server.serve_forever,daemon=True).start()
source=(ROOT/'assets/game.js').read_bytes();sha=hashlib.sha256(source).hexdigest()
script=source.decode().replace('// SOURCE: 99-instrumentation.js',r'''
window.__roadPlan=()=>{const start=roadId(5,58),net=graph(),parent=new Map([[start,-1]]),queue=[start],allowed=id=>{const x=id%T,y=id/T|0;return x>=2&&y>=2&&x<T-2&&y<T-2&&charterOwns(x,y)&&[0,1,3].includes(G.tiles[id])&&!buildingAt(x,y)&&!G.landUse[id]};let end=null;for(let i=0;i<queue.length;i++){const at=queue[i];if(net.parts[at]===net.mainPart){end=at;break;}for(const [dx,dy] of roadOffsets){const x=at%T+dx,y=(at/T|0)+dy,n=roadId(x,y);if(x<0||y<0||x>=T||y>=T||parent.has(n)||!allowed(n))continue;parent.set(n,at);queue.push(n);}}if(end==null)return null;const result=[];for(let at=end;at!==-1;at=parent.get(at))result.push([at%T,at/T|0]);return result.reverse();};
// SOURCE: 99-instrumentation.js''')
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390},has_touch=True);errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.route('**/game.js',lambda r:r.fulfill(body=script,content_type='application/javascript'));p.goto(f'http://127.0.0.1:{server.server_port}/index.html');p.locator('#newTown').click();p.locator('#pause').click();p.evaluate('__townTest.reset("settlement",42)');total=p.evaluate('__townTest.get().total')
 p.locator('[data-panel=construction]').click();p.locator('#charterOffice>summary').click();p.locator('[data-parcel-preview=river-reach]').click();p.locator('#surveyReview').click();p.locator('[data-parcel-buy=river-reach]').click();p.locator('[data-event-choice="0"]').click();p.locator('#panelClose').click();path=p.evaluate('__roadPlan()');assert path
 # Set the camera through the existing read/test capture facility; every paid
 # placement below uses normal buttons and pointer/touch events, never construct().
 p.evaluate('__townTest.capture({x:1438,y:1130,zoom:.4})');box=p.locator('#view').bounding_box()
 def point(x,y):
  c=p.evaluate('__townTest.view().camera');return (box['x']+box['width']/2+((x-y)*36+2950-c['x'])*c['zoom'],box['y']+box['height']/2+((x+y)*18+50-c['y'])*c['zoom'])
 def choose(kind):
  p.locator('[data-panel=construction]').click();p.locator('[data-build-category=all]').click();p.locator('[data-build='+kind+']').click()
 def place(kind,x,y):
  choose(kind);p.touchscreen.tap(*point(x,y));p.keyboard.press('Escape')
 place('road',5,58);place('fishery',4,58);g=json.loads(p.evaluate('__townTest.save()'));fish=g['firms'][-1];assert fish['kind']=='fishery' and fish['workers']==[]
 choose('road');p.mouse.move(*point(*path[0]));p.mouse.down()
 for xy in path[1:]:p.mouse.move(*point(*xy),steps=2)
 p.mouse.up();p.keyboard.press('Escape');place('road',5,59);place('wharf',4,59);place('home',6,59)
 g=json.loads(p.evaluate('__townTest.save()'));home_hh=next(bld['hh'] for bld in g['buildings'] if bld['x']==6 and bld['y']==59);occupied={i for bld in g['buildings'] for i in bld.get('footprint',[bld['y']*80+bld['x']])};sites=[]
 for y in range(56,61):
  for x in range(4,12):
   at=y*80+x
   if g['tiles'][at] in [0,3] and at not in occupied and not g['landUse'].get(str(at)) and any(g['tiles'][(y+dy)*80+x+dx]==1 for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]):sites.append((x,y))
 assert len(sites)>=2;place('clinic',*sites[0]);place('grocer',*sites[1]);p.locator('#speedRange').fill('6');target=p.evaluate('__townTest.get().day')+90;p.locator('#pause').click();p.wait_for_function('day=>__townTest.get().day>=day',arg=target,timeout=15000);p.locator('#pause').click();g=json.loads(p.evaluate('__townTest.save()'));newfish=g['firms'][fish['id']];wharf=next(f for f in g['firms'] if f['kind']=='wharf' and f['building']!=g['firms'][25]['building']);assert g['day']>=40 and newfish['workers'] and wharf['workers'],(g['day'],newfish['workers'],wharf['workers']);assert any(m['port']==wharf['id'] for m in g['waterway']['manifests']),wharf
 care_before=g['serviceProvision']['health']['coverage'];p.locator('[data-panel=community]').click();p.locator('[data-service-policy=health]').click();p.locator('input[data-policy=healthBudget]').fill('170');p.locator('#enactPolicy').click();p.locator('#panelClose').click();target=p.evaluate('__townTest.get().day')+90;p.locator('#pause').click();p.wait_for_function('day=>__townTest.get().day>=day',arg=target,timeout=15000);p.locator('#pause').click();g=json.loads(p.evaluate('__townTest.save()'));newfish=g['firms'][fish['id']];wharf=g['firms'][wharf['id']];assert g['serviceProvision']['health']['coverage']>care_before,(care_before,g['serviceProvision']['health']);assert g['households'][home_hh]['utilityConnected'];assert p.evaluate('__townTest.validate().ok');assert max(abs(x['error']) for x in p.evaluate('__townTest.goods()'))<.001;assert abs(p.evaluate('__townTest.get().total')-total)<.001
 expected_detail=str(int(g['serviceProvision']['health']['coverage']*100+.5))+'% care · '+str(int(g['serviceProvision']['school']['coverage']*100+.5))+'% school · '+str(sum(not f.get('closed',False) for f in g['firms']))+' firms';assert p.locator('#marketDetail').inner_text()==expected_detail
 visual=ROOT/'reports/development-visual-acceptance';visual.mkdir(parents=True,exist_ok=True);p.locator('#toast').wait_for(state='hidden',timeout=5000);p.evaluate('__townTest.capture({x:1060,y:1190,zoom:.9})');p.screenshot(path=str(visual/'waterfront-day-844x390.png'));p.locator('[data-panel=settings]').click();p.locator('#nightView').click();p.locator('#panelClose').click();p.screenshot(path=str(visual/'waterfront-evening-844x390.png'));p.locator('[data-panel=settings]').click();p.locator('#nightView').click();p.locator('#panelClose').click();p.touchscreen.tap(*point(4,59));assert 'Cargo needed to cover today' in p.locator('#panelBody').inner_text();saved=p.evaluate('__townTest.save()');p.locator('#panelClose').click();assert p.evaluate('s=>__townTest.load(s)',saved);g2=json.loads(p.evaluate('__townTest.save()'));assert g2['charter']==g['charter'] and g2['firms'][wharf['id']]['cash']==wharf['cash'];assert not errors,errors
 result={'httpOrigin':True,'source_sha256':sha,'day':g['day'],'roadTilesPainted':len(path),'newFisheryCrew':len(newfish['workers']),'newWharfCrew':len(wharf['workers']),'newWharfCargo':wharf.get('cargoToday',0),'newWharfProfit':wharf.get('netProfit',0),'householdUtilityConnected':g['households'][home_hh].get('utilityConnected'),'careBeforeFunding':care_before,'careCoverage':g.get('serviceProvision',{}).get('health',{}).get('coverage'),'careStaffing':g.get('serviceProvision',{}).get('health',{}).get('staffing'),'treasury':g['treasury'],'cashDrift':p.evaluate('__townTest.get().total')-total,'roundTrip':True};b.close()
server.shutdown();server.server_close()
assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha
out=ROOT/'reports/development-survey-play';out.mkdir(exist_ok=True);(out/'player-journey.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS actual-control deed, isolated fishery, painted connection, wharf/home/clinic/grocer, live recruitment/trade, accounting, inspector and save round trip',result)
