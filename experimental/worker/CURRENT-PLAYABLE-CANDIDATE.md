# Current experimental worker candidate

Based on public 87811c52cdb9aecd13cd23beebd52f6475c6dd9c, including reviewed Newfoundland 3D and current freight/import/transit freshness fixes. Native Java remains identical to public 87811c/01eeda. Production activation is disabled; normal synchronous startup remains available.

The static registry has 82 operations:34 civic,22 land and26 transit/freight, with 93 bindings. Terminal family sources 9ab9166 and6702b498 are composed. This count is a finite implementation inventory, not universal acceptance. Civic actual UI compares 23 complete model/RNG states without exclusions. Terminal family receipts remain available; some older transit runners omit visual metadata and must not be described as complete visual parity. The transport-alias and funded land completion gates retain every field.

## Build and startup

Run `python tools/assemble.py`, then `WORKER_PAID_COMMAND_OWNER=1 NODE_PATH=/workspace/Village-worker/experimental/worker/node_modules node experimental/worker/build.cjs` (or install the pinned experimental package dependencies normally). Inject generated `real-view.generated.js` inside the game closure before 99-instrumentation. It includes the finite default route bindings. The build artifacts are ignored; record their SHA256 for each native/composite test.

Call `__workerRealView.enable(workerSource, null, {realtime:true,startPaused:true,initializeAuthority:async ask=>{const result=await ask({type:'initialize-command-owner'});if(!result.ordinaryDayReady)throw Error('Owner unavailable');}})`. Use null only before a town exists; an existing town requires its committed archive. The actual founding, Continue, import and export UI uses retained asynchronous ownership and original durable writers. `debugControls:true` exposes diagnostic buttons; default startup has only nonintercepting pending status and fatal saved recovery. Tests must use original player controls for acceptance.

One model/RNG authority lives in the worker. Command-only transactions snapshot user mutations and preserve rollback; ordinary complete days do not take whole-graph transaction snapshots. Existing creator record caps and completion reservations remain. This is not generic bytes/nodes certification or whole-day atomic rollback. Model confirmation and durable readback/ACK are separate. Unsupported or stale commands refuse; no host-side optimistic financial mutation is allowed.

## Acceptance and limits

`worker_realtime_player_journey.py` drives ordinary live clock, council, real park/depot/station building, deeds/charters/renewal, bus/elevated networks, paid freight and the actual save/export/import path. The first full run passed 26 checkpoints over 33 live days, raw archive roundtrip equality and an independent full cold public 87811c UI oracle. Observer barriers await real completion and affect elapsed days; this is not a performance benchmark. The final source-matched repeat after pause/debug/3D brush hardening passed 26 checkpoints over 38 live days, with the same complete roundtrip and independent cold-oracle gates.

`test_worker_webgl_road_brush.py` passed actual 3D pointer input: one three-tile root, exact $450 capital charge, preserved total money, stable camera, live graph and canonical durable save. The original debug bar initially intercepted panel-close; diagnostic buttons are now explicit opt-in. Brushes retain world epoch/realm and cannot settle onto a replacement town. 3D transit/cargo actor inspection uses authoritative requests.

`current-realtime-metrics.json` is a short sequential dense 778-person Classic measurement, one sample per mode/rate, not a physical-device claim. At 16×: synchronous 14.92x versus worker 15.01x, RAF P99 266.6/66.7ms, input-next-RAF P95 185.7/37.8ms. At 64×: synchronous 22.51x versus worker 19.13x, RAF P99 416.7/66.7ms and input P95 432.8/27.9ms. Worker maximum frame gap 283.4ms and owed backlog 148.57days remain failures; throughput is not improved at 64×. Different wall-clock blocking gives different completed-day counts, so this does not claim matched deterministic output. Model replay is tested separately.

Remaining gates: independent whole-control/realtime review, supported native arithmetic/runtime and actual picker/durable-save/lifecycle acceptance, current combined3D performance and long-session validation. No rollout or physical smoothness claim follows from these desktop results. The synchronous public game remains the release fallback.

Current generated hashes: game f08cdd9cf77bed07c94722995f4e14f45ff6c9a2f85c77406badcdfc13eaa905; worker 70ba7c53ecef1aa5785ddb3fe0b50eb8e96a26db41bf7199eef9a1423fe15b5c; generated bridge 5b1c64909d36bd5b2fb0ca115b836f8a6ae2583b42671622464948b829ae6341. The final journey and 3D brush proofs bind these generated hashes. Fatal-recovery and lifecycle use the same source/model with the handwritten bridge concatenation and record its separate hash.
