# Private-service investment review performance

This change shares immutable projections **only during one synchronous investment review**. It keeps all candidate sites, staffing plans, fees, capital requirements, returns, competition and eligibility rules. It introduces no save fields, persistent financial cache, altered economic coefficients or skipped monthly decisions.

A proposal pass shares household ordering/liquidity, school eligibility and public-course exclusions, public coverage, existing-provider allocations by exclusion, qualified staff portals/bids, and deterministic housing-site geometry. Every scan retains the original number/order of random draws and freshly ranks its own scores; ranked lists are never reused. School demand still includes eligible public-course students while the revenue forecast excludes those already training. Fire demand and forecast retain their original response arithmetic. Real daily fee/subsidy purchases remain fresh. A new call rebuilds the projection, so policy, wallets, roads, provider ownership/closure, staffing, vouchers and imported towns are reconsidered.

## Exactness evidence

`tests/test_private_proposal_equivalence.py` compares the private-services module against the exact `03cb546` fixture in one browser and runs the current module in another. Four paired histories (settlement seeds 42/101, hardtimes 909, synthetic 2,000-resident regional town) run four changing policy/budget/staffing/wealth phases and three monthly checkpoints per phase: 1,440 unique simulated days and 48 exact full-model comparisons. Accounts, goods, firms, households, projects, history and RNG are compared without numeric tolerance. The synthetic/controlled mutations test equivalence; they are not player-earned growth or balance evidence.

`PROPOSAL_DIRECT_ONLY=1` additionally compares 14,400 exact demand/forecast results across 50 sites, both services, one/two-worker plans, existing-provider exclusions, public training, client allocations, provider closures and same-day policy changes. A separate original-development oracle checks exact ranked sites and RNG state over three successive geometry scans per state (48 scans total). Both paths use original affordability/voucher arithmetic; no forecast coefficient is rounded to make tests pass.

The end-state microtimings in the paired-history report are diagnostic only: several towns legitimately hit licensing/project/workforce guards. They must not be cited as full proposal performance improvements. The real-RAF evolving-city profile is the performance measurement.

## Rejected optimization

An intermediate attempt reused the complete ranked site list. The exact oracle rejected it in the dense regional history because original site enumeration consumes fresh random scores. That intermediate source was not committed or shipped. The final implementation shares deterministic geometry while repeating every original random draw and ranking; the RNG assertion was retained.

## Release boundary

This is an integration checkpoint, not a final release. A separate randomized save acceptance run found a canonical day-102 continuation failure in `03cb546`. Repeating that sequence on the first proposal projection stage reproduced the same failure; this optimization is not a save-continuation repair. The save specialist owns localization and correction. Do not claim the extended canonical save gate passes from the older core gate alone.

Host Chromium timings do not establish Android device FPS, subjective fun or listening quality. Whole-game input/frame tails include other work and remain separately measured even when investment review time falls.

## Isolated evolving-city observations

`reports/integration/8-private-proposal-performance.json` binds all final functional evidence to the assembled source and embeds the original and final profile records. The workload has 2,000 residents, all 21 deeds, 48 operating routes, real HTTP-served music, providers, cargo and autonomous development, requested64×; each near/far sample lasts six seconds.

| Observed host metric | Original near / far | Final near / far |
|---|---:|---:|
| Largest private-service review |124 /145 ms|62.4 /67.9 ms|
| Total review time in sample |233.5 /281.9 ms|109.9 /127.4 ms|
| Largest complete tick |186.1 /223.1 ms|153.9 /161.6 ms|
| RAFP99 |116.7 /83.4 ms|116.7 /116.6 ms|
| Trusted touch to next-frame maximum |97.1 /69.0 ms|129.8 /287.6 ms|

Review time falls substantially, but this short workload does **not** establish better complete-game responsiveness: trusted-touch tails remain serious and other growth/render work dominates some frames. Simulation rates are59.7–61.0× in the final sample, with valid goods/cash accounts and no JavaScript errors. The whole-session performance specialist should inspect those tails on this checkpoint. Timings are observed samples rather than deterministic equivalence or physical-device benchmarks.
