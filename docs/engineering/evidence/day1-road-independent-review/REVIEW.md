# Independent decision: accept scoped day1 startup fix

Candidate64d4316a337847aa14e4f0b8e420a6de4d1ef900 is directly ahead of72419dc89e0526888afcb956d34bcc78abff3f3e. The only production source change is src/70-interaction.js:start: after invalidateRoads(), assign G.roadMetrics=roadMetrics(). No native/index/persistence/header/clock algorithm or archive-format change. roadMetrics uses existing deterministic graph/route reads and returns numeric derived metrics; no money/RNG call. No broad cache or recompute introduced.

Independent baseline actual UI negative reproduces day1 New Town→Pause→Options Save→reload→Continue, with roadMetrics alone changing null→object. The fixed actual controls preserve every archive field exactly. Fresh actual live-clock day6 and normalized v6.0 UI import→Save→Continue also pass with no exclusions. Paired actual New Town starts differ only at the intended initial road snapshot, then complete model/RNG/money/route state is exactly equal at days2/31/60/120. Five independent functional commands pass.

Six paired startup measurements run alone after functional runners: exactly four roadMetrics calls baseline and five fixed. Extra last call1.8–4.8ms, median2.75ms. Whole synchronous start median311.6→333.5ms, maxima326.1→345.7ms in this run; no startup-speed benefit is asserted and host noise/other startup work is not attributed to the extra call. This small once-per-start correctness cost is acceptable for this bounded fix. It is not a physical/native/cold-application performance test.

The published commit is source-only and retains the old assembled asset. Packaging must run python tools/assemble.py. Independently regenerated101-module bundleSHA256d3ed25306c7c4754485d0691d04d9d4f9739dccafc1d2efbaa909762977a7081 matches owner expectation. Only the local generated assets/game.js differs from the source-only checkout after review; no production source edits were made.

Scope limits are retained: documented later monthly derived-state coherence negatives, tenancy-index normalization, full native startup/provider/lifecycle durability and physical smoothness are not solved/certified by this one line. This review does not promote any ref, approve a PR or upload an APK/manifest. Fresh independent aggregate evidence is local in this directory; blocked reviewer evidence was not copied or republished.

## Authorized assembled follow-up

A separately authorized follow-up includes the exact canonical assembled bundle and this fresh independent aggregate evidence on codex/8-day1-road-assembled-reviewed. It is directly ahead of the reviewed source-only64d4316. The generated bundle equals72419dc assets/game.js with ONLY the one intended startup assignment inserted; no other runtime change. The historical review statement that no publication occurred describes the review phase. This follow-up changes no public integration ref, PR, APK or manifest, and copies none of the earlier blocked reviewer files.
