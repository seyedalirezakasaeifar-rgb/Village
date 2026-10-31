package org.townledger.vale;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
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
import org.json.JSONObject;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;

/** Offline-only host. The native bridge is exposed solely to bundled assets. */
public final class MainActivity extends Activity {
    private WebView web;
    private String pendingBackup;
    private static final int WRITE = 410, READ = 411;
    private static final int LIMIT = 8 * 1024 * 1024;
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN,WindowManager.LayoutParams.FLAG_FULLSCREEN);
        web = new WebView(this);
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
    @Override protected void onResume() {super.onResume();if(web!=null){web.onResume();immersive();}}
    @Override protected void onDestroy(){if(web!=null){web.removeJavascriptInterface("AndroidArchive");web.destroy();}super.onDestroy();}
    @Override public void onBackPressed() {
        web.evaluateJavascript("window.__townArchive ? window.__townArchive.back() : false", new ValueCallback<String>() { public void onReceiveValue(String result) {
            if(!"true".equals(result)){
                web.evaluateJavascript("window.__townArchive && window.__townArchive.suspend()", null);
                MainActivity.this.finish();
            }
        }});
    }
    public final class Archive {
        @JavascriptInterface public void writeBackup(final String text) {
            if(text==null || text.length()>LIMIT)return;
            runOnUiThread(new Runnable() { public void run() {
                pendingBackup=text;
                Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);
                i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("application/json");
                i.putExtra(Intent.EXTRA_TITLE,"TownLedger-town.json");startActivityForResult(i,WRITE);
            }});
        }
        @JavascriptInterface public void openBackup(){runOnUiThread(new Runnable() { public void run() {
            Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);
            i.setType("*/*");startActivityForResult(i,READ);
        }});}
    }
    @Override protected void onActivityResult(int request,int result,Intent data){
        super.onActivityResult(request,result,data);
        if(result!=RESULT_OK || data==null || data.getData()==null){pendingBackup=null;return;}
        Uri uri=data.getData();
        try {
            if(request==WRITE && pendingBackup!=null){
                try(OutputStream out=getContentResolver().openOutputStream(uri)){
                    if(out==null)throw new IllegalStateException("No document destination");
                    out.write(pendingBackup.getBytes(StandardCharsets.UTF_8));
                }
                pendingBackup=null;Toast.makeText(this,"Town backup saved",Toast.LENGTH_SHORT).show();
            }else if(request==READ){
                ByteArrayOutputStream bytes=new ByteArrayOutputStream();
                try(InputStream in=getContentResolver().openInputStream(uri)){
                    if(in==null)throw new IllegalStateException("No document source");
                    byte[] buffer=new byte[8192];int n;
                    while((n=in.read(buffer))!=-1){if(bytes.size()+n>LIMIT)throw new IllegalArgumentException("Archive exceeds 8 MB");bytes.write(buffer,0,n);}
                }
                String text=new String(bytes.toByteArray(),StandardCharsets.UTF_8);
                web.evaluateJavascript("window.__townArchive.restore("+JSONObject.quote(text)+")",null);
            }
        }catch(Exception ex){pendingBackup=null;Toast.makeText(this,"Could not read or write the town archive",Toast.LENGTH_LONG).show();}
    }
}
