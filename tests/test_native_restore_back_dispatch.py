"""Compile the real import-busy Back branch with host state and the real registry."""
from pathlib import Path
import subprocess,tempfile,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
activity=ROOT/'android/app/src/main/java/org/townledger/vale/MainActivity.java';source=activity.read_text();start=source.index('if(restoringArchive)',source.index('@Override public void onBackPressed()'));opening=source.index('{',start);depth=1;end=opening+1
while depth:
 if source[end]=='{':depth+=1
 elif source[end]=='}':depth-=1
 end+=1
branch=source[start:end]
harness='''package org.townledger.vale;
public final class NativeRestoreBackDispatchTest {
 boolean restoringArchive=true,workerRestoreAwaitingSave=false;int cancelCalls;
 final WorkerArchiveRequests workerArchiveRequests=new WorkerArchiveRequests();
 void cancelWorkerRestore(){cancelCalls++;}
 void pressBack(){BRANCH}
 void check(int n){if(cancelCalls!=n)throw new AssertionError("unexpected async cancellation dispatch "+cancelCalls+" expected "+n);}
 public static void main(String[]a){NativeRestoreBackDispatchTest t=new NativeRestoreBackDispatchTest();
 t.pressBack();t.check(0);
 if(!t.workerArchiveRequests.register(1,0,"restore"))throw new AssertionError();t.pressBack();t.check(1);
 t.workerArchiveRequests.clear();t.workerRestoreAwaitingSave=true;t.pressBack();t.check(2);
 t.workerRestoreAwaitingSave=false;if(!t.workerArchiveRequests.register(2,0,"export"))throw new AssertionError();t.pressBack();t.check(2);
 t.restoringArchive=false;t.pressBack();t.check(2);
 System.out.println("PASS synchronous/read-phase restore Back stays busy; registered async restore and admitted-save Back use async feedback only");}
}'''.replace('BRANCH',branch)
with tempfile.TemporaryDirectory()as tmp:
 p=Path(tmp)/'NativeRestoreBackDispatchTest.java';p.write_text(harness);subprocess.run(['java','com.sun.tools.javac.Main','-d',tmp,str(ROOT/'android/app/src/main/java/org/townledger/vale/WorkerArchiveRequests.java'),str(p)],check=True);subprocess.run(['java','-cp',tmp,'org.townledger.vale.NativeRestoreBackDispatchTest'],check=True)
print(json.dumps({'MainActivity_sha256':hashlib.sha256(activity.read_bytes()).hexdigest(),'scope':'Actual first Back branch extracted and compiled with the real registry; cancellation body and Android activity are not emulated.'}))
