# Shared root transaction/outbox API v1 — disabled experiment

Base `f4f094d5c3bd7fe025a9f2a463fa795f2caf36c8`, source SHA-256 `8be2585815ad9585f3fde86d2fb00909589b44f39956c4faa0e146fe47bb970a`. Next clean integration target is `ca0c6d07af3cdd380aa42b624bb66d95645edfce`; this task did not repeatedly rebase onto moving integration.

`experiments/root-capacity-api.js` is outside src and not assembled. Inject it inside the game closure before 99-instrumentation, after current source wrappers. No production action, tick, enable flag, format or persistence path changes merely by assembling this branch. The shared controller starts disabled and unconfigured. This is a tested mechanism and interface checkpoint, NOT complete day/paid admission, reservation policy or native acceptance.

## Shared interface for automatic-day and paid-command owners

Use exactly one `window.__capacityAdmissionProtocol.shared` controller in combined experiments. `create(hooks)` creates isolated controllers for tests, not one competing controller per actor. Configure while disabled, idle and with scheduled saves drained.

| API | Contract |
| --- | --- |
| `configure(hooks)` | Required hooks: capture, restore, enter, leave, certify, generation, save, onRefusal, onFatal. Only save may be async. Hooks are trusted and synchronous otherwise. |
| `setEnabled(true)` | Requires complete hooks and an initial successful capacity certificate. Does not enable the codec or register actor coverage. Default is false. |
| `run('day' or 'command', work, intent)` | Returns `{ok, joined, value}` on committed work or `{ok:false, reason}` on a known refusal. Nested work joins its existing root; it does not snapshot, certify or save independently. Supported work is synchronous. |
| `refuse(reason)` | Poisons the root and throws a marked refusal. Catching it inside an outer callback cannot turn the transaction into success. |
| `afterCommit(key, effect)` | Presentation-only, synchronous outbox. Equal nonnull keys coalesce to the last effect in their first queue position. Outside a root it runs immediately. It must not contain logical model changes. |
| `requestSave()` | Takes NO payload. It invokes the registered actual saver only after successful root completion, coalescing requests across the current JS turn and checking town generation. Refused/stale requests resolve false. Ordinary outside-root saves dispatch directly with zero capture/certificate calls. |
| `assertIdle(operation)` | Rejects restore/new-town operations within a root. |
| `isActive/isHalted/phase/status` | Read-only protocol diagnostics. A fatal restore failure halts subsequent registered roots and persistence rather than continuing with an uncertain world. |

`ok` means transaction commit, not business approval: a legitimate denied credit decision can commit metadata and return null. An outer paid choice must explicitly propagate a refused operation instead of charging and inferring success from controller.ok. Unsupported/unclassified operations are not automatically granted. `intent` is advisory; no heuristic or arbitrary callback becomes a capacity certificate merely by being passed here.

Every opaque apply callback which may throw must run as joined model work so caught errors poison the outer root. Unexpected work errors restore then rethrow; they are not disguised as success or a capacity denial. Asynchronous model callbacks are unsupported, not sandboxed; do not register functions which schedule later model mutations.

## Hook ownership and certification

`capture` must cover the complete model and all mutable runtime state relevant to the root. `restore` must restore that state with identities and chronology intact. `enter/leave` acquire/release the transaction lock; leave on commit must not overwrite legitimate crew/resource changes with old values. generation is a town/adoption epoch such as saveEpoch, NOT the advancing day counter.

The hook certify returns a synchronous `{ok:true}` or `{ok:false,reason}` for the COMPLETE model including final history/RNG and reservations. Its policy must include pending construction/cargo obligations and future growth; this library supplies no granting policy. The root mechanism currently supports exact-oracle certification; cheap certified headroom/accounting remains a separate required adapter. It never performs a hidden serialization itself.

`graphSnapshot/graphRestore` are identity-preserving journals for audited data roots. They handle shared references, cycles, sparse arrays, exact own-key order/descriptors, Map/Set entries, Date values and typed-buffer bytes. They preserve quoted G/entity references on refusal instead of hydrating a replacement world. No hydrateSave is used for rollback. Unsupported accessor/custom-prototype/non-extensible mutable objects refuse snapshot preparation; opaque DOM/audio/native resources require separately audited scalar/runtime hooks, not traversal. Frozen containers can retain mutable children, whose data is journaled. Irreversible property changes after capture are unsupported engine work; a failed restore halts the protocol and requires recovery from a verified complete save.

`captureArchiveRuntime` alone is NOT a model or command undo. A real adapter may journal G plus its mutable data roots and capture other audited scalar/UI references, then restore both. Do not reset adoption caches at day entry: preserving oracle cache behavior and logical RNG ordering is part of acceptance. The library is not a sandbox for arbitrary impure callbacks or external side effects.

## One I/O fence, installed once

`installFences(shared)` captures the current final save/archive/import/seed entrypoints, configures the underlying saver, and returns a bridge. Install after all current wrappers and before enabling. Do not add competing save/export wrappers in day and command experiments.

- save requests during a root queue a saver function, never a partial payload. The actual save runs in a microtask after the synchronous caller/outer busy flag finishes, checks the adoption epoch again, and coalesces same-generation requests.
- archivePayload refuses partial exports and poisons the root, even if a caller catches the error. hydrateSave/seed refuse nested lifecycle changes before their work.
- `bridge.serializeCandidate()` exposes the captured serializer only for a completed certification phase (or complete idle state), not inside model work.
- fence removal requires a disabled, healthy, idle controller with scheduled saves drained, and verifies no other owner replaced the entrypoints.

Captured aliases or unregistered external mutations can bypass any wrapper. Coverage must be audited before activation. This prototype does not claim every native/UI path is already fenced. Storage failures after a successful model commit remain persistence failures, not permission to undo published financial effects. Presentation-only outbox errors likewise do not roll back an already committed model; they are reported separately.

Logical modal/inbox state must be prepared during model work. In particular showCustomEvent also sets pendingEvent/councilInbox and can save; do not defer that entire function as though it were paint-only. Paid-choice refactoring and the automatic-day adapter must separate these effects and preserve their ordering/RNG semantics.

## Executable protocol evidence

`node --check experiments/root-capacity-api.js` and `python tools/assemble.py && python tools/test_root_capacity_api.py` pass. Source and protocol hashes are retained separately because the experiment is unassembled.

The test covers exact journal key order, descriptors, alias identity, sparse arrays, Map/Set/Date/typed buffers and frozen containers; one capture/certificate for joined roots; queued/coalesced completed saves; caught nested refusal and callback exceptions; certificate refusal; async work rejected before capture; stale generation cancellation; irreversible-fault halt; and actual game save/archive/import entrypoint fences. The real-entrypoint witness injects a synthetic model edit, verifies no storage call before final history/RNG, then one completed save. It is not an actual tick/birth/city-economy admission corpus. No native performance or general actor coverage is claimed.

The ordinary save control makes one actual saver call and ZERO captures/certificates. This proves the protocol adds no scans/serialization to ordinary saves; it does not make the underlying experimental codec cheap. Normal source/default flags remain unchanged.

## New negative reservation witness: animation

`python tools/test_visual_archive_headroom.py` proves that a valid synthetic near-limit archive (8,388,592 bytes, 16 bytes spare) becomes unsaveable after ONE actual beginVehicle call. Day, total money, financial RNG, building/person/household/firm IDs and transportNext remain unchanged; one traffic vehicle alone causes the wire-budget exception. The previous complete archive remains recoverable. This is a host synthetic-padding witness, not evidence naturally grown towns have already reached that size.

A current-snapshot-only day certificate is therefore insufficient. The common budget contract must reserve bounded visual vehicle/path/clock/RNG metadata growth, or use an independently bounded lossless visual representation. Do not waive those fields in comparisons or silently drop them. Future reservations must also cover death/departure classification, completion materialization and bounded history. On a genuine automatic-day refusal, restore then pause/drain the frame accumulator so the same failing day is not retried many times inside one frame. Discretionary command refusal need not pause unrelated safe activity.

## Next scoped work

Automatic day/birth/migration integration belongs to the save owner. Full outer paid-choice/construction/completion integration belongs to the independent command owner. Neither should install leaf-only refusal. Both should consume this shared root/outbox API or propose an explicit reviewed change to it before broad integration. No production activation until root financial/world/RNG/history/refusal corpora, reservations, normal-case cost and native validation pass. The older refusal-only paid experiment must not be stacked as a silent child skip inside an automatic-day grant.
