# Property frontage and street-readability pass

Actual runtime comparison, same archived towns/camera in each pair. `town-{off,on}.png` and `dense-close-{off,on}.png` refresh the actual HUD after test-only archive restoration; `*-world.png` are direct renderer canvas captures. The previous benchmark HUD could show the newly generated town's pre-load employment text, so screenshots were recaptured with the existing capture/updateHeader helper. No image editing or fake world backdrop was used.

Changes: home lot gardens and stone entrance paths replace full grey title slabs; restrained timber rear boundaries stay inside actual footprints; detached homes have lower storey proportions, and actual open-countryside/agricultural contexts allow single-storey forms. Existing legally adjoining home titles retain party-wall frontage. Road stripes occur only on actual straight segments; intersection crossing paint follows real connected arms. Narrow mineral shoreline bands remain inside actual water edges. Fine garden/road/shore details are omitted at distant LOD. These are architectural/landscape representations, not invented residents, sales or new facilities.

Dense fixture: the original mayor construction function bought four real cottages from town funds, then50 real days ran. No population or building was injected. The closer camera selects the real densest housing location: (19,22),14 actual housing buildings within7×7 cells. It does not fabricate continuous frontage across vacant or separately owned land. Archives here are generated test towns, not personal/user saves.

Serial SwiftShader low-tier measurements (no shadows, reduced raster),20 warm observations per mode:
- Original town18→19calls,128408→137592 triangles; RAF median223.05→226.90ms, p95250.30→258.70ms.
- Developed town17→18calls,139712→148560 triangles; median220.45→232.70ms, p95244.50→250.40ms.
- Dense closer view18→20calls,143254→151862 triangles; median209.60→199.80ms, p95229→205.40ms. This noisy decrease is not claimed as a speed improvement.

Full raw metrics and module hashes are in paired.json/dense-close.json. Every pair passed archive digest, renderer read invariance and HTTP save checks. A preliminary run is retained separately: it used more fence parts and its final context timed out during startup; no source defect was inferred. Reduced parts are included in final measured source. Footprint tests40+128 and real inspector/road/resize/save/fallback controls passed.

This is a bounded improvement for review, not a claim of meeting the concept's quality. The underlying sparse town still has vacant parcels and many apartment silhouettes. Filling those gaps with invented buildings or ownership would misrepresent the model; broader continuous streets need actual legal infill from gameplay. Native performance/visual acceptance remains pending, and Canvas stays default.
