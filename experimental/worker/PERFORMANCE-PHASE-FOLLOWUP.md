# Worker phase follow-up

The independently reviewed candidate `a649a55` is unchanged. This branch contains only a presentation-header shortcut and validation reuse inside one original synchronous persistence invocation. It changes no economics, authoritative day work, snapshot contents, command ownership, archive format, pause/backlog accounting or renderer algorithms.

## Measured attribution

A diagnostic 778-person late-town trace uses real pans, a real economy panel and a real Settings save. CPU sampling and function timing add overhead; these are attribution runs, not final performance acceptance. Each run starts from the same generated day-41681 fixture. Variable wall-clock scheduling produces different completed-day counts, so aggregate totals are accompanied by call counts and are not compared as identical economic work.

| Main-thread component | Frozen baseline | Header candidate | Header + save candidate |
| --- | --- | --- | --- |
| Header total / calls | 741.2 ms / 27 | 15.1 ms / 29 | 18.7 ms / 29 |
| Header maximum | 75.2 ms | 0.9 ms | 3.6 ms |
| Synchronous persist total / calls | 320.2 ms / 4 | 336.2 ms / 4 | 260.5 ms / 4 |
| Synchronous persist maximum | 82.6 ms | 88.4 ms | 68.7 ms |
| Ground redraw maximum | 252.6 ms | 264.4 ms | 261.1 ms |
| Draw maximum | 285.1 ms | 299.4 ms | 292.5 ms |

The 283 ms-class frame gap is primarily the synchronous render-quality-transition `drawGround` call, not the simulation worker. Main-thread snapshot staging also costs CPU, but prepareScene was at most 6.8 ms in the baseline. Its last publication at pause took 374 ms wall time to adopt, including the ground redraw. The fixture has climateSeasons:false. The two calls occur on entering 64× fast detail and pausing back to full detail; the final game day also happens to be a monthly boundary, which initially led to incorrect attribution. Ground work remains a renderer-owned follow-up; these changes do not make that maximum disappear.

The baseline worker spent 12.59 seconds inside 229 complete days. Full snapshots cost 998 ms and delta construction 425 ms across 31 complete view publications/replies; postMessage consumed about 175 ms cumulatively. Ordinary save-drain checks cost 2.7 ms across 300 requests. Simulation CPU therefore dominates throughput, while cloning/delta/transfer remains meaningful overhead. No faster 64× claim follows from the header improvement. The earlier dense noninstrumented sample delivered 19.1x worker versus 22.5x synchronous, and remains a failed throughput gate.

## Changes and correctness

The original compact header displays a signal title, active-firm count and project count. Its first four warning branches depend only on already committed food-access, unmet-food, hardship and employment values. They now avoid building the full household/shop demand snapshot. Later branches still call the unchanged full signal function. The original header formatting and refresh logic remain authoritative. Five synthetic presentation branches compare exact displayed headline/detail and unchanged model/RNG. Synthetic inputs are unit-test inputs, not an economic-play claim. Civic full-state parity and the original-controls full player journey also pass for the header candidate.

The original persist function validates the same primary text twice. A temporary two-entry memo reuses validation only for identical text during that single synchronous call, returns fresh envelope objects, then restores the original validator in finally. It retains no cross-call cache. Different/corrupt text is validated independently; asynchronous IndexedDB callbacks and final readback still invoke the original strict validator. Focused tests verify two synchronous validations, corruption preserving the valid backup, exact payload, chronology and a fresh validator call after return. This does not move or weaken the durable ACK boundary.

One attempted save-profile run briefly overlapped a functional runner and was stopped before producing an accepted result. It supplies no performance evidence. The retained combined profile was run alone after functional work finished. Baseline/header/combined raw receipts and source hashes are retained separately.

## Recommended activation policy

Keep synchronous production as the default. Offer worker mode only as an explicit experimental choice after independent current-source whole-control review, arithmetic/runtime checks and native save/load/picker/lifecycle durability acceptance pass. A failed startup guard must leave the original synchronous controls usable; do not override it. An already-owned fatal worker must recover through a fresh realm from acknowledged durable state, never silently resume mutations on a stale host snapshot.

Keep truthful requested/actual speed and owed-days feedback. Do not promise 64× delivery, choose lower requested speed silently, discard backlog, or activate on a renderer-only result. Native/physical smoothness, worker long-session memory bounds and current combined 3D timing remain unaccepted.

The combined candidate also passes actual command-owner fresh-realm fatal recovery, stale replies and failed-write retry. Its source-matched original-controls journey passes 26 checkpoints over 36 live days, complete raw archive equality, full independent public 87811c cold-UI oracle and zero page errors. The generated bridge hash is 1054075b5629040c6552b380d947a2f40b89a31c451c8a953b964d9667ca837f; source and worker hashes remain those of a649a55. This is a separate candidate, not promotion of the frozen review source.

Native owner result: public a649a55 on API30/WebView83 refuses before any worker/command because the arithmetic guard fails; source 102-field cold Continue remains exact in synchronous fallback (dbefead, codex/8-native-worker-runtime-guard-results). This is a successful guard/fallback test, not worker-native durability or performance acceptance. Never override the guard.
