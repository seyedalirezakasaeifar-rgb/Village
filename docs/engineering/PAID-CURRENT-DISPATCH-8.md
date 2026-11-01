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

Supported DTO kind is currently council-choice only: authored council choices plus the explicitly registered current bridge build/repair/decommission and street retirement reviews, prior registered deed/named construction choices. Unsupported custom choices still refuse. This is NOT a general callback transport or a claim of complete101-handler routing. Existing construct/policy worker commands can invoke their actual functions inside the same owner's root; further DTO kinds require an explicit shared contract, not a second financial implementation.

## Current road operations

Bridge and removal source choices receive explicit model-only road command descriptors. Their existing commit/repair/decommission/retire functions remain the only payment/geometry algorithms. Source callbacks now return their actual result so failed/no-op/stale operations refuse the whole outer root instead of committing a closed modal or charging partial work. Zero-cost structurally sound repair refuses. Generic PUBLIC WORKS/BRIDGE WORKS choices retain current council journals/settlement; direct CIVIC PROJECT street retirement retains its current direct settlement path. Cancel choices retain current behavior.

Current plain streets already recompute/save on repair; current public transit construction already initializes systems/finance/market. Those current defaults are preserved. Housing-retention c.validate and inbox titles are preserved; enabled paid dispatch runs validation within the shared root. Failed-day flags are never cleared by a paid action. The current bridge/removal guard still rejects simulationTickActive/Failed. Recovery/new-town/import remains with current original owner/fences.

## Evidence scope / production blockers

`tools/fixtures/current-paid-owner.js` is explicitly a HOST TEST OWNER. It tests one shared controller, registered rollback and injected reservation refusal on current source; it does not implement the admission owner's normalized-capacity reserve or certify production composition. Actual accepted operations are passed through current hydrateSave and normalized export twice, comparing fixed points and completed-day payment evidence. No legacy codec is added or limit raised.

`python tools/assemble.py`; `python tools/test_current_paid_roads.py`; `python tools/test_current_paid_direct.py`. Current vanilla road bridge/removal and council regressions are separate controls. Host tests are not Android, native lifecycle, worker/save ACK, capacity-reserve or performance acceptance.

Actual production composition is pending: published automatic-day686ae40 depends on older experimental codec/prepareArchiveCandidate helpers absent in d2b7086; it must be ported by its owner without replacing current retention/receipts. Worker current90544529 and its native/save ACK protocol must be assembled and jointly tested with this exact layer and an approved admission owner. This branch keeps all experiments disabled and leaves source defaults unchanged.
