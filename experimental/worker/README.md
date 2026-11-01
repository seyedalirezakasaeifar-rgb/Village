# Disabled worker model proof

Base ca0c6d07. Run from repository root:

```
npm ci --prefix experimental/worker --cache /tmp/worker-npm-cache
node experimental/worker/build.cjs
python experimental/worker/prove.py
```

No production entrypoint imports this experiment. Acorn extracts declarations and function assignments from the actual model sources; excluded initialization statements are recorded in excluded.json for audit. This is a prototype bootstrap, not a release bundle pipeline. No fake document/canvas is installed. Browser Blob Worker runs the authoritative model. UI is used only to generate the starting archive and synchronous oracle.

61 complete days, two monthly boundaries, actual minimum-wage policy change with journal/recompute, completed snapshot/export and stale council ID rejection pass exact model/RNG comparison. Only trafficState/visualState are excluded as the separately owned presentation envelope. Notifications, ambience refresh, panel/header invalidation and save requests go to a structured outbox. Save requests are intents delivered after commit, not storage writes. Mid-day version on an effect denotes the preceding committed version; snapshot version identifies the delivery boundary. Policy snapshot version currently counts days only, so a separate command revision is required before UI adoption.

proof.json records one bounded 60-day timing sample after equality gates: sync 414.9ms versus worker409.7ms, main timer maximum gap499.8ms versus10.5ms. This measures event-loop availability, not trusted physical input latency. It is a small generated town, not the late-town performance acceptance fixture; no general speed gain is claimed.

Remaining gates: valid council choice settlement extraction (currently explicitly rejects rather than discards it); UI readonly snapshot adoption and command routing; save-owner visual-envelope/archive validation contract; failures and cancellation; dense-town matched repetitions and trusted input; API30/WebView83 native Blob support. No security settings changed. Production remains synchronous.

## Dense fixture and command boundaries

`python experimental/worker/dense.py` uses retained generated archive SHA ad6256fd… (778 residents/day41681). It compares 62 complete days and a real petition settlement to the original DOM council handler, checks the monthly semantic effect types, exports an identical model, and rejects consumed events/repeated command sequences/old epochs after load. The whole model/RNG comparison still excludes only the presentation envelope.

Step batches yield between complete days so commands can run at committed boundaries; they never yield inside a financial day. Concurrent step batches reject. A load increments the epoch, invalidates a running batch, clears pending council callbacks and effects, and rejects old-epoch requests. No promise or callback crosses postMessage. Commands have monotonic sequence admission; this is rejection protection, not a durable retry/result cache.

The independent UI renders building positions from its last completed snapshot and updates that snapshot only on acknowledged replies. Five trusted Playwright clicks submit wage changes while a 60-day worker batch runs. The original renderer is explicitly stopped before this UI starts. `dense-detached-renderer-negative.json` retains the earlier contaminated trace with original drawing still active on a detached canvas, including its ~717ms frame gap.

Outbox contract for parent/save-owner review: effects are ordered records with type/day/preceding committed-day version/payload; delivery is attached to a completed snapshot bearing epoch and command sequence. Save requests are intents only; this prototype never writes persistence. Export produces worker-model JSON at a committed boundary. Durable ownership, visual-envelope composition, deduplication across crash/retry, and root transaction admission remain external gates. Event settlement exceptions currently fail the request without rollback; this must be reconciled with root transaction ownership before production. Direct transaction dialogs deliberately reject.

Latest retained dense result: first source-matched31-day interval1.430s synchronous versus3.877s worker including snapshot and task yields. Five trusted command acknowledgements60.2–88.7ms. The minimal readonly view still records a533.2ms maximum RAF gap across299 samples, including snapshot/export/protocol costs. This is a negative rollout result: model correctness and boundary command responsiveness passed, while throughput and frame continuity did not. Do not extrapolate the small-town timing to dense towns or claim smooth rendering from worker isolation alone.

## Bounded render projection profiling

`projection.py` runs the dense correctness gates before a readonly UI trace; `RENDER_PROJECTION=0` selects full replies and `=1` selects projected replies. `components.py` measures browser-local request time, worker tick/snapshot/stringify/parse/post CPU, transfer/dispatch, main reference adoption, and the minimal building renderer. Full canonical exports remain explicit and unchanged. Projection replies contain only fields used by this experimental screen (building identity/position/kind, wage, population/employment, treasury), epoch/command/day/RNG and the complete pending outbox. They never replace authoritative G and are not sufficient for production report panels. Cadence is request/batch completion, not every simulation day.

Matched UI traces: full3,954,350 bytes versus projected38,003 bytes; trusted command acknowledgement59–89ms versus14–32ms; transfer/dispatch28–40ms versus0.7–12.9ms; worst RAF517ms versus117ms. Cumulative worker tick CPU remains similar (4.32s/full and4.50s/projection over their trace), confirming that projection changes transport/presentation, not economic work. The two traces include the same initial canonical correctness checks, which contribute full-snapshot CPU to both totals. Negative tails are retained in receipts.

Correction to prior throughput interpretation: first31DayWallSeconds in dense receipts includes returning the full model through Playwright/Python, while its synchronous comparison returns no model. It is protocol-inclusive wall time, not a fair simulation throughput comparison. Use component-profile.json browserRoundTripMs/workerRequestMs/syncTickMs instead. These are single sequential cold/warm samples; their order/JIT effects prohibit claiming a throughput win. Main snapshot adoption is a reference assignment and minimal-map drawing is submillisecond in the component test; this does not measure the production renderer. Production remains disabled because sustained dense rendering, transaction recovery, durable save ownership, native execution and truthful speed/admission still require acceptance.
