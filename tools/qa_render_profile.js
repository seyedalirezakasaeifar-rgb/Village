window.__liveProfile={};
const profileRenderStage=(name,fn)=>function(...args){const t=performance.now();try{return fn.apply(this,args)}finally{const rows=__liveProfile[name]||(__liveProfile[name]=[]);if(rows.length<200000)rows.push(performance.now()-t)}};
drawGround=profileRenderStage('ground',drawGround);prepareScene=profileRenderStage('scene',prepareScene);paintCastShadows=profileRenderStage('shadows',paintCastShadows);drawSceneSprite=profileRenderStage('sprite',drawSceneSprite);drawUrbanOverlay=profileRenderStage('urbanOverlay',drawUrbanOverlay);drawDistrictLife=profileRenderStage('districtLife',drawDistrictLife);drawTransitInfrastructure=profileRenderStage('transitInfrastructure',drawTransitInfrastructure);transitArtActors=profileRenderStage('transitActors',transitArtActors);drawStatic=profileRenderStage('static',drawStatic);

spriteFor=profileRenderStage('spriteCache',spriteFor);
