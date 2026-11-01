package org.townledger.vale;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.ApplicationInfo;
import android.net.Uri;
import android.os.Bundle;
import android.os.Build;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;
import android.util.AtomicFile;
import android.util.Log;
import org.json.JSONObject;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** Offline-only host. The native bridge is exposed solely to bundled assets. */
public final class MainActivity extends Activity {
    private WebView web;
    private int archiveRequest;
    private boolean pickerLaunched;
    private volatile boolean restoringArchive;
    private AlertDialog importDialog;
    private final BackNavigation backNavigation=new BackNavigation();
    private Runnable backTimeout;
    private boolean activityResumed;
    private boolean rendererFailed;
    private AlertDialog recoveryDialog;
    private AlertDialog savingDialog;
    private boolean rendererCrashed;
    private Object modernBackToken;
    private String pendingExportName;
    private boolean workerArchivePicker;
    private volatile boolean workerArchiveUiBusy,workerRestoreAwaitingSave;
    private long workerArchiveNextId;
    private final WorkerArchiveRequests workerArchiveRequests=new WorkerArchiveRequests();
    private final ExecutorService archiveWorker = Executors.newSingleThreadExecutor();
    private static final int WRITE = 410, READ = 411;
    private AtomicFile pendingExport(String name) {return new AtomicFile(new File(getFilesDir(), name));}
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        archiveRequest = state == null ? 0 : state.getInt("archiveRequest", 0);
        pendingExportName = state == null ? null : state.getString("pendingExportName");
        workerArchivePicker=state!=null&&state.getBoolean("workerArchivePicker",false);
        workerArchiveNextId=state==null?0:Math.max(0,state.getLong("workerArchiveNextId",0));
        if(archiveRequest==WRITE&&!ArchiveIO.pendingName(pendingExportName))archiveRequest=0;
        if(archiveRequest!=WRITE&&archiveRequest!=READ)archiveRequest=0;
        pickerLaunched=archiveRequest!=0;
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN,WindowManager.LayoutParams.FLAG_FULLSCREEN);
        web = new WebView(this);
        if((getApplicationInfo().flags & ApplicationInfo.FLAG_DEBUGGABLE)!=0)WebView.setWebContentsDebuggingEnabled(true);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowFileAccess(false);
        s.setAllowContentAccess(false);
        s.setAllowFileAccessFromFileURLs(false);
        s.setAllowUniversalAccessFromFileURLs(false);
        s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        s.setMediaPlaybackRequiresUserGesture(true);
        web.setWebChromeClient(new WebChromeClient());
        web.setWebViewClient(Build.VERSION.SDK_INT>=26?new RendererClient26(this):new LocalClient(this));
        web.addJavascriptInterface(new Archive(), "AndroidArchive");
        setContentView(web);
        immersive();
        if(Build.VERSION.SDK_INT>=33)modernBackToken=BackApi33.attach(this);
        web.loadUrl("file:///android_asset/index.html");
    }
    private void immersive() {
        web.setSystemUiVisibility(View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY | View.SYSTEM_UI_FLAG_FULLSCREEN |
            View.SYSTEM_UI_FLAG_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_LAYOUT_STABLE |
            View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION);
    }
    @Override public void onWindowFocusChanged(boolean focus) {
        super.onWindowFocusChanged(focus); if(focus && web != null) immersive();
    }
    @Override protected void onPause() {
        activityResumed=false;backNavigation.cancel();clearBackTimeout();dismissSavingDialog();
        if(web!=null){web.evaluateJavascript("window.__townArchive && window.__townArchive.suspend()", null);web.onPause();}super.onPause();
    }
    @Override protected void onResume() {super.onResume();activityResumed=true;if(web!=null){web.onResume();resumeGame();immersive();}else if(rendererFailed)showRendererRecovery();}
    @Override protected void onSaveInstanceState(Bundle state){state.putInt("archiveRequest",pickerLaunched?archiveRequest:0);if(pickerLaunched&&pendingExportName!=null)state.putString("pendingExportName",pendingExportName);state.putBoolean("workerArchivePicker",pickerLaunched&&workerArchivePicker);state.putLong("workerArchiveNextId",workerArchiveNextId);super.onSaveInstanceState(state);}
    @Override protected void onDestroy(){workerArchiveRequests.clear();finishImport();backNavigation.cancel();clearBackTimeout();dismissSavingDialog();if(recoveryDialog!=null)recoveryDialog.dismiss();if(Build.VERSION.SDK_INT>=33&&modernBackToken!=null)BackApi33.detach(this,modernBackToken);archiveWorker.shutdown();if(web!=null){web.removeJavascriptInterface("AndroidArchive");web.destroy();web=null;}super.onDestroy();}
    private void clearBackTimeout(){if(web!=null&&backTimeout!=null)web.removeCallbacks(backTimeout);backTimeout=null;}
    private void dismissSavingDialog(){if(savingDialog!=null){savingDialog.dismiss();savingDialog=null;}}
    private void showSavingDialog(int request){if(!backNavigation.isCurrent(request)||isFinishing()||isDestroyed())return;dismissSavingDialog();savingDialog=new AlertDialog.Builder(this).setTitle("Saving your town…").setMessage("Finishing the on-device save before leaving.").setCancelable(false).show();}
    private void resumeGame(){if(activityResumed&&web!=null&&!isFinishing()&&!isDestroyed())web.evaluateJavascript("window.__townArchive && window.__townArchive.resume()",null);}
    private void finishImport(){restoringArchive=false;workerRestoreAwaitingSave=false;workerArchivePicker=false;archiveRequest=0;if(importDialog!=null){importDialog.dismiss();importDialog=null;}if(web!=null)web.requestFocus();}
    @Override public void onBackPressed() {
        if(restoringArchive){if(workerRestoreAwaitingSave||workerArchiveRequests.current("restore")!=null)cancelWorkerRestore();return;}
        if(web==null){if(rendererFailed)showRendererRecovery();else finish();return;}
        final int request=backNavigation.begin();if(request==0)return;
        backTimeout=new Runnable(){public void run(){if(backNavigation.claim(request)){clearBackTimeout();dismissSavingDialog();message("The town is busy. Back did not close it; try again shortly.");resumeGame();}}};
        web.postDelayed(backTimeout,4000);
        web.evaluateJavascript(BackNavigation.script(request),null);
    }
    private void receiveBackResult(int request,boolean handled,boolean saved){
        if(isFinishing()||isDestroyed()||!backNavigation.claim(request))return;
        clearBackTimeout();dismissSavingDialog();if(handled)return;if(saved){finish();return;}
        recoveryDialog=new AlertDialog.Builder(this).setTitle("Town could not be saved")
            .setMessage("Keep playing and export a backup, or leave without saving. Unsaved changes may be lost.")
            .setPositiveButton("KEEP PLAYING",new DialogInterface.OnClickListener(){public void onClick(DialogInterface d,int which){resumeGame();}})
            .setNegativeButton("LEAVE WITHOUT SAVING",new DialogInterface.OnClickListener(){public void onClick(DialogInterface d,int which){finish();}})
            .setOnCancelListener(new DialogInterface.OnCancelListener(){public void onCancel(DialogInterface d){resumeGame();}}).show();
    }
    private static class LocalClient extends WebViewClient {
        final MainActivity owner;LocalClient(MainActivity owner){this.owner=owner;}
        @Override public boolean shouldOverrideUrlLoading(WebView v,String url){return !url.equals("file:///android_asset/index.html");}
    }
    // This class is instantiated only where the renderer-loss API exists.
    private static final class RendererClient26 extends LocalClient {
        RendererClient26(MainActivity owner){super(owner);}
        @Override public boolean onRenderProcessGone(WebView view,android.webkit.RenderProcessGoneDetail detail){owner.rendererLost(view,detail.didCrash());return true;}
    }
    private void rendererLost(WebView failed,boolean crashed){
        if(failed!=web)return;
        finishImport();
        backNavigation.cancel();clearBackTimeout();dismissSavingDialog();if(recoveryDialog!=null){recoveryDialog.dismiss();recoveryDialog=null;}web=null;rendererFailed=true;rendererCrashed=crashed;
        if(failed.getParent() instanceof ViewGroup)((ViewGroup)failed.getParent()).removeView(failed);
        failed.destroy();
        if(activityResumed&&!isFinishing()&&!isDestroyed())showRendererRecovery();
    }
    private void showRendererRecovery(){
        if(isFinishing()||isDestroyed()||(recoveryDialog!=null&&recoveryDialog.isShowing()))return;
        recoveryDialog=new AlertDialog.Builder(this).setTitle(rendererCrashed?"Game view stopped":"Android reclaimed the game view")
            .setMessage("Reopen the game. Choose Continue if a completed save is available. Recent unsaved changes may be unavailable.")
            .setPositiveButton("REOPEN GAME",new DialogInterface.OnClickListener(){public void onClick(DialogInterface d,int which){recreate();}})
            .setNegativeButton("CLOSE",new DialogInterface.OnClickListener(){public void onClick(DialogInterface d,int which){finish();}}).setCancelable(false).show();
    }
    // Keep newer platform types out of the API-24 Activity's field signatures.
    private static final class BackApi33 {
        static Object attach(final MainActivity activity) {
            android.window.OnBackInvokedCallback callback=new android.window.OnBackInvokedCallback(){public void onBackInvoked(){activity.onBackPressed();}};
            activity.getOnBackInvokedDispatcher().registerOnBackInvokedCallback(android.window.OnBackInvokedDispatcher.PRIORITY_DEFAULT,callback);
            return callback;
        }
        static void detach(MainActivity activity,Object token){activity.getOnBackInvokedDispatcher().unregisterOnBackInvokedCallback((android.window.OnBackInvokedCallback)token);}
    }
    private void message(final String text) {runOnUiThread(new Runnable() {public void run() {
        if(!isFinishing() && !isDestroyed())Toast.makeText(MainActivity.this,text,Toast.LENGTH_LONG).show();
    }});}
    private void launchPicker(int request) {
        try {
            Intent i=new Intent(request==WRITE?Intent.ACTION_CREATE_DOCUMENT:Intent.ACTION_OPEN_DOCUMENT);
            i.addCategory(Intent.CATEGORY_OPENABLE);i.setType(request==WRITE?"application/json":"*/*");
            if(request==WRITE)i.putExtra(Intent.EXTRA_TITLE,"TownLedger-town.json");
            pickerLaunched=true;startActivityForResult(i,request);
        }catch(Exception ex){
            pickerLaunched=false;archiveRequest=0;workerArchivePicker=false;
            final String abandoned=pendingExportName;pendingExportName=null;
            if(ArchiveIO.pendingName(abandoned))archiveWorker.execute(new Runnable(){public void run(){pendingExport(abandoned).delete();}});
            message("No document chooser is available on this device");
        }
    }
    private void submitWorkerArchive(final String operation,final String archive){
        if(web==null||isFinishing()||isDestroyed()){message("The async archive session is unavailable; the current town is unchanged.");if("restore".equals(operation))finishImport();else workerArchiveUiBusy=false;return;}
        final long id=++workerArchiveNextId;final String quotedArchive=archive==null?"null":JSONObject.quote(archive);
        String archiveField=archive==null?"":",archive:"+quotedArchive;
        final String expression="(function(){var a=window.__workerArchiveAsync;if(!a||typeof a.submit!=='function'||typeof a.status!=='function')return JSON.stringify({accepted:false,error:'ASYNC_ARCHIVE_UNAVAILABLE'});var s=a.status(),epoch=s&&s.epoch;if(!Number.isSafeInteger(epoch)||epoch<0)return JSON.stringify({accepted:false,error:'INVALID_EPOCH'});if(!AndroidArchive.workerArchiveStarted("+id+",epoch,"+JSONObject.quote(operation)+"))return JSON.stringify({accepted:false,error:'NATIVE_REQUEST_REFUSED'});var r=a.submit({id:"+id+",epoch:epoch,op:"+JSONObject.quote(operation)+archiveField+"});if(!r||r.accepted!==true){AndroidArchive.workerArchiveRejected("+id+",epoch);return JSON.stringify(r||{accepted:false,error:'NO_REPLY'});}return JSON.stringify({accepted:true,id:"+id+",epoch:epoch});})()";
        web.evaluateJavascript(expression,new android.webkit.ValueCallback<String>(){public void onReceiveValue(String value){if(value==null||"null".equals(value)||value.contains("accepted\\\":false")){workerArchiveRequests.refuseId(id);if("restore".equals(operation))finishImport();else workerArchiveUiBusy=false;message("The worker did not accept the archive request. The current town is unchanged.");}}});
    }
    private void handleWorkerArchiveResult(final WorkerArchiveRequests.Request request,final WorkerArchiveReply reply){
        if(isFinishing()||isDestroyed()||web==null)return;
        if("export".equals(request.operation)){
            workerArchiveUiBusy=false;
            if(!reply.ok||reply.archive==null){message("Could not prepare the async archive: "+(reply.error==null?"no archive was returned":reply.error));return;}
            final byte[] bytes;try{bytes=ArchiveIO.encode(reply.archive);}catch(Exception ex){message("The worker archive is invalid or exceeds the 8 MB UTF-8 limit.");return;}
            if(archiveRequest!=0||restoringArchive){message("Finish the open archive operation first; export was not written.");return;}
            archiveRequest=WRITE;pendingExportName="pending-town-export-"+UUID.randomUUID().toString()+".json";final AtomicFile prepared=pendingExport(pendingExportName);
            archiveWorker.execute(new Runnable(){public void run(){FileOutputStream out=null;try{out=prepared.startWrite();ArchiveIO.write(out,bytes);prepared.finishWrite(out);out=null;runOnUiThread(new Runnable(){public void run(){if(!isFinishing()&&!isDestroyed())launchPicker(WRITE);}});}catch(Exception ex){if(out!=null)prepared.failWrite(out);runOnUiThread(new Runnable(){public void run(){archiveRequest=0;pendingExportName=null;message("Could not prepare the worker archive; the current town is unchanged.");}});}}});return;
        }
        if("restore".equals(request.operation)){
            if(!reply.ok||!reply.restored){finishImport();if(reply.admitted)message("Restore did not complete after application began; reopen the game and inspect the current saved town.");else message("Backup could not be restored. The current town is unchanged.");return;}
            workerRestoreAwaitingSave=true;if(importDialog!=null)importDialog.setMessage("The backup has passed validation and is applied in memory. Saving the restored town before closing this dialog.");submitWorkerArchive("save",null);return;
        }
        if("save".equals(request.operation)&&workerRestoreAwaitingSave){boolean saved=reply.ok&&reply.persisted;finishImport();if(saved)message("Backup restored and saved on this device.");else message("Backup was applied to this session, but durable saving failed. The backup file remains unchanged.");}
    }
    private void cancelWorkerRestore(){
        if(workerRestoreAwaitingSave){message("The backup is already applied; keep the game open until its save completes.");return;}WorkerArchiveRequests.Request request=workerArchiveRequests.current("restore");if(request==null||web==null){message("The backup is still being read. Wait for validation to begin before cancelling.");return;}final long id=request.id;
        web.evaluateJavascript("(function(){var a=window.__workerArchiveAsync;return JSON.stringify(a&&a.cancel?a.cancel("+id+"):{cancelled:false,reason:'ASYNC_ARCHIVE_UNAVAILABLE'});})()",new android.webkit.ValueCallback<String>(){public void onReceiveValue(String value){if(value!=null&&value.contains("ALREADY_ADMITTED"))message("The restore is already being applied; keep the game open while it finishes.");else if(value!=null&&value.contains("cancelled\\\":true"))message("Cancel requested. The current town remains unchanged until validation completes.");else message("The restore is still running; the game will remain open until it reports its result.");}});
    }
    public final class Archive {
        @JavascriptInterface public void requestWorkerExport(){runOnUiThread(new Runnable(){public void run(){if(isFinishing()||isDestroyed()||archiveRequest!=0||restoringArchive||workerArchiveUiBusy){message("Finish the open archive operation first");return;}workerArchiveUiBusy=true;submitWorkerArchive("export",null);}});}
        @JavascriptInterface public void requestWorkerImport(){runOnUiThread(new Runnable(){public void run(){if(isFinishing()||isDestroyed()||archiveRequest!=0||restoringArchive||workerArchiveUiBusy){message("Finish the open archive operation first");return;}workerArchivePicker=true;archiveRequest=READ;launchPicker(READ);}});}
        @JavascriptInterface public boolean workerArchiveStarted(long id,long epoch,String operation){if(isFinishing()||isDestroyed()||web==null)return false;if("export".equals(operation)&&!workerArchiveUiBusy)return false;if("restore".equals(operation)&&!restoringArchive)return false;if("save".equals(operation)&&!workerRestoreAwaitingSave)return false;return workerArchiveRequests.register(id,epoch,operation);}
        @JavascriptInterface public void workerArchiveRejected(long id,long epoch){workerArchiveRequests.refuse(id,epoch);}
        @JavascriptInterface public void workerArchiveResult(final String json){final WorkerArchiveReply reply;try{reply=WorkerArchiveReply.parse(json);}catch(Exception ex){Log.w("TownLedgerArchive","Rejected malformed async archive completion: "+ex.getClass().getSimpleName());final WorkerArchiveRequests.Request failed=workerArchiveRequests.failFirst();if(failed!=null)runOnUiThread(new Runnable(){public void run(){workerArchiveUiBusy=false;if("restore".equals(failed.operation))finishImport();message("The async archive result could not be verified. Reopen the game and check the saved town before continuing.");}});return;}final WorkerArchiveRequests.Request request=workerArchiveRequests.complete(reply.id,reply.epoch);if(request==null){Log.w("TownLedgerArchive","Ignored unmatched async archive completion id="+reply.id+" epoch="+reply.epoch);return;}runOnUiThread(new Runnable(){public void run(){handleWorkerArchiveResult(request,reply);}});}
        @JavascriptInterface public void restoreResult(final boolean ok){runOnUiThread(new Runnable(){public void run(){if(!restoringArchive)return;finishImport();if(!ok)message("Backup could not be restored. The current town is unchanged.");}});}
        @JavascriptInterface public void backSaving(final int request){runOnUiThread(new Runnable(){public void run(){showSavingDialog(request);}});}
        @JavascriptInterface public void backResult(final int request,final boolean handled,final boolean saved){runOnUiThread(new Runnable(){public void run(){receiveBackResult(request,handled,saved);}});}
        @JavascriptInterface public void writeBackup(final String text) {
            runOnUiThread(new Runnable() {public void run() {
                if(isFinishing()||isDestroyed())return;
                if(archiveRequest!=0||restoringArchive){message("Finish the open archive operation first");return;}
                archiveRequest=WRITE;pendingExportName="pending-town-export-"+UUID.randomUUID().toString()+".json";final AtomicFile prepared=pendingExport(pendingExportName);
                archiveWorker.execute(new Runnable() {public void run() {
                    FileOutputStream out=null;
                    try {
                        byte[] bytes=ArchiveIO.encode(text);out=prepared.startWrite();ArchiveIO.write(out,bytes);prepared.finishWrite(out);out=null;
                        runOnUiThread(new Runnable() {public void run() {if(!isFinishing()&&!isDestroyed())launchPicker(WRITE);}});
                    }catch(Exception ex){if(out!=null)prepared.failWrite(out);runOnUiThread(new Runnable() {public void run(){archiveRequest=0;}});message("Could not prepare backup; archives must be at most 8 MB of UTF-8");}
                }});
            }});
        }
        @JavascriptInterface public void openBackup(){runOnUiThread(new Runnable() {public void run() {
            if(isFinishing()||isDestroyed())return;
                if(archiveRequest!=0||restoringArchive){message("Finish the open archive operation first");return;}
            archiveRequest=READ;launchPicker(READ);
        }});}
    }
    @Override protected void onActivityResult(final int request,int result,Intent data){
        super.onActivityResult(request,result,data);
        if((request!=WRITE&&request!=READ)||request!=archiveRequest)return;
        pickerLaunched=false;final AtomicFile prepared=request==WRITE&&pendingExportName!=null?pendingExport(pendingExportName):null;
        if(result!=RESULT_OK||data==null||data.getData()==null){archiveRequest=0;pendingExportName=null;workerArchivePicker=false;if(prepared!=null)archiveWorker.execute(new Runnable(){public void run(){prepared.delete();}});return;}
        final Uri uri=data.getData();
        if(request==READ&&workerArchivePicker){workerArchivePicker=false;restoringArchive=true;importDialog=new AlertDialog.Builder(this).setTitle("Restoring town…").setMessage("Checking the backup before replacing your current town. Press Back to cancel before it is applied.").setCancelable(false).show();archiveWorker.execute(new Runnable(){public void run(){try{byte[] bytes;try(InputStream in=getContentResolver().openInputStream(uri)){bytes=ArchiveIO.read(in);}final String archive=ArchiveIO.decode(bytes);runOnUiThread(new Runnable(){public void run(){if(isFinishing()||isDestroyed()||web==null){finishImport();message("Reopen the game and select the backup again. The backup file is unchanged.");return;}submitWorkerArchive("restore",archive);}});}catch(Exception ex){runOnUiThread(new Runnable(){public void run(){finishImport();message("Could not read the backup. The current town is unchanged.");}});}}});return;}
        if(request==READ){restoringArchive=true;importDialog=new AlertDialog.Builder(this).setTitle("Restoring town…").setMessage("Checking the backup before replacing your current town. Large archives can take a while.").setCancelable(false).show();}
        archiveWorker.execute(new Runnable(){public void run(){
            try {
                if(request==WRITE){
                    byte[] bytes;try(InputStream in=prepared.openRead()){bytes=ArchiveIO.read(in);}
                    try(OutputStream out=getContentResolver().openOutputStream(uri,"wt")){ArchiveIO.write(out,bytes);}
                    prepared.delete();message("Town backup saved");
                }else{
                    byte[] bytes;try(InputStream in=getContentResolver().openInputStream(uri)){bytes=ArchiveIO.read(in);}
                    final String quoted=JSONObject.quote(ArchiveIO.decode(bytes));
                    runOnUiThread(new Runnable(){public void run(){if(isFinishing()||isDestroyed())return;if(web==null){finishImport();message("Reopen the game before restoring this backup. The backup file is unchanged.");return;}getWindow().getDecorView().postOnAnimation(new Runnable(){public void run(){getWindow().getDecorView().postOnAnimation(new Runnable(){public void run(){if(web==null||isDestroyed()){finishImport();return;}web.evaluateJavascript("(function(){var box=document.createElement('div');box.setAttribute('role','alertdialog');box.setAttribute('aria-label','Restoring town');box.style.cssText='position:fixed;inset:0;z-index:2147483647;background:rgba(22,43,35,.94);color:#fff4d5;display:flex;align-items:center;justify-content:center;padding:32px;text-align:center;font:18px sans-serif';box.textContent='Restoring town… Checking the backup before replacing your current town. Large archives can take a while.';document.body.appendChild(box);document.body.setAttribute('aria-busy','true');requestAnimationFrame(function(){requestAnimationFrame(function(){setTimeout(function(){var ok=false;try{ok=!!(window.__townArchive&&window.__townArchive.restore("+quoted+"));}catch(e){}finally{box.remove();document.body.removeAttribute('aria-busy');AndroidArchive.restoreResult(ok);}},0);});});})()",null);}});}});}});
                }
            }catch(Exception ex){runOnUiThread(new Runnable(){public void run(){if(request==READ)finishImport();}});message("Could not read or write the town archive. The current town is unchanged.");}
            finally{runOnUiThread(new Runnable(){public void run(){if(request==WRITE)archiveRequest=0;pendingExportName=null;}});}
        }});
    }
}
