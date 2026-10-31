# Scale-aware district life

Sequential follow-up to `517e23f` on `codex/8-world-services`. Cherry-pick after that provider/night commit; regenerate the integration bundle. No economy, routing, panels, audio, climate or archive changes.

Far zoom replaces invisible trucks with cached regional consignment counts and actual sampled road-route ribbons. Market markers clamp to viewport edges; a small legend explicitly calls the dotted paths samples and counts active loads. The summary scans at most the existing240 consignments once per shipment-array/network/length change, retains three market rows and never iterates people or visual vehicles. It does not claim that all loads take the representative route. Traffic/decor preferences control the presentation.

At middle zoom, bounded school/fire labels distinguish municipal and independent ownership, while distressed properties receive a restrained rust frontage cue. Labels disappear at close zoom where the architecture/signs carry the information.

Occupied household gardens receive a bounded decorative stroll, using an existing living adult only for appearance; no location, commute, purchase or schedule is invented in economic state. Parks/squares can receive one explicitly decorative path stroller within the same budget. There are at most four balanced/seven high-quality ambient actors, all culled before item iteration at far zoom, low quality, disabled effects or reduced motion. Paused positions are stable. Existing service/production activity guards are preserved.

Owned source: new `src/98zzzz-district-life.js`, two renderer call hooks, generated bundle. `tests/test_district_life.py` verifies unchanged economic state, caching, actor caps, paused positions and early LOD/reduced-motion exits; it creates actual844×390 screenshots at0.25/0.55/1.15 zoom. Existing visual LOD/world tests passed before the last annotation-position-only adjustment. Final near/far live2,000-resident evidence is included in `reports/district-life`.

Known integration limitation: the previous UI's persistent bottom cards can still cover edge markers; that UI is owned by the gameplay worker. Review the annotations after that worker's card changes. Decorative strolls do not establish a residential schedule simulation. Physical-phone review and long-form subjective play remain outstanding.
