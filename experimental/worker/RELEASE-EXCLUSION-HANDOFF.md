# Release exclusion and ownership handoff

Worker mode stays out of the default release. Public `87811c52cdb9aecd13cd23beebd52f6475c6dd9c` and the normal assets on experimental `9730423bace3039047a0b5c910e1c461083bc303` are tested separately without injecting or evaluating experimental source. Merely retaining this branch in the repository does not install its bridge.

The normal assembler reads ordered `src/*.js` only. The Android packager passes only `assets/` to aapt. Experimental model/bridge outputs are generated under `experimental/worker/`, ignored by git and absent from the default index and game script. No normal packaging or startup path calls the experimental builder, injects the bridge or enables its owner. Java contains optional asynchronous worker callbacks, but the default JavaScript backup/import dispatch checks for an active worker endpoint and otherwise uses the original native methods.

The full committed assets are served unchanged in the browser test. Actual New Town, pause, Settings save, backup and import controls produce:

- Zero Worker constructions and zero experimental asset requests.
- No `__workerRealView` or `__workerArchiveAsync` endpoint.
- Identical original localStorage and IndexedDB save envelopes, with valid format/order/revision.
- Original native write/open dispatch once each; worker export/import dispatch zero times.
- No page errors and valid town accounting.

Native methods in this browser test are counting stubs. This does not certify a native picker, APK binary contents or physical performance. The native owner separately reports that API30/WebView83 refuses experimental arithmetic admission before any worker command, while synchronous cold Continue matches all 102 fields. Its report is `dbefead` on `codex/8-native-worker-runtime-guard-results`; keep that owner’s native evidence distinct from these browser results.

Run `python experimental/worker/test_release_exclusion.py --commit FINAL_COMMIT --output experimental/worker/release-exclusion-final.json` against the exact final source. After packaging, inspect actual APK entries as part of the native owner’s final pass; repository/static pipeline evidence is not a substitute for that artifact check.

## Candidate and remaining limits

Frozen whole-control/native review source: `a649a55ccb752b6f1fd170e9f0689edb92dff34c`. Separate measured header/save candidate: `9730423bace3039047a0b5c910e1c461083bc303`; no routing or activation changes. Its generated bridge hash is `1054075b5629040c6552b380d947a2f40b89a31c451c8a953b964d9667ca837f`. Source/worker hashes remain `f08cdd9cf77bed07c94722995f4e14f45ff6c9a2f85c77406badcdfc13eaa905` / `70ba7c53ecef1aa5785ddb3fe0b50eb8e96a26db41bf7199eef9a1423fe15b5c`.

Native worker durability, actual picker completion, supported-runtime lifecycle and physical performance remain unverified. The arithmetic guard must not be bypassed. Failed startup must leave synchronous controls usable; a fatal owned worker needs fresh-realm recovery from acknowledged saved state, not stale-host mutations.

The short dense benchmark remains a negative 64× throughput gate: worker 19.1x versus synchronous 22.5x, despite input P95 improving 433→28 ms. Requested speed and retained owed-days remain visible. Maximum draw gaps around 293 ms persist at fast-detail/pause-quality transitions; no monthly attribution or smooth 64× promise is justified. Worker long-session memory bounds and combined 3D performance remain unaccepted. Whole-control review is pending independently; only a bounded reproduced defect should trigger further code edits.

Recommendation: synchronous release default. Optional experimental build or opt-in is the parent’s decision after the complete host/runtime/durability gates; no automatic activation.
