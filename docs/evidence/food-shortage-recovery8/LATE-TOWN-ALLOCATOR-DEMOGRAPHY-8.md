# Late-town allocator and demographic continuation

## Question

Does the cash-backed vacancy ranking (`fundedVacancyIncome`) change the long-run demographic/economic trajectory of the generated late-city archive, compared with the prior effective-wage-only ranking? This isolates the allocator change from the ordinary-hour soak's actions and speed schedule.

## Method

`tests/test_late_allocator_demography.py` loads the retained synthetic QA archive from `codex/8-session-soak` (day 41,681; 778 residents) into Chromium and advances 25 simulated years at one day per step. It runs the same save through the current bundle and the prior `c188a6f` bundle, which uses effective wage only. Policies and autonomous development remain unchanged. Council-choice prompts are suppressed and counted so policies cannot drift (200 prompts per run). It then repeats the 25-year current-source arm and requires exact annual-row replay. No residents, funds, or goods are injected. Every year checks the town archive, cash and goods balance, and unchanged policy.

The fixture archive SHA-256 is `ad6256fd85d4146fda9eeac0b16d5b182ed352c23bbd96af3b320553c29ce786`. The current bundle is from `a7acbe82986d5dc8727687ef3c7562f92f0a6346`; the comparison bundle is `c188a6fe802982969a02e3a3aa5f719e03027658`. The full source-bound annual data and both run snapshots are in `late-town-demographic-comparison.json`.

## Results

The 25 annual rows match exactly between the cash-backed and prior rankings. The repeated current-source run also matches exactly. Both histories end at 729 residents, a net change of -49 from the starting 778. The measured identity is 778 + 202 births + 12 arrivals - 150 deaths - 113 departures = 729. Population peaks at 837 in year 13, then falls to 729. This is a mild decline, not the 25-year population loss described in the separate ordinary-hour soak.

There are 480 vacant housing units at year 25, and only two firm vacancies; housing quantity is not the apparent town-wide constraint in this archive. Job fill and available adults vary: 491 recorded in the workforce, 410 filled firm jobs, two vacancies, and 33 free adults at year 25. Food hardship remains measurable: the trailing-30-day unmet-food measure is 3,383 units at year 25 and ranges from 3,504 to 7,873 in the years shown. Aggregate capacity and household-level reach are different measures, so this run does not prove a town-wide production shortage or identify which specific households miss food. Public school and health coverage report zero in the yearly snapshots; the causes and reachability of those service gaps were not isolated here.

Cash drift is at most a few millionths of a unit per recorded yearly checkpoint, commodity error stays below `2.8e-8`, archive validation passes, and no policy changes. These invariants passed for both source variants and the exact replay.

## Interpretation and limits

The funded-vacancy fix does not explain this retained fixture's 25-year demographic path: it is bit-for-bit identical at the annual metrics to the prior ranking. The prior one-year credit histories still show that the fix corrects misranking in deliberately isolated underfunded-vacancy cases; this naturally evolving archive simply does not expose that difference in its measured outcomes.

The 25-year run does not reproduce the ordinary-hour soak's reported 598 residents. The soak ran for roughly a simulated century and included player actions (public green placement and road extensions), while this experiment ran only 25 years with council choices suppressed. Its cohort and service flows therefore cannot establish the cause of that longer decline. Nor does this synthetic archive establish a real-world demographic forecast. Persistent unmet food, unpaid wage days, aging cohorts, and zero reported public school/health coverage are retained negative outcomes for targeted follow-up; no coefficient change or forced recovery is justified by this comparison alone.
