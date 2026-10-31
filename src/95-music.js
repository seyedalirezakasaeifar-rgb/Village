// Original offline chamber score. Two HTML media elements bound decoder memory;
// no synthesis or per-note scheduling competes with the simulation at runtime.
let musicEnabled=true,musicVolume=.45,musicGesture=false,musicTrack=-1,musicDecks=[],musicFade=null,musicError='';
try{const p=JSON.parse(localStorage.getItem('townledger-music')||'{}');if(typeof p.enabled==='boolean')musicEnabled=p.enabled;if(Number.isFinite(p.volume))musicVolume=clamp(p.volume,0,1)}catch(_){}
const MUSIC_TRACKS=[{file:'morning-ledger',title:'Morning Ledger',seconds:201.923},{file:'river-and-road',title:'River and Road',seconds:171.956},{file:'lamplit-windows',title:'Lamplit Windows',seconds:224.429}];
function rememberMusic(){try{localStorage.setItem('townledger-music',JSON.stringify({enabled:musicEnabled,volume:musicVolume}))}catch(_){}}
function musicAllowed(){return musicEnabled&&musicVolume>0&&musicGesture&&!!G&&!document.hidden&&!hostSuspended}
function musicStatus(){return !musicEnabled?'Music off':musicError?'Tap Play music to retry':!musicGesture?'Starts after your first tap':musicTrack<0?'Ready':MUSIC_TRACKS[musicTrack].title}
function stopMusic(){if(musicFade){clearInterval(musicFade);musicFade=null}for(const d of musicDecks)d.audio.pause()}
function setMusicVolumes(){for(const d of musicDecks)d.audio.volume=musicVolume*.72*d.gain}
function playMusicTrack(index){
 if(!musicAllowed())return;const previous=musicDecks.find(d=>d.index===musicTrack);musicTrack=index%MUSIC_TRACKS.length;musicError='';
 if(musicFade){clearInterval(musicFade);musicFade=null}
 for(const d of musicDecks)if(d!==previous)d.audio.pause();musicDecks=previous?[previous]:[];
 const audio=new Audio('music/'+MUSIC_TRACKS[musicTrack].file+'.ogg'),next={audio,index:musicTrack,gain:0};audio.preload='auto';musicDecks.push(next);setMusicVolumes();
 audio.addEventListener('timeupdate',()=>{if(next!==musicDecks[musicDecks.length-1]||!musicAllowed())return;if(MUSIC_TRACKS[next.index].seconds-audio.currentTime<4)playMusicTrack((next.index+1)%MUSIC_TRACKS.length)});
 audio.addEventListener('ended',()=>{if(next===musicDecks[musicDecks.length-1]&&musicAllowed())playMusicTrack((next.index+1)%MUSIC_TRACKS.length)});
 audio.addEventListener('error',()=>{if(next!==musicDecks[musicDecks.length-1])return;musicError='Unable to decode soundtrack';stopMusic()});
 const fadeFrom=previous?.gain||0,started=performance.now();
 audio.play().then(()=>{if(next!==musicDecks[musicDecks.length-1]){audio.pause();return}if(!musicAllowed()){stopMusic();return}musicFade=setInterval(()=>{if(!musicAllowed()){stopMusic();return}const t=clamp((performance.now()-started)/4000,0,1);next.gain=Math.sin(t*Math.PI/2);if(previous)previous.gain=fadeFrom*Math.cos(t*Math.PI/2);setMusicVolumes();if(t>=1){if(previous)previous.audio.pause();musicDecks=[next];clearInterval(musicFade);musicFade=null}},100)}).catch(()=>{musicError='Playback needs a tap';stopMusic()});
}
function refreshMusic(){
 if(!musicAllowed()){stopMusic();return}
 if(musicFade)return;
 if(musicTrack<0||musicError){playMusicTrack(musicTrack<0?0:musicTrack);return}
 const current=musicDecks.find(d=>d.index===musicTrack);if(!current){playMusicTrack(musicTrack);return}
 // Resume one current deck after interruption; never resume a stale fade tail.
 for(const d of musicDecks)if(d!==current)d.audio.pause();musicDecks=[current];current.gain=1;setMusicVolumes();if(current.audio.paused)current.audio.play().catch(()=>{musicError='Playback needs a tap'});
}
function musicControls(){return head('Music & atmosphere')+`<div class="council-card"><p class="desc">An original three-piece chamber soundtrack · about ten minutes of composed music. Music and effects have independent controls. ${esc(musicStatus())}</p><div class="btnrow"><button id="musicToggle" aria-pressed="${musicEnabled}">${musicEnabled?'MUSIC ON':'MUSIC OFF'}</button><button id="musicNext">NEXT PIECE</button></div><label class="range">Music volume <input id="musicVolume" type="range" min="0" max="100" value="${Math.round(musicVolume*100)}" aria-label="Music volume"></label></div>`}
const musicSettingsBase=renderSettingsFull;renderSettingsFull=function(){return musicControls()+musicSettingsBase()};
document.addEventListener('click',e=>{if(!e.isTrusted)return;musicGesture=true;const b=e.target.closest('button');if(b?.id==='musicToggle'){musicEnabled=!musicEnabled;musicError='';rememberMusic();refreshMusic();renderPanel('settings')}else if(b?.id==='musicNext'){musicEnabled=true;rememberMusic();playMusicTrack((musicTrack+1)%MUSIC_TRACKS.length);renderPanel('settings')}else refreshMusic()},{capture:true});
document.addEventListener('input',e=>{if(e.target.id!=='musicVolume')return;musicVolume=clamp(+e.target.value/100,0,1);rememberMusic();setMusicVolumes();refreshMusic()});
