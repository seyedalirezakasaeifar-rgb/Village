# Normal performance tier and safe automatic selection

This is actual full-town gameplay rendering, not the old13×13 QA scene or concept art. Both benchmark variants restore the same generated archive/camera and load100 actual buildings. Full128×128 overview/control tests retain all102 building IDs; there is no hard world-radius crop.

Economy caps the physical backing edge at384pixels (and scale at50%), independent of deviceDPR. Pixel-aware geometry LOD keeps original legal massing/roof forms and uses original instanced window/trim atlases at small sizes. Close zoom restores middle-detail real geometry. Forests aggregate to actual terrain-cover planes once individual crowns are sub-pixel. Individual agents do zero work at coarse zoom; simulation continues. UI/picking uses CSS coordinates and remains full-resolution.

Final same-source serial SwiftShader result,20 warm observations each:
- Legacy low: 23calls/137826triangles, buffer[960, 447], RAF median242.3ms/p95266.6ms.
- Economy: 20calls/15450triangles, buffer[384, 179], median40.9ms/p9552.0ms. Actor projection sources/positions0/0.

These are host measurements, not physical-device FPS or an accepted native performance result. Earlier trial JSONs preserve variation/negative evidence. The final paired.json records every renderer/art module hash; it uses forced tiers to keep measurement independent of automatic policy. Economy is deliberately coarse; it is not the high-reference art target.

Normal Settings retain existing stored keys: Performance(low) requests Economy with a severe-frame guard; Balanced is adaptive; Rich detail explicitly requests reference quality and is never silently downgraded. On observed software or unclassified renderer capability, default Balanced returns to Canvas before scene/shader submission. Identified GPU Balanced has a measured-frame guard. Saved preferences are never overwritten by policy. Changing the quality preference retries3D after fallback; after context loss selecting another quality or reloading can retry. Explicit cityQuality query overrides are diagnostic and bypass automatic performance policy.

Tests: real paid road/inspector/pan/wheel/resize/save/fallback controls; actual Performance settings, full atlas/all building IDs, coarse/mid zoom and normal1×clock;128far legal-footprint/identity cases; bounded resources with exact paused return pixels; actual software-capability Canvas fallback and Performance/Rich retries with retained camera/saved preference; pure capability/frame-policy rules and a separately labeled synthetic observed-decision fixture. The synthetic fixture is NOT a performance measurement.

Two harness corrections are retained in this report: opening Settings legitimately initializes mayorJourney.visited, so the strict archive baseline is taken AFTER that existing visit (no fields excluded); a600ms idle check caught sample5 of6 bounded warmup frames, so readiness now waits for all6 before asserting zero extra draws. Final world.json records that sample5 observation.

A reproduced coarse-LOD defect dropped every thin closed-bridge barrier. Semantic closure primitives now survive detail culling; four cardinal pure tests and same-seed before/after closed-bridge captures verify this. Those screenshots are controlled diagnostics with real fixture notices, not polished showcase images.

Native full-gameplay tier and automatic-default behavior still require source-matched Android testing. Older664b44c low-tier native7–11second interactions remain a valid negative result. Shader/context failure still exposes the failure and restores Canvas. The default URL remains Canvas; no production renderer promotion is included.

Host actual wheel-to-next-render sample8: median64.3ms,p9574.3ms including automation overhead (input.json). Not Android input latency.

Final additional checks: nine CSS-picking/overview cases across actual DPR1–3 with longest backing edge≤384; full rich night/12-overlays matrix followed by the real Performance preference; injected shader/late-build fallback cleanup. All passed on host Chromium.
