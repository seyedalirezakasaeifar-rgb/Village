package org.townledger.vale;

/** One acknowledged Back request; expired/replaced callbacks cannot close a town. */
final class BackNavigation {
    private int generation;
    private boolean pending;
    int begin(){if(pending)return 0;pending=true;return ++generation;}
    boolean isCurrent(int request){return pending&&request==generation;}
    boolean claim(int request){if(!isCurrent(request))return false;pending=false;return true;}
    void cancel(){pending=false;generation++;}
    static String script(int request){
        String ack="AndroidArchive.backResult("+request+",";
        return "(function(){try{const a=window.__townArchive;if(!a){"+ack+"false,true);return;}if(a.back()){"+ack+"true,true);return;}AndroidArchive.backSaving("+request+");Promise.resolve(a.prepareExit?a.prepareExit():false).then(ok=>{"+ack+"false,ok===true);},()=>{"+ack+"false,false);});}catch(e){"+ack+"false,false);}})();";
    }
}
