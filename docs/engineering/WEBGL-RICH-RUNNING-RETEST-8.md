# Fixed-source Rich running-city retest

Immutable source commit `f26d6969001704919755d48f1ea4e4fda71ea2fa`; game bundle SHA-256 `ba03c5017a9353521600f55014af46fcd1512051c817dcb56a385801f61f2c0d`. This is the sequential Rich retest after the two independently reproduced actor-cache fixes, not a rewrite of the frozen29 negative result.

Actual timed run: 2026-11-01T08:19:49.249157+00:00 through 2026-11-01T08:49:52.900413+00:00, **1803.651 seconds**. Result completed: 58 paused full-archive/RNG and exact raw-canvas checks, five post-GC samples, zero browser errors and zero actor mismatch findings. Source hashes remained unchanged. Normal clock advanced day2→815; population169→205 and buildings102→122. No synthetic actors, inserted money or accelerated simulation API was used.

Ordinary controls executed reviewed clearance/paid parks, a paid residential plan, four reviewed river import orders, Traffic OFF/ON, context loss/quality retry, save and repeated portrait/landscape camera/overlay changes. Actual water shipments progressed to Delivered in the retained timeline. Context loss left the complete save unchanged; retry retained the explicit Rich preference.

Post-GC JS heap at five-minute samples: 15.63,17.35,17.31,16.13,18.74 MB. Geometry counts16,17,16,5,15; textures8,8,8,7,8. Final scene16 geometries/8 textures. Live population/building growth means these are bounded observations over this run, not proof that all leaks are impossible. Different camera bounds explain varying geometry. One WebGL canvas and one annotation layer were checked throughout.

Raw manifest, five actual screenshots and source hashes: `docs/previews/webgl-rich-retest-8/`. The synthetic saved-town fixture is inherited from the committed Economy test. No user files, credentials or personal data were included. Representative Economy/Rich same-camera pair remains in `codex/8-webgl-running-soak` commit d28ddf1 under `docs/previews/webgl-running-soak-29/`.

Host Chromium uses SwiftShader software rendering. This timed acceptance is about state, actors, caches and lifecycle; it does not certify physical-device performance or produce individual input latency percentiles. Rich is still an explicit costly reference tier. Economy's separate frozen29 run completed30minutes but found the now-fixed Traffic cache issue; it has not been silently relabelled as a clean fixed-source30minute run.

## Follow-up oracle corrections

The additional two-tier lifecycle harness initially made two invalid assumptions: Effects OFF was expected to hide all traffic (the actual option suppresses decorative effects/boats while real road traffic remains), and a camera move was sampled before its requested frame. Both test assumptions were corrected without changing game code. A third initial cold/warm equality assertion observed Rich textures8→12 after visiting far LOD; the second identical camera cycle stayed at12, geometries17. The final test compares the two fully warmed returns and separately requires zero GPU resources after complete disposal. These observations are retained here rather than claimed as renderer fixes.

## Final two-tier lifecycle result

`tests/test_webgl_tier_actor_resources.py` passed sequential Economy and explicit Rich after the timed run ended (no GPU benchmark contention). Both exercised actual normal-clock trips, paused Traffic OFF/ON and Effects OFF/ON, two complete camera/LOD cycles, unchanged full archive/RNG, stable paused frame count, successful save and visible Canvas fallback. Complete disposal reported exactly0 geometries/0 textures in both tiers and removed both WebGL/annotation nodes. Final warm return texture counts were11 Economy and10 Rich; actual trip timing differs between fresh runs, so this does not replace the earlier recorded12-texture observation. No continuing growth was observed across the identical warmed cycles. Raw final results and game-only screenshots are in `docs/previews/webgl-tier-actor-resources-8/`.

No running soak/test process remains owned by this handoff. No additional game-source changes were required after dfe4a2c; subsequent commits contain harnesses/evidence only. Native source-matched review remains separate and is required before promotion.
