# 30-minute overlay and cache soak

The 30-minute run used an archived, immutable copy of commit `d4607eefbadee15a8347568f4e5e8ade7a1c322c`; `assets/game.js` SHA-256 was `6260809a99d39d3f3c8131bcd9e85343695617d5629950409cca1ba7ef2aa1aa`. It ran in host headless Chromium on the 128×128 stress fixture with 2,000 residents, all 21 annexed deeds, three transit routes and five simulated days. Gameplay was paused for the visual pass.

From 2026-10-31 23:43:05.65 UTC to 2026-11-01 00:13:05.89 UTC, the tour performed 18,565 overlay/camera/lighting/quality/motion/viewport transitions, 1,547 state/RNG checkpoints, and 10 full renderer-cache invalidations. It covered four landscape/portrait sizes at DPR 1–2. Every cold cache reset reproduced the paused canvas pixels and preserved game state and RNG. No browser errors, stale overlay key, accumulated DOM nodes or cache-bound failures occurred. The Town Signals key remained one node and the total DOM count stayed at 406.

Sampled atlas use peaked at 8.62 MB; night-emission cache peaked at 2.20 MB at DPR 2. The post-GC JavaScript heap measured 17.1 MB at 5, 10, 15 and 20 minutes, then 33.1 MB at 25 and 30 minutes. That is a persistent 16 MB step during the final third, with no further growth over five minutes. The audit did not identify the allocation; treat it as a memory follow-up if the target device budget is tight, rather than claiming no leak.

Across the six five-minute windows, host canvas draw time p50 was 4.3–4.6 ms, p95 83.3–85.4 ms and max 353.6 ms. Request-animation-frame interval p95 was 66.7 ms. Paired Town Signals click latency p50 was about 67 ms and p95 83–91 ms. These headless host measurements include software-rendering and shared-container scheduling; they are not Android WebView FPS claims. No failure occurred, so no failure frames were generated.

Full timestamped sample data is in [soak.json](../previews/overlay-soak-8/soak.json). The copied game source was not modified during the run.
