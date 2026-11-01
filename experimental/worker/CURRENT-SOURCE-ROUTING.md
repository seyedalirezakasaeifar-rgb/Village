# Current-source routing checkpoint

Public source d2b7086187621ae8c3c147fc3c04764efaadf49d; branch codex/8-worker-current. Production src/assets are unchanged. The experiment is copied from guarded6ec4713 and rebuilt against current public functions, including completed-day service payment evidence and current construction initialization.

## Finite entrypoint inventory

command-inventory.json enumerates101 actual addEventListener/property-handler bindings with source line, body hash and referenced controls/data attributes. It is reproducible with inventory.cjs. REVIEW_REQUIRED is deliberate: no unreviewed handler is presumed safe. In addition, native callable methods in src/92-government.js (__townArchive suspend/prepareExit/resume/export/restore/back), archive form callbacks, worker enable/load and test instrumentation are explicit external boundaries.

Routing families and current state:

| Family | Authoritative path | Current worker status |
| --- | --- | --- |
| Pointer construction/road paint/repair/facilities | construct and facility functions | single construction/inspect routed; road batching/input coverage incomplete |
| Policy form/package/service authorization/import toggle | enactPolicyPackage | original enact control routed; actual package validation, experiments and journal preserved |
| Council petition review/choice/convene/defer | worker-local choice callbacks and settlement | proof review/choice routed; remaining original controls blocked |
| Explicit/pause/lifecycle/periodic save | original persistSnapshot/saveEnvelope/queueIndexedWrite | original saveNow and save() now route worker prepare → existing owner → ACK; realtime cadence/lifecycle acceptance pending |
| Native export/restore, web pasted import/new-town/continue | epoch admission and archive validation | explicitly reject native synchronous export/restore; other unsupported buttons blocked; complete asynchronous admission pending |
| Camera/selection/panel tabs/draft fields | main view state only | readonly snapshot view; immutable model; UI handler audit incomplete |
| Treasury credit, loans, deeds, roads, transit, private providers, renewal, contracts, cargo, procurement, civic projects/calendar | existing paid decision/root functions | blocked until shared paid-root dispatcher/admission contract is available |
| Preferences/audio/help and keyboard/file inputs | mixed presentation/persistence entrypoints | not yet completely audited/routed; production promotion blocked |

This is not a claim of complete routing. Button capture guards and frozen snapshots do not replace auditing keyboard/file/native/direct G-assignment paths. Unsupported native calls return null/false, and unsupported buttons display refusal rather than running stale model code.

## One persistence owner

The bridge now calls existing persistSnapshot(payload,saveEpoch), with existing readiness promise, chronology/checksum envelope, backup/IndexedDB queue and error result. It does not introduce a second localStorage save path. Worker pins canonical payload/token; main waits for the existing owner result and unchanged timeline before acknowledging the canonical checksum. Concurrent bridge save callers share the same pending promise. load advances the main save timeline only after worker epoch admission. Completed-day paid-service evidence remains in the authoritative canonical payload. Test uses an isolated HTTP origin so no real save is touched.

## Exact integration blockers for paid-root/admission owners

The fetched public source has no published paid-root dispatcher API. Expose one serializable command registry with existing root validation/payment outcomes; worker will invoke that registry at committed boundaries rather than duplicating review/commit logic or inventing competing roots. Define quote identity/stale stamp rules under immutable view snapshots. Current review objects often retain a town object/function closure and cannot cross postMessage as executable commands.

Native restore presently returns a synchronous boolean and export a synchronous string. Worker validation/export is asynchronous. Returning a Promise to that Java call site would incorrectly look like success; this bridge therefore rejects rather than pretending integration is complete. Native/admission owners must provide request ID + epoch + asynchronous completion callback, plus cancellation and failed-restore preservation. Worker raw load is not equivalent to hydrateSave normalization/validation; shared headless validation/founding must be extracted before enabling import/new-town.

No worker startup or mode switch is added to production. Synchronous startup remains the release path until all entrypoints, actual-speed/backlog accounting, durable lifecycle and native arithmetic acceptance pass.

## Alignment with published paid owner7aef91a

Read-only inspection of codex/8-paid-direct-controls confirms shared API4ee829c plus owner.registerRuntime({capture,restore}) is the single controller. root-runtime.js supplies only that registration hook; it creates no root/journal/fence. Its snapshot (outbox array, event serial, committed view version and prepared save record) MUST be a graph root in the owner's checkpoint, with graph contents restored before restore(). Immutable host render snapshots stay outside worker graph capture. Admission epoch and monotonic anti-replay command sequence are not financial model rollback state; they must remain consumed after refusal, and must be managed by the admission owner. Native transport request correlation is likewise outside the root.

The paid layer's actual routePanelControl(event,work)/routeRoadStroke(event,work) currently depend on DOM event/context, so directly invoking them in a Worker is not a serializable dispatcher. Expose paid descriptors with worker-local authoritative review/callback identity and a synchronous dispatcher under the same shared controller; register the worker runtime before enabling or installing wrappers. Automatic tick roots remain the day owner's responsibility. No attempt is made here to wrap async day batches in a synchronous root. The owner is porting bridge/removal controls onto d2b7086 separately; this branch does not modify or duplicate those production changes.

Save owner's unpublished99cc44f/5dbc files are excluded: no read, copy, cherry-pick or publication through this branch. This checkpoint uses only already-public d2b7086 persistSnapshot. Its slow guarded-day mechanism is not stacked into this worker prototype or represented as production acceptance.
