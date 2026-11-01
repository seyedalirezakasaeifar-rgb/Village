# Experimental worker handoff — development only

**Release policy: keep synchronous startup and save ownership as the default.** No worker activation or player-facing experimental option is approved. Current public release base is 72419dc, still synchronous with the independently reviewed header/save backport; the worker model/oracle remains based on 87811c; the independent whole-control correction candidate is `a2f49fbd3994f27042a2c56c34500af80ef7a9c8`. The separate header/save work on 9730423/bc6a174 is not part of this candidate. This document supersedes earlier experimental readiness/count summaries, not their retained evidence.

## What was tested

| Current candidate evidence | Verified scope |
| --- | --- |
| `audit-fixed-control-comparison.json` | All 15 originally reported enabled buttons produce expected source behavior: manual; food/local-production/export onboarding; programme and supplier/monetary navigation; vacant-land planning; neighbourhood overlay; shopping-centre proposal; waterfront camera/business navigation; borough camera; land-values view; parcel growth outlook. |
| `independent-control-census.json` | Same 2146-control/112-shape census and frozen original regression targets. Three supplier selectors retain their chosen buyer, commodity and producer without authoritative archive mutation. Registration is not treated as behavioral proof. |
| `audit-financial-parity-proof.json` | Sixteen complete model/RNG comparisons against untouched 87811c: inbound food review/payment; vacant-land tool/quote/payment; mall review/private investment; growth report/site selection/actual cottage purchase; buyer/commodity/producer selection; selected supplier agreement quote/payment; malformed selection refusal. Zero excluded fields. |
| `realtime-player-journey-proof.json` | 26 actual-UI checkpoints over 46 live days: import; requested speed/live 8×/16x; council; real park/depot/stations; deed/charter/renewal; quoted-bus cancellation and construction; suspend/resume; elevated line; freight priority/paid shifts/agreement/cargo inspection; fleet retirement; presentation settings; save/export/import. Raw archive roundtrip and complete independent cold 87811c UI oracle match, with no page errors. |
| `fresh-recovery-ui-proof.json` | Actual command-only owner, no reference owner; failed paid write remains unsaved; retry does not repeat payment; saved-state recovery uses a fresh realm; stale replies/clients reject; owner reinitializes; ordinary failed-day restore remains distinct from fatal-root recovery; coldContinue and IndexedDB-only discovery pass. Faults are diagnostic injections, not ordinary player actions or native acceptance. |

The mall’s positive correctness case uses the preexisting controlled source-unit fixture that adds household members before published population rolls forward. It is deliberately synthetic, without an organic-growth or performance claim. Other targeted cases use generated founding/day 1081 QA towns. No macroeconomic recovery was forced. Functional observer barriers and concurrent work change elapsed days; these receipts are not timing benchmarks.

Older land/transit/civic/3D and lifecycle receipts remain in history. Some older transit runs excluded visual metadata; they must not be described as whole visual-state equivalence. The current targeted financial proof has zero exclusions. This candidate has 96 registered operations and 112 bindings, which is an inventory, not all-game acceptance. Seven census shapes remain statically unclassified in the retained owner receipt: existing agenda navigation, two service-budget inputs, music volume/mood and renderer/quality selects. The parent now reports independent host review 4fb183d726888bc8ec09ccd1632d534e97b46be9 accepts those seven inputs together with all 15 corrected buttons/three selectors and the broader census. Static classification was not changed to manufacture that result. This is bounded host acceptance, not a universal or native certification.

## Independent host acceptance update

The parent reports review 4fb183d726888bc8ec09ccd1632d534e97b46be9 accepts unchanged code candidate a2f49fb: 15 reported buttons, three supplier selectors, broader census/seven inputs, a separate 26-checkpoint/41-day journey with full cold replay, 16 financial parity checkpoints, recovery and actual 3D roads. No host blocker was reproduced within that scope. The reviewer’s runtime/artifact hashes and full receipts remain with that owner; this handoff records the parent’s confirmed outcome. No release activation follows. Native worker durability and sustained performance remain open.

## Exact artifacts

| Artifact | SHA256 |
| --- | --- |
| Normal assembled `assets/game.js` | `f08cdd9cf77bed07c94722995f4e14f45ff6c9a2f85c77406badcdfc13eaa905` |
| Generated worker | `7a19e5e45960030f1d7c5637e7a6b1b5f1f9373f6c43f6ff65790fccb1ce7b53` |
| Generated combined bridge | `d56223f2d6c9a5e61b82c3130c8eb54da1ec5d5f8a22055d8f37416dd381c3f8` |

Native Java, normal assembler, release packager and default save owner are unchanged from the candidate’s frozen base. Generated outputs live under `experimental/worker/`, are ignored by git, and are not included by the normal `src/*.js` assembler or assets-only APK packaging. Separate release-exclusion evidence on bc6a174 confirms zero workers/endpoints and original save/native dispatch without injected experimental code. Final packaging must still inspect the actual APK; no experimental bundle should be copied into release assets.

## Reproduce only in development

From the experimental checkout:

```sh
npm ci --prefix experimental/worker
python tools/assemble.py
WORKER_PAID_COMMAND_OWNER=1 node experimental/worker/build.cjs
```

Do not select `WORKER_PAID_TEST_OWNER`, copy a reference owner, change WebView security flags or alter arithmetic. Serve a separate local development page/test route. Its in-memory game response must insert generated `real-view.generated.js` **inside the game closure immediately before** `// SOURCE: 99-instrumentation.js`. Do not append it outside the closure or overwrite the release asset. The generated bridge includes all finite family bindings; the three handwritten bridge files alone are for separately labelled isolated tests.

On a fresh development page before a town exists, use the locally generated worker text:

```js
window.devWorker = await __workerRealView.enable(workerSource, null, {
  realtime: true,
  startPaused: true,
  initializeAuthority: async ask => {
    const result = await ask({type: 'initialize-command-owner'});
    if (!result.ordinaryDayReady || result.authority?.referenceTestOwner) {
      throw new Error('Command-only worker authority unavailable');
    }
  }
});
```

`null` is permitted only before a town exists. An existing town requires its acknowledged committed archive and the normal epoch/adoption barrier; never adopt a mutable in-flight host object. Initialization is retained for actual founding, Continue, import and fatal recovery. `debugControls:true` exposes diagnostic buttons only; acceptance tests use the real player controls. The nonintercepting pending status and fatal saved-state recovery remain visible without those buttons.

Useful bounded checks are `audit_fixed_control_comparison.py`, `audit_financial_parity_test.py`, `independent_control_census.py`, `fresh_recovery_ui_test.py` and `worker_realtime_player_journey.py`. Build artifacts must match the hashes above. Each evidence file states its exact source/worker/bridge or diagnostic fault suffix. Do not run timing measurements alongside functional runners.

## Unfinished acceptance and known limits

- **Native runtime/durability:** parent’s API30/WebView83 probe rejected arithmetic admission before Worker creation; synchronous coldContinue matched 102 fields. This certifies guard/fallback behavior, not worker save/load picker completion, process-death durability, lifecycle, rendering or performance on a supported native runtime. Never override the guard.
- **Throughput:** the earlier dense 778-person short sample delivered 19.1x in worker mode versus 22.5x synchronous at requested 64×, while input P95 improved 433→28 ms. Retained backlog reached 148.57 days. Requested/actual speed and owed-days must remain truthful; no dropped work or silent lower-speed setting is approved.
- **Main-thread hitches:** roughly 293 ms draw gaps remain at entering fast 64× detail and pausing back to full detail. The fixture had seasons disabled; this was not a monthly scenery attribution. Renderer ground rebuilds remain a separate issue. No claim of smooth 64× or physical-device certification is justified.
- **Memory and graphics:** current worker long-session heap/cache bounds and combined 3D performance are unaccepted. Main-thread observations do not bound worker heap.
- **Transaction scope:** one authoritative model/RNG and command-only paid roots are implemented; ordinary complete days do not take whole-graph rollback snapshots. Existing person/household/firm creator caps and completion reservations remain, but there is no generic bytes/nodes certificate or universal whole-day atomicity claim. Archive schema 8 remains unchanged.
- **Recovery:** a startup refusal must preserve usable synchronous controls. Once worker ownership has begun, fatal recovery must load acknowledged durable state in a fresh realm; it must not resume financial mutations on the stale host snapshot. Model commit is separate from durable writer/readback acknowledgement.

Do not expand features or activate by default. Fix only a bounded reproduced defect reported by independent review, preserve its negative evidence, and rerun affected exact-source gates. The parent owns whether this stays on a branch or becomes an optional development build.
