// Explicit DOM boundaries for existing civic model functions, worker realm only.
function workerRouteAppendSurvey(markup){if(typeof markup!=='string'||markup.length>262144)throw Error('Invalid trusted survey markup');workerEffect('route-presentation',{version:1,module:'civic',kind:'rendered-survey',markup});}
openCivicProjects=function(kind=''){openPanel('agenda');workerRoutePresent('civic',{kind:'focus-project',projectKind:kind});};
civicProjectVisit=function(x,y,kind='',projectKind=''){
 if(!Number.isInteger(x)||!Number.isInteger(y)||x<0||x>=T||y<0||y>=T)throw Error('Invalid civic visit');
 if(!kind&&buildMode){cancelTransitDraft();buildMode='';pointer.hover=null;pointer.down=false;pointer.activeId=null;pointer.lastRoad=null;roadPainted.clear();}
 if(kind&&projectKind){const project=G.civicProjects?.active[projectKind];civicProjectSurveyTarget=project?{town:G,id:project.id,projectKind,kind,x,y}:null;}
 overlay='none';parcelFocus=null;workerRoutePresent('civic',{kind:'overlay',value:'none'});
 if(kind){buildMode=kind;pointer.hover={x,y};workerRoutePresent('civic',{kind:'build-tool',tool:kind,x,y,projectKind});}
 workerRoutePresent('civic',{kind:'camera-grid',x,y,zoom:.85});workerRoutePresent('civic',{kind:'panel-close'});dirty=true;
};

revealCharterOffice=function(){workerEffect('route-presentation',{version:1,module:'civic',kind:'focus-office',office:'charter'});};
openCivicOperations=function(){openPanel('economy');workerEffect('route-presentation',{version:1,module:'civic',kind:'focus-office',office:'logistics'});};
previewParcel=function(id){const p=ANNEX_PARCELS.find(p=>p.id===id);if(!p)return;parcelFocus=id;overlay='charter';active='';workerEffect('route-presentation',{version:1,module:'civic',kind:'parcel-preview',parcel:id});dirty=true;toast(p.name+': '+(G.charter.owned.includes(id)?'chartered land':'regional land · review its deed in Public Works'));};
