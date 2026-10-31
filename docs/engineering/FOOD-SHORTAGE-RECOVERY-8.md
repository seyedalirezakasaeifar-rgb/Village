# Food shortage and recovery check (8.0)

**Source:** `codex/8-balance-lab` at `89730e5` (game bundle SHA-256 `293fe306631099dfaacdd37e724d4c6e3b89991f56a1e15c50f872606f662c90`). The deterministic browser harness and full daily observations are in [`results.json`](../evidence/food-shortage-recovery8/results.json). This is a two-seed model check, not a balance benchmark.

## Method

For each real starting town (settlement seed 42; regional seed 909), simulated 60 ordinary days, saved that checkpoint, then ran matched 240-day histories. The control left regional imports enabled. The intervention disabled new import orders for 120 days and restored orders for 120 days. Roads stayed connected in both arms; this isolates supplier-order interruption and does not simulate a road closure. Previously dispatched cargo could still arrive. The harness sampled daily inventories, store stockouts, unmet and disconnected household food demand, prices, CPI, wages, payroll, employment, retailer margins, household wallets and hardship, upstream inventories, population, money, and goods accounts.

Each interruption/recovery history replayed exactly from the same save. Daily town validation and retailer statements reconciled; total money drift per 240-day run was below one cent, and commodity-account errors stayed below 0.000000002 goods units.

## Observed outcomes

- **Settlement:** The connected control had 43 empty-store-days and one day of unmet food (17 units) in its first 120 days, but no townwide stockout. During the import pause it had no empty-store or unmet-food days: local stocks and cargo already in transit buffered the new-order interruption. Grocer stock fell 2,539 to 899 units. Retail food price fell $4.65 to $3.88 and wholesale food price $3.14 to $2.90; employment rose 98% to 100%, average wages $32.58 to $32.85, and hardship stayed zero. Once imports were restored, grocer stock rose 1,107 to 2,547; there were no unmet-food days.
- **Regional town:** The connected control experienced 430 empty-store-days, one townwide stockout day and 74 unmet-food days (28,107 units) in its first 120 days; hardship stayed zero while employment stayed 100%. In the import-pause arm, there were no empty-store or unmet-food days; grocer stock fell 6,453 to 4,601. In recovery, stock rose 4,397 to 10,453, with eight empty-store-days and six unmet-food days (318 units). Employment stayed 100%, hardship stayed zero, while the low-wallet household measure declined from $521 to $406.
- **Prices and wages did not rise monotonically during the import pause or observed shortages.** In the regional intervention, retail food fell $4.20 to $3.83, wholesale food $3.14 to $2.91, and CPI 92.3 to 90.7 during the pause; all fell further by the end of restored trade. Average wages rose modestly ($31.63 to $32.00, then $32.08 to $32.30). Retailers' aggregate reported margin remained positive. These are model outputs, not claims about real-world inflation dynamics.

## Interpretation and limit

In these two histories, disabling new import orders was not a reliable way to induce scarcity: local production, reserves, and already-dispatched cargo dominated, and the connected control's regional seed had substantially more food hardship. Restoring imports replenished regional retail stocks, but did not create a price spike in this sample. Food availability is not directly reflected in the CPI formula: it uses grocer prices (55%), rent index (25%), and a fixed remainder. A falling CPI can therefore coexist with unmet food demand, as the regional control shows. Players need to consult food availability and hardship alongside CPI.

No runaway price/wage loop or conservation defect was confirmed, so no production coefficients were changed. Two seeds cannot establish general balance. The test did not simulate physical road topology failure; roads stayed connected in both arms. The full daily results preserve the trajectories for later multi-seed and actual-route interruption testing.
