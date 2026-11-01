# Current Canvas/control inspection and two localized fixes

Base `13633d49fa5815ce56ee9f7bbdf2af0c92ace4fe` preserves the district review/oracle checkpoint and has the same public runtime as `e3fae439e96b33bc3a62340f9a898029af674111` (SHA-256 `dbbb77a8…`). Final source SHA-256: `78f4c3b5dc1a34313ff8752b6a6a5e85410a832b597b04fba4a0f1005ec62174`.

## Verified and fixed

**Repeated expansion saved stale derived data.** On the actual large-text Public Works/region-survey controls, three ordinary paid adjacent deeds reduced treasury to $997,474.4191579521, but `stats.townBalance` still reported the opening $1,097,734.419157952. `roadMetrics` was null. Cold restore recalculated both, so complete state differed. These are the only changed top-level fields in the preserved negative; no money was created or lost. Deed completion now invalidates roads and recomputes existing derived figures before publishing its journal baseline, header and save. No price, adjacency, land, title, workforce, utility or service rule changed.

The new repeated-control regression uses the existing synthetic regional seed-42 two-year town with earned resources. On both 568×320 and 390×844 large-text layouts it previews/reviews/cancels/reopens/buys three successive districts, verifies exact charges and conserved total money, finds the recorded deed, confirms private titles and terrain unchanged, reloads the complete state with zero exclusions and repeats fifteen days exactly. The first raw-string comparison was strengthened to complete parsed-state comparison to distinguish key order; it still exposed the two real differences. A later driver click toggled an already-open construction panel closed after reload; the preserved timeout was corrected by opening the panel idempotently. It was not a production control defect.

**A real frontage worker disappeared at a viewport edge.** The Canvas scene already culled building sprites using their paint bounds, then discarded their activity if the building centre was outside the viewport. At zoom 1.4, actual worker 152's frontage was inside the left edge while parent building 101's centre was outside. An independent full-scene insertion of that same eligible actor changed 183 actual canvas pixels with the model unchanged. Actor selection now reuses the already bounds-culled viewport building list. Existing detail thresholds and actor caps remain unchanged; no mesh, style, economic trip or model data was added.

The new edge regression covers left/top boundaries at zoom 0.65, 0.9 and 1.4. Every actual actor is present, and the independent actor oracle differs by zero pixels while the entire model remains unchanged. Far-view detail suppression remains the existing deliberate LOD policy; this correction concerns an otherwise eligible visible actor.

## Actual visual/control review

Six unaltered bounded captures are [curated here](evidence/current-controls-inspection/screens): original/fixed actor view, actual deed review in landscape/portrait, and the three-deed recorded state in both orientations. The real portrait quote shows its price, terms, keep-boundary option and Cancel. Landscape keeps its cost/action/Cancel available; an actual wheel gesture scrolls the long copy to its end (94 px), with the complete archive unchanged. Portrait fits the copy without scrolling. Existing large-text modal/inspector/ledger, overlay/readability, expansion network/employment and camera/depth checks are rerun. The current actual retail-invitation refusal also identifies the existing funded project and leaves the complete archive unchanged. Only verified failures above are claimed as defects.

This is Canvas correctness/control QA, not acceptance of the rejected old visual style or the selected Newfoundland overhaul. No experimental renderer/worker/admission/codec is enabled. The urban transition/cache files and graphics meshes are untouched. Corrected district candidate `ff837b3eabb921ced2b5266d8a009cea8bbfdeb2` was fetched read-only for the next separate review; its claimed tenant-order normalization and acceptance fixes are not certified by this batch.

## Source-matched acceptance

**36 final scripts pass** on the exact assembled source: twenty core gates, fifteen focused camera/control/network/recovery gates and the actual planning-refusal control. The repeated-deed test was additionally rerun with the real wheel gesture.

[Manifest and logs](evidence/current-controls-inspection/manifest.json) bind final results and original negatives. Core release gates run with `TOWNLEDGER_CORE_ONLY=1`; the older 115-year endurance result is not reassigned to these later bytes. Camera timing samples collected alongside correctness tests are not standalone throughput/FPS measurements. No Android/device/thermal, selected-style visual-fidelity, packaging, signing, release or integration promotion is performed here. Native wrapper and committed-day save fence remain unchanged.
