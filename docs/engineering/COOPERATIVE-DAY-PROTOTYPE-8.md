# Experimental cooperative day controller

Model base `662ec6f3b0998ce3c3c560d5bef39e4e17a4bcc1`, reconciled with compositor/district integration `cc8631158cb004a8e4c26dead85df66f6b4468e8`. This is an opt-in prototype, **disabled by default**, with no saved preference, archive-schema change, Worker or new game mode. Do not turn it on for a release until combined native and adversarial acceptance is complete.

## Interfaces for persistence and UI owners

- `cooperativeDayBusy()` identifies an incomplete day. The existing `simulationBusy` flag is also held true across the whole continuation and restored before commit effects, so separately scheduled presentation/serialization tasks can retain their existing guard. Code must not read its partial `G` for presentation or persistence.
- `afterCommittedDay(fn)` returns a promise and runs `fn` at the completion barrier. Deferred work from a replaced town resolves false. `save()` uses this barrier, then the existing chronology/storage path unchanged.
- `finishCooperativeDaySync(reason)` finishes the current continuation, invalidates its scheduled task token and publishes a completed day. Synchronous archive export/import/founding and native suspension use this exceptional barrier. This may block briefly; it is not a promise of low-latency export or suspend.
- `setCooperativeSimulation(enabled)` changes the experimental flag at a completed-day boundary. Public test/diagnostic access is `window.__cooperativeSimulation.enable(enabled)`. There is no normal settings toggle.
- `window.__cooperativeSimulation.command(label, fn)` queues a model command at commit and returns its result. The callback must use the existing authoritative validation/transaction function. This is a main-thread interface, not serialized code or a Worker protocol.
- `window.__cooperativeSimulation.status()` exposes enabled/busy/displayed header day/last committed day/working day/stage/queue/token; `.samples()` supplies bounded diagnostic measurements. `.finish(reason)` is an explicit synchronous barrier.

`tick()` and `outwardMigration()` retain their original synchronous implementations as the default path and equivalence oracle. `stagedTick()` preserves their exact call order. The staged migration implementation preserves the complete filtering pass, then the assessment pass, final sort and random-departure sequence. It yields between households, not within an individual assessment.

A MessageChannel task continuation runs until its approximately 4ms deadline at a yield boundary. This is a soft bound: an unsliced function can overrun it. Daily economy, systems work and private investment are still atomic in this first prototype. There is no microtask-based pseudo-yield or reliance on APIs newer than the existing WebView floor.

## Committed view and input

The frame controller presents completed state before admitting another experimental day. During an incomplete day it suppresses existing model-reading map/header/panel/traffic updates. Final wrappers also defer rendering/audio refresh/toast calls made from inside economic functions. A banner explicitly identifies the working day, last completed day and queued input events; the header retains its ordinary refresh cadence.

Pause has immediate clock-control feedback while the current day finishes. Pointer pans preview a translation of the previously completed canvas; the renderer never reads partial accounts for that preview. Model-facing clicks/input/change/map gestures/Escape are captured and replayed in order after commit through existing handlers. Native focus, text editing and slider default behavior remain available. A proposed policy input marks Enact as queueable; its normal budget/policy validation runs after commit. A vanished, disabled or town-replaced target is explicitly declined with a renewed-review message. Replay diagnostics mean an event reached its handler, not that its requested purchase was accepted. Existing route/land/cargo quote guards remain authoritative.

A day is not admitted while a map gesture is already active. Queued gestures can complete before another day starts. On import/founding, the preceding day finishes, already queued actions are settled against their original town, and old continuation messages become inert. Native Back finishes the current day before returning the real navigation result to Android; it never claims a queued dismissal already happened. Exit preparation waits for commit and then uses the existing save protocol. Native suspension/document unload also use synchronous completion, since an activity may immediately stop running JavaScript.

## Failure and rollback

Before a staged day, the controller captures one completed snapshot, including model RNG and current visual transport archive data. It also retains market-open state, construction crew allocation, civic candidate sets, transit reservation generation and migration session diagnostics; these are mutable simulation state outside `G`. That serialization has a real cost and is included in staged-day CPU measurements. A stage exception restores the snapshot, invalidates derived road/transit ownership, pauses the simulation, disables the experiment, rejects command/save promises and explicitly reports declined queued inputs. No half-day snapshot becomes an autosave. Rollback restores those mutable transients and discards derived caches; persisted economic state remains the recovery authority.

The simplest rollback is to leave the default false or call `.enable(false)` at a completed boundary. The synchronous engine remains available without an archive migration.

## Scope and remaining acceptance

The generic input fence and final function wrappers are deliberately isolated prototype hooks. They require native touch, text/slider, keyboard, audio-gesture, document-picker, Back/exit and lifecycle testing before enabling in production. Synchronous explicit interruption barriers may still incur a long task. Snapshot preparation, unsliced economic work and map publication remain measurable main-thread costs. No guarantee of 64× throughput or physical-device smoothness follows from host tests.

Tests and measurements will be recorded against the exact assembled source hash. The first acceptance target is exact archives/RNG and command ordering, then truthful committed-state barriers and trusted-input latency. Presentation/persistence optimizations outside these barriers remain with their respective owners.

Periodic presentation candidates `9c9f9c0`/`b2af737` were not available as fetchable remote refs during this checkpoint; no blind merge was attempted. Their reported epoch/town/focus/`simulationBusy` guards are compatible with the flag above, provided every deferred task rechecks at execution time. Tasks must neither clear that flag nor serialize `G` while it is true. The explicit commit callback is the safe admission point for missed periodic work. The current compositor is covered by the final draw wrapper; no compositor/district ownership changes were made.
