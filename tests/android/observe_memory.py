#!/usr/bin/env python3
"""Observe programmatic native-test stages; snapshots are not peak/FPS evidence."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import json, re, subprocess, time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--adb', required=True)
parser.add_argument('--log', type=Path, required=True, help='FullGameHarness am instrument output')
parser.add_argument('--out', type=Path, required=True)
parser.add_argument('--timeout', type=int, default=900)
args = parser.parse_args()
args.out.mkdir(parents=True, exist_ok=True)
markers = {
    'map': 'Native map contains rendered scene pixels',
    'crossfade': 'Native soundtrack crossfade runs two streaming media elements',
    'large-city': 'Large city ready for external memory sample',
}
rows = {}
started = time.monotonic()

def command(argv, path):
    try:
        run = subprocess.run([args.adb, 'shell', *argv], capture_output=True, text=True, timeout=25)
        text = run.stdout + run.stderr
        path.write_text(text)
        return text, run.returncode
    except subprocess.TimeoutExpired:
        path.write_text('TIMED OUT\n')
        return '', 'TIMED OUT'

while time.monotonic() - started < args.timeout:
    log = args.log.read_text() if args.log.exists() else ''
    for name, marker in markers.items():
        if name in rows or marker not in log:
            continue
        began = time.monotonic()
        row = {'observed_utc': datetime.now(timezone.utc).isoformat(), 'snapshots': []}
        # The app/browser process is attributable. Other WebView sandbox processes
        # are listed separately; their memory is not silently attributed to this app.
        text, status = command(['dumpsys', 'meminfo', 'org.townledger.vale'], args.out / (name + '-app.txt'))
        total = re.search(r'TOTAL PSS:\s*(\d+)', text)
        row['app_pss_kib'] = int(total.group(1)) if total else None
        row['app_status'] = status
        processes, _ = command(['ps', '-A', '-o', 'PID,NAME'], args.out / (name + '-processes.txt'))
        for line in processes.splitlines():
            fields = line.split(None, 1)
            if len(fields) == 2 and 'webview' in fields[1] and 'sandboxed_process' in fields[1]:
                pid = fields[0]
                text, status = command(['dumpsys', 'meminfo', pid], args.out / (name + '-webview-' + pid + '.txt'))
                total = re.search(r'TOTAL PSS:\s*(\d+)', text)
                row['snapshots'].append({'pid': int(pid), 'process': fields[1], 'pss_kib': int(total.group(1)) if total else None, 'status': status, 'attribution': 'observed WebView sandbox; inspect process ownership before summing'})
        row['sampling_seconds'] = round(time.monotonic() - began, 3)
        rows[name] = row
        (args.out / 'snapshots.json').write_text(json.dumps({'peak_memory_tested': False, 'physical_device': False, 'stages': rows}, indent=2) + '\n')
        print(name, row, flush=True)
    if 'INSTRUMENTATION_RESULT: outcome=' in log:
        break
    time.sleep(.25)
missing = sorted(set(markers) - set(rows))
print('Missing stages:', missing, flush=True)
