const settings61Base=renderSettingsFull;
renderSettingsFull=function(){
 const toggle=(k,label,note)=>`<div class="option-row"><div><strong>${label}</strong><small>${note}</small></div><button data-option="${k}" aria-pressed="${k==='seasons'?seasonsEnabled():k==='weather'?weatherEnabled():gameOptions[k]}">${(k==='seasons'?seasonsEnabled():k==='weather'?weatherEnabled():gameOptions[k])?'ON':'OFF'}</button></div>`;
 const select=(k,label,values)=>`<label class="option-row"><strong>${label}</strong><select data-preference="${k}">${values.map(([v,t])=>`<option value="${v}" ${String(gameOptions[k])===String(v)?'selected':''}>${t}</option>`).join('')}</select></label>`;
 return head('Display & accessibility')+select('quality','Graphics quality',[['low','Performance'],['balanced','Balanced'],['high','Rich detail']])+select('fps','Frame-rate limit',[[20,'20 FPS'],[30,'30 FPS'],[60,'60 FPS']])+toggle('streetNames','Street names','Named streets and a visible road hierarchy.')+toggle('traffic','Visible traffic','Commuters and trucks. Cargo and jobs continue when hidden.')+toggle('effects','Atmospheric effects','Smoke, water shimmer and weather particles.')+toggle('decor','Gardens & landscape detail','Flowers, fences, masonry and roof texture.')+toggle('reducedMotion','Reduced motion','Stop decorative movement and traffic animation.')+toggle('largeText','Larger text','Larger menu labels and reading text.')+toggle('showHints','Map hints','Show the short map guidance below the town.')+
 head('Climate rules')+toggle('seasons','Seasonal cycle','OFF by default: green landscape and stable farm output all year. Saved with this town.')+toggle('weather','Weather events','OFF by default: no storms or droughts. Saved with this town.')+
 head('Saving')+select('autoSave','Autosave interval',[[15,'15 seconds'],[30,'30 seconds'],[60,'1 minute'],[120,'2 minutes']])+tip('Pausing or leaving the app also saves. At 64×, Balanced and Performance simplify ground detail and reduce map resolution; pause or choose Rich detail to restore full detail. At high speed, the map refreshes at up to 20 FPS to give the economy more CPU time. The speed indicator measures days actually completed; slower devices may run below the selected rate.')+settings61Base();
};
function changePreference(key,value){
 if(!(key in OPTION_DEFAULTS))return;
 gameOptions[key]=value;
 if(key==='seasons'&&G){G.climateSeasons=value;staticDirty=true;}
 if(key==='weather'&&G){G.climateWeather=value;if(!value)G.weather='clear';refreshAmbience();}
 try{localStorage.setItem('townledger-options',JSON.stringify(gameOptions));}catch(_){}
 applyPresentationOptions();if(G){save();renderPanel('settings');}
}
document.addEventListener('click',e=>{const b=e.target.closest('[data-option]');if(b){const k=b.dataset.option;changePreference(k,!(k==='seasons'?seasonsEnabled():k==='weather'?weatherEnabled():gameOptions[k]));}});
document.addEventListener('change',e=>{const k=e.target.dataset.preference;if(k)changePreference(k,typeof OPTION_DEFAULTS[k]==='number'?Number(e.target.value):e.target.value);});
