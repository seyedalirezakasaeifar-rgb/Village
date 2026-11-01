# Material identity and explicit quality tiers

Actual same archived town and camera, not a concept rendering. `low-before.png` disables new material detail; `low-after.png` enables it in the LOW preset (no shadow map,75% raster). `high-after.png` is the visual target in the REFERENCE preset (1024 directional shadow map,100% raster). Each image includes the real HUD refreshed after test-only archive restore. The high image must not be described as low-tier/device performance or finished quality acceptance.

Original generated textures: restrained metal-roof standing seams, masonry/stone courses, asphalt granularity and broad natural ground modulation. Building-use palettes differentiate civic brick/stone, pale timber cottage clinics, fire apparatus halls, timber waterfront/workshops and warmer industrial masonry. Garden greens vary deterministically within real titles. One bounded instanced contact-grounding layer survives the no-shadow LOW preset; its planes stay within real occupied building footprints and do not intercept picking. No photographic assets, postprocessing, invented occupancy or terrain-use changes.

Final serial SwiftShader comparison (same archive/camera,20 warm observations):
- LOW before:19calls/137592triangles,29material groups/5programs,14geometries/1texture; RAF median230.2ms,p95252.8ms.
- LOW detailed:23calls/137742triangles,33groups/7programs,15geometries/7textures; median247.3ms,p95261.2ms.
- REFERENCE detailed:23cached-shadow colour calls/137958triangles,33groups/9programs,15geometries/8textures; median420.7ms,p95444.6ms. The initial shadow pass is outside these warm cached-shadow samples.

The low-tier visual detail costs about7.4% median in this one software-rendered pair; it is not free or a performance improvement. Native GPU quality/performance remains unaccepted. Maps are shared128×128 originals, cached across scene rebuilds and disposed on full fallback. Eight camera/LOD transitions returned to identical GPU counts; full fallback had0geometries/0textures. Actual Hall picking, paused zero-extra-frames, archive/RNG invariance and HTTP save passed. Original family geometry/envelope tests40+68+128 passed. Normal pre-town/post-town import and idle tests are merged from the standalone startup correction.

`paired.json` includes exact module hashes and raw metrics. `pre-palette.json` preserves a previous controlled texture-only trial. `resources.json` records bounded resources/disposal. `town.json` is a generated test fixture, not a user save. No native probe source was changed: deed02bc4 remains frozen independently.
