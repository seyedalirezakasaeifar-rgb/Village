# Staged procurement scaffold — review boundary

Based on 1cf6af50b66904e5d208e1a3af00d85051aa3b9f. This commit adds an unmounted read-only planner and preview renderer. The assembled game is unchanged. No contracts, cargo, saves, cash or prices are mutated.

`regionalProcurementPlan({day,quantity,stock,reserve,production,existing,freight,cash,journeyDays,dailyCapacity})` returns two milestone forecasts (day+15 and day+30), shortfalls, shared freight requirement and explicit uncertainty. Output and stock available by the final deadline cannot satisfy an earlier deadline retroactively. Both milestones share one stock buffer, production forecast, loading envelope and wallet. Existing commitments are conservatively deducted once. Forecast capacity is not reserved future capacity. The preview explains these actual differences; no new action button is mounted yet.

Proposed reusable authorization signature for lead approval:

`authorizeRegionalProcurement({town,reviewDay,stamp,firmId,marketId,good,milestones:[{quantity,deadline},{quantity,deadline}]}) -> {ok,reason,contractIds}`

Required implementation: recompute quote/stamp and all eligibility before changing state; validate both quantities, deadlines, market commodity, supplier output and two available active-contract slots together; establish the single existing market-priced quote without a new premium; preflight retained-history pruning; allocate both IDs and insert both contracts atomically. Any rejection leaves serial/history/contracts unchanged. Do not reserve stock a second time: existing dispatch sums both ordinary commitments. No settlement hook is necessary. Group metadata should contain only a group identifier, index and milestone count; archive validation must require a complete consistent pair, including cancelled/completed members. Group cancellation must change active future dispatch statuses together while leaving shipments and liabilities alone.

Open review decision: the existing 24-contract retention limit must evict whole completed groups, never half a group. Do not derive persistent trade reputation solely from this bounded history: eviction would erase earned reliability. Initial version can display observed milestone reliability, explicitly limited to retained records, with no eligibility or price reward. A persistent reputation mechanic requires separately approved schema policy.

Shared files pending lead review: src/98-trade-ui.js (authorization extraction and controls), src/98-alternative-suppliers.js (review stamp coverage), src/26-logistics.js (whole-group retained-history behavior only if authorization cannot own it), src/90-archive-panels.js or existing regional validator (metadata consistency). No edits to these files are included.

`node tests/test_procurement_planner.cjs` passes shared-stock/cash/handling limits, early-deadline failure, prior promises, immutable inputs, invalid quantity, deterministic replay and preview. Integration tests still required after authorization approval: atomic rejection with only one free slot, stale quote and load replacement, no partial serial/history mutation, group cancellation with in-flight cargo, completed/missed pair retention, malformed archive rejection, cash/goods conservation and actual successful/failed delivery histories.
