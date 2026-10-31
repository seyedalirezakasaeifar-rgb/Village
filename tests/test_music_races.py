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
 // Native resume creates another play epoch for the same element. Its later
 // media errors must still surface, while old play-promise failures stay stale.
 refreshMusic();const resumed=__mediaRequests[__mediaRequests.length-1];resumed.resolve();await Promise.resolve();resumed.audio.dispatchEvent(new Event('error'));
 if(!musicError||!resumed.audio.paused)throw Error('Resumed current media error was ignored');
 musicError='';playMusicTrack(3);const pending=__mediaRequests[__mediaRequests.length-1],incoming=musicDecks[musicDecks.length-1],tail=incoming.previous,tailGain=tail.gain;
 // The synchronous play mock marks paused=false before its deferred promise
 // resolves, exactly the interval in which ordinary refreshes used to cut tails.
 refreshMusic();refreshMusic();
 if(musicDecks.length!==2||incoming.gain!==0||incoming.previous!==tail||tail.retired||tail.gain!==tailGain)throw Error('Routine refresh interrupted a pending handoff');
 pending.resolve();await Promise.resolve();stopMusic();refreshMusic();__mediaRequests[__mediaRequests.length-1].resolve();await Promise.resolve();
 const fullTrack=musicTrack;incoming.audio.duration=100;incoming.audio.currentTime=95;incoming.audio.dispatchEvent(new Event('timeupdate'));
 if(musicTrack!==fullTrack)throw Error('Partial stream duration truncated the composition');
 incoming.audio.currentTime=MUSIC_TRACKS[fullTrack].seconds-7;incoming.audio.dispatchEvent(new Event('timeupdate'));
 if(musicTrack===fullTrack)throw Error('Full score duration did not hand off');
 stopMusic();
 return {staleRejectionIgnored:true,suspendDecks:musicDecks.length,fadeStopped:true,retiredSourcesCleared:retired.length,activeDeckLimit:2,resumedMediaErrorSurfaced:true,pendingHandoffPreserved:true,partialDurationIgnored:true};
};
'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page();p.set_content(html);p.add_script_tag(content=mock);p.add_script_tag(content=source.replace('// SOURCE: 99-instrumentation.js',probe+'\n// SOURCE: 99-instrumentation.js'));p.locator('#newTown').click();p.locator('#pause').click();result=p.evaluate('__musicRace()');b.close()
assert hashlib.sha256((ROOT/'assets/game.js').read_bytes()).hexdigest()==sha
(ROOT/'reports/development-8.0/music-races.json').write_text(json.dumps({'source_sha256':sha,'mockedMediaPromises':True,'result':result},indent=2)+'\n');print('PASS stale playback rejection cannot stop current music; suspended fade/tails stop and retired sources unload',result)
