package org.townledger.vale;

import android.app.Activity;
import android.content.Intent;
import android.content.pm.ApplicationInfo;
import android.net.Uri;
import android.os.Bundle;
import android.os.Build;
import android.view.View;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.ValueCallback;
import android.widget.Toast;
import android.util.AtomicFile;
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
    private boolean backPending;
    private Object modernBackToken;
    private final Runnable exitFallback=new Runnable(){public void run(){if(backPending&&!isFinishing())finish();}};
    private String pendingExportName;
    private final ExecutorService archiveWorker = Executors.newSingleThreadExecutor();
    private static final int WRITE = 410, READ = 411;
    private AtomicFile pendingExport(String name) {return new AtomicFile(new File(getFilesDir(), name));}
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        archiveRequest = state == null ? 0 : state.getInt("archiveRequest", 0);
        pendingExportName = state == null ? null : state.getString("pendingExportName");
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
        web.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView v, String url) {
                return !url.equals("file:///android_asset/index.html");
            }
        });
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
        web.evaluateJavascript("window.__townArchive && window.__townArchive.suspend()", null);
        web.onPause(); super.onPause();
    }
    @Override protected void onResume() {super.onResume();if(web!=null){web.onResume();web.evaluateJavascript("window.__townArchive && window.__townArchive.resume()",null);immersive();}}
    @Override protected void onSaveInstanceState(Bundle state){state.putInt("archiveRequest",pickerLaunched?archiveRequest:0);if(pickerLaunched&&pendingExportName!=null)state.putString("pendingExportName",pendingExportName);super.onSaveInstanceState(state);}
    @Override protected void onDestroy(){if(Build.VERSION.SDK_INT>=33&&modernBackToken!=null)BackApi33.detach(this,modernBackToken);archiveWorker.shutdown();if(web!=null){web.removeCallbacks(exitFallback);web.removeJavascriptInterface("AndroidArchive");web.destroy();}super.onDestroy();}
    @Override public void onBackPressed() {
        if(backPending||web==null)return;
        backPending=true;web.postDelayed(exitFallback,3000);
        web.evaluateJavascript("window.__townArchive ? window.__townArchive.back() : false",new ValueCallback<String>(){public void onReceiveValue(String result){
            if(isFinishing()||isDestroyed())return;
            if("true".equals(result)){backPending=false;web.removeCallbacks(exitFallback);return;}
            web.evaluateJavascript("window.__townArchive && window.__townArchive.suspend()",new ValueCallback<String>(){public void onReceiveValue(String saved){
                web.removeCallbacks(exitFallback);if(!isFinishing()&&!isDestroyed())MainActivity.this.finish();
            }});
        }});
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
        }catch(Exception ex){pickerLaunched=false;archiveRequest=0;message("No document chooser is available on this device");}
    }
    public final class Archive {
        @JavascriptInterface public void writeBackup(final String text) {
            runOnUiThread(new Runnable() {public void run() {
                if(isFinishing()||isDestroyed())return;
                if(archiveRequest!=0){message("Finish the open archive chooser first");return;}
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
                if(archiveRequest!=0){message("Finish the open archive chooser first");return;}
            archiveRequest=READ;launchPicker(READ);
        }});}
    }
    @Override protected void onActivityResult(final int request,int result,Intent data){
        super.onActivityResult(request,result,data);
        if((request!=WRITE&&request!=READ)||request!=archiveRequest)return;
        pickerLaunched=false;final AtomicFile prepared=request==WRITE&&pendingExportName!=null?pendingExport(pendingExportName):null;
        if(result!=RESULT_OK||data==null||data.getData()==null){archiveRequest=0;pendingExportName=null;if(prepared!=null)archiveWorker.execute(new Runnable(){public void run(){prepared.delete();}});return;}
        final Uri uri=data.getData();
        archiveWorker.execute(new Runnable(){public void run(){
            try {
                if(request==WRITE){
                    byte[] bytes;try(InputStream in=prepared.openRead()){bytes=ArchiveIO.read(in);}
                    try(OutputStream out=getContentResolver().openOutputStream(uri,"wt")){ArchiveIO.write(out,bytes);}
                    prepared.delete();message("Town backup saved");
                }else{
                    byte[] bytes;try(InputStream in=getContentResolver().openInputStream(uri)){bytes=ArchiveIO.read(in);}
                    final String quoted=JSONObject.quote(ArchiveIO.decode(bytes));
                    runOnUiThread(new Runnable(){public void run(){if(!isFinishing()&&!isDestroyed())web.evaluateJavascript("window.__townArchive && window.__townArchive.restore("+quoted+")",null);}});
                }
            }catch(Exception ex){message("Could not read or write the town archive. The current town is unchanged.");}
            finally{runOnUiThread(new Runnable(){public void run(){archiveRequest=0;pendingExportName=null;}});}
        }});
    }
}
