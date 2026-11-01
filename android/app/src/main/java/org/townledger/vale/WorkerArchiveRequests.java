package org.townledger.vale;

import java.util.HashMap;
import java.util.Map;

/** Correlates asynchronous worker completions with the exact request that admitted them. */
final class WorkerArchiveRequests {
    static final class Request {
        final long id,epoch;
        final String operation;
        Request(long id,long epoch,String operation){this.id=id;this.epoch=epoch;this.operation=operation;}
    }
    private final Map<Long,Request> pending=new HashMap<Long,Request>();
    private long lastId;

    synchronized boolean register(long id,long epoch,String operation){
        if(id<=lastId||id>9007199254740991L||epoch<0||pending.size()>=4)return false;
        if(!"export".equals(operation)&&!"restore".equals(operation)&&!"save".equals(operation))return false;
        lastId=id;pending.put(id,new Request(id,epoch,operation));return true;
    }
    synchronized boolean refuse(long id,long epoch){Request r=pending.get(id);if(r==null||r.epoch!=epoch)return false;pending.remove(id);return true;}
    synchronized void refuseId(long id){pending.remove(id);}
    synchronized Request complete(long id,long epoch){Request r=pending.get(id);if(r==null||r.epoch!=epoch)return null;pending.remove(id);return r;}
    synchronized Request current(String operation){for(Request r:pending.values())if(operation.equals(r.operation))return r;return null;}
    synchronized Request failFirst(){if(pending.isEmpty())return null;Long id=pending.keySet().iterator().next();return pending.remove(id);}
    synchronized int size(){return pending.size();}
    synchronized void clear(){pending.clear();}
}
