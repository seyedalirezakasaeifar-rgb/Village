# WebGL branch asset audit

Audited verified remote tips:

- `codex/8-webgl-taste` at `d035882008836a33a00fe982fa1608e28123b928`
- `codex/8-webgl-controls` at `7e9004f7c029be51b4c5f57b0bc8f0c49a00670e`

Both branches ship the same local ES module renderer and pinned Three.js `0.160.1` bundle. `assets/index.html` loads `webgl-taste.js` as a module; that module imports `./vendor/three-0.160.1.module.js`. The library is bundled locally (1,272,972 bytes), so the runtime import is available offline. Its adjacent `assets/vendor/THREE-LICENSE.txt` contains the MIT notice and copyright attribution for the three.js authors. The audit manifest records exact paths, sizes, and SHA-256.

The renderer constructs geometry and colors in code. The reviewed module has no runtime model/texture fetches or external URLs. The current scanned asset tree contains no GLB/GLTF/BIN or raster/vector texture files. Runtime URL scan found no external or absolute media references. The deterministic manifest check passes: 20 entries, zero missing/empty or external references. The total exceeds the previous 16 audio references because it now includes the WebGL module, local Three.js bundle, and Three.js license notice; the Three.js bundle is represented twice by distinct origins (module import and explicit dependency record).

Evidence: `reports/asset-manifest-8.json`. The check is `python tools/check_asset_manifest.py`.
