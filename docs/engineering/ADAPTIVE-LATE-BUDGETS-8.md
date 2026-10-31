# Remaining adaptive-cache late-town budgets

Exact same generated terminal checkpoint and ordered actions; autonomous growth, private entry, audio and surviving transport retained. CPU profiling adds overhead. Values are host observations, not Android guarantees.

| Priority / stage | Calls | Median ms | P95 ms | P99 ms | Maximum ms |
|---|---:|---:|---:|---:|---:|
| tick | 780 | 22.0 | 54.0 | 330.0 | 494.3 |
| dailyEconomy | 780 | 17.2 | 29.0 | 54.5 | 108.3 |
| systemsDay | 780 | 0.1 | 0.4 | 122.4 | 167.2 |
| privateServiceInvestmentDay | 780 | 0.0 | 0.0 | 102.9 | 203.6 |
| urbanEvolutionDay | 780 | 0.0 | 0.0 | 88.8 | 109.7 |
| draw | 385 | 2.4 | 13.8 | 35.7 | 220.0 |
| renderPanel | 14 | 16.2 | 29.7 | 29.7 | 29.7 |
| save | 3 | 111.6 | 112.5 | 112.5 | 112.5 |
| persistSnapshot | 3 | 86.2 | 88.6 | 88.6 | 88.6 |
| archivePayload | 3 | 23.9 | 25.4 | 25.4 | 25.4 |
| updateHeader | 101 | 1.4 | 2.2 | 3.3 | 3.7 |

The maximum frame (494.3 ms) equals its maximum tick: that tail is atomic model work. Prioritize cooperative slicing / exact optimization of these unsliced children: systemsDay -> occupyVacantHousing (1,941 ms sampled CPU), privateServiceInvestmentDay -> seekPrivateServiceInvestment (2,546 ms), urbanEvolutionDay -> urbanRetailProposal (715 ms). Daily economy retains procurementLeadDays (1,944 ms), privateServiceDay (1,896 ms), urbanRentMultiplier (1,813 ms), groceryChoices (1,147 ms), regional sales (946 ms) and transit operations (879 ms). These are inclusive child sample totals, not sums of exclusive CPU. Economics/stage owners retain those changes.

Browser layout/style costs were only 0.152/0.095 seconds across 30.37 seconds, versus 28.61 seconds script time. Serialization/storage remain separate stalls: three saves, with repeated envelope reads and checksums. No persistence internals are changed here; its owner should preserve integrity/chronology and immediate-save barriers when caching reads or coalescing requests.

## Composable presentation candidate

The previously isolated periodic-presentation candidate was applied to the adaptive-cache source without tick/economic edits. It defers only automatic panel/save tasks, coalesces each kind before serialization, preserves original cadence timestamps, and rejects unfinished simulationBusy days, stale towns/epochs, focus, pause and suspension. Explicit actions remain immediate. Cooperative owner must hold simulationBusy until publication and coordinate explicit commands/save promises; if G clones change each commit, adapt identity checks to stable timeline identity.

Same ordered actions executed 14 panel renders and three saves in both cases. Observed baseline/candidate rates were 42.38/42.93x, RAF P99 333.4/316.6 ms, and maximum touch-to-next-RAF 506.2/336.1 ms. This is a modest favorable single observation, not statistical proof or acceptance of smooth play. Negative original tails and complete CPU/long-task receipts are retained. Atomic economic tails remain unresolved; no FPS cap, backlog or simulation work was reduced.
