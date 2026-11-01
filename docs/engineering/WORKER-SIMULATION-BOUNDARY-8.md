# Worker simulation boundary assessment

Source: ca0c6d07, experimental branch codex/8-worker-simulation. Production unchanged. No worker throughput or equivalence claim is made by this assessment.

The existing bundle cannot safely execute unchanged in a Worker. src/00-foundation.js creates two canvases and queries the document during initialization. The entire model shares an IIFE with renderer and event bindings. Supplying a dummy document would hide effects rather than establish a valid model boundary.

The complete-day tick in src/50-clock.js calls updateCouncilAndMissions. In src/80-civic.js that function invokes save() inside ambition completion, before the day is complete, and toast() at lower speeds. These must become explicit effects with committed-day delivery; moving only tick to a Worker is insufficient. Council events retain choice functions in pendingEvent; functions cannot be structured-cloned. Keep those closures worker-side and send stable event/choice IDs plus serializable descriptions. A command must identify the event generation to reject stale clicks.

archivePayload in src/05-systems.js mutates G by attaching main-thread traffic, frameClock, gates and visualState. It is not a pure model export. The worker must capture model/RNG after a committed day; the UI must separately supply visual state tagged to that committed version. Autosave effects during a day must request a save after commit, not serialize partial balances.

journalPolicy in src/70-interaction.js is model behavior embedded with UI handlers. Extract its actual policy mutation/validation/journal behavior into the model command dispatcher; preserve defs-based names, baseline stats and story records. UI commands require sequence IDs, acknowledged committed version, and explicit rejected/stale results. UI must not mutate its snapshot optimistically.

## Minimal safe refactor and proof gate

1. Split foundation into DOM-free model constants/state and presentation initialization. Assemble a separate model bundle using the same source functions, without duplicating economic algorithms.
2. Extract civic event construction and policy commands from DOM bindings. Introduce typed notification/save-request effects, retain worker-side event closures, and test event choice effects against synchronous execution.
3. Extract pure model archive serialization from visual capture. Worker serializes only at day boundaries; export requests are queued barriers with version/RNG. Snapshot messages contain completed model states only, initially at a bounded cadence. No per-day rollback copy is needed.
4. Create Blob Worker only through opt-in test entrypoint, fail closed to synchronous mode on unsupported Worker/CSP/startup error. Never enable insecure WebView settings. Production stays synchronous until exact model/RNG/action/event/export replay passes.
5. Measure source-matched late fixture: synchronous versus worker actual committed days per second, snapshot clone cost/bytes, command acknowledgment, export barrier latency, main-thread trusted input/RAF tails and worker backlog. Include event and ambition days, not just empty normal days. API30/WebView83 Blob execution remains a native-owner gate.

This assessment establishes concrete extraction boundaries only. A complete-day Worker proof, measured speed/input comparison and native compatibility remain pending; no empty-worker or animation-only result is substituted.
