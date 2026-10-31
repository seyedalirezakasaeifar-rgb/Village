package org.townledger.vale;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.Instrumentation;
import android.content.Intent;
import android.content.ComponentName;
import android.content.IntentFilter;
import android.net.Uri;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import org.json.JSONObject;
import android.os.UserManager;
import android.os.Bundle;
import android.os.SystemClock;
import android.webkit.ValueCallback;
import android.webkit.WebView;
import android.view.KeyEvent;
import android.view.accessibility.AccessibilityNodeInfo;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

/** Private native host checks; lightweight HTML replaces only the game page. */
public final class RecoveryHarness extends Instrumentation {
    volatile MainActivity current;
    boolean pickerOnly;
    final ArrayList<String> checks=new ArrayList<String>();
    interface Check {boolean ok() throws Exception;}
    void until(Check check,String label) throws Exception {long end=SystemClock.uptimeMillis()+25000;while(SystemClock.uptimeMillis()<end){if(check.ok())return;SystemClock.sleep(100);}throw new AssertionError("Timeout: "+label);}
    Object field(Object target,String name)throws Exception{Field f=target.getClass().getDeclaredField(name);f.setAccessible(true);return f.get(target);}
    void setField(Object target,String name,Object value)throws Exception{Field f=target.getClass().getDeclaredField(name);f.setAccessible(true);f.set(target,value);}
    void archiveResult(final int request,final int result,final Uri uri){runOnMainSync(new Runnable(){public void run(){try{setField(current,"archiveRequest",request);current.onActivityResult(request,result,uri==null?null:new Intent().setData(uri));}catch(Exception e){throw new RuntimeException(e);}}});}
    void archives()throws Exception{
        final Uri document=Uri.parse("content://org.townledger.vale.tests.archive/archive");
        final String town="{\"town\":\"Oak · آبادی 🌲\"}";
        try(OutputStream out=getTargetContext().getContentResolver().openOutputStream(document,"wt")){out.write(("\ufeff"+town).getBytes(StandardCharsets.UTF_8));}
        js("qaRestore=null");archiveResult(411,Activity.RESULT_OK,document);
        until(new Check(){public boolean ok()throws Exception{return JSONObject.quote(town).equals(js("qaRestore"))&&(Integer)field(current,"archiveRequest")==0;}},"provider Unicode import");
        require(true,"Actual external ContentProvider import preserves Unicode and accepts BOM");
        try(OutputStream out=getTargetContext().getContentResolver().openOutputStream(document,"wt")){out.write(new byte[]{(byte)0xc3,(byte)0x28});}
        archiveResult(411,Activity.RESULT_OK,document);until(new Check(){public boolean ok()throws Exception{return (Integer)field(current,"archiveRequest")==0;}},"malformed import settles");
        require(JSONObject.quote(town).equals(js("qaRestore")),"Malformed provider UTF-8 does not reach game restore");
        try(OutputStream out=getTargetContext().getContentResolver().openOutputStream(document,"wt")){byte[] block=new byte[8192];for(int i=0;i<1024;i++)out.write(block);out.write(1);}
        archiveResult(411,Activity.RESULT_OK,document);until(new Check(){public boolean ok()throws Exception{return (Integer)field(current,"archiveRequest")==0;}},"oversized import settles");
        require(JSONObject.quote(town).equals(js("qaRestore")),"Provider import over 8 MiB leaves live restore unchanged");
        archiveResult(411,Activity.RESULT_CANCELED,null);require((Integer)field(current,"archiveRequest")==0,"Cancelled import releases archive busy state");
        // Intercept only the chooser to test cancellation of a real bridge-prepared export.
        IntentFilter filter=new IntentFilter(Intent.ACTION_CREATE_DOCUMENT);filter.addCategory(Intent.CATEGORY_OPENABLE);filter.addDataType("application/json");
        ActivityMonitor chooser=addMonitor(filter,new ActivityResult(Activity.RESULT_CANCELED,null),true);
        js("AndroidArchive.writeBackup("+JSONObject.quote(town)+")");
        until(new Check(){public boolean ok()throws Exception{return chooser.getHits()>0&&(Integer)field(current,"archiveRequest")==0;}},"cancelled export settles");removeMonitor(chooser);
        require(chooser.getHits()==1&&field(current,"pendingExportName")==null,"Bridge export cancellation clears pending request");
        until(new Check(){public boolean ok(){String[] names=current.getFilesDir().list();if(names!=null)for(String n:names)if(ArchiveIO.pendingName(n))return false;return true;}},"cancelled prepared file removed");
        require(true,"Cancelled export removes private prepared archive");
        // Deliver a provider result to the real worker, using a staged prepared file.
        final String pending="pending-town-export-123e4567-e89b-12d3-a456-426614174000.json";
        try(OutputStream out=new java.io.FileOutputStream(new java.io.File(current.getFilesDir(),pending))){out.write(town.getBytes(StandardCharsets.UTF_8));}
        setField(current,"pendingExportName",pending);archiveResult(410,Activity.RESULT_OK,document);
        until(new Check(){public boolean ok()throws Exception{return (Integer)field(current,"archiveRequest")==0;}},"provider export settles");
        try(InputStream in=getTargetContext().getContentResolver().openInputStream(document)){require(town.equals(ArchiveIO.decode(ArchiveIO.read(in))),"Actual external provider export truncates previous larger document and preserves Unicode");}
    }
    boolean systemPicker(){AccessibilityNodeInfo root=getUiAutomation().getRootInActiveWindow();if(root==null)return false;try{return root.getPackageName()!=null&&root.getPackageName().toString().contains("documentsui");}finally{root.recycle();}}
    void cancelSystemPicker(){long now=SystemClock.uptimeMillis();if(!getUiAutomation().injectInputEvent(new KeyEvent(now,now,KeyEvent.ACTION_DOWN,KeyEvent.KEYCODE_BACK,0),true)||!getUiAutomation().injectInputEvent(new KeyEvent(now,now+80,KeyEvent.ACTION_UP,KeyEvent.KEYCODE_BACK,0),true))throw new AssertionError("Could not inject system picker Back");}
    void picker()throws Exception{
        js("AndroidArchive.openBackup()");until(new Check(){public boolean ok(){return systemPicker();}},"actual system import picker");require(!(Boolean)field(current,"activityResumed"),"Actual system import picker backgrounds native host");cancelSystemPicker();until(new Check(){public boolean ok()throws Exception{return (Integer)field(current,"archiveRequest")==0&&(Boolean)field(current,"activityResumed");}},"system import cancellation");require(true,"Actual system import cancellation resumes host and releases archive request");
        js("AndroidArchive.writeBackup('{\"town\":\"Oak 🌲\"}')");until(new Check(){public boolean ok(){return systemPicker();}},"actual system export picker");final MainActivity before=current;final String prepared=(String)field(before,"pendingExportName");runOnMainSync(new Runnable(){public void run(){before.recreate();}});SystemClock.sleep(1500);cancelSystemPicker();until(new Check(){public boolean ok()throws Exception{return current!=before&&(Boolean)field(current,"activityResumed")&&(Integer)field(current,"archiveRequest")==0;}},"recreated host receives system picker cancellation");until(new Check(){public boolean ok(){return !new java.io.File(current.getFilesDir(),prepared).exists();}},"recreated export prepared file removed");require(true,"Actual system export cancellation survives Activity recreation and removes private prepared archive");
    }
    WebView web()throws Exception{return (WebView)field(current,"web");}
    String js(final String expression)throws Exception{final CountDownLatch done=new CountDownLatch(1);final String[] value={null};runOnMainSync(new Runnable(){public void run(){try{web().evaluateJavascript(expression,new ValueCallback<String>(){public void onReceiveValue(String r){value[0]=r;done.countDown();}});}catch(Exception e){value[0]="ERROR:"+e;done.countDown();}}});if(!done.await(25,TimeUnit.SECONDS))throw new AssertionError("JS callback: "+expression);return value[0];}
    boolean dialog(String name)throws Exception{final boolean[] showing={false};runOnMainSync(new Runnable(){public void run(){try{AlertDialog d=(AlertDialog)field(current,name);showing[0]=d!=null&&d.isShowing();}catch(Exception e){throw new RuntimeException(e);}}});return showing[0];}
    void click(final String name,final int button){runOnMainSync(new Runnable(){public void run(){try{((AlertDialog)field(current,name)).getButton(button).performClick();}catch(Exception e){throw new RuntimeException(e);}}});}
    void back(){runOnMainSync(new Runnable(){public void run(){current.onBackPressed();}});}
    void require(boolean value,String label){if(!value)throw new AssertionError(label);checks.add(label);sendStatus(0,status(label));}
    Bundle status(String text){Bundle b=new Bundle();b.putString("progress",text);return b;}
    @Override public void onCreate(Bundle b){super.onCreate(b);pickerOnly=b!=null&&"true".equals(b.getString("picker"));start();}
    @Override public void callActivityOnResume(Activity activity){super.callActivityOnResume(activity);if(activity instanceof MainActivity)current=(MainActivity)activity;}
    @Override public void onStart(){Bundle result=new Bundle();try{
        result.putBoolean("userUnlocked",((UserManager)getTargetContext().getSystemService(android.content.Context.USER_SERVICE)).isUserUnlocked());
        ActivityMonitor started=addMonitor(MainActivity.class.getName(),null,false);getTargetContext().startActivity(new Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER).setComponent(new ComponentName(getTargetContext(),MainActivity.class)).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK|Intent.FLAG_ACTIVITY_CLEAR_TASK));
        Activity launched=waitForMonitorWithTimeout(started,25000);removeMonitor(started);if(!(launched instanceof MainActivity))throw new AssertionError("MainActivity did not launch through its explicit launcher intent");current=(MainActivity)launched;
        until(new Check(){public boolean ok()throws Exception{return "\"handled\"".equals(js("window.qaMode"));}},"page ready");
        if(pickerOnly){picker();result.putString("outcome","PASS");result.putString("checks",checks.toString());finish(Activity.RESULT_OK,result);return;}
        archives();
        final int initialResumes=Integer.parseInt(js("qaResumes"));back();until(new Check(){public boolean ok()throws Exception{return !(Boolean)field(field(current,"backNavigation"),"pending");}},"handled acknowledgement");require(!current.isFinishing()&&!dialog("savingDialog")&&!dialog("recoveryDialog")&&Integer.parseInt(js("qaResumes"))==initialResumes,"Handled layer acknowledged without timeout or exit");
        js("qaMode='unsaved'");back();until(new Check(){public boolean ok()throws Exception{return dialog("recoveryDialog");}},"unsaved dialog");require(!current.isFinishing(),"Failed save does not finish Activity");click("recoveryDialog",AlertDialog.BUTTON_POSITIVE);until(new Check(){public boolean ok()throws Exception{return Integer.parseInt(js("qaResumes"))>0;}},"resume after Keep playing");require(true,"Keep playing resumes renderer");
        js("qaMode='hung'");back();final int expiredRequest=(Integer)field(field(current,"backNavigation"),"generation");until(new Check(){public boolean ok()throws Exception{return dialog("savingDialog");}},"busy dialog");until(new Check(){public boolean ok()throws Exception{return !dialog("savingDialog");}},"timeout dismisses busy dialog");require(!current.isFinishing(),"Hung save timeout preserves Activity");js("AndroidArchive.backResult("+expiredRequest+",false,true)");require(!current.isFinishing(),"Late saved acknowledgement cannot exit after timeout");
        js("localStorage.setItem('qa-native-recovery','retained')");final MainActivity before=current;
        final boolean[] terminated={false};runOnMainSync(new Runnable(){public void run(){try{terminated[0]=web().getWebViewRenderProcess()!=null&&web().getWebViewRenderProcess().terminate();}catch(Exception e){throw new RuntimeException(e);}}});require(terminated[0],"Terminated only the app's WebView renderer through API29");
        until(new Check(){public boolean ok()throws Exception{return dialog("recoveryDialog")&&web()==null;}},"renderer recovery dialog");require(!current.isFinishing(),"Renderer termination retains host and offers recovery");result.putBoolean("rendererDidCrash",(Boolean)field(current,"rendererCrashed"));click("recoveryDialog",AlertDialog.BUTTON_POSITIVE);
        until(new Check(){public boolean ok()throws Exception{return current!=before&&"\"handled\"".equals(js("window.qaMode"));}},"recreated view");require("\"retained\"".equals(js("localStorage.getItem('qa-native-recovery')")),"Recreated view retains same-origin persistent data");
        js("qaMode='saved'");final MainActivity leaving=current;back();until(new Check(){public boolean ok(){return leaving.isFinishing()||leaving.isDestroyed();}},"saved exit");require(true,"Acknowledged successful save allows exit");
        result.putString("outcome","PASS");result.putString("checks",checks.toString());finish(Activity.RESULT_OK,result);
    }catch(Throwable e){result.putString("outcome","FAIL");result.putString("checks",checks.toString());result.putString("error",android.util.Log.getStackTraceString(e));finish(Activity.RESULT_CANCELED,result);}}
}
