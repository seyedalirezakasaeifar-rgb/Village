// Pure artistic classification of committed facts. It never creates wealth,
// population, damage, capacity or a simulated district designation.
export function newfoundlandFamily(b,state){
 const area=b.footprint.length;
 if(b.stage?.redevelopment||b.kind==='worksite')return 'construction';
 if(b.retailCentre)return 'retail-centre';
 if(b.kind==='tower')return 'urban-residential-block';
 if(b.kind==='apartment')return 'urban-terrace';
 if(b.kind==='home'){
  // These cues are authored by the model's urbanBuildingDescriptor, not a
  // second renderer-side income or district classifier. Old saves use a
  // neutral timber form until the authoritative projection is available.
  const cue=state.districtSemanticsAccepted?b.architecture?.buildingCue:undefined;
  if(cue==='nl-historic-town-row')return 'downtown-row';
  if(cue==='nl-outport-house')return 'coastal-saltbox';
  if(cue==='nl-new-suburb-house')return b.id%2?'suburban-cape':'suburban-bungalow';
  if(cue==='nl-merchant-house'&&area>=4)return 'detached-merchant';
  return 'compact-timber';
 }
 if(['grocer','bakery','tavern'].includes(b.kind))return 'market-street';
 if(['bank','office'].includes(b.kind))return 'financial-commercial';
 if(['townhall','courthouse','police','school','college'].includes(b.kind))return 'civic-institution';
 if(b.kind==='clinic')return 'cottage-hospital';
 if(b.kind==='fire')return 'apparatus-hall';
 if(['warehouse','wharf','fishery'].includes(b.kind))return b.kind==='warehouse'?'freight-store':'working-waterfront';
 if(['factory','mill','sawmill','contractor'].includes(b.kind))return 'industrial-workshop';
 if(['farm','forestry','quarry'].includes(b.kind))return 'resource-property';
 if(['park','square'].includes(b.kind))return 'public-space';
 if(['transit_depot','elevated_station','metro_station','airport','watchtower'].includes(b.kind))return 'network-facility';
 return 'unclassified';
}
export function newfoundlandCondition(b){return b.condition<45?'distressed':b.condition<75?'weathered':'maintained';}
