package org.townledger.vale;
public final class BackNavigationTest {
    static void check(boolean ok){if(!ok)throw new AssertionError();}
    public static void main(String[] args){
        if(args.length>0){System.out.print(BackNavigation.script(17));return;}
        BackNavigation b=new BackNavigation();int first=b.begin();check(first>0);check(b.begin()==0);check(!b.claim(first+1));check(b.claim(first));check(!b.claim(first));
        int expired=b.begin();check(b.claim(expired));int next=b.begin();check(next>expired);check(!b.claim(expired));check(b.claim(next));
        int paused=b.begin();b.cancel();check(!b.claim(paused));int resumed=b.begin();check(resumed>paused);check(b.claim(resumed));
        System.out.println("PASS Back request identity, duplicate suppression, timeout/pause cancellation and stale acknowledgements");
    }
}
