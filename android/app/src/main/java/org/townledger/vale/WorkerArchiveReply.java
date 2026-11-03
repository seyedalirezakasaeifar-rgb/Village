package org.townledger.vale;

import android.util.JsonReader;
import android.util.JsonToken;
import java.io.StringReader;

/** Bounded, streaming parser for the worker completion envelope. */
final class WorkerArchiveReply {
    final long id,epoch;
    final boolean ok,admitted,committed,restored,persisted;
    final String archive,error,outcome;
    private WorkerArchiveReply(long id,long epoch,boolean ok,boolean admitted,boolean committed,boolean restored,boolean persisted,String archive,String error,String outcome){
        this.id=id;this.epoch=epoch;this.ok=ok;this.admitted=admitted;this.committed=committed;this.restored=restored;this.persisted=persisted;this.archive=archive;this.error=error;this.outcome=outcome;
    }
    static WorkerArchiveReply parse(String json)throws Exception{
        if(json==null||json.length()>(long)ArchiveIO.LIMIT*6L+131072L)throw new IllegalArgumentException("completion envelope exceeds the bounded archive transport limit");
        long id=0,epoch=-1;boolean ok=false,admitted=false,committed=false,restored=false,persisted=false,hasId=false,hasEpoch=false,hasOk=false,hasAdmitted=false,hasCommitted=false;String archive=null,error=null,outcome=null;
        WorkerArchiveReplyFields fields=new WorkerArchiveReplyFields();
        JsonReader reader=new JsonReader(new StringReader(json));reader.beginObject();
        while(reader.hasNext()){
            String name=reader.nextName();
            fields.envelope(name);
            if("id".equals(name)){id=reader.nextLong();hasId=true;}else if("epoch".equals(name)){epoch=reader.nextLong();hasEpoch=true;}else if("ok".equals(name)){ok=reader.nextBoolean();hasOk=true;}else if("admitted".equals(name)){admitted=reader.nextBoolean();hasAdmitted=true;}else if("committed".equals(name)){committed=reader.nextBoolean();hasCommitted=true;}else if("error".equals(name))error=reader.nextString();else if("outcome".equals(name))outcome=reader.nextString();
            else if("result".equals(name)){if(reader.peek()==JsonToken.NULL){reader.nextNull();continue;}reader.beginObject();while(reader.hasNext()){String field=reader.nextName();fields.result(field);if("archive".equals(field))archive=reader.nextString();else if("restored".equals(field))restored=reader.nextBoolean();else if("persisted".equals(field))persisted=reader.nextBoolean();else reader.skipValue();}reader.endObject();}
            else reader.skipValue();
        }
        reader.endObject();if(reader.peek()!=JsonToken.END_DOCUMENT||!hasId||!hasEpoch||!hasOk||!hasAdmitted||!hasCommitted||id<=0||id>9007199254740991L||epoch<0)throw new IllegalArgumentException("invalid worker archive completion");
        return new WorkerArchiveReply(id,epoch,ok,admitted,committed,restored,persisted,archive,error,outcome);
    }
}
