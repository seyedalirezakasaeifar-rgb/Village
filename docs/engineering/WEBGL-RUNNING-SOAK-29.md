# Frozen 29dd12af running-city soak

Source: 29dd12af7d4aac6b22efcfe1cec1e2d59aff2c1f. Sequential host Chromium/SwiftShader runs; no simultaneous GPU benchmarks. Full raw manifest, synthetic failure save, frames and paired screenshots: `docs/previews/webgl-running-soak-29/`.

Economy ran 1800.733 seconds, 07:24:48–07:54:49 UTC, with 58 paused checkpoints. Day 2 advanced to 990 through the normal clock; population 169→222 and buildings 102→136. Full archive/RNG and stable paused pixels matched at checkpoints. Context loss, preference retry, save and real paid water deliveries were exercised. Post-GC heap at five-minute samples: 15.10, 15.79, 16.57, 17.92, 17.75 MB; actual model growth prevents interpreting this as a fixed-state leak test. Sampled geometry counts 15/18/15/15/15, textures 11.

Rich stopped after approximately 133 seconds on a concrete missing-boat actor oracle failure, after three successful checkpoints. It did not complete 30 minutes. Failure save and frame are preserved. No success claim is made for Rich.

Two confirmed bugs are fixed separately on codex/8-webgl-actor-options: ded5834 invalidates paused actors after Traffic/Effects changes; dfe4a2c passes the current explicit waterfront budget rather than consulting the previous published LOD. Focused HTTP regressions reproduce the old failures and pass the fixes with full archive/RNG invariance. The fixed Rich 30-minute retest is separate; its terminal result is pending.

The paired economy-representative.png and reference-representative.png use the same saved town and camera; archive hash 4cfc3956f1eacadaf5dc3d2cd4bcd6c182bb4b18a50897be4ca575e709da2084. They show actual quality tiers, not concept art or final visual acceptance.

Limitations: checkpoint-wall-times.jsonl measures whole-checkpoint upper bounds, including GPU reads, optional GC and actions; it is not per-input latency. The first harness left the Park tool active, preventing its later paid-planning action; do not claim that coverage. Its corrected retest clears the tool using ordinary Escape and verifies a real $600 residential plan. Initial reviewed clearance and paid park placement did execute. No physical-device performance inference is supported.
