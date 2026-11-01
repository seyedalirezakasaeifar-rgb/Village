// Typed model-to-view effects only; no DOM, arbitrary selector or host model write.
function workerRoutePresent(module,dto){
 if(!dto||typeof dto!=='object'||Array.isArray(dto)||Object.prototype.hasOwnProperty.call(dto,'module')||Object.prototype.hasOwnProperty.call(dto,'version'))throw Error('Invalid route presentation');
 const fields={ 'camera-grid':['kind','x','y','zoom'],'build-tool':['kind','tool','x','y','projectKind','projectId'],overlay:['kind','value'],'policy-draft':['kind','values'],'focus-policy':['kind','key'],'transit-draft':['kind','draft'],'clear-transit-draft':['kind'],'panel-close':['kind']};if(!fields[dto.kind]||Object.keys(dto).some(k=>!fields[dto.kind].includes(k)))throw Error('Unknown presentation field');
 const finite=(n,min,max)=>typeof n==='number'&&Number.isFinite(n)&&n>=min&&n<=max;
 switch(dto.kind){
 case 'camera-grid':if(!finite(dto.x,0,T-1)||!finite(dto.y,0,T-1)||!finite(dto.zoom,.025,1.7))throw Error('Invalid route camera');break;
 case 'build-tool':if(typeof dto.tool!=='string'||!Object.prototype.hasOwnProperty.call(buildCost,dto.tool)&&!['inspect','road_bridge','road_remove','urban_plan','urban_clearance','transit_route',''].includes(dto.tool)||dto.x!==undefined&&!finite(dto.x,0,T-1)||dto.y!==undefined&&!finite(dto.y,0,T-1))throw Error('Invalid route tool');buildMode=dto.tool;break;
 case 'overlay':if(dto.value!=='none'&&!Object.prototype.hasOwnProperty.call(MAP_OVERLAY_KEYS,dto.value))throw Error('Invalid route overlay');overlay=dto.value;break;
 case 'policy-draft':workerRouteValue(dto.values,{type:'object',fields:Object.fromEntries(Object.entries(dto.values||{}).map(([key,value])=>{const d=defs.find(d=>d[0]===key);if(key==='imports')return [key,{type:'boolean'}];if(!d)throw Error('Unknown policy proposal');return [key,{type:'number',min:d[2],max:d[3]}];}))});draftPolicy={...draftPolicy,...dto.values};break;
 case 'focus-policy':if(!defs.some(d=>d[0]===dto.key)&&dto.key!=='imports')throw Error('Unknown policy focus');break;
 case 'transit-draft':{let d=dto.draft;if(d&&!d.cancelOperation&&workerRouteModules.get(module)?.operations.has('draft-cancel')){d={...d,cancelOperation:'draft-cancel'};dto={...dto,draft:d};}if(!d||!['bus','elevated'].includes(d.mode)||!Number.isSafeInteger(d.depot)||!Array.isArray(d.stops)||d.stops.length>16||d.stops.some(x=>!Number.isSafeInteger(x)||x<0)||!Number.isSafeInteger(d.level)||d.level<0||d.level>3||!Number.isSafeInteger(d.editing)||d.editing< -1||!routeName(d.cancelOperation)||Object.keys(d).some(k=>!['mode','depot','stops','level','editing','quote','cancelOperation'].includes(k)))throw Error('Invalid presentation transit draft');transitDraft={...d,town:G};break;}
 case 'clear-transit-draft':cancelTransitDraft();if(buildMode==='transit_route')buildMode='';break;
 case 'panel-close':active='';break;
 default:throw Error('Unsupported route presentation kind');
 }
 const text=JSON.stringify(dto,(key,value)=>{if(typeof value==='function'||typeof value==='symbol'||typeof value==='bigint'||typeof value==='number'&&!Number.isFinite(value)||key==='town')throw Error('Presentation must be finite JSON without authority references');return value;});if(text.length>131072)throw Error('Presentation DTO too large');workerEffect('route-presentation',{version:1,module,...JSON.parse(text)});
}
