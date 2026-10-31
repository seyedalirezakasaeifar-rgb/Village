"""Controlled deferred play promises exercise retirement and stale rejection safety."""
from test_mobile_rendering import ROOT,html
from playwright.sync_api import sync_playwright
import json,hashlib
source=(ROOT/'assets/game.js').read_text();sha=hashlib.sha256(source.encode()).hexdigest()
mock=r'''
window.__mediaRequests=[];window.__media=[];
window.Audio=class extends EventTarget{
 constructor(src){super();this.src=src;this.paused=true;this.volume=1;this.currentTime=0;this.loads=0;__media.push(this);}
 play(){this.paused=false;if(!this.src.startsWith('music/'))return Promise.resolve();return new Promise((resolve,reject)=>__mediaRequests.push({audio:this,resolve,reject}));}
 pause(){this.paused=true;}
 removeAttribute(name){if(name==='src')this.src='';}
 load(){this.loads++;}
};
'''
probe=r'''
window.__musicRace=async()=>{
 stopMusic();for(const d of musicDecks)retireMusicDeck(d);musicDecks=[];musicTrack=-1;musicEnabled=true;musicVolume=.4;musicGesture=true;musicError='';
 playMusicTrack(0);const old=__mediaRequests[__mediaRequests.length-1];playMusicTrack(1);const fresh=__mediaRequests[__mediaRequests.length-1];fresh.resolve();await Promise.resolve();old.reject(Error('Stale play failure'));await Promise.resolve();await Promise.resolve();
 if(musicTrack!==1||musicError||fresh.audio.paused||!musicFade)throw Error('Stale rejected play silenced newer music');
 playMusicTrack(2);const next=__mediaRequests[__mediaRequests.length-1];next.resolve();await Promise.resolve();stopMusic();
 if(musicDecks.length!==1||!musicDecks[0].audio.paused||musicFade)throw Error('Suspend retained fade/tail');
 const retired=__media.filter(a=>a!==musicDecks[0].audio&&a.loads>0);if(retired.length<2||retired.some(a=>a.src!==''||!a.paused))throw Error('Retired decoder sources retained');
 return {staleRejectionIgnored:true,suspendDecks:musicDecks.length,fadeStopped:true,retiredSourcesCleared:retired.length,activeDeckLimit:2};
};
'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=mock);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();result=p.evaluate('__musicRace()');b.close()
assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha
(ROOT/'reports/development-8.0/music-races.json').write_text(json.dumps({'source_sha256':sha,'mockedMediaPromises':True,'result':result},indent=2)+'\n');print('PASS stale playback rejection cannot stop current music; suspended fade/tails stop and retired sources unload',result)
