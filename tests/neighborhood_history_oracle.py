"""Independent authoritative quarter observation for paired source comparisons."""
ORACLE_PROBE = r'''let independentlyObserved=[];
function independentQuarter(){const blocks={};for(const b of G.buildings){const key=Math.floor(b.x/8)+':'+Math.floor(b.y/8),row=blocks[key]||(blocks[key]={residents:0,occupiedHomes:0,staffedJobs:0,jobCapacity:0}),households=G.households.filter(h=>h.home===b.id&&h.people.length);row.residents+=households.reduce((n,h)=>n+h.people.length,0);if(households.length)row.occupiedHomes++;const f=G.firms[b.firm];if(f&&!f.closed){row.staffedJobs+=(f.attendingWorkers||f.workers).length;row.jobCapacity+=f.jobs;}}for(const row of Object.values(blocks)){row.staffedJobs=Math.round(row.staffedJobs);row.jobCapacity=Math.round(row.jobCapacity);}independentlyObserved=[...independentlyObserved.slice(-1),{day:G.day,blocks}];}
const independentReviewBase=urbanDistrictReview;urbanDistrictReview=function(){independentReviewBase();if(G.day%90===0)independentQuarter();};
window.__historyOracle=()=>independentlyObserved;window.__resetHistoryOracle=()=>{independentlyObserved=[]};
'''
