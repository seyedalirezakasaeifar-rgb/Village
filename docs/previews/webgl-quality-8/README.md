# Exact-town WebGL quality diagnostic

All final tiers restore one canonical archive, use the same1000×700 viewport, and have the same model digest in tiers.json. No image/style/geometry changes occur between tiers. The warm measurements discard the first eight draws. Backend: ANGLE Vulkan SwiftShader (software). These results are not physical-phone performance.

| Tier | Backing canvas | Shadow map/pass | Total draw calls | Total triangles | RAF median / p95 ms | Submission CPU median ms |
|---|---|---|---|---|---|---|
| reference |1000×577|1024 /1|705|178618|423 /436.7|3.45|
| balanced |1000×577|512 /1|705|178618|405.5 /429.5|3.20|
| unshadowed |1000×577|off /0|315|86578|208.1 /229.8|2.10|
| low |750×432|off /0|315|86578|180.3 /195.8|2.00|

The shadow pass roughly doubles this software backend's frame time and submitted geometry; halving the shadow-map dimension alone helps little. Reducing pixels after disabling shadows helps a further modest amount. Even the lowest tier remains slow here. The scene also makes hundreds of real draw calls, so it has a genuine batching opportunity independent of hardware limitations. Next measurable improvement: shared instanced tree crowns/trunks and roof variants, preserving their silhouettes/materials. No claim of smooth gameplay follows from3ms submission CPU.

Counter correction: Three0.160.1 renders shadows before its default renderer.info reset (vendor source around line29594). Earlier reported calls/triangles therefore described the colour pass, not all passes. This diagnostic disables autoReset and explicitly resets before the entire render, counting shadow+colour work. One directional shadow pass is enabled where indicated.

Negative run retained: uncontrolled-tiers.json came from separate fresh foundings and failed the model-digest equality assertion. Those timings are not a valid quality comparison. The final tiers.json run restores one archive in every case and passes that assertion, per-frame day/total/RNG invariance, local save and no page errors. No negative result was discarded as a success.

Prototype-only query: cityQuality=reference|balanced|unshadowed|low (high also available but not benchmarked). Default reference retains the previous1024shadow setting; this report does not select a production quality preset. Default Canvas now loads only the tiny webgl-entry.js and avoids parsing/loading Three or the art kit. A forced module-load failure leaves Canvas visible and saving operational. Both paths pass test_webgl_loading_fallback.py.

Reproduce: python tests/bench_webgl_quality.py; python tests/test_webgl_controls.py; python tests/test_webgl_loading_fallback.py. Actual inspect/road paid action/live refresh/camera/portrait/save/fallback remain covered. Native module loading, worker projection wiring and physical GPU budgets remain separate integration gates. No concept matching or production promotion is claimed.
