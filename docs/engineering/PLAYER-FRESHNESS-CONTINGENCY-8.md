# Player freshness contingency fixes

Base: 01eeda3d2ff09822b9422721f75e97fabbc9958a. Baseline runner/probe: 856f944b551296ebe3c61c862439a946c803dc21. Scope is four small source changes, two tests and aggregate synthetic evidence. No worker startup, coefficients, storage owner, archive schema or paid transaction wrapper changes. No reviewer's branch is modified.

## Reproduced negative

Actual original controls reproduce all three reported defects on source SHA256 84ecbaef6b0ae999a9c5adcd49b9ba1678840cabfc36cf02b617c74a93d208a4. The 26-checkpoint journey advances16 actual live days1081→1097. Freight button19304 references neither active nor recent ledger, Settings remains selected while Town Hall is shown after restore (twice), and raw export/import differs at ONLY stats.townBalance after the fleet refund. All validators pass and there are no uncaught errors; strictFreshViewAccepted remains false. No initial money/people/stock/drivers are injected by this journey. Its funded fixture is the existing published accelerated QA trajectory, not an ordinary human save.

## Fixes

- Pausing refreshes the active read-only panel once, using the same editable-panel exclusions as ordinary live refresh. This presents completed-day freight records even when panel focus had suppressed live replacement. Draft/policy/settings forms keep their existing preservation behavior. Refresh occurs before the existing pause save, without a new saver or simulation step.
- Cargo inspection resolves active then recent delivery records. If both have expired, it explains that fact and refreshes Economy rather than silently doing nothing. Completed ledger inspection preserves its recorded outcome. An empty legacy recent path does not move the camera to an invalid coordinate.
- Successful text restore calls the existing openPanel('overview') path, keeping active context, selected tab, visible panel and title coherent. Validation failure remains on the existing non-adoption path. The existing hydrate/save fence and storage owner are unchanged.
- transitChanged refreshes ONLY stats.townBalance from the existing formula treasury+publicReserve−debt. This central transit invalidation point covers capital/refunds from building/resizing/retiring fleets and infrastructure. It does not run full recompute or alter the money transfer, fleet capacity, accounting entries or RNG. The balance has no economic consumer in current source; it is derived display/archive state.

## Fixed evidence

Source SHA256 be8415bd0427598cb7900e44c116681c9fa7c9deb5e471a04be4fa02ede4fdec passes the same actual-UI journey:26 checkpoints,15 live days1081→1096, no stale panel/cargo flags, strictFreshViewAccepted true, raw archive roundtrip equality and entire independent cold original-UI equality. Cash drift is approximately2.3e-7 and there are no page errors. Wall-clock input timing legitimately changes the final day, so this is not a claim of identical live action admission sequences between the two journeys.

Paired deterministic model/RNG checks independently exercise actual transit build, fleet resize, retirement and site removal on identical input state. Both versions have identical money, RNG and every model field after the baseline's one stale scalar is corrected to the explicitly asserted existing account formula. No fields are excluded and no other differences are accepted. This model test reuses the existing transit fixture's conserved treasury transfer and reassignment of existing residents; it is separately labeled, not confused with actual-UI-only evidence.

Native archive transport regression passes Unicode/BOM, exact8MB byte limits, malformed Unicode, bounded provider errors and private pending filenames on the host JVM. Actual Android Activity/provider/lifecycle and final composed worker/native acceptance remain separate. No FPS, hardware smoothness or long-endurance claim is made.

Run python tools/test_player_freshness_journey.py --expect-stale for the pinned negative, then python tools/assemble.py and python tools/test_player_freshness_journey.py --source-file assets/game.js for strict fixed acceptance. Run python tools/test_player_freshness_model_parity.py and python tests/test_native_archive_io.py. Tests read the existing public fixture from git. Reports retain hashes/aggregate evidence only; generated whole checkpoints remain ignored and are not part of this candidate.
