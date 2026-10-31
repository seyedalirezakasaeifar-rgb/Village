package org.townledger.vale;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.Instrumentation;
import android.content.Intent;
import android.os.Bundle;
import android.os.SystemClock;
import android.webkit.ValueCallback;
import android.webkit.WebView;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

/** Private native host checks; lightweight HTML replaces only the game page. */
public final class RecoveryHarness extends Instrumentation {
    volatile MainActivity current;
    final ArrayList<String> checks=new ArrayList<String>();
    interface Check {boolean ok() throws Exception;}
    void until(Check check,String label) throws Exception {long end=SystemClock.uptimeMillis()+25000;while(SystemClock.uptimeMillis()<end){if(check.ok())return;SystemClock.sleep(100);}throw new AssertionError("Timeout: "+label);}
    Object field(Object target,String name)throws Exception{Field f=target.getClass().getDeclaredField(name);f.setAccessible(true);return f.get(target);}
    WebView web()throws Exception{return (WebView)field(current,"web");}
    String js(final String expression)throws Exception{final CountDownLatch done=new CountDownLatch(1);final String[] value={null};runOnMainSync(new Runnable(){public void run(){try{web().evaluateJavascript(expression,new ValueCallback<String>(){public void onReceiveValue(String r){value[0]=r;done.countDown();}});}catch(Exception e){value[0]="ERROR:"+e;done.countDown();}}});if(!done.await(25,TimeUnit.SECONDS))throw new AssertionError("JS callback: "+expression);return value[0];}
    boolean dialog(String name)throws Exception{final boolean[] showing={false};runOnMainSync(new Runnable(){public void run(){try{AlertDialog d=(AlertDialog)field(current,name);showing[0]=d!=null&&d.isShowing();}catch(Exception e){throw new RuntimeException(e);}}});return showing[0];}
    void click(final String name,final int button){runOnMainSync(new Runnable(){public void run(){try{((AlertDialog)field(current,name)).getButton(button).performClick();}catch(Exception e){throw new RuntimeException(e);}}});}
    void back(){runOnMainSync(new Runnable(){public void run(){current.onBackPressed();}});}
    void require(boolean value,String label){if(!value)throw new AssertionError(label);checks.add(label);sendStatus(0,status(label));}
    Bundle status(String text){Bundle b=new Bundle();b.putString("progress",text);return b;}
    @Override public void onCreate(Bundle b){super.onCreate(b);start();}
    @Override public void callActivityOnResume(Activity activity){super.callActivityOnResume(activity);if(activity instanceof MainActivity)current=(MainActivity)activity;}
    @Override public void onStart(){Bundle result=new Bundle();try{
        current=(MainActivity)startActivitySync(new Intent(getTargetContext(),MainActivity.class).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));
        until(new Check(){public boolean ok()throws Exception{return "\"handled\"".equals(js("window.qaMode"));}},"page ready");
        back();SystemClock.sleep(500);require(!current.isFinishing()&&!dialog("savingDialog")&&!dialog("recoveryDialog"),"Handled layer remains in app");
        js("qaMode='unsaved'");back();until(new Check(){public boolean ok()throws Exception{return dialog("recoveryDialog");}},"unsaved dialog");require(!current.isFinishing(),"Failed save does not finish Activity");click("recoveryDialog",AlertDialog.BUTTON_POSITIVE);until(new Check(){public boolean ok()throws Exception{return Integer.parseInt(js("qaResumes"))>0;}},"resume after Keep playing");require(true,"Keep playing resumes renderer");
        js("qaMode='hung'");back();until(new Check(){public boolean ok()throws Exception{return dialog("savingDialog");}},"busy dialog");until(new Check(){public boolean ok()throws Exception{return !dialog("savingDialog");}},"timeout dismisses busy dialog");require(!current.isFinishing(),"Hung save timeout preserves Activity");
        js("localStorage.setItem('qa-native-recovery','retained')");final MainActivity before=current;
        final boolean[] terminated={false};runOnMainSync(new Runnable(){public void run(){try{terminated[0]=web().getWebViewRenderProcess()!=null&&web().getWebViewRenderProcess().terminate();}catch(Exception e){throw new RuntimeException(e);}}});require(terminated[0],"Terminated only the app's WebView renderer through API29");
        until(new Check(){public boolean ok()throws Exception{return dialog("recoveryDialog")&&web()==null;}},"renderer recovery dialog");require(!current.isFinishing(),"Renderer termination retains host and offers recovery");result.putBoolean("rendererDidCrash",(Boolean)field(current,"rendererCrashed"));click("recoveryDialog",AlertDialog.BUTTON_POSITIVE);
        until(new Check(){public boolean ok()throws Exception{return current!=before&&"\"handled\"".equals(js("window.qaMode"));}},"recreated view");require("\"retained\"".equals(js("localStorage.getItem('qa-native-recovery')")),"Recreated view retains same-origin persistent data");
        js("qaMode='saved'");final MainActivity leaving=current;back();until(new Check(){public boolean ok(){return leaving.isFinishing()||leaving.isDestroyed();}},"saved exit");require(true,"Acknowledged successful save allows exit");
        result.putString("outcome","PASS");result.putString("checks",checks.toString());finish(Activity.RESULT_OK,result);
    }catch(Throwable e){result.putString("outcome","FAIL");result.putString("checks",checks.toString());result.putString("error",e.toString());finish(Activity.RESULT_CANCELED,result);}}
}
