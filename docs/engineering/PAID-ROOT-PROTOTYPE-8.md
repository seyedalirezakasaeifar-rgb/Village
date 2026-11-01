# Paid-root admission boundary prototype

Base: common disabled codec candidate `f4f094d5c3bd7fe025a9f2a463fa795f2caf36c8`. Assembled source SHA256 `8be2585815ad9585f3fde86d2fb00909589b44f39956c4faa0e146fe47bb970a`. The five paid-core source files (20-world, 40-development, 49-persistence, 70-interaction, 80-civic) match published integration 6c02aad. No production source or enable flag changed.

**Outcome:** direct root refusal is safe and cheap; complete public paid-command admission cannot safely be enabled with the current outer callback boundaries. This is a refusal-boundary prototype plus a concrete minimal refactor contract, not a working grant/reservation provider.

`experiments/paid-root-admission.js` is outside src and omitted by the assembler. The harness inserts it inside the existing game closure immediately before 99-instrumentation, after all current wrappers. It starts disabled. When enabled it intercepts actual construct and the entire completeDevelopmentProjects batch before any model work. A developer-supplied pure read-only callback supplies a refusal reason; grants deliberately remain unimplemented and also refuse. It performs no model clone/rollback, no hydrateSave, no persistence interception or notification suppression. An arbitrary impure callback is not sandboxed or supported.

## Verified boundaries

`python tools/assemble.py && python tools/test_paid_root_prototype.py` passes:

- Actual funded grocer construction and actual funded, ready grocer project completion: six runs each on the baseline and six with the prototype loaded but disabled produce exactly equal full logical model and RNG. Construction crew/visual fixture state is reset explicitly between runs; economic fields are not filtered.
- Both actual roots refuse on a certified initialized near-limit state (about 8,380,416 / 8,380,470 wire bytes). A controlled conservative 16 KiB reservation exceeds remaining headroom. Full G JSON, live RNG, crew state, save chronology, pending-save reference, and all watched persistence/story/toast calls remain unchanged; no success effects occur. This is a controlled refusal policy, not a proved forecast of these operations' actual byte growth. The experiment cannot grant even if a callback returns ok:true.
- The common candidate's pure encodeInactiveLogicalArchive certifies the initialized near-limit fixture. hydrateSave is used only to prepare/import the test fixture before command snapshots; it is never a command/day commit or rollback helper. captureArchiveRuntime is not used as a whole-model rollback mechanism.

The same strict corpus on bare f4f094d (without the experimental root) fails the four external/financial/world gates, as expected because this common candidate has no paid-command admission yet. The receipt is bare-common-negative.json. No expected conservation or committed-state checks were relaxed.

The reused side-effect corpus passes strict atomic mode with this actual root interceptor:

`CAPACITY_EXPECT_ATOMIC=1 CAPACITY_ROOT_PROTOTYPE=1 python tools/test_capacity_side_effects.py`

It checks exact model restoration in the queued-write witness, no partial local/queued IDB payloads, ordered distinct borrow/save/export controls, exact legitimate borrower/world/RNG signature, truthful committed export, and metadata-only credit refusal conservation. This configuration injects the experimental root into disposable pages; it is not the earlier replacement-test-function positive control. IndexedDB/native export remain spies, real localStorage is isolated, and no physical Android result is claimed. Runtime feedback is dispatched only if the refusal actually throws; a normal false return does not invent a runtime-error toast.

## The exact missing boundary

The prototype independently demonstrates both failures in src/80-civic.js:

1. Normal paid choice: the event handler debits treasury before c.apply. A refusing construct callback leaves no property, but the outer handler retains a $1000 debit/regional credit, appends decision records, closes the dialog and performs two save calls.
2. CIVIC PROJECT/direct transaction choice: construct refusal preserves money/world/RNG, but the outer handler still closes its dialog and performs two saves. Root refusal cannot leave pending persistence/UI unchanged while this caller unconditionally publishes effects.

The direct branch closes before calling apply and ignores its result; the normal branch precharges and catches exceptions as ordinary decisions. Calling a leaf or root guard later cannot undo these effects. Existing callbacks are opaque closures, often return undefined, and may capture a quoted town object. Substituting G with an experimental draft can invalidate those quote comparisons; executing the closure against live G and later calling restoreArchiveRuntime is not a model rollback. That helper retains references to mutable maps/arrays and covers adoption runtime only. No such unsafe workaround was added.

completeDevelopmentProjects additionally performs constructionWork/material trades, removes a project and converts escrow before creating a firm. The experiment can safely refuse the entire batch at entry. It cannot safely certify/commit individual completion grants while allowing nested creation, payment or save calls to commit separately. Date advancement and other daily work belong to the owner's automatic-day root, not this paid-command wrapper.

## Minimal shared transaction/outbox refactor

1. Give paid choices explicit operation descriptors and structured results, starting with construction, rather than opaque apply callbacks for model changes. Review the quote and enter one shared root **before** cost debit or closeCouncilDialog. On refusal return without journal, charge, persistence, dialog-success or other notification effects. Update civicProjectReviewBuild/Road, publicPlaceReview, district follow-through and brownfield reuse to propagate the same result instead of inferring success from a building search or falling through after false.
2. Split construct into model work and published effects. Model work includes treasury/region, building/firm/household creation, RNG, job/roster changes, recompute, goods books and story/transaction records; all must be represented in the completed candidate. UI/header/toast/save/native export are outbox effects, released only after the common root certifies and adopts the candidate. Keeping history outside certification would undercount archive growth.
3. Treat completion as owned model work under the same root context. Reserve/prepare the full completion before constructionWork consumes materials or the project/escrow is removed. Carry the root token through createFirm, bankLoan and any household additions; nested work must neither certify nor save independently. Automatic-day ownership stays with the save owner.
4. The owner-supplied root context owns candidate model and RNG plus an audited runtime context; encodeInactiveLogicalArchive(JSON.stringify(completedCandidate)) is the certification boundary. captureArchiveRuntime may help adoption cleanup but is not proof of rollback for mutated live state. hydrateSave must never be used for adoption of a paid/day candidate because it normalizes, resets UI and advances save timelines.
5. Flush one committed outbox after adoption. queueIndexedWrite and the synchronous localStorage write must not see a candidate before certification. Refuse unsupported/unclassified paid callbacks while the experiment is enabled; do not grant on a heuristic reservation or catch a refusal as a successful council decision. Production remains unchanged until exact financial/world/RNG/chronology, pending-write, action-order, UI and native tests pass on the common implementation.

This contract lets day and paid-command owners share one root API without creating competing rollback managers. The missing implementation is the shared owned-candidate context/reservation provider and the public dispatcher/result boundary, not an additional leaf count check. No grants were implemented because those boundaries are not yet present.

## Measured costs and limits

Host Chromium only, small six-sample control batches: actual construction median 7.40 ms baseline / 6.65 ms disabled prototype; completion 0.80 / 0.70 ms. These noisy samples are equivalence controls, not evidence of a speedup. A 20000-command no-op entry loop took 5.2 ms disabled and 18.8 ms with a pure refusal callback.

Near-limit root refusal took 0.1–0.2 ms **after** preparing its certified quote/fixture. That preparation took 405–438 ms and includes export, padding construction, import/normalization and pure certification. It is not a measured full admission-provider cost, and must not be hidden behind the cheap entry timing. A real provider still needs a proved cheap ordinary headroom path and bounded exact near-capacity work. No native-performance or peak-memory claim is made.

Receipts: docs/previews/paid-root-common/prototype.json and side-effects.json. Production codec remains disabled and this unassembled prototype is not eligible for rollout. Parent coordination is required for the shared root API and UI refactor; no permissions were denied and no deployment/signing occurred.
