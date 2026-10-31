package org.townledger.vale;

import android.app.Activity;
import android.app.Instrumentation;
import android.content.ComponentName;
import android.content.Intent;
import android.os.Bundle;
import android.os.SystemClock;
import android.view.MotionEvent;
import android.view.KeyEvent;
import android.webkit.WebView;
import android.webkit.ValueCallback;
import java.lang.reflect.Field;
import java.io.FileOutputStream;
import java.io.File;
import android.util.Base64;
import java.util.ArrayList;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import org.json.JSONObject;
import org.json.JSONArray;

/** Full bundled game in the native host. No test hooks are inserted into JS. */
public final class FullGameHarness extends Instrumentation {
    MainActivity current;
    boolean largeCity;
    boolean audioOnly;
    boolean additionalFailure;
    final ArrayList<String> checks=new ArrayList<String>();
    WebView web()throws Exception{Field field=MainActivity.class.getDeclaredField("web");field.setAccessible(true);return (WebView)field.get(current);}
    String js(final String expression)throws Exception{final CountDownLatch done=new CountDownLatch(1);final String[] value={null};runOnMainSync(new Runnable(){public void run(){try{web().evaluateJavascript(expression,new ValueCallback<String>(){public void onReceiveValue(String r){value[0]=r;done.countDown();}});}catch(Exception e){value[0]="ERROR:"+e;done.countDown();}}});if(!done.await(90,TimeUnit.SECONDS))throw new AssertionError("JS timeout: "+expression);return value[0];}
    void waitFor(String expression)throws Exception{long end=SystemClock.uptimeMillis()+90000;while(SystemClock.uptimeMillis()<end){if("true".equals(js(expression)))return;SystemClock.sleep(250);}throw new AssertionError("Timeout: "+expression);}
    void require(boolean condition,String label){if(!condition)throw new AssertionError(label);checks.add(label);Bundle progress=new Bundle();progress.putString("progress",label);sendStatus(0,progress);}
    void tap(String selector)throws Exception{
        js("(function(){var e=document.querySelector("+JSONObject.quote(selector)+");if(e)e.scrollIntoView({block:'center',inline:'nearest'})})()");
        String target=js("(function(){var e=document.querySelector("+JSONObject.quote(selector)+");if(!e)return {error:'missing',selector:"+JSONObject.quote(selector)+"};var r=e.getBoundingClientRect(),x=r.left+r.width/2,y=r.top+r.height/2,hit=document.elementFromPoint(x,y);if(!r.width||!r.height||!hit||!(hit===e||e.contains(hit)))return {error:'covered',selector:"+JSONObject.quote(selector)+",x:x,y:y,hit:hit?hit.outerHTML.slice(0,500):null};return [x/innerWidth,y/innerHeight]})()");
        if(!target.startsWith("["))throw new AssertionError("Native input target: "+target);
        JSONArray position=new JSONArray(target);
        final float x=(float)position.getDouble(0),y=(float)position.getDouble(1);final int[] screen=new int[4];runOnMainSync(new Runnable(){public void run(){try{WebView view=web();view.getLocationOnScreen(screen);screen[2]=view.getWidth();screen[3]=view.getHeight();}catch(Exception e){throw new RuntimeException(e);}}});
        long now=SystemClock.uptimeMillis();MotionEvent down=MotionEvent.obtain(now,now,MotionEvent.ACTION_DOWN,screen[0]+x*screen[2],screen[1]+y*screen[3],0);sendPointerSync(down);down.recycle();SystemClock.sleep(80);MotionEvent up=MotionEvent.obtain(now,SystemClock.uptimeMillis(),MotionEvent.ACTION_UP,screen[0]+x*screen[2],screen[1]+y*screen[3],0);sendPointerSync(up);up.recycle();waitForIdleSync();
    }
    @Override public void onCreate(Bundle bundle){super.onCreate(bundle);largeCity=bundle!=null&&"true".equals(bundle.getString("large"));audioOnly=bundle!=null&&"true".equals(bundle.getString("audio"));start();}
    @Override public void onStart(){Bundle result=new Bundle();try{
        current=(MainActivity)startActivitySync(new Intent(Intent.ACTION_MAIN).setComponent(new ComponentName(getTargetContext(),MainActivity.class)).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK|Intent.FLAG_ACTIVITY_CLEAR_TASK));
        waitFor("typeof __townTest==='object'&&!!document.querySelector('#newTown')");result.putString("userAgent",new JSONArray("["+js("navigator.userAgent")+"]").getString(0));
        js("window.qaClicks=[];document.addEventListener('click',function(e){var b=e.target.closest('button');qaClicks.push({id:b?b.id:e.target.id,trusted:e.isTrusted,x:e.clientX,y:e.clientY})},true);window.qaAudio=[];window.qaNativeAudio=window.Audio;window.Audio=function(url){var audio=new qaNativeAudio(url);qaAudio.push(audio);return audio};window.qaErrors=[];window.addEventListener('error',function(e){qaErrors.push(e.message)});window.addEventListener('unhandledrejection',function(e){qaErrors.push(String(e.reason))})");
        tap("#newTown");waitFor("__townTest.get().population>0");tap("#pause");js("document.querySelector('#panelClose').click()");
        require("true".equals(js("__townTest.validate().ok")),"Native input founds a valid town");
        require("true".equals(js("(function(){var c=document.querySelector('canvas');return c.width>0&&c.height>0&&c.getBoundingClientRect().height>100})()")),"Full game has visible nonzero native map");
        String colors=js("(function(){__townTest.capture({zoom:.7});var c=document.querySelector('canvas'),data=c.getContext('2d').getImageData(0,0,c.width,c.height).data,seen={};for(var i=0;i<data.length;i+=64)seen[data[i]+','+data[i+1]+','+data[i+2]]=1;return Object.keys(seen).length})()");result.putString("mapRasterColors",colors);require(Integer.parseInt(colors)>64,"Native map contains rendered scene pixels");
        String capture=new JSONArray("["+js("document.querySelector('canvas').toDataURL('image/png')")+"]").getString(0);try(FileOutputStream file=new FileOutputStream(new File(current.getFilesDir(),"native-game-map.png"))){file.write(Base64.decode(capture.substring(capture.indexOf(',')+1),Base64.DEFAULT));}
        if(!audioOnly){
        for(int day=0;day<3;day++)js("__townTest.step(1)");require("true".equals(js("__townTest.validate().ok")),"Three settlement economy days validate in actual native engine");
        for(String panel:new String[]{"overview","economy","community","agenda","policies","settings"}){
            js("document.querySelector('[data-panel="+panel+"]').click()");require("true".equals(js("!document.querySelector('#panelBody').textContent.includes('Panel error')")),"Native "+panel+" panel opens");js("document.querySelector('#panelClose').click()");
        }
        js("(function(){var music=document.querySelector('#musicNext');if(!music||!music.getClientRects().length)document.querySelector('[data-panel=settings]').click()})();document.querySelector('#restart').click()");waitFor("document.querySelector('#eventDialog').style.display!=='none'");sendKeyDownUpSync(KeyEvent.KEYCODE_BACK);waitFor("document.querySelector('#eventDialog').style.display==='none'");require("true".equals(js("document.querySelector('#panel').classList.contains('show')"))&&!current.isFinishing(),"Native Back dismisses topmost confirmation while retaining settings and town");sendKeyDownUpSync(KeyEvent.KEYCODE_BACK);waitFor("!document.querySelector('#panel').classList.contains('show')");require(!current.isFinishing(),"Next native Back dismisses underlying drawer without exit");
        }
        if(audioOnly){for(int layer=0;layer<3;layer++){String open=js("(function(){var h=document.querySelector('#helpDialog'),e=document.querySelector('#eventDialog');return getComputedStyle(h).display!=='none'||getComputedStyle(e).display!=='none'})()");if(!"true".equals(open))break;sendKeyDownUpSync(KeyEvent.KEYCODE_BACK);SystemClock.sleep(500);}}
        result.putString("mediaBeforeExplicitControl",js("qaAudio.map(function(a){return {src:a.src,paused:a.paused,time:a.currentTime,duration:a.duration,ready:a.readyState,error:a.error?{code:a.error.code,message:a.error.message}:null}})"));
        js("(function(){var music=document.querySelector('#musicNext');if(!music||!music.getClientRects().length)document.querySelector('[data-panel=settings]').click()})()");waitFor("!!document.querySelector('#musicNext')");tap("#musicNext");
        // Native lifecycle calls exercise the production host; the host-JS harness
        // separately injects a long wall gap and checks clearing of queued time.
        waitFor("qaAudio.some(function(a){return /music/.test(a.src)&&!a.paused&&a.currentTime>0&&!a.error})");require(true,"Native Vorbis soundtrack advances real media playback after explicit music control touch");
        result.putString("mediaAfterExplicitControl",js("qaAudio.map(function(a){return {src:a.src,paused:a.paused,time:a.currentTime,duration:a.duration,ready:a.readyState,error:a.error?{code:a.error.code,message:a.error.message}:null}})"));
        js("document.querySelector('[data-panel=overview]').click()");
        if("\"Resume simulation\"".equals(js("document.querySelector('#pause').getAttribute('aria-label')")))tap("#pause");
        waitFor("document.querySelector('#pause').getAttribute('aria-label')==='Pause simulation'");
        js("window.qaSuspendSaved=false;window.qaSuspension={paint:0,writes:0,dom:0};var suspend=__townArchive.suspend;__townArchive.suspend=function(){qaSuspendSaved=false;var result=suspend();Promise.resolve(result).then(function(ok){qaSuspendSaved=ok===true});return result};var paint=CanvasRenderingContext2D.prototype.drawImage;CanvasRenderingContext2D.prototype.drawImage=function(){qaSuspension.paint++;return paint.apply(this,arguments)};var set=Storage.prototype.setItem;Storage.prototype.setItem=function(){qaSuspension.writes++;return set.apply(this,arguments)};var put=IDBObjectStore.prototype.put;IDBObjectStore.prototype.put=function(){qaSuspension.writes++;return put.apply(this,arguments)};new MutationObserver(function(records){qaSuspension.dom+=records.length}).observe(document.querySelector('#panelBody'),{childList:true,subtree:true,characterData:true,attributes:true})");
        runOnMainSync(new Runnable(){public void run(){callActivityOnPause(current);}});waitFor("qaSuspendSaved");SystemClock.sleep(1500);
        final String before=js("__townTest.get().day"),counts=js("qaSuspension");result.putString("hiddenDuringNativeSuspension",js("document.hidden"));SystemClock.sleep(3000);
        require(before.equals(js("__townTest.get().day")),"Native pause holds a running simulation day");require(counts.equals(js("qaSuspension")),"Native suspension parks observed map painting, Overview DOM and extra storage writes");result.putString("suspensionCounters",counts);
        require("true".equals(js("qaAudio.every(function(a){return a.paused})")),"Native pause stops soundtrack and effects media");
        long resumed=SystemClock.uptimeMillis();runOnMainSync(new Runnable(){public void run(){callActivityOnResume(current);}});String after=js("__townTest.get().day");long readMs=SystemClock.uptimeMillis()-resumed;result.putLong("resumeDayReadMs",readMs);require(Integer.parseInt(after)-Integer.parseInt(before)<=readMs/1650+1,"Native resume avoids a backlog burst after suspension");
        waitFor("qaAudio.some(function(a){return /music/.test(a.src)&&!a.paused&&a.currentTime>0})");require(true,"Native resume restarts soundtrack");
        tap("#pause");waitFor("document.querySelector('#pause').getAttribute('aria-label')==='Resume simulation'");runOnMainSync(new Runnable(){public void run(){callActivityOnPause(current);}});waitFor("qaSuspendSaved");runOnMainSync(new Runnable(){public void run(){callActivityOnResume(current);}});require("\"Resume simulation\"".equals(js("document.querySelector('#pause').getAttribute('aria-label')")),"Native suspend and resume preserve the player's own pause preference");
        js("window.qaSaved=__townTest.save();__townTest.load(qaSaved)");require("true".equals(js("__townTest.validate().ok")),"Native full-game archive roundtrip validates");
        js("(function(){var music=document.querySelector('#musicNext');if(!music||!music.getClientRects().length)document.querySelector('[data-panel=settings]').click()})()");tap("#musicToggle");tap("#musicToggle");SystemClock.sleep(5000);
        js("(function(){var music=document.querySelector('#musicNext');if(!music||!music.getClientRects().length)document.querySelector('[data-panel=settings]').click()})()");result.putString("musicStatus",js("document.querySelector('#panelBody').textContent"));
        require("true".equals(js("qaAudio.some(function(a){return /music/.test(a.src)&&!a.paused&&a.currentTime>0&&!a.error})")),"Native soundtrack reports no decoder error after gesture playback");
        try{tap("#musicNext");waitFor("qaAudio.filter(function(a){return /music/.test(a.src)&&!a.paused}).length===2");require(true,"Native soundtrack crossfade runs two streaming media elements");waitFor("qaAudio.filter(function(a){return /music/.test(a.src)}).length===1&&qaAudio.filter(function(a){return /music/.test(a.src)&&!a.paused}).length===1");require(true,"Native crossfade retires and unloads previous media source");}catch(Throwable error){additionalFailure=true;result.putString("crossfadeFailure",android.util.Log.getStackTraceString(error));result.putString("clicksAtCrossfadeFailure",js("qaClicks.slice(-10)"));Bundle progress=new Bundle();progress.putString("progress","Crossfade probe failed; independent large-city checks continue");sendStatus(0,progress);}
        require("[]".equals(js("qaErrors")),"No captured full-game JavaScript errors");
        if(largeCity){
            js("__townTest.reset('settlement',42)");String stress="(function(){var g=JSON.parse(__townTest.save()),busy=new Set();g.buildings.forEach(function(b){(b.footprint||[b.y*g.gridSize+b.x]).forEach(function(id){busy.add(id)})});var free=[];for(var y=3;y<53;y++)for(var x=3;x<53;x++)if(g.tiles[y*g.gridSize+x]===0&&!busy.has(y*g.gridSize+x)&&!(g.landUse||{})[g.gridSize*y+x])free.push([x,y]);var n=0;while(g.people.length<2000&&n<700){var xy=free[n],i=g.households.length,h={id:i,name:'Newcomer'+n,cash:500,home:g.nextId,owner:i,people:[],income:0,rent:0,food:0,tax:0,aid:0,crimeLoss:0,stress:25,security:80,last:[],worklessness:0},bb={id:g.nextId++,kind:'home',x:xy[0],y:xy[1],value:25000,condition:100,owner:i,firm:-1,hh:i};g.buildings.push(bb);g.homes.push(bb.id);g.households.push(h);g.region-=500;for(var a=0;a<3&&g.people.length<2000;a++){var id=g.people.length;g.people.push({id:id,name:'Resident '+id,age:26+a*3,skill:.5,health:80,hh:i,job:-1,life:70,last:[]});h.people.push(id)}n++}window.qaLargeTown=g;return g.people.length===2000})()";
            require("true".equals(js(stress)),"Synthetic 2000-resident archive prepared in native engine");require("true".equals(js("__townTest.load(qaLargeTown)&&__townTest.get().population===2000")),"Synthetic 2000-resident city loads in native engine");js("__townTest.capture({zoom:.7})");require("true".equals(js("__townTest.validate().ok")),"Native synthetic 2000-resident archive validates after loading");require("true".equals(js("qaAudio.some(function(a){return /music/.test(a.src)&&!a.paused&&a.currentTime>0&&!a.error})")),"Soundtrack remains active with synthetic large city");Bundle sample=new Bundle();sample.putString("progress","Large city ready for external memory sample (30 seconds)");sendStatus(0,sample);SystemClock.sleep(30000);
        }
        result.putString("town",js("__townTest.get()"));result.putString("outcome",additionalFailure?"FAIL":"PASS");result.putString("checks",checks.toString());finish(Activity.RESULT_OK,result);
    }catch(Throwable error){try{result.putString("mediaAtFailure",js("typeof qaAudio==='undefined'?null:qaAudio.map(function(a){return {src:a.src,paused:a.paused,time:a.currentTime,duration:a.duration,ready:a.readyState,error:a.error?{code:a.error.code,message:a.error.message}:null}})"));}catch(Throwable ignored){}result.putString("outcome","FAIL");result.putString("checks",checks.toString());result.putString("error",android.util.Log.getStackTraceString(error));finish(Activity.RESULT_CANCELED,result);}}
}
