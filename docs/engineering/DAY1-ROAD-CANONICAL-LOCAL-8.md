# Current day-1 canonical road snapshot: local proven fix

Exact base 72419dc89e0526888afcb956d34bcc78abff3f3e; assembled source 3e262a51d4a95992c2b9df3f8205025ffdb1f05d6a5376a528ff75ddceedae8b. This is an isolated review candidate, with no public ref promotion, APK or manifest operation. Earlier acceptance-evidence publication remains paused; this distinct startup source/test candidate is reviewed separately.

## Proven actual-player defect

The actual New Town button calls start(true). seed computes roadMetrics and requests its founding save. start then calls invalidateRoads(), clearing G.roadMetrics, and opens Overview without rebuilding that persisted derived snapshot. A subsequent actual Pause/Options/Save overwrites it with null before the first day. Cold Continue hydrates and rebuilds the object.

The strict real-UI negative reproduces exactly the native report on current source: day1/169 people, roadMetrics null becomes {connectedFirms:26,totalFirms:26,connectedHomes:67,totalHomes:67,roadTiles:385,roadClusters:1,averageJourney:13,quality:75}. This is not merely an obsolete fixture possibility. Every other archive field matches. RAF is disabled to hold the completed first day, while New Town, Pause, Options, Save and cold Continue use their actual handlers. HTTP origin and real local/IDB persistence are used.

The older cold-canonical regression does pass, but its prepare helper reseeds directly AFTER clicking New Town. That bypasses start's invalidation and conceals this startup path. __townTest.reset also explicitly invalidates after seed; its synthetic null alone would not prove a normal-player defect. The new actual-UI test avoids that ambiguity. start is identical on baseline87811c and candidate72419dc; this is pre-existing, not caused by the header/save optimization.

## Minimal local source change

Immediately after start invalidates the graph, set G.roadMetrics=roadMetrics(), using the same scoped rebuild already used by enterContinuedTown. No full recompute, field exclusion, arbitrary default, serializer mutation, account transfer, RNG call, schema change or persistence fence change is introduced. The one initial derived cache now exists before first-save eligibility. Other production files remain unchanged.

Fixed assembled source SHA256 d3ed25306c7c4754485d0691d04d9d4f9739dccafc1d2efbaa909762977a7081.

## Passed strict tests

- Actual day1 New Town → Pause → Options Save → reload → Continue: no differences, all fields compared.
- Actual live-clock advancement to day6, Pause and committed Save → cold Continue: no differences, including live traffic/visual state. No direct tick helper advances this case.
- Published v6.0 distressed fixture → actual UI import/Overview normalization → explicit Options Save → cold Continue at day18001: no differences. First legacy adoption may initialize documented absent state; only the subsequently saved canonical town is compared.
- Paired actual New Town startup followed by deterministic QA stepping: initial difference is ONLY the intended null-to-derived road snapshot. Complete model, financial RNG, accounts and route state then match baseline at days2,31,60,120 with no excluded fields. The stepping phase is clearly labeled synthetic QA, not human live play.

The baseline diagnostic matrix also covers ordinary day offsets, regional startup, v6.0, planned894 and retained778 fixtures. Its direct reset helper has an extra invalidation, so day1 helper results are not independent normal-player proof. Planned894 and retained778 normalized imports are immediately stable through warm reload/Continue and next-day replay.

## Separate retained negatives / scope limits

Some baseline monthly checkpoints are not globally canonical: day30 has missing newly constructed building baseValue defaults, stale stats.businessCash and a road connectedHomes count; day60 has stale stats.cash (500) and roadMetrics null; regional monthly snapshots show related derived defaults/stats. Those late clock stages run after the day's final recompute. No production changes were made for these separate cases. At seed42 day60, the next replayed day differs only at stats.avgCash; actual accounts, routes and RNG match, and a 30-day full continuation converges exactly. This is bounded evidence, not proof of zero downstream effects at every horizon. Raw hydrate-first v6.0 also acquires an absent urban default on first overview; the normalized actual-UI save case above is stable.

The local one-line startup fix does NOT claim to solve all monthly derived-state coherence. Native owner should verify the new source if parent chooses this patch. No physical-device performance or native APK lifecycle result is claimed here. All strict comparisons retain roadMetrics and every other field.

Run tools/assemble.py, tools/test_724_actual_newtown_cold.py --expect-mismatch, the same tool without flags, --live-days 5, --legacy-v60, and tools/test_day1_road_replay.py. Source and aggregate receipts are local under evidence/day1-road-canonical-local; no complete saves are added.

## Bounded startup timing follow-up

Six paired actual New Town clicks in fresh browser pages (RAF held; host synchronous start only) measure exactly four roadMetrics calls baseline and five fixed. The additional rebuild costs [1.7,1.7,1.7,1.9,5.6,2.4] ms, median1.8 ms. Whole synchronous start median324.15→323.80 ms, maxima340.1→344.4 ms; the noisy overall samples do not establish a startup speed change. No per-day call is added. Financial RNG after every paired start matches. This is neither native nor full cold-application startup timing. Run tools/profile_day1_road_start.py alone; receipt start-timing.json records raw samples and exact source hashes.
