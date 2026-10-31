#!/usr/bin/env python3
"""Kill/relaunch an isolated debug game process and inspect actual Continue recovery.

Requires websockets and official ADB. Never writes or publishes save payloads;
only synthetic-test-state hashes, counts and differences are retained.
"""
import argparse, asyncio, hashlib, io, json, subprocess, sys, time, urllib.request, zipfile
from pathlib import Path
import websockets

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--adb', required=True)
parser.add_argument('--serial', required=True)
parser.add_argument('--source-sha', required=True)
parser.add_argument('--out', type=Path, required=True)
parser.add_argument('--port', type=int, default=9234)
args = parser.parse_args()
if not args.serial.startswith('emulator-'):
    parser.error('This synthetic-data probe is restricted to an isolated emulator')
root = Path(__file__).resolve().parents[2]
out = args.out.resolve()
if out == root or root in out.parents:
    parser.error('Keep process-death evidence outside the repository')
out.mkdir(parents=True, exist_ok=True)
package = 'org.townledger.vale'
report = {'outcome': 'NOT RUN', 'source_sha256': args.source_sha, 'serial': args.serial,
          'input': 'CDP trusted browser events; not physical touch', 'clock_control': 'public host suspend bridge holds simulation around Continue to isolate persistence', 'physical_device': False}

def stage(name, **data):
    report['stage'] = name
    report.update(data)
    (out / 'process-death-progress.json').write_text(json.dumps(report, indent=2) + '\n')
    print(name, flush=True)

def adb(*words, timeout=45, check=True):
    r = subprocess.run([args.adb, '-s', args.serial, *words], capture_output=True, timeout=timeout)
    if check and r.returncode:
        raise RuntimeError('ADB command failed: ' + ' '.join(words[:4]) + ': ' + r.stderr.decode(errors='replace'))
    return r.stdout

def pid():
    return adb('shell', 'pidof', package, check=False).decode().strip()

class Page:
    def __init__(self, socket):
        self.socket, self.counter = socket, 0
    async def command(self, method, params):
        self.counter += 1
        number = self.counter
        await self.socket.send(json.dumps({'id': number, 'method': method, 'params': params}))
        while True:
            response = json.loads(await asyncio.wait_for(self.socket.recv(), 100))
            if response.get('id') == number:
                if 'error' in response:
                    raise RuntimeError(response['error'])
                return response['result']
    async def evaluate(self, expression):
        r = await self.command('Runtime.evaluate', {'expression': expression, 'returnByValue': True, 'awaitPromise': True})
        if r.get('exceptionDetails'):
            raise RuntimeError(r['exceptionDetails'])
        return r['result'].get('value')
    async def wait(self, expression):
        end = time.monotonic() + 120
        while time.monotonic() < end:
            if await self.evaluate(expression):
                return
            await asyncio.sleep(.5)
        raise TimeoutError(expression)
    async def click(self, selector):
        point = await self.evaluate('(function(){var e=document.querySelector(' + json.dumps(selector) + ");if(!e)return null;e.scrollIntoView({block:'center'});var r=e.getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]})()")
        if not point:
            raise RuntimeError('Missing control ' + selector)
        x, y = point
        await self.command('Input.dispatchMouseEvent', {'type': 'mousePressed', 'x': x, 'y': y, 'button': 'left', 'clickCount': 1})
        await self.command('Input.dispatchMouseEvent', {'type': 'mouseReleased', 'x': x, 'y': y, 'button': 'left', 'clickCount': 1})

async def connect():
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    end = time.monotonic() + 90
    while time.monotonic() < end:
        current = pid().split()
        if current:
            adb('forward', 'tcp:' + str(args.port), 'localabstract:webview_devtools_remote_' + current[0])
            try:
                targets = json.load(opener.open('http://127.0.0.1:' + str(args.port) + '/json', timeout=5))
                target = next(t for t in targets if t.get('type') == 'page' and t.get('url', '').startswith('file:///android_asset/'))
                socket = await websockets.connect(target['webSocketDebuggerUrl'])
                try:
                    ready = await Page(socket).evaluate("typeof __townTest==='object'&&!!document.querySelector('#newTown')")
                    if ready:
                        return socket
                except websockets.exceptions.ConnectionClosed:
                    pass
                await socket.close()
            except (OSError, StopIteration, ValueError, websockets.exceptions.ConnectionClosed):
                pass
        await asyncio.sleep(1)
    raise TimeoutError('Debug game page did not become available')

async def loaded_state(create=False):
    socket = await connect()
    page = Page(socket)
    await page.wait("typeof __townTest==='object'&&!!document.querySelector('#newTown')")
    if not create:
        await page.wait("!document.querySelector('#continue').disabled")
    # Isolate saved-state recovery from legitimate simulation time spent waiting
    # on the software renderer. This does not alter the stored town or bypass load.
    await page.evaluate('window.__townArchive.suspend()')
    await page.click('#newTown' if create else '#continue')
    await page.wait('__townTest.get().population>0')
    await page.evaluate('window.__townArchive.suspend()')
    valid = await page.evaluate('__townTest.validate().ok')
    if not valid:
        raise RuntimeError('Continued town failed validation')
    return socket, page

async def main():
    try:
        flags = adb('shell', 'dumpsys', 'package', package).decode(errors='replace')
        if 'DEBUGGABLE' not in flags or 'TEST_ONLY' not in flags:
            raise RuntimeError('Refusing to kill a non-test/debug installation')
        path = adb('shell', 'pm', 'path', package).decode().strip().splitlines()[0].removeprefix('package:')
        data = adb('exec-out', 'cat', path, timeout=60)
        with zipfile.ZipFile(io.BytesIO(data)) as apk:
            source_sha = hashlib.sha256(apk.read('assets/game.js')).hexdigest()
        if source_sha != args.source_sha:
            raise RuntimeError('Installed payload is not the requested immutable source')
        report['installed_apk_sha256'] = hashlib.sha256(data).hexdigest()
        stage('installed exact debug payload verified')
        adb('shell', 'am', 'start', '-W', '-n', package + '/.MainActivity', timeout=120)
        stage('initial app started', initial_pid=pid())
        socket, page = await loaded_state(create=True)
        stage('synthetic baseline loaded')
        saved = await page.evaluate('window.__townArchive.suspend()')
        if saved is not True:
            raise RuntimeError('Actual on-device save did not confirm completion')
        before = json.loads(await page.evaluate('__townTest.save()'))
        old_pid = pid()
        stage('completed save confirmed', old_pid=old_pid)
        await socket.close()
        adb('shell', 'input', 'keyevent', '3', timeout=45)
        await asyncio.sleep(3)
        stage('app backgrounded', background_pid=pid())
        adb('shell', 'am', 'kill', '--user', '0', package)
        end = time.monotonic() + 30
        while pid() and time.monotonic() < end:
            await asyncio.sleep(1)
        if pid():
            raise RuntimeError('Background process did not die after supported am kill; no forced-kill fallback')
        stage('background process death observed', process_gone=True)
        adb('shell', 'am', 'start', '-W', '-n', package + '/.MainActivity', timeout=120)
        stage('fresh process started', relaunched_pid=pid())
        socket, page = await loaded_state()
        stage('Continue completed')
        after = json.loads(await page.evaluate('__townTest.save()'))
        new_pid = pid()
        await socket.close()
        def digest(value):
            return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()
        report.update({'old_pid': old_pid, 'new_pid': new_pid, 'actual_process_changed': bool(old_pid and new_pid and old_pid != new_pid),
                       'before_sha256': digest(before), 'after_sha256': digest(after),
                       'before_day': before.get('day'), 'after_day': after.get('day'),
                       'before_people': len(before.get('people', [])), 'after_people': len(after.get('people', [])),
                       'different_top_level_fields': [k for k in sorted(set(before) | set(after)) if before.get(k) != after.get(k)]})
        if not report['actual_process_changed'] or before != after:
            raise AssertionError('Recovered state differs; see hashes and differing fields (payloads not retained)')
        report['outcome'] = 'PASS'
    except Exception as error:
        report['outcome'], report['error'] = 'FAIL', repr(error)
    finally:
        adb('forward', '--remove', 'tcp:' + str(args.port), check=False)
        (out / 'process-death.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report, indent=2))

asyncio.run(main())
sys.exit(0 if report['outcome'] == 'PASS' else 1)
