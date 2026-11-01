# Shared opt-in WebGL infrastructure

Separate from the preserved d035882 style-choice capture. Camera drag, wheel zoom, viewport resize, read-only screen-to-world tile picking, resource disposal and Canvas fallback now have a browser interaction regression. Rendering becomes dirty-driven after a short90-frame warmup; idle camera frames do not submit new GPU draws.

Validated in host Chromium over local HTTP: centre ray maps to actual town-hall tile26,26; actual pointer drag changes ray-picked tile to20,27; wheel increases zoom; portrait resize adjusts viewport; full read-only snapshot remains exactly unchanged; real save succeeds; dispose removes WebGL canvas and reveals the existing Canvas. No page errors. Results controls.json, reproducible test tests/test_webgl_controls.py.

Still unvalidated/unimplemented: dispatch of WebGL picks to real inspect/build actions, native gesture behavior, live economic snapshot refresh, property selection highlighting, full-world streaming, bridge and economic actor meshes, device performance. Do not promote as completed building controls or live3D gameplay. Newfoundland style selection is recorded, but private concept image materialization failed through the supported Library helper; no specific reference matching claim is made.
