// Presentation preferences persist independently. Climate rules travel with the town archive.
const OPTION_DEFAULTS={quality:'balanced',fps:30,traffic:true,effects:true,decor:true,seasons:false,weather:false,largeText:false,reducedMotion:false,autoSave:30,showHints:true,streetNames:true};
let gameOptions={...OPTION_DEFAULTS};
try{const old=JSON.parse(localStorage.getItem('townledger-options')||'{}');for(const k of Object.keys(OPTION_DEFAULTS))if(typeof old[k]===typeof OPTION_DEFAULTS[k])gameOptions[k]=old[k];}catch(_){}
if(!['low','balanced','high'].includes(gameOptions.quality))gameOptions.quality='balanced';
if(![20,30,60].includes(gameOptions.fps))gameOptions.fps=30;
if(![15,30,60,120].includes(gameOptions.autoSave))gameOptions.autoSave=30;
function seasonsEnabled(){return G?.climateSeasons===true;}
function weatherEnabled(){return G?.climateWeather===true;}
function visualMonth(){return seasonsEnabled()?G.month:5;}
function applyPresentationOptions(){
 document.body.classList.toggle('large-text',gameOptions.largeText);document.body.classList.toggle('hide-hints',!gameOptions.showHints);
 if(typeof atlas!=='undefined')clearAtlas();if(typeof fit==='function')fit();staticDirty=true;dirty=true;
}
// Apply classes now; renderer initialization follows in the ordered bundle.
document.body.classList.toggle('large-text',gameOptions.largeText);document.body.classList.toggle('hide-hints',!gameOptions.showHints);
