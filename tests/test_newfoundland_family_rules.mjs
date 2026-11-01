import fs from 'node:fs';
const code=fs.readFileSync(new URL('../assets/newfoundland-families.js',import.meta.url),'utf8'),{newfoundlandFamily, newfoundlandCondition}=await import('data:text/javascript;base64,'+Buffer.from(code).toString('base64'));
const size=16,base={id:7,x:5,y:5,kind:'home',condition:100,footprint:[85],districtKey:'a',waterDistance:null};
function family(b=base,d={},neighbors=[]){return newfoundlandFamily(b,{size,districts:{a:d},buildings:[b,...neighbors]});}
for(const incomeBand of ['Lower income','Middle income','Higher income'])for(const condition of [20,60,100]){const b={...base,condition,architecture:{buildingCue:'nl-historic-town-row',incomeBand}};if(family(b)!=='downtown-row')throw Error('authoritative cue changed');if(newfoundlandCondition(b)!==(condition<45?'distressed':condition<75?'weathered':'maintained'))throw Error('condition not authoritative');}
for(const [cue,expected] of [['nl-outport-house','coastal-saltbox'],['nl-new-suburb-house','suburban-cape'],['nl-compact-worker-house','compact-timber']])if(family({...base,architecture:{buildingCue:cue}})!==expected)throw Error(cue);
if(family({...base,footprint:[85,86,101,102],architecture:{buildingCue:'nl-merchant-house'}})!=='detached-merchant')throw Error('large actual lot required');
if(family({...base,architecture:{buildingCue:'nl-merchant-house'}})==='detached-merchant')throw Error('cue cannot enlarge a lot');
if(family(base,{incomeBand:'Higher income',density:1})!=='compact-timber')throw Error('renderer invented context without authoritative cue');
if(family({...base,kind:'grocer',retailCentre:true})!=='retail-centre')throw Error('mall flag');
if(family({...base,stage:{redevelopment:true}})!=='construction')throw Error('project stage');
for(const [kind,expected] of [['bank','financial-commercial'],['clinic','cottage-hospital'],['fire','apparatus-hall'],['warehouse','freight-store'],['fishery','working-waterfront'],['farm','resource-property'],['tower','urban-residential-block']])if(family({...base,kind})!==expected)throw Error(kind);
console.log('PASS independent use, actual lot/density/water/income, condition and project family rules');
