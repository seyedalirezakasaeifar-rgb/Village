# Periodic presentation tasks after the frame

The 31987fc late-city trace found 195 ms periodic panel replacements and 93 ms synchronous save calls inside an already overloaded frame callback. The terminal checkpoint CPU trace separately identifies road-distance trees as the dominant economic cost: 16.39 seconds exclusive CPU in a 30-second profile, including 8.36 seconds under transitOperatingDay, 3.57 seconds under workerCanCommute and 1.66 seconds under regional exports. Routing/economic optimization remains with those owners.

## Scoped candidate

Only `70-interaction.js` changes production behavior. Periodic report refresh and autosave each get a separate zero-delay task, with at most one pending request per kind before any serialization. Original due timestamps retain the 1.5-second report and configured autosave cadences. Header, drawing, the tick budget/admission/backlog, all simulation work and actual-speed reporting are unchanged. Explicit user actions, pause/save, native suspension and unload retain their existing synchronous save paths. Persistence implementation and archive schema are untouched.

A deferred report rechecks active tab, town identity, focus, pause, native suspension and visibility. A deferred save rechecks town identity and save epoch. Both reject `simulationBusy` so they cannot read an unfinished cooperative day. A successful immediate save while an automatic request waits satisfies that request; a failed immediate save does not suppress its retry. Old-town tasks cannot serialize or repaint an imported/founded town.

Shared-hook proposal for the cooperative prototype: hold existing `simulationBusy` across all unfinished day stages and clear it at the committed/published boundary. These periodic callbacks then retry through the normal due checks after commit. Immediate commands and explicit save promises still need the prototype's own queued-command/commit barrier. If the prototype replaces the `G` object at every commit, adapt the callback's town-identity check to a stable timeline identifier rather than treating each published clone as a new town. This candidate does not rewrite the frame/tick controller or enable cooperative simulation.

## Safety evidence

`test_periodic_presentation.py` uses real loopback browser storage. It verifies that periodic report/save calls execute outside the frame callback; 200 queued automatic requests serialize once; paused requests cancel; explicit Save starts immediately and satisfies the queued request; injected storage failures retain the automatic retry and recover on a later explicit save; focused input is preserved; and suspended, busy-day and replaced-town callbacks do not leak work into the wrong state. Existing native-idle/host lifecycle, bounded save queue, twelve chronology/fault scenarios and older-WebView API checks pass on source SHA-256 `e458f8f483cc97074618517b88362d0ee377836b504b4a60f8666e109ca01c72`.

The executor briefly disconnected during the regression run. No uncertain test was duplicated while running; durable source-bound receipts confirmed the periodic and idle tests. The remaining tests were resumed after checking that no test process remained. The legacy save queue's file-URL navigation was blocked by browser administrator policy before app execution; the repository's existing opt-in loopback asset adapter completed the queue/chronology checks. That initial transport failure is retained in `frame-regressions.json`.

## Measured limits

The paired scripted runs load the exact same retained day-41,683 checkpoint (hash `ad6256fd85d4146fda9eeac0b16d5b182ed352c23bbd96af3b320553c29ce786`), retain autonomous growth/private entry/audio and surviving cargo/transit, and execute the same ordered 12 trusted touches, panel actions and two explicit saves. The samples last 44.27 / 43.41 seconds because input execution itself is delayed by the busy main thread. Both execute 17 panel renders and three save calls; draw counts are 472 / 465, with 471 / 465 real simulated days. There is no disabled economic stage or replenished route funding.

Observed original/candidate rates are 17.56 / 17.68x; RAF P99 is 383.4 / 383.4 ms, frame P99 376.5 / 370.8 ms, and maximum trusted input to next RAF 382.0 / 401.7 ms. **This pair does not establish a whole-game input improvement.** The candidate establishes task separation and correctness boundaries; atomic economic work still dominates. Keep that limitation when deciding integration alongside routing fixes or cooperative stages. No physical Android performance claim is made.

`scripted-comparison.json` binds both hashes, action sequences and workload counts. Earlier variable-action-count experiments remain as diagnostic receipts, including unfavorable samples; their counts differed and must not be used as a controlled performance claim. The 45-minute terminal run and CPU attribution remain on `codex/8-session-soak` through `1197151`.

For the persistence owner, the same trace shows repeated readSaveEnvelope parse/checksum work (12 reads/15 checksums for three saves). A bounded cache of exact already-validated local storage texts/envelopes may avoid redundant reads while preserving cross-tab changes, order promotion and backup corruption recovery. That is a proposal requiring the owner's integrity/fault tests; no such cache or general manual-save coalescing is implemented here.
