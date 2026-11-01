# Frozen diagnostic, not release graphics settings

Base30b91f7. Open the existing native asset URL with `?cityArt=webgl&cityProbe=1` (cityQuality is intentionally ignored by this explicit QA mode). No security/engine flags required. Normal URLs have no badge or diagnostic settings and Canvas stays default.

1. Badge appears BEFORE Three import: “QA · Canvas · Start paused 3D”. No3D dependency loads yet. Create/Continue Town, then close Town Hall with its real close button.
2. Tap the top-left QA badge (x8,y72 CSS). It uses the existing Pause control if needed, BEFORE loading Three or submitting GPU work.
3. Badge progresses through loading modules, building actual geometry, submitting WebGL frame, then “WebGL drawn3 · paused true”. A failure reports Canvas fallback; do not interpret requested URL as successful initialization.
4. Diagnostic forces mid geometry, no shadows, deviceDPR1,25% raster dimensions, a13×13-tile actual-town window around Hall. The omitted outer geometry is an explicit QA limitation, not a production scene. Actual models/roads/buildings remain unchanged.
5. After three warmup draws, unchanged paused state submits ZERO additional GPU frames. Probe idle polling sleeps100ms. Observe badge draw count stationary for10seconds, take OS screenshot, sample CPU after warmup; then tap zoom to confirm a requested redraw. Save still uses existing storage.

Host test844×390 verifies pre-import badge/no3Dcanvas, real Pause dispatch, mid-tier quarter-size buffer, three-second zero-extra-draw/archive invariance, save and no JS errors. This is not proof of native compatibility/performance. Native API30/WebView83 software probe is pending. Existing observed83–153%CPU/input/CDP timeouts on the prior full scene remain an acceptance blocker until diagnosed, not a physical-device FPS estimate.

## Reproduced initialization defect

The controlled delayed import exposed an actual initialization-order bug: when a town already existed at module load, start() synchronously called build() BEFORE the module's `let clapboardTexture,lampTexture,renderSerial` declaration initialized. Negative oracle reproduces `ReferenceError: Cannot access 'clapboardTexture' before initialization`; cleanup could hit the same temporal dead zone. The declaration now precedes start dispatch. This is a correctness fix, not merely a badge. It may explain intermittent host startup waits; native causality is not yet established.

Final host result:211×69 backing buffer at844×390 viewport, mid21,872 triangles/15calls; actual pause true, draw count3 unchanged over3seconds, archive unchanged and save successful. No JS errors. Negative error and positive screenshot/JSON retained under docs/previews/webgl-native-probe-8. Only actual native probe can determine whether its previous initialization/input hang is resolved.
