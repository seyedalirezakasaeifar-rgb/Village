# Disabled realtime and core control checkpoint

This is an isolated extension of published25770f5 on the669c908 economic model. It does not contain public01eeda3 or the separate graphics experiment. Production does not import this worker/bridge. The existing source archive schema, original writer, creator preflight and actual command-only paid owner remain in use; there is no generic byte/node capacity guarantee.

## Startup

Build with `WORKER_PAID_COMMAND_OWNER=1 node experimental/worker/build.cjs` after installing experimental/worker dependencies. Inject runtime-guard.js, archive-endpoint.js and real-view-bridge.js inside the assembled game closure, then call:

```js
const real = await __workerRealView.enable(workerCode, committedArchive, {
  realtime: true,
  startPaused: true,
  initializeAuthority: async ask => {
    const result = await ask({type: 'initialize-command-owner'});
    if (!result.ordinaryDayReady) throw Error('Automatic creator scope unavailable');
  }
});
```

Without `realtime:true`, the prior paused integration contract remains. Runtime arithmetic admission is unchanged. No native WebView security setting is changed. Main-thread synchronous debug mutations still refuse.

## Clock and ownership

One authoritative complete day runs per request. Requested active wall time accumulates as owed days without a backlog cap or simulation-work discard. User pause, visibility/native suspension, council review and restore explicitly interrupt admission; a previously admitted complete day may finish. Already owed days remain when paused. Commands/save work can delay simulation and that time continues to accrue honestly. The HUD shows requested speed, delivered rolling wall rate and owed days. The real pause button, clickable speed label and range route safely; speed is persisted only by the worker.

A bounded16-command queue gives user commands priority at complete-day boundaries. Paid requests show immediate queued/pending feedback and reject duplicate concurrent paid submissions. Pre-admission stale epochs refuse. Once admitted, actions cannot be falsely cancelled. Clock stepping and snapshot publication are separate: the worker can advance complete days while main stages an older complete view. A model command waits for in-flight day and view adoption before dispatch. Ordinary failed-day and fatal-root recovery modes remain distinct. Fresh saved-realm recovery explicitly pauses and clears the abandoned world's owed work.

## Complete views and effects

Publications are at most twice a second while advancing, with additional committed publication for a council interruption or explicit barrier/command. Each publication is the complete canonical JSON model, encoded as a full view or a sequence-bound structural delta. Changed record rows travel intact; dense primitive arrays travel intact. No financial/history field is projected away. Main reconstructs/finalizes a new immutable view in approximately3ms staging tasks and only then swaps the view. Old complete views remain visible meanwhile. A mismatched base requests a full publication; malformed/stale local application stops the experiment.

Effects retain the existing epoch/serial outbox ACK. Exports do not consume effects. Canonical explicit export/save still requests the complete authoritative committed model, independently of presentation cadence. Original save writes and token ACK ordering remain; advancing days keep `unsaved` true until the pinned revision is saved. Rendering/traffic uses complete views only; visual session traffic is not authoritative financial state. Native persistence and visual save continuity are not certified here.

## Core routes added

The same paid root now handles finite `panel-control` DTOs for enactPolicy, borrow, repay, toggleDevelopment and ambition; and `construction`/`road-stroke` DTOs for map placement, repair and bounded road gestures. There is no eval, source callback or competing root. Actual original model bodies are shared through DOM-free helpers. Paid roots retain graph/runtime rollback, cash conservation, current validators and creator guards. Refused construction/payment restores model/RNG and emits no success/save effects. A road gesture collects only coordinates on main; one bounded paid root performs its actual road algorithm. A pointer cancellation before admission buys nothing.

The coverage file records35 retained/new semantic identifiers and51 pending operations. These are not comparable to a coverage percentage of the101 raw handler entries. Pending operations include all custom review families, district/land/renewal, bridge/removal, public projects, route operation, freight/contracts, gathering review and native acceptance. They continue to refuse visibly; full playable routing is not complete. See control-coverage.json for exact names.

## Evidence and failed gates

`test_core_actual_ui.py`: ten trusted actual game actions (borrow, repay, development toggle, ambition, enact, park/home/firm placement, repair and road gesture) match unchanged669c908 complete model/RNG after each action. Both sides use the real panel and canvas handlers.

`test_direct_family.py`: six operations against unchanged669c908 original UI bodies, exact complete model/RNG, five invalid/no-op DTO refusals unchanged. `test_construction_family.py`: original park/home/firm/repair/road-stroke algorithms, exact complete model/RNG, four invalid/occupied refusals unchanged. Fixture site selection preserves test RNG; it is setup, not an omitted player action. `test_view_delta.cjs`: arrays, deletion, type replacement, structural sharing and immutable predecessor.

`test_realtime_lifecycle.py`: delayed real completed-day replies, immediate queued pending UI, duplicate refusal, pause/backlog, actual council/defer, actual speed label/range, synthetic page visibility and original committed writer. Synthetic visibility is not Android acceptance. Existing fresh recovery and independent paid UI runners retain exact669 oracle and no reference owner.

`test_realtime_view.py` is a short diagnostic of the generated778-resident checkpoint at1/16/64×, eight trusted pans each, complete monthly-boundary model/RNG equality and paused no-drain checks. It is not sustained play or physical-device smoothness acceptance. Negative first/leaf-delta/serial-publication receipts are retained. The leaf encoding generated40,000+ operations and hundreds of milliseconds of staging; row/array encoding removes that waste. Independent publication avoids leaving the worker idle during main staging. A remaining long frame or low actual64× is a failed performance gate, not hidden by a requested-speed label.


Final short matched receipt (`realtime-view-proof.json`):

| Requested | Complete days | Delivered over trace wall time | RAF P99 / maximum | Trusted input→next RAF P95 |
|---|---:|---:|---:|---:|
| 1× | 2 | 0.7× | 33.4 / 100.0 ms | 22.8 ms |
| 16× | 44 | 15.1× | 50.0 / 83.3 ms | 22.9 ms |
| 64× | 69 | 22.2× | 66.7 / 266.7 ms | 22.3 ms |

The roughly4–5second windows include cold first-day work, actual pans and final paused view synchronization; the1× result has only two days and is quantized. They are diagnostic, not a sustained speed guarantee. The64× window retains over100 owed days and a267ms frame gap: **release performance gate fails**. Coarse complete-row deltas reduce changed operation counts from40,000+ to roughly1,300–4,300 per publication; snapshots still cost CPU and memory. There is no claim of a64× or physical-device smoothness pass. Main writer/renderer/GC long tasks still need separate attribution; effects or financial fields were not dropped.
