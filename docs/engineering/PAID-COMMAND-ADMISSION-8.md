# Paid commands on the shared root — disabled prototype

Base: `4ee829c731da5f517ebb7a11277fa0691bed2bec` (`codex/8-root-admission-api`). This layer uses exactly `__capacityAdmissionProtocol.shared`. It introduces no second controller, checkpoint engine, save fence or automatic-day wrapper. Both experiments remain outside assembled source. Production has no new activation flag.

## Integration

Inject `experiments/root-capacity-api.js` inside the game closure before instrumentation, followed by a game-hook owner and `experiments/paid-command-root.js`. Call `__installPaidCommandLayer(ownerAdapter)` after the owner configures the common shared API. Its adapter needs `.shared`, `.metrics()` and `.registerRuntime(adapter)`; a configured owner can omit metrics/registry and attach the paid layer without replacing hooks. Do not stack the earlier refusal-only prototype. Nested construction, completion and grant work joins the existing day or command root; it cannot certify or save independently. Unexpected model errors restore and rethrow; top-level public controls show a truthful failure after rollback.

`experiments/game-capacity-root-adapter.js` is a reference hook owner for independent tests, not an approved reservation policy. It captures game/archive/cache runtime and uses the owner's identity-preserving graph journal, leaving opaque DOM references out of traversal. It restores original G, array/entity references, RNG, crew maps, chronology and runtime on refusal. It never uses hydration to commit. Register additional runtime before enabling. A production owner must audit its own complete mutation surface; the reference is not proof that arbitrary callbacks or automatic days are covered.

The reference certifies completed archive encoding and property/identity validity. It requires `certifyReservations({kind,intent,model,encodedBytes})`; without this, activation fails. Explicit `oracleOnly:true` is restricted to tests and proves current-snapshot behavior only. It is insufficient for release. No budget was increased.

## Covered outer commands

* Normal direct construction encompasses original validation, charges, firm/household/building creation, grants/settlement, recomputation, persistence requests and notifications. A stale/unfunded/no-op site refuses.
* The complete development-project batch joins one root, including model/accounting changes and downstream grants.
* Built-in `COUNCIL_EVENTS` choices are selected by actual event/choice identity. Their original paid/free/grant behavior, goods accounting, conserved regional settlement, journal/story/inbox, recomputation and campaign synchronization run before certification. Modal closure, success feedback and persistence publish only after commit.
* The actual civic-project “Commission this exact site” control carries a structured construction descriptor. Town/project identity, blueprint signature, location, price and funds are revalidated inside the outer root. It includes the original construct call, project tracking, prepared agenda and modal/survey cleanup.

Panel markup is prepared during model work because existing panel functions can initialize model defaults. Only DOM paint is deferred. Modal/inbox logical state changes before certification; modal/survey DOM remains intact on refusal. Toast/header/export are publication effects. The common fence queues a save request with NO partial payload; nested requests coalesce after completed root work. Ordinary saves add zero root captures/certificates.

## Explicit remaining boundaries

This is NOT complete admission and must remain disabled:

* Quiet continuous road painting is explicitly refused outside an active owner root. It needs a bounded stroke command including flush/recompute before certification; per-cell certificates or a transaction held across asynchronous gestures are not supported.
* Unclassified event-choice callbacks refuse before charges. This includes land purchase, regional agreements/recovery, district assembly/zoning, brownfield and provider/retail choices until they receive reviewed descriptors.
* Direct custom form/document handlers bypassing eventChoices are **not automatically protected**: project adoption/withdrawal, direct policy/debt actions, transit route edits, logistics settings and other public mutations require registration/audit. A successful ordinary borrow in the side-effect corpus is a recovery witness, not admission coverage.
* Automatic ticks, births, migration, bank/cargo/private-development operations need the owner's whole-day root using the same controller. This layer does not wrap tick. Test-only direct instrumentation may bypass real controls.
* Visual/runtime/lazy-default growth outside a root needs explicit reservations. The owner has a real beginVehicle witness exceeding the byte budget with only16 bytes spare.
* Native aliases/I/O and physical-device memory/latency require independent native acceptance. Trusted callbacks must remain synchronous; this is not a sandbox for arbitrary asynchronous or irreversible mutations.

## Newly reproduced initialization blocker

With oracle-only admission, seed42 grocer construction produces a valid 8,388,480-byte archive (128 bytes below the unchanged8MiB cap); `validateArchiveRecords` passes, but self-import refuses atomically with `lastArchiveCapacityFailure=true`. Removing padding and importing the same valid candidate increases its canonical encoded size by **305 bytes** during normalization. Thus current-snapshot encoding is not an initialization reservation. The corpus retains this failure witness and separately checks a valid near-limit command with4KiB headroom. Do not treat the latter as fixing the former. The initialization/reservation owner must solve this before activation.

## Evidence / reproduction

Assemble with `python tools/assemble.py`; experiments are intentionally excluded. Then:

* `python tools/test_root_transactions.py`: real construction/completion/grant full-model/RNG equivalence; actual paid/grant/project controls; capacity refusal with original references, financial/world state, RNG, chronology, pending writes, modal/survey and notification checks, including original map-survey target identity; graph fault restoration; record boundaries; nested single-capture/single-certificate/coalesced saver; ordinary-save zero-root work; default reservation gate; ghost-property grant rejection; normalization failure witness.
* `ROOT_COUNCIL_MATRIX_ONLY=1 python tools/test_root_transactions.py`: every authored choice through actual modal controls, baseline versus shared-root full logical model/RNG equality, and self-import.
* `CAPACITY_EXPECT_ATOMIC=1 CAPACITY_ROOT_TRANSACTIONS=1 python tools/test_capacity_side_effects.py`: independent storage/native-export/notification refusal and subsequent-action corpus. Fault injection is disclosed; not native certification.
* `python tools/profile_root_transactions.py`: sequential founding and public terminal-day41681 fixture, five runs per ordinary actor. Measures synchronous command and through-committed-saver time separately, checkpoint/model/certificate/restore work, sampled heap (not peak), source/fixture hashes. A near-cap operation may legitimately fit if it shrinks prior visual data; the benchmark records that rather than forcing refusal.
* `python tools/test_root_capacity_api.py`: inherited common mechanism contract.
* `tools/run_http_regressions.py` serves repository fixtures on localhost for legacy file-URL tests when managed Chromium disallows file navigation; it changes only fixture navigation, no test assertions.

Host Chromium only. This prototype is substantially more expensive than unguarded production. Typed-view own-key reflection in graph capture and a second encoding by the committed saver are measured separately; neither was hidden or bypassed. The graph/save owners must review any optimization. Passing atomic scope tests is not an activation recommendation.
