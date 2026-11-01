# WebGL direction taste — user choice pending

Enable `?cityArt=webgl`. This isolated vertical slice renders the actual paused169-resident town's buildings, legal footprints and terrain tiles with original3D geometry and the real game HUD. Canvas remains the default and fallback. The paired canvas-baseline.png uses the same saved town; camera projection/framing differs and is not a pixel-matched comparison.

Locally bundled dependency: Three.js0.160.1, fetched from official registry.npmjs.org/three/0.160.1 and its published package tarball. MIT license included under assets/vendor. No CDN or commercial art.

Actual1440×900 WebGL capture: webgl-candidate.png. Local HTTP, zero page errors, simulation day/total/RNG unchanged while rendering. Real save succeeded, then Continue/reload restored total funds and the same town. Browser-submitted render CPU median3.5ms,345 draw calls,59,826 triangles, host Chromium only. This is not a GPU completion measurement, sustained FPS or physical Android result. Raw measurements.json retains the real state snapshot and render samples.

Unfinished and not approved for production: fixed paused snapshot/orthographic camera, full-world streaming, WebGL picking/camera/build controls, economic actor animation, bridge meshes, accessibility/reduced-motion handling and native/device budgets. Existing controls still act on the underlying Canvas; they are not claimed to control the WebGL camera. Roads/footprints come from real state; detailed architectural forms are artistic representations, not added economic capacity. No production rollout until user selects a direction and these correctness checks pass.

Refined choice image: webgl-refined.png. Ordinary home massing is lower and wider within the same legal plots; tree crown/trunk sizes vary deterministically and planting near homes is reduced so buildings remain legible. Previous iteration remains in commit d5bce359. User choice and all control/production limitations above still apply.
