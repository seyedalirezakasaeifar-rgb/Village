# Independent cooperative rollout check: keep disabled

Inspected prototype 2f5a73ee6e0c1df00b30e65736e6be506ed84bea without modifying its production code. Both default and experimental admission flags remain false. The matched comparison opts into cooperative mode only in the test browser.

Comparability limitation: prototype model order is reconciled through6e8665e. Latest synchronous mainbb02bbce differs in music, procurement, calendar and gathering-art modules. Therefore this is an independent matched-source prototype-versus-its-synchronous-oracle check, not current-main acceptance. Do not enable it on current main based on these results. Reconciling those changes and rerunning exactness is a separate gate.

The exact retained terminal fixture is unchanged. Sixteen identical trusted status-toggle taps execute in both cases. The independent harness keeps measurement open until all taps plus a settling interval finish; all16 actions have associated real attribute mutations and two-RAF opportunities, with zero pending responses. No final tap is silently excluded. No concurrent heavy test ran.

| Metric | Synchronous | Cooperative |
|---|---:|---:|
| Actual requested64x throughput |46.76x|28.24x|
| RAF P99 |283.3 ms|66.7 ms|
| Maximum causal action mutation |567.3 ms|328.9 ms|
| Maximum subsequent two-RAF opportunity |646.8 ms|390.2 ms|
| Maximum completed-draw gap |493.6 ms|335.1 ms|

This decisive reproduction confirms a substantial throughput regression despite smoother scheduling and favorable input observations in this sample. **Keep disabled; no rollout recommendation.** A two-RAF opportunity is not physical display latency. More benchmark repetitions are unnecessary before fixing the already-decisive throughput loss.

Recovery snapshot preparation consumes2,469.5 ms across215 cooperative days (about11.49 ms/day), maximum26.8 ms. Commit and queued-command replay total only26.4/8.7 ms. Pump maximum remains146.9 ms; staged private proposal maximum145.8 ms, staged retail86.9 ms and daily economy99.2 ms. Thus the nominal4ms slice remains soft, with unsliced work and snapshot copying still material. Presentation details and task-wait distributions remain in the raw receipt; no work or speed labels were reduced to manufacture a win.

Exact retained-town120-day model archives/RNG comparison passed. Monthly-day barriers also passed, retaining their real costs: export call375.7 ms, suspend call347.2 ms, save completion473.4 ms, exit completion390.9 ms, and300-command overflow279.3 ms. Save/exit initial calls were near-zero, but their completion promises waited for the boundary; do not describe them as zero-latency durable operations.

Evidence: reports/cooperative-independent-8.json, cooperative-terminal-equivalence.json and cooperative-late-barriers.json, plus retained logs. The independent harness is tools/independent_cooperative_check_8.py. No source/model/scheduling change or main enablement was performed. Host Chromium only; no native Android acceptance claim.
