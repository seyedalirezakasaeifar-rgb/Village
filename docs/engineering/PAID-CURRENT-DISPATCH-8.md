# Current-source shared paid dispatch — disabled

Base d2b7086187621ae8c3c147fc3c04764efaadf49d; branch codex/8-paid-controls-current. This ports the earlier paid layer without importing its obsolete production archive/codec files. Current completed-day serviceCashEvidence, retention validation/fence and construction initialization remain owned by current public source. No startup enable flag or native bridge is changed.

## Worker interface available now

Inject `experiments/root-capacity-api.js` (unchanged shared API4ee829c), configure the single `__capacityAdmissionProtocol.shared` through the admission owner, and call `__installPaidCommandLayer(ownerAdapter)` while disabled/idle. There is no second controller.

`ownerAdapter` supplies `shared` and `registerRuntime({capture,restore})`; metrics() is optional. Every registered capture result must be a root in the owner's single graph checkpoint; graph contents restore BEFORE registered restore(), and then the owner's leave hook runs. Paid registration covers current model/runtime/cache/UI references, current bridge cache, failure/busy/save-after-tick flags, road paint/input state and opaque DOM opener. It does not own transport anti-replay state. Worker runtime/outbox registration must occur on this same owner before activation. Neither the old adapter's minimal-owner proofs nor current host test owner prove production composition.

Synchronous model-side call:

```js
__rootAdmission.dispatchSerializable(
 {version:1,kind:'council-choice',requestId:42,epoch:3,reviewToken:7,index:0},
 {requestId:42,epoch:3,reviewToken:7}
)
```

The second object is trusted admission context derived from the worker's current admitted envelope, current adoption epoch and current worker-local review serial. NEVER echo context from the packet. Request IDs are positive safe integers, epochs nonnegative safe integers, review tokens positive safe integers and choice indices nonnegative safe integers. The owner permanently consumes/checks command IDs BEFORE dispatch, including on refusal. Paid dispatch does not introduce another request counter or roll back anti-replay/native correlation state.

The worker creates/retains its OWN pendingEvent from the same current source. Its response/outbox sends labels, index, epoch and review token only. Packet selection resolves the worker-local choice/callback, then runs the existing shared financial dispatcher. Town references and callbacks in source-local quote objects NEVER cross structured clone. Wrong identity/epoch/review/index, missing pending review and disabled admission reject without applying a choice. Existing current validators and commit quote keys run again; stale condition/cash/network/retention and creator refusal poison the containing root.

Returns a plain cloneable result with ok/reason, requestId/epoch/reviewToken, joined/provisional and publicationErrors. If called inside the owner's outer command root, joined/provisional is true: the owner MUST withhold response, snapshot, outbox and persistence until that outer root finishes. A joined result is not a commit acknowledgement. Presentation errors cannot negate an already committed financial result; report them separately. Existing worker save prepare/owner-write/ACK and native asynchronous callbacks remain owned by their respective owners.

Supported DTO kinds are council-choice and private-provider (specified below): authored council choices plus the explicitly registered current bridge build/repair/decommission and street retirement reviews, prior registered deed/project construction choices. Named-place and other unsynchronized form-input choices are not admitted by this DTO path: index-only packets cannot carry a user-entered name, so the worker must block them until an authoritative field protocol exists. Unsupported custom choices still refuse. This is NOT a general callback transport or a claim of complete101-handler routing. Existing construct/policy worker commands can invoke their actual functions inside the same owner's root; further DTO kinds require an explicit shared contract, not a second financial implementation.

## Current road operations

Bridge and removal source choices receive explicit model-only road command descriptors. Their existing commit/repair/decommission/retire functions remain the only payment/geometry algorithms. Source callbacks now return their actual result so failed/no-op/stale operations refuse the whole outer root instead of committing a closed modal or charging partial work. Zero-cost structurally sound repair refuses. Generic PUBLIC WORKS/BRIDGE WORKS choices retain current council journals/settlement; direct CIVIC PROJECT street retirement retains its current direct settlement path. Cancel choices retain current behavior.

Current plain streets already recompute/save on repair; current public transit construction already initializes systems/finance/market. Those current defaults are preserved. Housing-retention c.validate and inbox titles are preserved; enabled paid dispatch runs validation within the shared root. Failed-day flags are never cleared by a paid action. The current bridge/removal guard still rejects simulationTickActive/Failed. Recovery/new-town/import remains with current original owner/fences.

## Evidence scope / production blockers

`tools/fixtures/current-paid-owner.js` is explicitly a HOST TEST OWNER. It tests one shared controller, registered rollback and injected reservation refusal on current source; it does not implement the admission owner's normalized-capacity reserve or certify production composition. Actual accepted operations are passed through current hydrateSave and normalized export twice, comparing fixed points and completed-day payment evidence. No legacy codec is added or limit raised.

`python tools/assemble.py`; `python tools/test_current_paid_roads.py`; `python tools/test_current_paid_direct.py`. Current vanilla road bridge/removal and council regressions are separate controls. Host tests are not Android, native lifecycle, worker/save ACK, capacity-reserve or performance acceptance.

Actual production composition is pending: published automatic-day686ae40 depends on older experimental codec/prepareArchiveCandidate helpers absent in d2b7086; it must be ported by its owner without replacing current retention/receipts. Worker current90544529 and its native/save ACK protocol must be assembled and jointly tested with this exact layer and an approved admission owner. This branch keeps all experiments disabled and leaves source defaults unchanged.

## Additional model-safe provider DTO

```js
__rootAdmission.dispatchSerializable(
 {version:1,kind:'private-provider',requestId:43,epoch:3,providerKind:'school'},
 {requestId:43,epoch:3}
)
```

providerKind is school or fire. No pending review may exist. It shares the same privateInvitation function as the actual panel click, including the increased-construction-spending-without-project refusal. Success and a creator returning null after payment are both covered by current host DTO tests. It does not transport source callbacks. Automatic investment still belongs to the day owner and must independently poison its containing root on creator refusal.

## DOM-free worker adapter requirements

Worker90544529's generated source includes the economic globals, but its adapter has no DOM. Define `globalThis.window=globalThis` (namespace alias only), keep source-local pending choices in the worker, and override these presentation boundaries before installing paid wrappers:

* `closeCouncilDialog(defer)`: call the new pure current-source `closeCouncilDialogState(defer)`; reproduce any active-agenda invalidation and request save; append semantic council-close to the registered worker outbox. Do not call the browser project-survey wrapper or invent another inbox algorithm. The helper preserves current housing-retention inbox behavior.
* Existing toast/updateHeader/renderPanel/showCustomEvent/save overrides remain semantic worker/outbox functions. playSfx must also be an explicit worker-local presentation hook, not the original Audio/document implementation. Worker review creation uses current source review functions (reviewRoadBridge, reviewBridgeRepair, reviewBridgeRemoval and reviewRoadRemoval; structural review is extracted intact from the source button handler and reused by that handler).
* `ownerAdapter.deferDOM()` is an optional synchronous semantic view-invalidation hook. When supplied, paid `deferUI` queues this hook after root commit instead of executing opaque browser focus/scroll closures. Failure discards it. No closure is posted to the main thread. Without it, ordinary browser behavior remains unchanged.
* Browser openPanel must be replaced by the worker's logical active-panel/outbox boundary before any deed/project choice that calls it. Main readonly rendering/panel previews must not silently change worker model RNG. This port preserves the exact current browser render call count; it does not certify headless rendering parity by analogy.

Root registration must include the worker outbox, review event serial and provisional save state as described by worker CURRENT-SOURCE-ROUTING.md. Admission epoch/consumed request sequence/native request correlation are NOT rollback fields. The worker's old hand-written choice settlement must be replaced by this dispatcher, never run before or after it. A joined result is withheld until the single owner root succeeds. These are concrete integration requirements, not a production acceptance result.

The current direct-dialog tail deliberately does not add the generic council's extra active-panel render: day2 agenda previews consume model RNG in current source. The port originally found971 versus1456 preview RNG calls for named-place commit; restoring the original direct path's call count restores full model/RNG equality. No RNG reset/filter or discarded archive field is used.

Two worker90544529 ordering requirements identified from its published adapter:

1. The shared controller's generation hook must use the worker adoption epoch (or an owner identity including it). Browser saveEpoch alone does not advance on worker raw load. Epoch and consumed request sequence remain outside registered financial rollback; a new load must invalidate old queued save groups and prepared transport requests.
2. Shared root scheduleSave dispatches the single committed saver in a Promise microtask. The old worker `reply()` takes/splices workerOutbox synchronously inside workerRequest, before its outer onmessage await. That can capture a reply before the current save-request intent exists. After a root finishes, drain committed saver microtasks BEFORE constructing workerSnapshot/reply; do not merely await a reply object already built. The current host harness explicitly awaits the shared pending-save queue and actual writer. It is not evidence this worker ordering is already fixed. Save intent is not a main-store write/ACK; existing owner I/O and ACK remain authoritative.

Selection support is not review/form admission. A family must remain blocked in the worker until its worker-local review creation and any typed fields are DOM-free and tested. Current pure review entrypoints cover the four road/bridge families; project survey forms still require separate worker work. Index-only named-place choices explicitly reject. No main-thread callback or town reference may be imported to fill this gap.
