# Institutions, working land and night

This slice starts from integrated `cae1bf426b0b1b534319415e3eacaa25972fa916`, which already contains the earlier graphics commits. Cherry-pick this new commit once; do not replay the earlier graphics commits. Reassemble the integrated bundle after resolving any renderer hooks against newer lead changes.

Ownership and activity use `isPublicFacility` and the documented private provider fields. Independent schools receive a blue/copper palette, academy sign, brass entrance marks and lamps; municipal schools retain civic colours and a shield. Independent brigades have a distinct brick/roof palette and brigade sign. Closed providers have crossed entrance boards. Ownership enters the sprite/view cache key so converting or restoring a provider cannot reuse a public facade.

Teaching retains the existing paid-private-client guard. Brigade readiness requires paid clients, positive usable capacity and a road portal; public readiness requires funded fire provision and road access. A small hose-check tableau shows crew readiness without inventing an incident, vehicle dispatch, fee or response. Public school activity also requires a road portal. No household-by-household service routing or new economic queries were added to rendering.

Five remaining production sectors now use original diorama models: broken-pitch barns and banded silos; forestry cabins and timber cradles; terraced quarry faces and screening machinery; tide-stained raised cargo sheds/cranes and fisheries with net racks/iced benches. Existing production, catch, manifests, piers, boats and staffing remain authoritative and unchanged.

Night now has a cooler, darker ambient wash with warm glazed windows and entrance pools. Window emission metadata is captured while a sprite is authored and retained with that bounded atlas entry. A single viewport-sized emission canvas is cached by the existing view key and provider operating flags. Foreground sprite masks remove rear light, preserving roof/building/tree occlusion. It holds no town object, household or firm references. Emission work returns before iterating items below0.32 zoom; existing actor LOD remains intact. Atlas clearing releases its small coordinate arrays alongside the corresponding sprites.

Owned source: new `src/98zzz-rural-services-art.js`; sprite-emission capture and night-compositor hooks in `src/65-landscape.js`; three civic palette lines in `src/98zz-diorama.js`; generated bundle. New tests/capture tooling and this note accompany it. Economy, service-routing caches, archive schema, music and menu overlays were not edited. Seasons remain disabled; all new climate art reads `visualMonth()`.

Evidence in `reports/provider-world` binds to assembled SHA256 `ddc92ffdb81acde6db599ce2681ed69befaeefbf88123a4df71efe7bde9a038a`:

- `checks.json`: paid school/brigade activity, no unpaid/closed activity, no unstaffed readiness, stable paused night frames, finite bounded light metadata, no economic mutation, rural models, disabled seasons and far-night early return.
- `comparison.json`: identical-seed before/after public/rural/night captures from the integration base; private scenes explicitly use the existing controlled fee-provider fixture with real staff and paid clients.
- `living-city.gif` and `living-session.json`: an unedited host-browser night session after20 economic days. It has no audio track and is not an FPS benchmark.
- `day-live-performance.json`:2,000 residents /713 buildings,311 days in8.02s,39.4ms draw P95 and66.7ms RAF P99.
- `night-live-performance.json`: same authored population,311 days in8.02s,44.6ms draw P95,66.7ms RAF P99 and89.3ms economy-panel-to-next-frame latency. Cash drift remained below0.000004.

Both live gates passed throughput, RAF-tail, paint and UI-response bounds. Sprite-envelope and older-WebView API checks passed on the final source. Actual school and brigade invitations/construction/staffing/clients tests passed; the longer private fee/voucher/learning/closure/recapitalization suite passed before the final emission-cache ownership-only adjustment. No physical Android claims, APK, signing, release publication or UI-overlay changes. Final integrated/night-on-device review remains necessary.
