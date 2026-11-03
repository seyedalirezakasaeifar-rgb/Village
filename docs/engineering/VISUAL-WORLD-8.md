# Visual world integration slice

Branch `codex/8-visual-world` starts at `1de6930` and owns only the renderer hook in `src/65-landscape.js`, new `src/98z-world-art.js`, its test/capture script, generated bundle and this note. Cherry-pick the commit and run `python tools/assemble.py`; do not replace a newer integration bundle wholesale.

The module sorts after trade/waterfront UI and decorates existing renderer functions. It adds no economic fields or archive migration. Private service ownership, finance, goods settlement and menu contents are untouched.

Player-visible work:

- Three distinct regional carrier liveries, matching route gantries and roadside markers.
- Road ribbons beyond genuine regional boundary gateways. Interior gateways in older saves do not draw roads through private titles.
- Continuous, rounded physical consignment turns, with short loading dwells at journey endpoints.
- Recognizable log racks, aggregate hoppers, general cargo bodies and refrigerated food trucks; cab glazing, tandem wheels, restraints, hazard lamps and direction-aware lights.
- District-specific planting, stone entrance coping and address plaques, keyed into the bounded sprite atlas so cross-district reuse cannot show the wrong materials.
- Civic entrance seating and transoms; recessed industrial rolling doors, canopies, bumpers and warning posts; subtle residential gutters.
- Construction excavation, rising frames and roof decks driven by funded project progress.
- Offscreen atmospheric production effects use the already culled viewport list; microscopic atmospheric paths are skipped below 0.45 zoom. Freight pose generation returns before path/actor work when LOD suppresses traffic. Weakly held shipment geometry avoids rebuilding route arrays every frame and releases settled orders.

Run `python tests/test_world_art.py` for deterministic pause/state/continuity/LOD/atlas checks and near/far cached render timings. Run `python tools/capture_world_art.py` for identical-seed before/after industry/gateway frames and a controlled paid-import animation. Evidence lives in `reports/visual-world`; `comparison.json` and `checks.json` bind it to the assembled source hash. The animation advances an authored actual-consignment visual timeline with a following camera; it is not an unedited play session or a device FPS measurement.

Also verified: transport transition/state tests, paid regional trade/90-day browser-control journey, visual LOD, sprite envelope equivalence. Existing workday scene, atlas invalidation, older-WebView API, and 2,000-resident live performance gates passed before the final geometry-cache-only adjustment. The 2,000-resident host Chromium run measured 63.3 effective speed at requested 64x, 34.7 ms draw P95, and no browser errors; this is host-browser evidence, not physical Android certification.

Limitations: the sprite art improvements are a coherent refinement, not replacement of all building silhouettes. Trucks visualize active consignments; they do not create independent economic capacity or settle on graphical arrival. Existing regional accounting remains authoritative. No APK/signing/deployment was performed. The parent should run integrated acceptance and physical-device review.
