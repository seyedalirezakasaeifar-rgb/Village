# Zoom/detail budget review on bb02bbce

Source SHA-256 `8c7d3216d05355c6b15467c357bdc71f34e14d3714204f7a43c5e4cb8b03b26c`. Two actual conserved workloads: a controlled 2,000-resident/700-plus-building city with 48 paid routes/21 deeds and autonomous development/private entry enabled, and the retained late town (778 starting residents/797 buildings). Sequential four-second windows evolve each town, so differences between views are diagnostic budgets, not paired causal speed improvements. Host Chromium only.

| Town/view | Speed | Actual rate | RAF P99 ms | Tick total ms | Draw total ms | Panel handler→RAF ms |
|---|---:|---:|---:|---:|---:|---:|
| dense2000/near | 0 | 0.0 | 16.8 | 0.0 | 0.0 | 64.5 |
| dense2000/near | 64 | 59.2 | 183.4 | 3240.1 | 654.2 | 58.6 |
| dense2000/far | 0 | 0.0 | 16.8 | 0.0 | 0.0 | 39.8 |
| dense2000/far | 64 | 62.1 | 183.3 | 3234.5 | 349.9 | 61.9 |
| dense2000/offscreen | 0 | 0.0 | 16.8 | 0.0 | 0.0 | 28.1 |
| dense2000/offscreen | 64 | 53.9 | 200.0 | 3758.8 | 223.2 | 58.1 |
| lateTown/near | 0 | 0.0 | 16.8 | 0.0 | 0.0 | 48.3 |
| lateTown/near | 64 | 46.4 | 266.7 | 3437.0 | 504.2 | 68.1 |
| lateTown/far | 0 | 0.0 | 16.8 | 0.0 | 0.0 | 29.0 |
| lateTown/far | 64 | 50.9 | 233.4 | 3608.0 | 272.2 | 66.3 |
| lateTown/offscreen | 0 | 0.0 | 16.8 | 0.0 | 0.0 | 27.4 |
| lateTown/offscreen | 64 | 56.8 | 266.7 | 4175.4 | 99.7 | 97.8 |

Full receipt includes 1x/8x too. The panel metric executes the actual handler synthetically and waits for RAF; it excludes real-input queue delivery and must not be called touch-to-display latency.

## Culling observations and decision

At distant zoom 0.2, per-building spriteFor calls, building activity actors and vehiclePosition calls are zero in both towns at all speeds. Existing adversarial visual-LOD guard also passes: unreadable parcel collections throw if distant actors iterate them; far shadows/boats skip their loops, nearby traffic returns and aggregate economics advances. Traffic-state strings can still change during real far growth because authoritative topology changes/reset operations occur; that is not proof hidden traffic animation ran. Direct trafficUpdate isolation is the appropriate guard.

At nearby-detail offscreen camera positions, six explicit paused redraws perform **zero spriteFor calls**, compared with roughly 486–864 for nearby occupied views. Building/decoration activity actor output is zero offscreen. Both workloads therefore cull offscreen building raster work before atlas lookup. Nearby output/quality is untouched: no production changes were made. Every explicit paused paint retained exact complete G JSON and economic RNG.

Offscreen near-detail traffic still maintains its small bounded visual population and checks positions for visibility. On the 64x windows, trafficUpdate totals only 10.9/16.0 ms and vehiclePosition 1.3/2.4 ms across about four seconds, against 3,759/4,175 ms of tick work. This is not a high-impact rendering defect worth changing vehicle continuity or overlapping the compositor owner. No culling patch is proposed.

At64x the tick dominates every view, including offscreen with minimal draw cost. Far presentation reduces draw work but does not remove 183–267 ms RAF tails. Route/model computation and cooperative tick staging remain the high-impact owners. At1x/8x presentation is a larger relative cost, but observed RAF P99 is generally16.8–50.1 ms, with no demonstrated invisible-building/agent iteration defect. These short windows do not establish device smoothness, thermal behavior or subjective art quality.

Reproduce with tools/lod_budget_matrix_8.py and tests/test_visual_lod.py. No economic work, growth or private entry was disabled during live sampling; pause is an explicit control state. The six forced redraws are separate paused presentation probes rather than artificially increased live FPS.
