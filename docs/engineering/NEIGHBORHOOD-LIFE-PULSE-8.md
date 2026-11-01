# Neighbourhood life and needs pulse

The neighbourhood inspector now combines a live resident work picture with a small 90-day local trend and the existing service-reach overlays. It reports the resident household's recorded jobs and employer names, working-age people with no job record, commute-blocked workers, and grocery businesses that residents can reach within 24 road steps. Shop reach includes current staff and food stock; it is explicitly not a household purchase receipt or promise of affordability. The existing district summary continues to report medical/school road reach and funded coverage separately.

Every 90 simulation days, the model retains the last two block snapshots: residents, occupied homes, staffed job places, and job capacity. The inspector compares the two completed samples, labeling their actual dates. It does not infer growth between samples, create demand, or change any economic choice. The ledger is bounded to two samples for at most 256 map blocks. Version-1 urban saves without the optional `activity` field remain valid; malformed snapshots are rejected during normal archive validation.

The medical and school buttons enter the existing access overlays. They neither buy a service nor change policy. For funding or construction, the mayor continues to use Public Works and its reviewed paid actions.

## Verification

`tests/test_urban_neighborhood_pulse.py` advances ordinary seed 42 for 180 days and checks both 90-day snapshots against the rendered delta. It opens the actual inspector and existing medical overlay, checks the live worker/shop wording, toggles a test commute-blocked flag to prove the work-flow summary reads current records, and verifies mobile layout at 360×780. It also checks treasury/RNG/goods/history remain unchanged by inspection, exact 30-day archive continuation, legacy-save acceptance, and atomic rejection of a negative snapshot value.

Evidence: `docs/previews/urban8/neighborhood-pulse.json`. The sample's block 3:3 held 2 residents at both checkpoints while staffed local jobs fell by 4; it reported the change as decline rather than manufacturing growth. At day 180, named nearby grocers showed their actual staff and food stock, and the test-only blocked commute moved one worker from employed elsewhere to blocked without changing the snapshot or economy.
