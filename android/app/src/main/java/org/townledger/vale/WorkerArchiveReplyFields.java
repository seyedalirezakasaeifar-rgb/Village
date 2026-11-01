package org.townledger.vale;

import java.util.HashSet;
import java.util.Set;

/** Explicit uniqueness for the two objects whose members affect native completion. */
final class WorkerArchiveReplyFields {
    private static final int MAX_FIELDS=128, MAX_NAME_UNITS=256;
    private final Set<String> envelope=new HashSet<String>();
    private final Set<String> result=new HashSet<String>();

    void envelope(String name){record(envelope,name);}
    void result(String name){record(result,name);}
    private static void record(Set<String> fields,String name){
        if(name==null||name.length()>MAX_NAME_UNITS||fields.size()>=MAX_FIELDS)
            throw new IllegalArgumentException("completion member budget exceeded");
        if(!fields.add(name))throw new IllegalArgumentException("duplicate completion member");
    }
}
