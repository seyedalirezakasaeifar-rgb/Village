"""Real added territory, treasury/deed settlement, migration and purchase UI."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
source=(ROOT/'assets/game.js').read_bytes();sha=hashlib.sha256(source).hexdigest()
script=source.decode().replace('// SOURCE: 99-instrumentation.js','''
window.__annexProbe=()=>{const original=G;try{G=JSON.parse(JSON.stringify(original));const p=ANNEX_PARCELS[0],quote=parcelSurvey(p),total=totalMoney();let point=null;
 for(let y=4;y<15&&!point;y++)for(let x=57;x<63;x++)if([0,3].includes(G.tiles[roadId(x,y)])&&[0,3].includes(G.tiles[roadId(x+1,y)])){point={x,y};break;}
 const before=canPlace(point.x+1,point.y,false),cash=G.treasury,cell=G.tiles[roadId(point.x,point.y)];construct('road',point.x,point.y,true);const blocked=G.treasury===cash&&G.tiles[roadId(point.x,point.y)]===cell;
 G.region+=G.treasury;G.treasury=0;const poor=!purchaseParcel(p.id,quote.price)&&G.charter.owned.length===0;G.region-=cash;G.treasury=cash;
 const stale=!purchaseParcel(p.id,quote.price+1),far=!purchaseParcel('high-common',parcelSurvey(ANNEX_PARCELS[4]).price),titles=JSON.stringify(G.buildings.map(b=>[b.id,b.owner,b.title]));
 const bought=purchaseParcel(p.id,quote.price),after=canPlace(point.x+1,point.y,false),paid=cash-G.treasury,repeat=!purchaseParcel(p.id,quote.price)&&cash-G.treasury===paid,unchanged=JSON.stringify(G.buildings.map(b=>[b.id,b.owner,b.title]))===titles;
 construct('road',point.x,point.y,true);const road=G.tiles[roadId(point.x,point.y)]===1;const homeAvailable=canPlace(point.x+1,point.y,true,'home');
 return {size:G.tiles.length,before,after,blocked,poor,stale,far,bought,paid,price:quote.price,repeat,unchanged,road,homeAvailable,drift:totalMoney()-total,deeds:G.charter.deeds};
 }finally{G=original;invalidateRoads();staticDirty=true;dirty=true;}};
// SOURCE: 99-instrumentation.js''')
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':844,'height':390});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.add_script_tag(content=script);p.locator('#newTown').click();p.locator('#pause').click();p.evaluate('__townTest.reset("settlement",42)');r=p.evaluate('__annexProbe()');assert r['size']==128*128 and not r['before'] and r['after'] and all(r[k] for k in ['blocked','poor','stale','far','bought','repeat','unchanged','road','homeAvailable']),r;assert r['paid']==r['price'] and abs(r['drift'])<.001,r
 p.evaluate('__townTest.reset("settlement",42)');p.locator('[data-panel=construction]').click();p.locator('#charterOffice summary').first.click();p.locator('[data-parcel-preview=east-meadow]').click();p.evaluate('new Promise(r=>requestAnimationFrame(r))');assert p.locator('body').evaluate('e=>e.classList.contains("surveying-region")') and p.locator('#topNotice').is_hidden() and p.locator('#liveEconomy').is_hidden();p.locator('#center').click();p.evaluate('new Promise(r=>requestAnimationFrame(r))');assert not p.locator('body').evaluate('e=>e.classList.contains("surveying-region")');p.locator('[data-panel=construction]').click();p.locator('#charterOffice summary').first.click();total=p.evaluate('__townTest.get().total');cash=p.evaluate('__townTest.get().treasury');p.locator('[data-parcel-buy=east-meadow]').click();assert p.locator('#eventDialog').is_visible();p.keyboard.press('Escape');assert p.evaluate('__townTest.get().treasury')==cash
 p.locator('[data-parcel-buy=east-meadow]').click();p.locator('[data-event-choice="0"]').click();g=json.loads(p.evaluate('__townTest.save()'));assert g['charter']['owned']==['east-meadow'];assert p.locator('#funds').get_attribute('title')==f"${g['treasury']:,.0f}";assert abs(p.evaluate('__townTest.get().total')-total)<.001
 saved=p.evaluate('__townTest.save()');assert p.evaluate('s=>__townTest.load(s)',saved);assert json.loads(p.evaluate('__townTest.save()'))['charter']==g['charter']
 for change in ['g.charter.owned.push("missing")','g.charter.deeds[0].day=g.day+1','g.charter.deeds[0].price=-1','g.gridSize=56','g.charter.revision=99']:
  assert p.evaluate('''code=>{const raw=__townTest.save(),g=JSON.parse(raw);new Function('g',code)(g);return !__townTest.load(g)&&__townTest.save()===raw;}''',change),change
 legacy=json.loads((ROOT/'tests/fixtures/corporate-liquidity-trap.json').read_text());assert len(legacy['tiles'])==3136
 oldcash=sum(legacy[k] for k in ['treasury','region'])+sum(x['cash'] for k in ['households','firms','banks','investors'] for x in legacy.get(k,[]))+legacy.get('metro',{}).get('cash',0)
 assert p.evaluate('g=>__townTest.load(g)',legacy);m=json.loads(p.evaluate('__townTest.save()'));assert len(m['tiles'])==128*128 and m['gridSize']==128 and m['schema']==json.loads((ROOT/'release.json').read_text())['schema'] and m['charter']['owned']==[]
 assert abs(p.evaluate('__townTest.get().total')-oldcash)<.001
 assert [(x['id'],x['x'],x['y'],x['owner']) for x in legacy['buildings']]==[(x['id'],x['x'],x['y'],x['owner']) for x in m['buildings']]
 assert all(m['tiles'][y*m['gridSize']+x]==legacy['tiles'][y*56+x] for y in range(56) for x in range(56))
 assert p.evaluate('__townTest.validate().ok');p.evaluate('__townTest.step(30)');assert p.evaluate('__townTest.validate().ok');assert not errors,errors;b.close()
assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha
out=ROOT/'reports/development-annexation';out.mkdir(exist_ok=True);(out/'annexation.json').write_text(json.dumps({'source_sha256':sha,'probe':r,'migration':{'tiles':128*128,'schema':json.loads((ROOT/'release.json').read_text())['schema'],'privateTitlesPreserved':True,'coreTilesPreserved':True}},indent=2)+'\n');print('PASS genuine 128×128 territory, blocked/usable plots, prices, adjacency, treasury, repeat purchase, confirmation/cancel, deed restore, atomic rejection and complete 56×56 migration')
