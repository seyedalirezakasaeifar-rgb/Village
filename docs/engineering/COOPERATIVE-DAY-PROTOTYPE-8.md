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

## Independent save/native attack contract

Use the test-only hold/pump probe in `tests/test_cooperative_barriers.py` to suspend a real staged day at any named yield. Do not infer completion from the working `G.day`: use `cooperativeDayBusy()` or `afterCommittedDay(callback)`. Attack `save()`, native `prepareExit/suspend/back/export/restore`, valid/invalid import, and storage denial while held; verify acknowledged navigation, canonical saved payload, epoch isolation and inert old task tokens. Resume via the probe or the explicit synchronous finish barrier. Failure injection must preserve both the completed archive and subsequent deterministic continuation.

`tests/test_cooperative_queue.py` drives 300 trusted pan moves and 300 distinct economic transfer commands. Only consecutive non-building pan moves with the same pointer ID coalesce; road-paint, touch transitions, clicks and economic commands remain ordered. At 256 queued events a synchronous completion barrier settles the queue before accepting the next action. Its duration is recorded in `samples().barriers` (bounded to 100 entries). The initial host sample took 2ms; this is not a late-city or native upper bound. Long road painting, multi-touch and late-city overflow/suspend timing still need independent coverage before rollout.

Trusted music handling now occurs at the original click capture phase through the same `handleMusicGesture` helper as ordinary playback. UI repaint can defer; browser audio activation cannot. The pause control shares `renderPauseIcon()` with the existing SVG header renderer.

The periodic candidate was subsequently fetched explicitly from `codex/8-frame-scheduling`. Its documented execution-time epoch/town/focus/`simulationBusy` checks match this controller contract. No blind merge was made. Latest integration `1cf6af50` changes the road-distance implementation in the same renderer file but not the pause helper region; reconcile with an ordinary source merge and regenerate the bundle after the immutable media soak completes.

## Retained terminal acceptance: regression, keep disabled

`tools/profile_cooperative_late.py` loads the exact generated terminal fixture from `833afee` (day 41681), keeps autonomous behavior and adaptive road caching, and executes the same sixteen scheduled trusted status-toggle taps in each twelve-second window. Receipt: `docs/previews/cooperative8/late-profile-e68.json`; it binds source and decompressed fixture hashes. This is host Chromium, not Android. One final tap can occur after the measurement window, so recorded in-window counts are disclosed.

Synchronous/cooperative observed rates: 47.15× / 24.23×. RAF P99: 266.7 / 100ms. Maximum trusted handler delay: 117.2 / 183.5ms; next RAF: 150.7 / 183.9ms. Completed draw counts: 170 / 156; maximum completed-draw gaps: 343.5 / 324ms. Maximum cooperative slice was 170.4ms: the 4ms budget remains soft. Accounts validated, queues cleared, and money drift stayed below $0.000001.

This does **not** establish a better overall experience: throughput and sampled worst input delivery regressed, while drawing can still stall for hundreds of milliseconds. The harness's next-draw field is an opportunity after pointer delivery, not verified causal paint of the requested action; it must not be reported as action-to-display latency. No production enablement follows. Additional late-city synchronous save/exit/suspend/overflow timing and independently exercised painted-action response remain pending.

Diagnostic `__townTest` entry points now finish an in-progress day before running, except the pure perf/view diagnostics and `get`, which projects the retained completed snapshot. This prevents nested stepping, partial policy mutation and modal creation through instrumentation while retaining the lexical synchronous oracle for test probes. These explicit diagnostic barriers can block; performance probes must use the cooperative status/commit contract rather than repeatedly draining through diagnostics.

## Bounded optimization checkpoint

Reconciled model order with `f26bbe0`: brownfield review precedes private-service investment in both paths. A structural day-call-order assertion now supplements scenario/archive/RNG tests, while the original synchronous functions remain an independent oracle. Vacancy filtering and arrival assessment yield in stable building order through `stagedSystemsDay`; the entire filter still completes before arrival attempts.

Task scheduling was already MessageChannel-based and already drained multiple cheap stages per 4ms slice. There was no nested-setTimeout clamp to remove. The terminal breakdown attributed approximately 21ms per cooperative day to recovery snapshot preparation; commit and event replay were negligible by comparison. Aggregate task waits were also measured and are retained in the receipt.

The recovery snapshot is now a deeply isolated plain-data graph, rather than encoded JSON text. Mutable arrays/objects are copied; immutable strings can be shared. The model is archive data, not arbitrary DOM/Date/Map objects. `__proto__` own keys are copied without invoking the prototype setter. Diagnostic projection copies the snapshot before returning references, and failure rollback takes ownership of it. Exact archives/RNG, queued economic commands, every tested yield/export barrier, injected-fault restoration and fifteen subsequent deterministic days passed after this change. The default synchronous path is unchanged.

`terminal-snapshot-comparison.json` records three matched terminal runs on the brownfield-aware bundle, with the same fixture and timed touches: synchronous, in-memory JSON-snapshot reference, and graph-copy candidate. Source and variant hashes are included. Rates were **46.61× / 24.13× / 28.49×**. Snapshot preparation averaged **21.46 / 11.40ms per day** for the two cooperative variants. Causal status-toggle mutation maxima were **299.8 / 360.1 / 242.6ms**; the following two-RAF paint opportunities were **384.2 / 438.6 / 299.0ms**. All fifteen in-window toggles per case were associated with a real `aria-expanded` mutation, with zero pending responses. A paint opportunity is not measured physical display latency.

The observer is registered ahead of the input fence so it records original trusted clicks even when their actions queue. An earlier diagnostic placed it after the fence and missed queued clicks; those incomplete counts were discarded from causal conclusions. Completed-draw gap maxima remained **362.2 / 357.7 / 333.7ms**. Deep copying improves this prototype but does **not** meet the rollout gate: throughput remains substantially below synchronous, and large unsliced economy/private-service/retail work remains. Keep disabled. The three short host windows are observations, not calibrated tail percentiles or Android certification. Recovery serialization has not been removed or weakened to improve metrics.
