# Bridge integration correctness candidate

Base: `c0f4f6b10704ce0468e508082015ae78c48a3128`.
Reviewed source candidate: `133d2801d621fb63970eb05565a0ee3061d0aa5d`, including dependencies `5fb7005455e7990d306c5d5e17f637b7f5b82fb5` and `c68b9758846f7d5c3176842e4d6529661ea15d34`.
Final assembled source SHA-256: `8031901f1dca4e8b45d43d653e7657abff20f91f3bd5f2f823bd5c8a25e56a67`.

**Visual gate remains closed.** The user rejected the existing bridge imagery as janky and the earlier graphics as inadequate. The current renderer is provisional scaffolding pending the graphics owner's cohesive redesign. Geometry, depth, camera and pixel tests below are correctness checks; they do not constitute aesthetic acceptance, believable engineering, final art or release approval.

## Port and corrections

Applied the three reviewed commits as a chain, preserving the current retention save fence, canonical seed/Continue fixes, native wrapper and funded-wage comparator. The intermediate road-retirement commit contains literal conflict markers in landscape source; its bridge dependency removes them. Only the final combined source was assembled/tested, and no intermediate source was published as a verified checkpoint. No additional branch trees or experimental codecs were merged.

Two new independent negatives reproduced on the uncorrected port (assembled SHA-256 `9972d3ca90bc5ae3ed04772c8bcdb9c2da178fd82a5c154c9c3862a81c698b50`):

- After an actual interrupted tick, fresh bridge build/repair/decommission and road-retirement commands still accepted and changed cash/topology, although the existing save fence correctly refused persistence/export. The four authorizing transaction functions now reject failed or active tick state before any charge or topology mutation. Tests require unchanged model, cash, save chronology and failed persistence/export for all four commands. An initial test fixture injected the failure too late and legitimately encountered a newly dispatched protected cargo; that fixture error is retained separately.
- A fixed 100-world-unit center margin culled a five-cell bridge at the left/right viewport edges in 12 of 36 intersecting camera cases. Admission now derives its margin from declared paint bounds. All 36 edge/zoom cases pass with exact paused cold redraw and unchanged model.

Also corrected the stale 1–3-cell explanatory fallback to the actual supported 1–5-cell bound.

## Mechanics and render evidence

The five-tile East Meadow crossing uses an ordinary paid deed and approaches, costs $13,450, and requests $12.50/day upkeep. Bridge decks remain water to the water graph and connect structurally open road, freight, service and passenger topology. Actual construction/review/cancel/stale-quote controls, paid grain freight across every span tile, household service reach, protected bank roads and paid regional cargo refusal pass.

Additional independent state tests cover ten malformed bridge graph/archive mutations with atomic model/RNG/timeline/caller preservation; a normally funded bus route across all span tiles blocking decommission until route retirement; a real newly built fishery whose fishing route blocks the construction survey; near-threshold unfunded maintenance closing the road graph while preserving water; and actual repair/cancel/decommission controls. Repair transfers $6,773, and decommission returns $2,421 salvage, with conserved total currency. The closure fixture directly calls the real maintenance function at an authored near-threshold condition; it is not a natural long-run recession experiment.

The existing 36-case camera/DPR/quality matrix passes exact paused/cold redraw and actor pixel oracles, with zero differing channels in its sampled actor regions. The separate bridge test verifies truck/bus deck-plane ordering, elevated-metro exclusion, boat-below-deck ordering, closed-state rendering and water continuity. Existing compositor/guideway occlusion tests also pass. These host-browser checks do not establish Android FPS, vessel clearance or final visuals. The one-view warm render sample was 0.53 ms before / 1.12 ms with a bridge; it is not a device performance benchmark.

## Cold recovery and preserved negatives

Cold Continue of a bridge and live paid cargo after a committed day preserves every compared authoritative field, RNG and live traffic. The comparison explicitly excludes `serviceProvision` and `privateServiceProvision`, which the existing loader deliberately invalidates. Raw full-state equality therefore differs on those two derived caches; the negative is preserved rather than relabeled as exact full-state recovery.

Immediate cold recovery after freshly constructing a new farm/home also normalizes missing entity defaults and stale aggregate stats. This reproduces independently on untouched base `c0f4f6b` (source SHA-256 `346992b501f8622b007dddc6bf75baadbf850f6211b8989c6c3ccfcdefc98207`) without a bridge. This batch does not repair that inherited construction/default-publication behavior. The final bridge cold test first completes a real simulation day and documents its cache exclusions.

`test_waterfront_player_journey.py` still fails at its initial southern fishery-placement assertion, on both this candidate and the untouched base. The baseline diagnostic shows no building at target (4,58); the last firm is the existing wharf with workers [150,70]. This actual-control journey remains unresolved. Generic waterfront/mobile tests, paid freight fault/recovery, transit, road and bridge checks pass, but the full release gate is not clean.

The older annexation harness also initially expected an 80 × 80/schema-6 release. Its assertions and remap stride were updated to the current 128 × 128/schema-8 release; the current deed, price, title, rejection and legacy-migration checks then pass. The original obsolete-expectation failure is retained.

## Evidence and limits

[Final manifest](evidence/bridge-followup/final-manifest.json) binds all final inputs, results and preserved negatives. Twenty bounded core gates run on the final assembly, including full model/RNG replay, archive faults/legacy imports, currency/goods books, storage chronology/queue/failure and core release checks. Targeted final results separately identify the inherited waterfront journey failure and the explicit cold-cache exclusions.

No Android build/device/emulator/picker acceptance, full candidate APK pipeline, long-run endurance or physical performance test was run. No APK was built, signed or released. Cooperative simulation and experimental schema-9 capacity/identity codecs remain absent/disabled. The service-cash warning remains held. Only the recovery branch is published; the parent owns integration promotion.
