# Expanded-city visual continuity audit

Base main `f4e03152bdce9b38e8ea22c1d3918b52da06fd07`, plus gathering art `9b68ee6` (replayed here as `84edc0c`). Integrate this new commit after gathering art; do not replay that art twice.

## Confirmed correction

Fixed centre-based viewport margins could omit an off-screen tower while the end of its long authored shadow was still visible. `sceneIntersectsView()` now uses cached sprite envelopes plus a conservative 100-pixel maximum sun projection. Existing industrial smoke headroom is retained. Trees and custom site sprites also use their real retained envelopes. Street-prop/detail gates remain in place. No extra raster, agent scan or economic mutation is added.

`tests/test_shadow_culling.py` compares the previous cull and corrected cull against an uncropped render of the actual shadow painter. The isolated valid two-plot tower geometry gives **128 differing channels (maximum16) → zero**, with unchanged town state. This is a minimized renderer fixture, not a claim that a new economic tower was built for the screenshot. Before/fixed/reference pixels are committed under `docs/previews/city-continuity/`.

## Runtime sequences reviewed

`tools/qa_city_continuity.py` uses one authored 2,000-resident, all-21-deed city with three paid transit routes, real reviewed river imports, ordinary farms, paid groundworks and an authorized named gathering. Twelve local day/night sequences cover neighbourhood, rail/station, waterfront, farm neighbourhood, renewal and Willow Commons. Each includes an overview-to-phone-zoom pan before ordinary motion. To keep short events reviewable, each shot replays the same committed city checkpoint, then runs the normal unpaused game clock. Camera/lighting changes are QA controls. The fixture is an explicit stress town, not a claimed naturally grown mayor save.

Selected beginning/middle/end sequences were inspected across six sectors, including moving boats and ground traffic. No additional disappearing textures, night corruption or moving roof/deck defect was established. Orange rail lamps remain intentional infrastructure. This is sampled motion review, not a claim to have proven every frame or every route crossing correct.

All **24** paused/reduced-motion checks preserve exact warm/cold final pixels and economic state. Observed main atlas maximum is 20,124,672 bytes; existing bounded site/gathering/viewport caches remain in force. Twelve raw animations and the exact checkpoint remain LOCAL ONLY in `/workspace/scratch/city-continuity/`; no video or save is published or bundled. `motion-checks.json` records source and animation hashes, times, actual start/end state and local paths. Static samples are committed separately.

The real gathering in this stressed city had **zero** eligible modelled attendance and ends during ordinary playback; it correctly receives no event crowd. The suite does not fabricate residents or extend the calendar to make a busy clip. The normal seed42 named gathering is separately tested with real attendance in the same-source named-gathering receipt. The art QA selector was corrected to choose the newly named venue instead of the first existing town square; the calendar engine's selection was already correct.

The existing 36-case viewport/DPR/LOD cache matrix and 12 named-gathering cases also pass on this exact source. Worst matrix warm draw mean is 9.75 ms in host Chromium. These are cached draw timings, not session RAF-tail or Android FPS claims. Historical evidence directories are preserved. Native integrated animation/oracle acceptance remains pending.
