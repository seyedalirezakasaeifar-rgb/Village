package org.townledger.vale;

import android.app.Activity;
import android.app.Instrumentation;
import android.content.ComponentName;
import android.content.Intent;
import android.os.Bundle;
import android.os.SystemClock;
import android.graphics.Rect;
import android.view.MotionEvent;
import android.view.InputDevice;
import android.view.KeyEvent;
import android.view.accessibility.AccessibilityNodeInfo;
import android.webkit.ValueCallback;
import android.webkit.WebView;
import org.json.JSONArray;
import org.json.JSONObject;
import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

/** Actual DocumentsUI save/open selection using only a synthetic Unicode document. */
public final class DocumentsHarness extends Instrumentation {
    volatile MainActivity current;
    String selectionMethod="not attempted";
    final ArrayList<String> checks=new ArrayList<String>();
    interface Check {boolean ok()throws Exception;}
    void until(Check c,String label)throws Exception{long end=SystemClock.uptimeMillis()+60000;while(SystemClock.uptimeMillis()<end){if(c.ok())return;SystemClock.sleep(250);}throw new AssertionError("Timeout: "+label);}
    Object field(String name)throws Exception{Field f=MainActivity.class.getDeclaredField(name);f.setAccessible(true);return f.get(current);}
    String js(final String expression)throws Exception{final String[] value={null};final CountDownLatch done=new CountDownLatch(1);runOnMainSync(new Runnable(){public void run(){try{((WebView)field("web")).evaluateJavascript(expression,new ValueCallback<String>(){public void onReceiveValue(String r){value[0]=r;done.countDown();}});}catch(Exception e){value[0]="ERROR:"+e;done.countDown();}}});if(!done.await(30,TimeUnit.SECONDS))throw new AssertionError("JS callback: "+expression);return value[0];}
    void passed(String label){checks.add(label);Bundle b=new Bundle();b.putString("progress",label);sendStatus(0,b);}
    void require(boolean value,String label){if(!value)throw new AssertionError(label);passed(label);}
    AccessibilityNodeInfo match(AccessibilityNodeInfo n,String kind,String text){
        if(n==null)return null;String value="text".equals(kind)?String.valueOf(n.getText()):"desc".equals(kind)?String.valueOf(n.getContentDescription()):"id".equals(kind)?String.valueOf(n.getViewIdResourceName()):String.valueOf(n.getClassName());
        if(n.isVisibleToUser()&&("class".equals(kind)?value.contains(text):value.equalsIgnoreCase(text)))return AccessibilityNodeInfo.obtain(n);
        for(int i=0;i<n.getChildCount();i++){AccessibilityNodeInfo child=n.getChild(i),found=match(child,kind,text);if(child!=null)child.recycle();if(found!=null)return found;}return null;
    }
    AccessibilityNodeInfo find(String kind,String text){AccessibilityNodeInfo root=getUiAutomation().getRootInActiveWindow();try{return match(root,kind,text);}finally{if(root!=null)root.recycle();}}
    boolean click(String kind,String text){return clickNode(find(kind,text));}
    boolean clickNode(AccessibilityNodeInfo n){if(n==null)return false;try{for(int i=0;i<12&&!n.isClickable();i++){AccessibilityNodeInfo parent=n.getParent();if(parent==null)return false;n.recycle();n=parent;}return n.isEnabled()&&n.performAction(AccessibilityNodeInfo.ACTION_CLICK);}finally{n.recycle();}}
    boolean activateFile(String text){AccessibilityNodeInfo n=find("text",text);if(n==null)return false;try{for(int i=0;i<12;i++){if("com.android.documentsui:id/item_root".equals(n.getViewIdResourceName())){if(n.performAction(AccessibilityNodeInfo.ACTION_CLICK)){selectionMethod="document row accessibility click";return true;}if(n.performAction(AccessibilityNodeInfo.ACTION_FOCUS)){selectionMethod="focused document row and Enter";long now=SystemClock.uptimeMillis();boolean down=getUiAutomation().injectInputEvent(new KeyEvent(now,now,KeyEvent.ACTION_DOWN,KeyEvent.KEYCODE_ENTER,0),false);boolean up=getUiAutomation().injectInputEvent(new KeyEvent(now,now+80,KeyEvent.ACTION_UP,KeyEvent.KEYCODE_ENTER,0),false);return down&&up;}selectionMethod="row could not activate; actions="+n.getActionList();return false;}AccessibilityNodeInfo parent=n.getParent();if(parent==null)return false;n.recycle();n=parent;}return false;}finally{n.recycle();}}
    boolean picker(){AccessibilityNodeInfo root=getUiAutomation().getRootInActiveWindow();try{return root!=null&&root.getPackageName()!=null&&root.getPackageName().toString().contains("documentsui");}finally{if(root!=null)root.recycle();}}
    String activePackage(){AccessibilityNodeInfo root=getUiAutomation().getRootInActiveWindow();try{return root==null||root.getPackageName()==null?"<no-active-window>":root.getPackageName().toString();}finally{if(root!=null)root.recycle();}}
    void cancelPicker(){long now=SystemClock.uptimeMillis();if(!getUiAutomation().injectInputEvent(new KeyEvent(now,now,KeyEvent.ACTION_DOWN,KeyEvent.KEYCODE_BACK,0),true)||!getUiAutomation().injectInputEvent(new KeyEvent(now,now+80,KeyEvent.ACTION_UP,KeyEvent.KEYCODE_BACK,0),true))throw new AssertionError("Could not send Back to actual DocumentsUI");}
    void pickerCancellationAndRecreation()throws Exception{
        js("AndroidArchive.openBackup()");until(new Check(){public boolean ok(){return picker();}},"actual import picker before cancel");require(!(Boolean)field("activityResumed"),"Import chooser is the foreground system activity");cancelPicker();until(new Check(){public boolean ok()throws Exception{return (Integer)field("archiveRequest")==0&&(Boolean)field("activityResumed");}},"import cancellation returns to host");require(true,"Back cancels real import picker and releases request");
        js("AndroidArchive.writeBackup('{\"testOnly\":true}')");until(new Check(){public boolean ok(){return picker();}},"actual export picker before cancel");final String prepared=(String)field("pendingExportName");require(prepared!=null&&prepared.startsWith("pending-town-export-"),"Export picker holds only its synthetic private prepared file");cancelPicker();until(new Check(){public boolean ok()throws Exception{return (Integer)field("archiveRequest")==0&&(Boolean)field("activityResumed");}},"export cancellation returns to host");until(new Check(){public boolean ok()throws Exception{return field("pendingExportName")==null&&!new java.io.File(current.getFilesDir(),prepared).exists();}},"cancelled prepared export cleanup");require(true,"Back cancels real export picker and deletes its prepared file");
        js("AndroidArchive.writeBackup('{\"testOnly\":true,\"recreated\":true}')");until(new Check(){public boolean ok(){return picker();}},"actual export picker before Activity recreation");final MainActivity old=current;final String recreatedFile=(String)field("pendingExportName");runOnMainSync(new Runnable(){public void run(){old.recreate();}});SystemClock.sleep(1500);cancelPicker();until(new Check(){public boolean ok()throws Exception{return current!=old&&(Integer)field("archiveRequest")==0&&(Boolean)field("activityResumed");}},"recreated host receives picker cancellation");until(new Check(){public boolean ok()throws Exception{return field("pendingExportName")==null&&!new java.io.File(current.getFilesDir(),recreatedFile).exists();}},"recreated picker prepared file cleanup");require(true,"Back after Activity recreation cancels picker, restores host, and removes prepared export");
    }
    void downloads()throws Exception{
        AccessibilityNodeInfo breadcrumb=find("id","com.android.documentsui:id/breadcrumb_text");
        if(breadcrumb!=null){boolean here="Downloads".equals(String.valueOf(breadcrumb.getText()));breadcrumb.recycle();if(here)return;}
        if(!click("desc","Show roots"))throw new AssertionError("Could not open document roots");
        until(new Check(){public boolean ok(){return findAndRecycle("id","com.android.documentsui:id/roots_list");}},"document roots visible");
        AccessibilityNodeInfo roots=find("id","com.android.documentsui:id/roots_list");AccessibilityNodeInfo download=null;try{download=match(roots,"text","Downloads");}finally{if(roots!=null)roots.recycle();}
        if(!clickNode(download))throw new AssertionError("Could not select Downloads root");
        until(new Check(){public boolean ok(){AccessibilityNodeInfo n=find("id","com.android.documentsui:id/breadcrumb_text");if(n==null)return false;try{return "Downloads".equals(String.valueOf(n.getText()));}finally{n.recycle();}}},"Downloads directory active");
    }
    boolean findAndRecycle(String kind,String text){AccessibilityNodeInfo n=find(kind,text);if(n==null)return false;n.recycle();return true;}
    String tree(){StringBuilder s=new StringBuilder();AccessibilityNodeInfo root=getUiAutomation().getRootInActiveWindow();try{dump(root,s,0,new int[]{0});return s.toString();}finally{if(root!=null)root.recycle();}}
    void dump(AccessibilityNodeInfo n,StringBuilder s,int depth,int[] count){if(n==null||count[0]++>180)return;s.append(depth).append(' ').append(n.getClassName()).append(" text=").append(n.getText()).append(" desc=").append(n.getContentDescription()).append(" visible=").append(n.isVisibleToUser()).append(" clickable=").append(n.isClickable()).append(" enabled=").append(n.isEnabled()).append(" id=").append(n.getViewIdResourceName()).append('\n');for(int i=0;i<n.getChildCount();i++){AccessibilityNodeInfo c=n.getChild(i);dump(c,s,depth+1,count);if(c!=null)c.recycle();}}
    @Override public void callActivityOnResume(Activity activity){super.callActivityOnResume(activity);if(activity instanceof MainActivity)current=(MainActivity)activity;}
    @Override public void onCreate(Bundle b){super.onCreate(b);start();}
    @Override public void onStart(){Bundle result=new Bundle();try{
        current=(MainActivity)startActivitySync(new Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER).setComponent(new ComponentName(getTargetContext(),MainActivity.class)).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK|Intent.FLAG_ACTIVITY_CLEAR_TASK));
        until(new Check(){public boolean ok()throws Exception{return "\"complete\"".equals(js("document.readyState"));}},"target WebView document ready");
        until(new Check(){public boolean ok()throws Exception{return (Boolean)field("activityResumed")&&"org.townledger.vale".equals(activePackage());}},"foreground target activity and window");
        JSONObject page=new JSONObject(new JSONArray("["+js("JSON.stringify({url:location.href,ready:document.readyState,qaMode:String(window.qaMode),open:typeof AndroidArchive.openBackup,write:typeof AndroidArchive.writeBackup})")+"]").getString(0));
        String active=activePackage();boolean matching="org.townledger.vale".equals(active)&&"file:///android_asset/index.html".equals(page.optString("url"))&&"complete".equals(page.optString("ready"))&&"handled".equals(page.optString("qaMode"))&&"function".equals(page.optString("open"))&&"function".equals(page.optString("write"));
        if(!matching)throw new AssertionError("Wrong DocumentsUI fixture before picker launch: foregroundPackage="+active+" webView="+page.toString());
        require(true,"Foreground target loaded the matching lightweight DocumentsUI fixture asset");pickerCancellationAndRecreation();
        final String text="{\"testOnly\":true,\"town\":\"Oak · آبادی 🌲\",\"note\":\"Not a user save\"}";
        final String filename="TownLedger-QA-"+(SystemClock.uptimeMillis()%100000000)+".json";result.putString("syntheticFilename",filename);
        js("AndroidArchive.writeBackup("+JSONObject.quote(text)+")");until(new Check(){public boolean ok(){return picker();}},"actual create-document UI");passed("Production bridge launched actual DocumentsUI create-document activity");
        downloads();until(new Check(){public boolean ok(){return findAndRecycle("class","EditText");}},"save filename field");
        AccessibilityNodeInfo edit=find("class","EditText");try{Bundle value=new Bundle();value.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE,filename);if(!edit.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT,value))throw new AssertionError("Could not set synthetic filename");}finally{edit.recycle();}
        until(new Check(){public boolean ok(){return click("text","SAVE");}},"Save enabled");
        until(new Check(){public boolean ok()throws Exception{return (Integer)field("archiveRequest")==0&&(Boolean)field("activityResumed");}},"save result committed");passed("Actual DocumentsUI Save selection completed production export and resumed host");
        js("qaRestore=null;AndroidArchive.openBackup()");until(new Check(){public boolean ok(){return picker();}},"actual open-document UI");downloads();click("desc","List view");
        until(new Check(){public boolean ok(){return activateFile(filename);}},"select exported synthetic file");
        until(new Check(){public boolean ok()throws Exception{return JSONObject.quote(text).equals(js("window.qaRestore"))&&(Integer)field("archiveRequest")==0;}},"selected file restored through production bridge");passed("Actual DocumentsUI Open selection imported exact Unicode bytes from the exported synthetic document");
        if(!(Boolean)field("activityResumed"))throw new AssertionError("Host did not resume");passed("Successful system document roundtrip leaves host resumed and archive request idle");
        result.putString("selectionMethod",selectionMethod);result.putString("outcome","PASS");result.putString("checks",checks.toString());finish(Activity.RESULT_OK,result);
    }catch(Throwable e){result.putString("selectionMethod",selectionMethod);result.putString("outcome","FAIL");result.putString("checks",checks.toString());result.putString("error",android.util.Log.getStackTraceString(e));result.putString("uiTree",tree());finish(Activity.RESULT_CANCELED,result);}}
}
