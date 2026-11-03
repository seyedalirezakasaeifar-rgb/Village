# Standalone synchronous header and save preparation candidate

Base87811c52cdb9aecd13cd23beebd52f6475c6dd9c, bundle037c92b56d4b736f2c9c2bb96a950ae194bc815d1a393d36b3634f4272521d94. Candidate bundle3e262a51d4a95992c2b9df3f8205025ffdb1f05d6a5376a528ff75ddceedae8b. This is a separate review candidate; the fallback source/APK is unchanged. It includes no worker code/activation, new renderer behavior, archive format, chronology, durable-ACK rule, economic coefficient, clock/day admission or quality change.

Reviewed upstream provenance:9730423bace3039047a0b5c910e1c461083bc303, implementationb48a001f5a4675d1d4a6ba554bbe6d02ba02c1d3. Upstream modifies only the experimental bridge, so copying its wrapper would not affect ordinary production. This candidate instead makes two isolated source adaptations:

* src/60-renderer.js: compact-header helper uses the same first four warning predicates/order/titles and counts active firms/projects directly. Later warnings still call unchanged marketSignal/economySnapshot. Existing due/key/refresh and formatting logic are unchanged. Full Economy panels still receive the complete snapshot. No cache or model write is introduced.
* src/49-persistence.js: localSaveCandidates accepts an optional strict reader; persistSnapshot supplies a two-entry identical-string validation memo for its own synchronous local reads only. The global readSaveEnvelope is never replaced. Cache hits return fresh top-level envelope objects. Non-string/different/corrupt text still validates normally. All other callers, asynchronous IndexedDB work, corruption checks and later readback use the original strict reader. No memo survives another invocation. Primary reread/write, backup policy, observed order, saveEnvelope fields and queue completion remain unchanged.

## Paired real UI measurement

Same generated778-person/day41681 fixture (833afee35aa714919a38e420e74cee1f719315db; decompressedSHA256ad6256fd85d4146fda9eeac0b16d5b182ed352c23bbd96af3b320553c29ce786), two repeats, sequential baseline/candidate runs with no concurrent functional runner. Actual synchronous RAF, trusted pans, Economy, Pause, Options and three actual Save clicks; original automatic/pause persistence adds two calls, so five persist invocations per run. Audio stopped. Main-thread wrapper times are inclusive synchronous costs; IndexedDB completion latency is not included in save-preparation time. Same initial town, variable live scheduling; first pair completes116 days each, second116/117. Do not compare different endpoint worlds as identical economic work. These are host diagnostics, not phone/FPS or64× throughput acceptance.

| Repeat | Variant | Header total/calls | Header max | Persist mean/calls | Persist max |
|---|---|---:|---:|---:|---:|
|0|87811c|114.1ms/34|15.9ms|104.8ms/5|203.3ms|
|0|candidate|14.1ms/33|1.0ms|59.18ms/5|69.8ms|
|1|87811c|95.6ms/34|8.7ms|71.86ms/5|76.7ms|
|1|candidate|13.2ms/32|1.0ms|55.92ms/5|60.9ms|

The repeated reductions justify this bounded backport. The worker's741→19ms header result is **not** relabeled as synchronous performance; mutable-source results above are independently measured. No faster64× simulation claim follows. Drawing still reaches278–300ms maxima in these traces; model/ground work and physical-device performance remain separate limits. Prior rejected rent-descriptor experiment9efed5a remains rejected and is not included.

## Functional and persistence gates

* tools/test_sync_header_save.py:15 synthetic presentation cases across seeds42/91/909 compare exact source headline/detail, full archive and RNG. Earlier four branches make zero full snapshots instead of one; later branch still makes one. Valid/corrupt-primary persistence cases prove original validator identity, exact payload, strict fresh post-return readback and preserved valid backup. Two synchronous validations replace three; no cross-call reader shortcut.
* tools/test_sync_header_save_replay.py: settlement42, regional91, regional909 and retained778,180 days each. Complete parsed archives and RNG equal baseline with **no excluded fields**. Candidate restore/replay exact. Cash drift<3.1e-6, max goods error3.66e-8; no resource injections. The retained fixture is synthetic existing public test history, not a user save; no whole archives are published here.
* Strict current-source actual player journey:26 checkpoints over20 live days, zero errors/stale flags, raw archive roundtrip exact and full independent public87811c cold-UI equality. Money drift3.41e-7.
* Existing composite persistence: actual route fares, cargo, provider/mall escrow, atomic invalid-record faults and conserved funds pass.
* Existing storage recovery,12 chronology/failure scenarios and bounded queue pass on localhost HTTP: corrupt-primary backup recovery; newer indexed/local chronology; clock rollback; new-town epochs; invalid import; failed stores; late callbacks; backup quota; legacy migration;41 Save click attempts plus40 direct requests with only two indexed writes.

The three legacy runners initially failed at file:// navigation with browser ERR_BLOCKED_BY_ADMINISTRATOR, before game execution. tools/run_sync_persistence_http.py runs the unchanged case bodies over supported localhost HTTP and creates their expected output directory; it does not change browser security policy or persistence logic. Those original failures and the passing HTTP receipts are retained explicitly. An initial diagnostic profile had an incorrect Playwright route callback signature and produced no accepted timing; it was corrected before the four retained sequential traces. No performance sample overlapped functional tests.

Assembly, node syntax, Python compilation and diff checks pass. Native and assets/index.html are byte-identical to87811c. Native Activity/provider/lifecycle durability and actual phone smoothness are not certified by these host gates. Review candidate only; no integration ref/PR promotion or fallback APK replacement.

Reproduce: assemble; python tools/test_sync_header_save.py; python tools/profile_sync_header_save.py (alone); python tools/test_sync_header_save_replay.py; python tools/test_player_freshness_journey.py --source-file assets/game.js; python tests/test_save_composite.py; python tools/run_sync_persistence_http.py test_save_storage.py (and chronology/queue). Exact source/fixture hashes, aggregate timings, model digests and sanitized logs are under docs/engineering/evidence/sync-header-save/.
