# Fractional-resolution actor repair

Sequential dependency: `e8913c7` (renderer audit). No economic or routing changes.

Native review found that the initial shadow repair was not pixel-exact at smaller viewports. Host reproduction at 640×360 confirmed 224 differing channels, maximum 59, despite the 1280×720 oracle passing. Repainting scaled sprites inside a damage clip changes edge rasterization at fractional device coordinates. Repair now paints into an unclipped viewport-sized opaque scratch canvas and copies its completed pixels through the integer-aligned damage clip. Existing depth ordering stays intact.

Evidence: `docs/previews/render-precision-audit/`. Source-hashed independent full-scene comparisons now have **zero differing channels** for 640×360 DPR1, 640×360 DPR2, 844×390 DPR2 and 1280×720 DPR1. DPR is the browser device scale; game quality retains its normal backing-store cap. The seeded state and pause-icon assertions pass in each case.

A pedestrian silhouette at the real funded-bus corridor's ground position reproduces the deck overlap: old 45 wrong pixels of 47 overlapping pixels, corrected zero. This is a controlled renderer fixture, not a claim of a naturally scheduled resident crossing. The existing actual funded-bus case remains 151 wrong pixels → zero. Both leave economic state unchanged.

Ten day/night, pan and zoom captures preserve exact paused pixels and state. Each cache is bounded to one viewport; both release their backing stores at distant zoom. This correction adds one more canvas than the prior repair (941,904 bytes at the tested 844×390 viewport, 550,400 at 640×360 DPR1). It paints only selected intersecting scene layers into that canvas. No full-atlas texture is added.

The near live 2,000-resident/all-21-deed/three-route receipt is included separately. Host timing does not establish Android smoothness. Native WebView must rerun its original oracle and animation review; the native evidence folder is not mounted in this worker. No whole-page CDP missing-canvas symptom is classified as a runtime game defect. Original audit evidence remains unchanged; no video published or bundled.
