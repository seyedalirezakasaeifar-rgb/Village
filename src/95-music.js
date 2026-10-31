// Original offline score. Streaming HTML media, at most two live decks and one
// fade timer; no runtime synthesis or decoded-buffer playlist competes with town work.
const MUSIC_TRACKS=[{"file":"morning-ledger","title":"Morning Ledger","seconds":201.923,"tags":["home","quiet"],"mix":1.636},{"file":"river-and-road","title":"River And Road","seconds":171.957,"tags":["water","trade"],"mix":1.677},{"file":"lamplit-windows","title":"Lamplit Windows","seconds":224.429,"tags":["evening","quiet"],"mix":1.621},{"file":"orchard-footpaths","title":"Orchard Footpaths","seconds":281.5,"tags":["home","quiet"],"mix":1.0},{"file":"rails-to-greyhaven","title":"Rails to Greyhaven","seconds":287.457,"tags":["trade","work"],"mix":1.0},{"file":"waterline-work","title":"Work at the Waterline","seconds":275.786,"tags":["water","trade"],"mix":1.0},{"file":"market-day","title":"The Long Market Day","seconds":306.955,"tags":["market","home"],"mix":1.0},{"file":"after-the-rain","title":"Rooms after the Rain","seconds":379.682,"tags":["evening","quiet"],"mix":1.0},{"file":"a-borough-grows","title":"A Borough Grows","seconds":355.184,"tags":["growth","home"],"mix":1.0},{"file":"quiet-river-reprise","title":"The Quiet River","seconds":361.5,"tags":["water","evening","quiet"],"mix":1.0}];
const MUSIC_FADE_SECONDS=8,MUSIC_RECENT_LIMIT=6;
let musicEnabled=true,musicVolume=.45,musicMood='adaptive',musicGesture=false,musicTrack=-1,musicDecks=[],musicFade=null,musicError='',musicHistory=[],musicEpoch=0,musicRandomState=(Date.now()^0x6b84379d)>>>0;
try{const p=JSON.parse(localStorage.getItem('townledger-music')||'{}');if(typeof p.enabled==='boolean')musicEnabled=p.enabled;if(Number.isFinite(p.volume))musicVolume=clamp(p.volume,0,1);if(['adaptive','quiet','lively'].includes(p.mood))musicMood=p.mood;if(Number.isInteger(p.randomState))musicRandomState=p.randomState>>>0;if(Array.isArray(p.history))musicHistory=p.history.filter((id,i,a)=>MUSIC_TRACKS.some(t=>t.file===id)&&a.lastIndexOf(id)===i).slice(-MUSIC_RECENT_LIMIT)}catch(_){}
function rememberMusic(){try{localStorage.setItem('townledger-music',JSON.stringify({enabled:musicEnabled,volume:musicVolume,mood:musicMood,history:musicHistory,randomState:musicRandomState}))}catch(_){}}
function musicRandom(){musicRandomState^=musicRandomState<<13;musicRandomState^=musicRandomState>>>17;musicRandomState^=musicRandomState<<5;musicRandomState>>>=0;return musicRandomState/4294967296;}
function musicContext(){
 const tags=nightMode?['evening','quiet']:['home'];
 if((G?.regionalTrade?.shipments?.length||0)>2)tags.push('trade');
 if(G?.firms.some(f=>!f.closed&&['fishery','wharf'].includes(f.kind)&&(f.production>0||f.revenue>0)))tags.push('water');
 if((G?.stats.population||0)>240)tags.push('market','growth');
 if((G?.stats.hardship||0)>20)tags.push('quiet');
 return tags;
}
function chooseMusicTrack(){
 const recent=new Set(musicHistory.slice(-Math.min(MUSIC_RECENT_LIMIT,MUSIC_TRACKS.length-1)));if(musicTrack>=0)recent.add(MUSIC_TRACKS[musicTrack].file);
 let pool=MUSIC_TRACKS.map((t,index)=>({t,index})).filter(o=>!recent.has(o.t.file));if(!pool.length)pool=MUSIC_TRACKS.map((t,index)=>({t,index})).filter(o=>o.index!==musicTrack);
 const context=musicContext();let total=0;for(const o of pool){o.weight=1+o.t.tags.reduce((n,tag)=>n+(context.includes(tag)?2:0),0);if(musicMood==='quiet')o.weight+=o.t.tags.some(tag=>['quiet','evening'].includes(tag))?7:0;if(musicMood==='lively')o.weight+=o.t.tags.some(tag=>['trade','market','work','growth'].includes(tag))?7:0;total+=o.weight;}
 let pick=musicRandom()*total;for(const o of pool){pick-=o.weight;if(pick<=0)return o.index;}return pool[pool.length-1].index;
}
function recordMusicPlayback(index){const id=MUSIC_TRACKS[index].file;if(musicHistory[musicHistory.length-1]!==id)musicHistory.push(id);musicHistory=musicHistory.slice(-MUSIC_RECENT_LIMIT);rememberMusic();}
function musicAllowed(){return musicEnabled&&musicVolume>0&&musicGesture&&!!G&&!document.hidden&&!hostSuspended;}
function musicStatus(){return !musicEnabled?'Music off':musicVolume===0?'Music volume is zero':musicError?'Playback interrupted · tap Retry music':!musicGesture?'Starts after your first tap':musicTrack<0?'Ready':MUSIC_TRACKS[musicTrack].title;}
function retireMusicDeck(deck){if(!deck||deck.retired)return;deck.retired=true;try{if(deck.handlers&&deck.audio.removeEventListener)for(const [name,handler] of Object.entries(deck.handlers))deck.audio.removeEventListener(name,handler);deck.handlers=null;deck.previous=null;deck.audio.pause();if(deck.audio.removeAttribute)deck.audio.removeAttribute('src');else deck.audio.src='';if(deck.audio.load)deck.audio.load();}catch(_){}}
function stopMusic(){
 musicEpoch++;if(musicFade){clearInterval(musicFade);musicFade=null;}
 const current=musicDecks.find(d=>d.index===musicTrack&&!d.retired)||musicDecks[musicDecks.length-1];
 for(const d of musicDecks){d.audio.pause();d.starting=false;if(d!==current)retireMusicDeck(d);}musicDecks=current?[current]:[];if(current)current.previous=null;
}
function setMusicVolumes(){for(const d of musicDecks)d.audio.volume=clamp(musicVolume*.78*(MUSIC_TRACKS[d.index].mix||1)*d.gain,0,1);}
function musicPlayFailed(deck,epoch){if(epoch!==musicEpoch||deck.retired)return;musicError='Playback needs a tap or an available soundtrack file';stopMusic();}
function playMusicTrack(index=chooseMusicTrack()){
 if(!musicAllowed()||!Number.isInteger(index)||index<0||index>=MUSIC_TRACKS.length)return;
 const epoch=++musicEpoch,previous=musicDecks.filter(d=>!d.retired).sort((a,b)=>b.gain-a.gain)[0];
 if(musicFade){clearInterval(musicFade);musicFade=null;}for(const d of musicDecks)if(d!==previous)retireMusicDeck(d);musicDecks=previous?[previous]:[];if(previous)previous.previous=null;
 musicTrack=index;musicError='';const audio=new Audio('music/'+MUSIC_TRACKS[index].file+'.ogg'),next={audio,index,gain:0,starting:true,retired:false,previous};audio.preload='auto';musicDecks.push(next);setMusicVolumes();
 const advance=()=>{if(!next.retired&&next===musicDecks[musicDecks.length-1]&&musicAllowed())playMusicTrack(chooseMusicTrack());};
 // Streamed Vorbis duration can describe an incomplete HTTP buffer. The shipped
 // score manifest supplies the complete duration; ended still handles early EOF.
 next.handlers={timeupdate:()=>{if(MUSIC_TRACKS[index].seconds-audio.currentTime<=MUSIC_FADE_SECONDS)advance();},ended:advance,error:()=>{if(!next.retired&&next===musicDecks[musicDecks.length-1])musicPlayFailed(next,musicEpoch);}};
 for(const [name,handler] of Object.entries(next.handlers))audio.addEventListener(name,handler);
 Promise.resolve(audio.play()).then(()=>{
  next.starting=false;if(next.retired)return;if(!musicAllowed()){audio.pause();return;}if(epoch!==musicEpoch)return;
  recordMusicPlayback(index);const started=performance.now(),fadeFrom=next.previous?.gain||0;
  musicFade=setInterval(()=>{if(epoch!==musicEpoch||!musicAllowed()){if(epoch===musicEpoch)stopMusic();return;}const t=clamp((performance.now()-started)/(MUSIC_FADE_SECONDS*1000),0,1);next.gain=Math.sin(t*Math.PI/2);if(next.previous)next.previous.gain=fadeFrom*Math.cos(t*Math.PI/2);setMusicVolumes();if(t>=1){retireMusicDeck(next.previous);next.previous=null;musicDecks=[next];clearInterval(musicFade);musicFade=null;}},100);
 }).catch(()=>musicPlayFailed(next,epoch));
}
function refreshMusic(retry=false){
 if(!musicAllowed()){if(musicDecks.some(d=>!d.audio.paused)||musicFade)stopMusic();return;}const failed=!!musicError;if(failed&&!retry)return;if(retry)musicError='';if(musicFade)return;
 if(musicTrack<0||failed){playMusicTrack(musicTrack<0?chooseMusicTrack():musicTrack);return;}
 const current=musicDecks.find(d=>d.index===musicTrack&&!d.retired);if(!current){playMusicTrack(musicTrack);return;}
 // A pending decoder still owns its predecessor and its zero gain. Routine
 // clicks/daily ambience refreshes must not cut that tail before play resolves.
 if(current.starting)return;
 for(const d of musicDecks)if(d!==current)retireMusicDeck(d);musicDecks=[current];current.previous=null;current.gain=1;setMusicVolumes();
 if(current.audio.paused&&!current.starting){const epoch=++musicEpoch;current.starting=true;Promise.resolve(current.audio.play()).then(()=>{current.starting=false;if(current.retired)return;if(!musicAllowed()){current.audio.pause();return;}if(epoch===musicEpoch)recordMusicPlayback(current.index);}).catch(()=>musicPlayFailed(current,epoch));}
}
function musicControls(){return head('Music & atmosphere')+`<div class="council-card"><p class="desc">Ten original chamber pieces · about47 minutes. The next piece reflects the town’s activity and your preferred character, with six recent pieces held out. Changes take effect between pieces. Music and effects have separate controls.</p><p><b>${esc(musicStatus())}</b></p><div class="btnrow"><button id="musicToggle" aria-pressed="${musicEnabled}">${musicEnabled?'MUSIC ON':'MUSIC OFF'}</button><button id="musicNext">NEXT PIECE</button>${musicError?'<button id="musicRetry">Retry music</button>':''}</div><label class="range">Music volume <input id="musicVolume" type="range" min="0" max="100" value="${Math.round(musicVolume*100)}" aria-label="Music volume"></label><label>Music character <select id="musicMood" aria-label="Music character">${[['adaptive','Follow the town'],['quiet','Quieter selections'],['lively','Livelier selections']].map(([id,label])=>`<option value="${id}" ${musicMood===id?'selected':''}>${label}</option>`).join('')}</select></label><details><summary>Original score & credits</summary><p class="desc">Original melodies, arrangements and offline synthesis for TownLedger, dedicated under CC0. No borrowed recordings or samples.</p>${MUSIC_TRACKS.map(t=>`<p class="desc">${esc(t.title)} · ${Math.round(t.seconds/60)} min</p>`).join('')}</details></div>`;}
const musicSettingsBase=renderSettingsFull;renderSettingsFull=function(){return musicControls()+musicSettingsBase();};
function handleMusicGesture(e){if(!e.isTrusted)return;musicGesture=true;const b=e.target.closest('button');if(b?.id==='musicToggle'){musicEnabled=!musicEnabled;rememberMusic();refreshMusic(true);renderPanel('settings');}else if(b?.id==='musicNext'){musicEnabled=true;rememberMusic();playMusicTrack(chooseMusicTrack());renderPanel('settings');}else if(b?.id==='musicRetry'){refreshMusic(true);renderPanel('settings');}else refreshMusic();}
document.addEventListener('click',handleMusicGesture,{capture:true});
document.addEventListener('input',e=>{if(e.target.id!=='musicVolume')return;musicVolume=clamp(+e.target.value/100,0,1);rememberMusic();setMusicVolumes();refreshMusic();});
document.addEventListener('change',e=>{if(e.target.id!=='musicMood')return;if(['adaptive','quiet','lively'].includes(e.target.value)){musicMood=e.target.value;rememberMusic();}});
