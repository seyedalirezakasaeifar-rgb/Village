"""A planning boundary applies to the full site, including private larger sites."""
from pathlib import Path
import json,hashlib
from playwright.sync_api import sync_playwright
from test_mobile_rendering import ROOT,html
source=(ROOT/'assets/game.js').read_text()
probe=r'''
window.__planningBoundary={find:()=>{for(let y=3;y<53;y++)for(let x=3;x<53;x++){if(x%8!==7||!canPlace(x,y,true,'warehouse'))continue;const key=urbanBlockKey(x+1,y),b=G.buildings.find(b=>urbanBlockKey(b.x,b.y)===key);if(b)return{x,y,building:b.id,key};}return null;},select:id=>{selected={id};openPanel('inspect');},charter:()=>({home:districtPlacementReason(56,24,'home'),apartment:districtPlacementReason(56,24,'apartment'),tower:districtPlacementReason(56,24,'tower')}),check:s=>({warehouse:canPlace(s.x,s.y,true,'warehouse'),anchorReason:districtPlacementReason(s.x,s.y,'warehouse'),crossedReason:districtPlacementReason(s.x+1,s.y,'warehouse'),treasury:G.treasury,total:totalMoney(),valid:validateTown()})};
'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':1280,'height':800});p.set_content(html);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();p.evaluate("__townTest.reset('settlement',42)");site=p.evaluate('__planningBoundary.find()');assert site,'No authored boundary site';before=p.evaluate('s=>__planningBoundary.check(s)',site);assert before['warehouse'];p.evaluate('id=>__planningBoundary.select(id)',site['building']);p.locator('summary',has_text='Change the 8 × 8 neighbourhood plan').click();p.locator('[data-urban-plan=civic]').click();p.locator('[data-event-choice="0"]').click();after=p.evaluate('s=>__planningBoundary.check(s)',site);assert after['crossedReason'] and not after['anchorReason'],after
 assert not after['warehouse'],'A two-by-two private depot crosses into the civic reserve.'
 assert after['treasury']==before['treasury']-600 and abs(after['total']-before['total'])<.01 and after['valid']['ok']
 p.locator('[data-panel=construction]').click();p.locator('#charterOffice>summary').click();p.locator('[data-parcel-buy=east-meadow]').click();p.locator('[data-event-choice="0"]').click();p.get_by_text('District commitments & development programmes',exact=True).click();focus=p.locator('[data-district-id=east-meadow][data-district-focus=industry]');focus.locator('..').locator(':scope>summary').click();focus.click();p.locator('[data-event-choice="0"]').click();charter=p.evaluate('__planningBoundary.charter()');assert all(charter.values()),'Employment charter excludes all new dwellings, including apartments and towers: '+str(charter);b.close()
print('PASS real planning control protects every site tile, preserving existing property and conserved survey payment')
