# Android 30 WebGL diagnostic result

The frozen `deed02bc4a25603693d6c2a2b287555343ed78ed` diagnostic candidate rendered WebGL on the isolated Android API 30 emulator. The QA badge reported `WebGL drawn 3 · paused true`; the page returned the actual renderer string `Android Emulator OpenGL ES Translator (Google SwiftShader)`. This confirms the optional renderer can import and submit frames under WebView 83.0.4103.120 on this software-emulated runtime.

The test used the explicit QA URL `?cityArt=webgl&cityProbe=1`, package `org.townledger.vale.qagfxdiag`, version code 900019. The locally built APK SHA-256 is `f2eb06268bb13a10bdabad3b0d0a9d92c36a79d3cee50d9ea065b99007a7bab6`; pulling the installed APK back from the device produced the same hash. It was built from source commit `deed02bc4a25603693d6c2a2b287555343ed78ed`; the canonical assembled `assets/game.js` hash is `451bfa6f9686c9ad6c29e2ce19b8614908339596ddd02aa94f8a5e2b70374b03`. Only the QA package metadata and Java launch URL were changed for the scratch build; packaged renderer modules match the frozen source.

After the real on-screen badge paused the synthetic town and loaded Three, the probe used mid LOD, no shadows, a 160×53 backing buffer, and a 13×13 tile window. It submitted three warmup draws (14 calls, 24,682 triangles). The count remained at three across five samples spaced two seconds apart. The full saved-town SHA-256 remained `51c145bd18215bed70ae9bd5fbd554c2fdd090f128ff0e5ea4c155aa295d6c93`, with day 10 and pause unchanged. A real tap on the zoom control requested exactly one more draw (frame 4, zoom 1.22) and kept the same save hash.

A controlled context loss using `WEBGL_lose_context` produced the visible badge `Canvas fallback · 3D released`, removed the WebGL canvas, restored the visible `#view` canvas, and kept the town paused with identical saved-state hash. This is an intentional fallback exercise, not a spontaneous context-loss observation.

Actual emulator screenshots:

- [Paused WebGL render](renderer-paused.png)
- [Requested zoom redraw](zoom-requested-redraw.png)
- [Canvas fallback after controlled context loss](webgl-context-loss-canvas-fallback.png)

This validates renderer bootstrap, a real badge tap, the paused no-extra-draw interval, one UI-requested redraw, save-state invariance, and context-loss fallback for this source/runtime combination. The emulator identifies itself as SwiftShader software rendering. Startup was slow and CPU-heavy; samples after settling still showed roughly 46–51% WebView renderer and 26% app-main CPU under emulator accounting. These readings and the reduced diagnostic scene are not physical-device FPS or full-city performance certification.
