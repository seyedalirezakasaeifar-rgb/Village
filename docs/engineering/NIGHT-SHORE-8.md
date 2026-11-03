# Night and shoreline readability pass

**Source reviewed:** founding waterfront, settlement seed 42, paused. Before hash `37782fef40335d2cbe625c5246ad1c0db81cfbc3439ef2b47634f8b7b0efef94`; after hash `4a16cf2f4783d5aee515b8715c62fed9dbbf4576d3c18258c8c2ea13be3c615f`. Same source-bounded Chromium run at 844×390 and 568×320, DPR 1. The expanded town/rail night and waterfront evening scenes in `docs/previews/city-continuity/` and `docs/previews/visual-acceptance/` were reviewed before making the targeted change.

The pass gives existing streetlamps a modest warm pool over the curb and adds a fine cool wet-edge line along cached land/water boundaries. No lights, boats, terrain, or activity are added to simulation state. Pools render into the existing night emission cache at zoom ≥0.45; ordinary sorted opaque sprites continue to occlude them. Shore detailing remains part of the existing cached terrain artwork and respects low-quality/decor settings.

## Phone comparisons

- [Night, 844×390 before](../previews/night-shore-8/before-night-844.png) and [after](../previews/night-shore-8/after-night-844.png)
- [Shore, 844×390 before](../previews/night-shore-8/before-waterfront-day-844.png) and [after](../previews/night-shore-8/after-waterfront-day-844.png)
- [Night, 568×320 before](../previews/night-shore-8/before-night-568.png) and [after](../previews/night-shore-8/after-night-568.png)
- [Shore, 568×320 before](../previews/night-shore-8/before-waterfront-day-568.png) and [after](../previews/night-shore-8/after-waterfront-day-568.png)
- [`comparison.json`](../previews/night-shore-8/comparison.json) records source hashes, viewports, exact fixture, cache bytes, render samples and browser errors.

The paired 844×390 night captures differed by mean RGB channel values 0.199/0.110/0.022, localized to the shoreline and lamp pool; the day shoreline pair differed by 0.069/0.038/0.018. At 568×320, the corresponding means were 0.103/0.062/0.011 and 0.040/0.022/0.010. These small, localized shifts match the restrained art intent. The existing night emission canvas remained 941,904 bytes; render medians were 0.36 ms before and 0.52 ms after in this host Chromium run (40 samples, sub-millisecond and noisy; not a native-device FPS claim).

## Verification

`python tools/assemble.py`, `python tests/test_diorama_art.py`, `python tests/test_world_art.py`, `python tests/test_sprite_envelopes.py`, `python tests/test_mobile_rendering.py`, and `python tests/test_dynamic_camera_matrix.py`. Sprite-envelope comparison remained pixel-exact with 72.9% fewer atlas pixels; seven viewport/orientation layouts had no overflow or browser errors. The dynamic camera matrix passed all 36 combinations across 640×, 844× and 1280× canvases at DPR 1–3: paused-frame and cold-redraw oracles matched, with no state mutation.
