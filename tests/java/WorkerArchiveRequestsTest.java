package org.townledger.vale;

public final class WorkerArchiveRequestsTest {
    static void check(boolean value){if(!value)throw new AssertionError();}
    public static void main(String[] args){
        WorkerArchiveRequests requests=new WorkerArchiveRequests();
        check(requests.register(1,4,"export"));check(!requests.register(1,4,"export"));check(!requests.register(2,4,"delete"));
        check(requests.complete(1,3)==null);check(requests.size()==1);
        WorkerArchiveRequests.Request first=requests.complete(1,4);check(first!=null&&first.id==1&&first.epoch==4&&"export".equals(first.operation));
        check(requests.complete(1,4)==null);check(!requests.refuse(99,4));
        check(requests.register(2,4,"restore"));check(requests.refuse(2,4));check(requests.complete(2,4)==null);
        check(requests.register(3,5,"restore"));check(requests.current("restore").id==3);
        check(requests.register(4,5,"save"));check(requests.register(5,5,"export"));check(requests.register(6,5,"save"));check(!requests.register(7,5,"save"));
        requests.clear();check(requests.size()==0);check(!requests.register(3,5,"restore"));check(requests.register(7,5,"restore"));
        System.out.println("PASS async archive id/epoch correlation, duplicate refusal, stale reply, cancel, capacity and lifecycle clear");
    }
}
