function referenceRoadDistance(a,b){
 if(a==null||b==null)return Infinity;
 if(a===b)return 0;
 const net=graph();if(net.parts[a]!==net.parts[b])return Infinity;
 if(!net.distCache)net.distCache=new Map();
 const key=a<b?a*T*T+b:b*T*T+a;
 if(net.distCache.has(key))return net.distCache.get(key);
 const dist=routeBetween(a,b).length-1;
 if(net.distCache.size>3000)net.distCache.clear();
 net.distCache.set(key,dist);
 return dist;
}
