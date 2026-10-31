# Streaming lifecycle audit

The audio specialist audited stable soundtrack checkpoint `dc0ddab26532fc62342e5a614ea262ec6117cac1`, retaining the ten committed pieces, their mix gains and contextual selector. The checkpoint fixes the previously reproduced stale play-promise rejection and explicitly unloads retired media sources/listeners. No new compositions or assets are included here.

Three additional controller regressions are fixed:

- A current deck's media error after native resume was ignored because its event handler retained the original play epoch. Live media errors now use the current epoch; delayed play-promise callbacks retain their captured epoch so stale failures remain harmless.
- A routine click or daily ambience refresh while the next decoder was starting removed the outgoing deck and raised incoming gain before `play()` resolved. Refresh now preserves the pending handoff and lets its successful play start the fade.
- Streamed Vorbis metadata can initially report only part of a composition. Real browser starts reported estimates 91–202 seconds below manifest duration. Boundary selection now uses the canonical shipped score duration; the native `ended` event remains the fallback for an actual early end.

`tests/test_music_races.py` includes targeted regressions for all three cases. Each assertion was also run against its preceding controller behavior and observed failing. Stale rejection suppression, suspension cleanup and source unloading remain covered.

`tests/test_music_streaming_soak.py` uses the real HTTP application and real HTML media. It exercises trusted Next clicks, real decoder starts, a six-piece live no-repeat window, repeated host interruptions, a rapid Next burst, foreground playback, zero-volume pause, hidden/visible transitions and preserved resume position. Only the eight-second fade clock is accelerated during resource turnover. CDP queries all live HTMLAudioElements after garbage collection, rather than merely counting the controller's references. Process PSS covers the launched Chromium process family; it is observational host evidence, not a WebView or Android decoder measurement. The test needs Linux `/proc`, Chromium and the existing Playwright dependency; it adds no Python package dependency.

Complete-file FFmpeg EBU R128 analysis and asset SHA verification found a compensated integrated-loudness spread of **0.79 LU** across all ten pieces. Raw true peaks range from −15.1 to −9.2 dBFS; retained runtime compensation accounts for the three quieter originals. This supports consistent level and headroom. It does not establish subjective musical quality or an acoustically seamless transition.

The final host run passed **300 completed handoffs plus 12 rapid Next clicks**, 34 host interruptions, and **180 seconds of real foreground dwell**. All 19 post-GC snapshots contained four HTMLAudioElements: one music stream and three cached effects/ambience elements. JavaScript heap settled near 4.8 MB. Chromium process-family PSS warmed from roughly 426 MiB to a 615–625 MiB plateau after 100 handoffs, then measured 607 MiB after final resume. This is bounded observed turnover, with substantial desktop browser overhead; it is not an Android memory budget. A preliminary run had unrelated browser processes in its aggregate PSS, so the final harness isolates the launched process family.

Exact source hashes and observations are in `reports/audio-experience/regression-summary.json`, `mix-analysis.json` and `streaming-soak.json`; the controller race receipt is `reports/development-8.0/music-races.json`. The earlier browser decode/control test also passed after the first two fixes; all ten tracks decoded with stereo, nonzero signal and matching complete duration. The subsequent canonical-duration fix is covered by the targeted regression and final real streaming run.

No hearing-capable tool, physical Android audio route/focus test, or multi-hour uninterrupted audition was available. Rapid decoder turnover and several minutes of foreground playback should not be described as hours of continuous listening or device performance certification.
