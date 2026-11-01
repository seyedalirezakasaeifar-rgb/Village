# Normal gameplay performance candidate

Renderer remains opt-in; default application URL retains Canvas. This branch composes accepted669c908 model with prior140fad71 art/controls and the tested startup correction. Economic kernel is unchanged. Preferences retain existing low/balanced/high keys and saved values; labelBalanced is now explicitly adaptive.

## Tier contract

- Performance(low preference): Economy3D, no shadow map, physical backing edge≤384px and scale≤0.5 independent of deviceDPR. Actual projected pixels choose coarse/mid geometry. Original instanced façade/window atlases preserve regional identity without tiny window meshes. Real massing/footprints/roads/bridge geometry remain selectable. Forest cover aggregates at sub-pixel crown size. Close zoom restores mid geometry. Nothing is restricted to the diagnostic13×13 window.
- Balanced: conservative automatic policy. Observed software-renderer strings or unclassified capability use Canvas before3Dscene submission. Identified GPU starts Balanced with bounded frame observation. This is a conservative capability choice, not a physical-device performance rating.
- Rich detail(high preference): reference3D and explicit; performance policy never downgrades it or changes its saved selection. Actual shader/context errors still restore Canvas and expose the error.
- Forced cityQuality query: diagnostic override, bypasses automatic performance decisions. Legacy `low` is the older expensive tier retained for A/B measurement; native candidate must request `economy`, not `low`.

Automatic frame guard observes the first six submitted frames of a committed/rebuilt scene, discards the first two intervals, and uses a three-interval median. Hidden/busy observations are ignored. Balanced above100ms reduces to Economy; adaptive Economy above400ms returns to Canvas with notice. This is bounded, downward adaptation; it is not a guarantee of smoothness. Saved preference is never rewritten. An explicit quality change retries3D after fallback; Rich remains available. Camera is retained across policy fallback/retry. Renderer failure and performance/capability fallback have separate diagnostic state.

Default Canvas avoids optional dependency loading. No CDN, security-setting changes or renderer promotion is included. All textures/atlases are original and locally generated; Three0.160.1 remains pinned/offline/MIT.

## Native handoff (normal gameplay, not reduced QA scene)

Build `python tools/assemble.py` and copy the COMPLETE assets directory into the normal native build. Use the existing supported native asset origin.

1. Safe automatic path: `index.html?cityArt=webgl&cityBadge=1`. On actual SwiftShader the badge should report Canvas automatic fallback; no3Dscene is submitted. Create/Continue and exercise real pause/resume, panels, saves and orientation. Verify saved Graphics preference remains Balanced. Badge only exists with explicit cityBadge and changes no gameplay/tier by itself.
2. Forced performance measurement: `index.html?cityArt=webgl&cityQuality=economy&cityBadge=1`. This forces the normal full-world Economy renderer; no manual-start gate, no radius crop, no forced pause. Badge reports actual drawn tier/LOD/frame. Create/Continue, pause, verify actual Hall26,26/building1 pick, pan, real zoom and portrait resize. Verify longest backing edge≤384, same committed model/building identities, unchanged paused save and no repeated draws after warmup. Resume1×and confirm real days/traffic advance, then pause. Test controlled context-loss fallback/save. Record startup and OS-tap latency separately from warm steady frames.
3. Real settings behavior: DROP cityQuality from URL before testing preference changes (forced diagnostic override intentionally wins). Performance selects Economy, Rich explicitly retries reference3D, Balanced can restore Canvas on software. Do not repeatedly run known unresponsive high tiers just to get a screenshot. High remains optional, not native-performance certified.

`cityProbe=1` belongs only to the older frozen deed02bc4 diagnostic and must NOT be used here. New optional noninteractive badge ID is cityRendererIdentity. No badge appears in normal release UI.

## Evidence and limits

See docs/previews/webgl-economy-8/README.md and raw JSONs for same100-building forced-tier comparison, exact module hashes, full128atlas/all102IDs, actual controls/paid road, actual preference retry/saved choice, strict archive/RNG reads, resource disposal, paused pixels, input timing and closure-cue regression. Synthetic policy-decision tests are explicitly labeled and are NOT timing evidence.

Older native664b44c softwareGPU7–11second interactions remain a valid negative result. New Economy and automatic-default behavior require source-matched native acceptance; no physical-phone FPS claim. A static paused renderer can submit0WebGLframes while overall WebView CPU is nonzero: existing main loop still polls and calls updateHeader every250ms, so that is a profiling target rather than evidence of a repeated WebGL draw. Reference-art fidelity remains a separate review gate.
