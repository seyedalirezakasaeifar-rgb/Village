#!/usr/bin/env python3
"""Build real Java Android code with AOSP SDK tools; no hand-emitted DEX/manifest.

TOWNLEDGER_ANDROID_TOOLS: extracted distro tool root, or ANDROID_HOME for SDK tools.
TOWNLEDGER_ANDROID_JAR: optional platform android.jar override.
TOWNLEDGER_KEYSTORE: optional persistent development keystore path.
"""
from pathlib import Path
import hashlib, json, os, re, shutil, subprocess, zipfile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build'
OUT.mkdir(exist_ok=True)
META=json.loads((ROOT/'release.json').read_text())
TOOLROOT=Path(os.environ.get('TOWNLEDGER_ANDROID_TOOLS',os.environ.get('ANDROID_HOME','/opt/android-sdk')))
env=os.environ.copy()
env['LD_LIBRARY_PATH']=str(TOOLROOT/'usr/lib/x86_64-linux-gnu/android')+':'+str(TOOLROOT/'usr/lib/x86_64-linux-gnu')+':'+str(TOOLROOT/'usr/lib')+':'+env.get('LD_LIBRARY_PATH','')

def find_tool(name):
    for path in [TOOLROOT/'usr/bin'/name,*sorted(TOOLROOT.glob('build-tools/*/'+name),reverse=True)]:
        if path.exists():return str(path)
    path=shutil.which(name)
    if path:return path
    raise RuntimeError('Missing Android tool '+name)

def run(args):
    subprocess.run(list(map(str,args)),env=env,check=True)

def main():
    run(['python3',ROOT/'tools/assemble.py'])
    jar=Path(os.environ.get('TOWNLEDGER_ANDROID_JAR',TOOLROOT/'usr/share/java/com.android.android-23.jar'))
    if not jar.exists():
        candidates=sorted(TOOLROOT.glob('platforms/*/android.jar'),reverse=True)
        if not candidates:raise RuntimeError('Missing Android platform jar')
        jar=candidates[0]
    aapt=find_tool('aapt');align=find_tool('zipalign')
    manifest=re.sub(r'android:versionCode="[^"]+"','android:versionCode="'+str(META['code'])+'"',(ROOT/'android/AndroidManifest.xml').read_text())
    manifest=re.sub(r'android:versionName="[^"]+"','android:versionName="'+META['version']+'"',manifest)
    (OUT/'AndroidManifest.xml').write_text(manifest)
    classes=OUT/'classes'
    if classes.exists():shutil.rmtree(classes)
    classes.mkdir()
    sources=list((ROOT/'android/app/src/main/java').rglob('*.java'))
    run(['java','com.sun.tools.javac.Main','-source','7','-target','7','-Xlint:-options','-bootclasspath',jar,'-d',classes,*sources])
    dex=OUT/'classes.dex'
    d8=next(iter(sorted(TOOLROOT.glob('build-tools/*/d8'),reverse=True)),None)
    if d8:
        run([d8,'--min-api','24','--output',OUT,*classes.rglob('*.class')])
    else:
        dx=TOOLROOT/'usr/share/java/com.android.dx.jar'
        run(['java','-cp',dx,'com.android.dx.command.Main','--dex','--min-sdk-version=24','--output='+str(dex),classes])
    unsigned=OUT/'unsigned.apk'
    if unsigned.exists():unsigned.unlink()
    run([aapt,'package','-f','-M',OUT/'AndroidManifest.xml','-I',jar,'-S',ROOT/'android/res','-A',ROOT/'assets','-F',unsigned])
    with zipfile.ZipFile(unsigned,'a',compression=zipfile.ZIP_STORED) as z:z.write(dex,'classes.dex')
    aligned=OUT/'aligned.apk'
    run([align,'-f','4',unsigned,aligned])
    keystore=Path(os.environ.get('TOWNLEDGER_KEYSTORE',OUT/'development-signing.p12'))
    if not keystore.exists():
        run(['java','sun.security.tools.keytool.Main','-genkeypair','-keystore',keystore,'-storetype','PKCS12','-storepass','android','-keypass','android','-alias','townledger','-keyalg','RSA','-keysize','3072','-validity','10000','-dname','CN=TownLedger Development, O=TownLedger, C=CA'])
    apk=ROOT/('TownLedger-'+META['edition'].replace(' ','-')+'-'+'.'.join(META['version'].split('.')[:2])+'.apk')
    sdk_signer=next(iter(sorted(TOOLROOT.glob('build-tools/*/apksigner'),reverse=True)),None)
    signer=[sdk_signer] if sdk_signer else ['java','-cp',str(TOOLROOT/'usr/share/java/apksigner.jar')+':'+str(TOOLROOT/'usr/share/java/apksig.jar'),'com.android.apksigner.ApkSignerTool']
    run([*signer,'sign','--ks',keystore,'--ks-key-alias','townledger','--ks-pass','pass:android','--key-pass','pass:android','--min-sdk-version','24','--v1-signing-enabled','true','--v2-signing-enabled','true','--out',apk,aligned])
    run([*signer,'verify','--verbose','--print-certs',apk])
    run([align,'-c','4',apk])
    report={'apk':apk.name,'sha256':hashlib.sha256(apk.read_bytes()).hexdigest(),'bytes':apk.stat().st_size,'package':META['package'],'version':META['version'],'code':META['code'],'pipeline':'javac + dx/d8 + aapt + zipalign + apksigner','signature':'development; not a store release key','physical_device_tested':False}
    (ROOT/'reports/android-build.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
