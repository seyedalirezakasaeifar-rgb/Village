# Neighbourhood art-direction preview

Before/after: taste-before.png and taste-after.png. Actual gameplay rendering, same seeded town (169 residents), camera and 1280×720 viewport. Captured from source commit 90b3e283de05c306944bfaf8d44c4e01891e198b, bundle SHA256 d79c3701b5d99d69b47464b5968f1e3f24f4f1c7cb27375ea88032c459b3b2ad.

Caption: A first playable look at the new architectural direction: broader homes, varied rooflines, stronger material contrast, a civic clock tower, quieter continuous ground and new vegetation silhouettes.

This is a development preview. Service attachments, road edges, night-light integration and the bridge remain under review; the scene is not a declaration that the full graphics overhaul is finished. Default game renderer remains unchanged; opt in with ?cityArt=prototype.

Both modes saved and reloaded through the real Continue control over local HTTP. No page errors; drawing and a forced renderer-cache rebuild left the simulation archive and RNG unchanged. Host warm render sample (60 draws): before1.08ms, prototype1.01ms; these are host CPU measurements, not Android FPS. Detailed results: http-measurements.json.
