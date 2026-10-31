"""Independent SDK verification plus source/asset and DEX integrity checks."""
from pathlib import Path
import hashlib, json, struct, subprocess, sys, zipfile, zlib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import build_android as build
metadata=json.loads((ROOT/'release.json').read_text())
apk=ROOT/('TownLedger-'+metadata['edition'].replace(' ','-')+'-'+metadata['version']+'.apk')
with zipfile.ZipFile(apk) as z:
 assert z.testzip() is None
 dex=z.read('classes.dex')
 assert dex[:4]==b'dex\n' and struct.unpack_from('<I',dex,32)[0]==len(dex)
 assert dex[12:32]==hashlib.sha1(dex[32:]).digest()
 assert struct.unpack_from('<I',dex,8)[0]==zlib.adler32(dex[12:])&0xffffffff
 assert b'Lorg/townledger/vale/MainActivity;' in dex
 assert b'Lorg/townledger/vale/BackNavigation;' in dex
 assert b'backResult' in dex and b'onRenderProcessGone' in dex
 assert b'RecoveryHarness' not in dex,'Private instrumentation leaked into game APK'
 assert b'writeBackup' in dex and b'openBackup' in dex
 assets={}
 for p in (ROOT/'assets').rglob('*'):
  if p.is_file():
   name='assets/'+p.relative_to(ROOT/'assets').as_posix()
   assert z.read(name)==p.read_bytes(),name+' differs from source'
   assets[name]=hashlib.sha256(z.read(name)).hexdigest()
 assert 'resources.arsc' in z.namelist()
 assert not any('signing' in n or n.endswith(('.pem','.p12','.jks')) for n in z.namelist())
badging=subprocess.check_output([build.find_tool('aapt'),'dump','badging',str(apk)],env=build.env,text=True)
assert "package: name='"+metadata['package']+"'" in badging
assert "versionName='"+metadata['version']+"'" in badging
assert "versionCode='"+str(metadata['code'])+"'" in badging
assert "targetSdkVersion:'36'" in badging and "sdkVersion:'24'" in badging
assert 'uses-permission:' not in badging
assert 'application-debuggable' not in badging and 'testOnly=' not in badging,'Private test build is not a game deliverable'
sdk_signer=next(iter(sorted(build.TOOLROOT.glob('build-tools/*/apksigner'),reverse=True)),None)
signer=[str(sdk_signer)] if sdk_signer else ['java','-cp',str(build.TOOLROOT/'usr/share/java/apksigner.jar')+':'+str(build.TOOLROOT/'usr/share/java/apksig.jar'),'com.android.apksigner.ApkSignerTool']
verification=subprocess.check_output([*signer,'verify','--verbose','--print-certs',str(apk)],env=build.env,text=True)
assert 'Verified using v2 scheme (APK Signature Scheme v2): true' in verification
subprocess.run([build.find_tool('zipalign'),'-c','4',str(apk)],env=build.env,check=True)
report={'apk':apk.name,'sha256':hashlib.sha256(apk.read_bytes()).hexdigest(),'bytes':apk.stat().st_size,'dexIntegrity':True,'sourceAssetsMatch':True,'assets':assets,'badging':badging,'signatureVerification':verification,'alignment':True,'deviceInstallation':'NOT TESTED','frameRateOnAndroid':'NOT TESTED'}
(ROOT/'reports/final').mkdir(parents=True,exist_ok=True)
(ROOT/'reports/final/apk-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS source assets, real Java DEX, package, icon resources, no permissions, v2/v3 signature and ZIP alignment')
print('APK SHA-256',report['sha256'])
