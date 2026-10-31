#!/usr/bin/env python3
"""Build private native fixture/test APKs with official SDK tools, outside source.

Does not install, run, sign a release, or use the production signing key.
"""
from pathlib import Path
import argparse, hashlib, json, os, shutil, subprocess, zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
NS = '{http://schemas.android.com/apk/res/android}'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk', type=Path, default=Path(os.environ.get('ANDROID_HOME', '/opt/android-sdk')))
    parser.add_argument('--out', type=Path, required=True, help='Private scratch directory outside repository')
    parser.add_argument('--game', action='store_true', help='Use unmodified full game assets and FullGameHarness')
    parser.add_argument('--documents', action='store_true', help='Use synthetic fixture and actual DocumentsUI save/open harness')
    args = parser.parse_args()
    if args.documents and args.game:
        parser.error('--documents uses the lightweight synthetic fixture; run --game separately')
    out = args.out.resolve()
    if out == ROOT or ROOT in out.parents:
        parser.error('Keep debug APKs and their disposable signer outside the repository')
    out.mkdir(parents=True, exist_ok=True)
    def newest(paths):
        return max(paths, key=lambda p: tuple(int(n) if n.isdigit() else 0 for n in p.parent.name.removeprefix('android-').split('.')))
    tools = newest(list(args.sdk.glob('build-tools/*/aapt'))).parent
    jar = newest(list(args.sdk.glob('platforms/*/android.jar')))
    def run(argv):
        subprocess.run([str(a) for a in argv], check=True)
    key = out / 'disposable-debug.p12'
    if not key.exists():
        run(['java', 'sun.security.tools.keytool.Main', '-genkeypair', '-keystore', key, '-storetype', 'PKCS12', '-storepass', 'android', '-keypass', 'android', '-alias', 'debug', '-keyalg', 'RSA', '-keysize', '2048', '-validity', '30', '-dname', 'CN=TownLedger Private Native QA'])
    def package(name, manifest, sources, assets=None, classpath=None):
        stage = out / name
        if stage.exists():
            shutil.rmtree(stage)
        stage.mkdir()
        classes = stage / 'classes'
        classes.mkdir()
        (stage / 'AndroidManifest.xml').write_text(manifest, encoding='utf-8')
        compile_args = ['java', 'com.sun.tools.javac.Main', '-source', '8', '-target', '8', '-Xlint:-options', '-bootclasspath', jar, '-d', classes]
        if classpath:
            compile_args += ['-classpath', classpath]
        run(compile_args + sources)
        dex_args = [tools / 'd8', '--lib', jar, '--min-api', '24', '--output', stage]
        if classpath:
            dex_args += ['--classpath', classpath]
        run(dex_args + list(classes.rglob('*.class')))
        aapt_args = [tools / 'aapt', 'package', '-f', '-M', stage / 'AndroidManifest.xml', '-I', jar, '-F', stage / 'unsigned.apk']
        if assets:
            aapt_args += ['-A', assets]
        run(aapt_args)
        import zipfile
        if assets == ROOT / 'assets':
            with zipfile.ZipFile(stage / 'unsigned.apk') as check:
                source_game = hashlib.sha256((ROOT / 'assets/game.js').read_bytes()).hexdigest()
                packaged_game = hashlib.sha256(check.read('assets/game.js')).hexdigest()
            if source_game != packaged_game:
                raise RuntimeError('Packaged assets/game.js differs from source distribution')
        with zipfile.ZipFile(stage / 'unsigned.apk', 'a', compression=zipfile.ZIP_STORED) as archive:
            archive.write(stage / 'classes.dex', 'classes.dex')
        run([tools / 'zipalign', '-f', '4', stage / 'unsigned.apk', stage / 'aligned.apk'])
        apk = out / (name + '.apk')
        run([tools / 'apksigner', 'sign', '--ks', key, '--ks-key-alias', 'debug', '--ks-pass', 'pass:android', '--key-pass', 'pass:android', '--out', apk, stage / 'aligned.apk'])
        run([tools / 'apksigner', 'verify', '--verbose', apk])
        return classes, apk
    # Match the real file origin and unmodified production Activity without assets/resources
    # that could accidentally be delivered as a game build.
    manifest = ET.parse(ROOT / 'android/AndroidManifest.xml').getroot()
    manifest.set(NS + 'versionCode', '900004')
    manifest.set(NS + 'versionName', 'private-native-qa')
    queries = ET.SubElement(manifest, 'queries')
    ET.SubElement(queries, 'package', {NS + 'name': 'org.townledger.vale.tests'})
    app = manifest.find('application')
    app.attrib.pop(NS + 'icon', None)
    app.set(NS + 'debuggable', 'true')
    app.set(NS + 'testOnly', 'true')
    assets = out / 'fixture-assets'
    assets.mkdir(exist_ok=True)
    shutil.copyfile(ROOT / 'tests/android/host-page.html', assets / 'index.html')
    if args.game:
        assets = ROOT / 'assets'
    java = list((ROOT / 'android/app/src/main/java').rglob('*.java'))
    classes, target = package('native-host-fixture', ET.tostring(manifest, encoding='unicode'), java, assets)
    harness = 'DocumentsHarness' if args.documents else 'FullGameHarness' if args.game else 'RecoveryHarness'
    test_manifest = '''<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="org.townledger.vale.tests"><uses-sdk android:minSdkVersion="29" android:targetSdkVersion="36"/><queries><package android:name="org.townledger.vale"/></queries><application android:label="Private native checks" android:debuggable="true" android:testOnly="true"><provider android:name="org.townledger.vale.ArchiveProvider" android:authorities="org.townledger.vale.tests.archive" android:exported="true"/></application><instrumentation android:name="org.townledger.vale.RecoveryHarness" android:targetPackage="org.townledger.vale"/></manifest>'''
    test_manifest = test_manifest.replace('org.townledger.vale.RecoveryHarness', 'org.townledger.vale.' + harness)
    _, test = package('native-host-tests', test_manifest, [ROOT / ('tests/android/' + harness + '.java'), ROOT / 'tests/android/ArchiveProvider.java'], classpath=classes)
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in java + [ROOT / ('tests/android/' + harness + '.java'), ROOT / 'tests/android/ArchiveProvider.java'] if p.is_file()}
    hashes.update({'assets/' + str(p.relative_to(assets)): hashlib.sha256(p.read_bytes()).hexdigest() for p in assets.rglob('*') if p.is_file()})
    report = {'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'source_files': hashes, 'artifacts': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [target, test]}, 'game_assets': args.game, 'asset_source': 'assets' if args.game else 'tests/android/host-page.html', 'sdk_platform': jar.parent.name, 'build_tools': tools.name, 'run_status': 'NOT RUN', 'production_signer_used': False}
    if args.game:
        with zipfile.ZipFile(target) as check:
            embedded = hashlib.sha256(check.read('assets/game.js')).hexdigest()
        expected = hashlib.sha256((ROOT / 'assets/game.js').read_bytes()).hexdigest()
        if embedded != expected:
            raise RuntimeError('Signed APK contains stale game.js')
    (out / 'build-evidence.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Built test-only APKs. Install both with adb install -t, then run:')
    print('adb shell am instrument -w org.townledger.vale.tests/org.townledger.vale.' + harness)

if __name__ == '__main__':
    main()
