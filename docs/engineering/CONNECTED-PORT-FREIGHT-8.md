# Connected Greyhaven river freight

## Why this connection exists

The three-city audit found a structurally narrow port role: wharves served old spot exports, while named regional imports/contracts only used road depots. New wharves competed for that narrow stream. Greyhaven now offers actual river import/export consignments through staffed navigable wharves, using the existing owned-stock, prepaid-carriage, delayed-invoice and recovery engine. Other named regions remain road counterparties.

This is a strategic transport alternative, not a port bonus. Water saves some long road haulage but adds voyage time and ties up cash/inventory. Some firms still have cheaper road quotes. Outside demand/capacity, firm cash, working stock, attending crews and queues remain bounded. The original 120-unit consignment bound and market-wide daily capacity remain; roads and boats share that buyer limit. No subsidy, guaranteed order or automatic recapitalization is added.

## Engine and account contracts

* `regionalQuote(f,market,good,direction,forcedDepot)` can return `mode:'river'`, `waterPath`, `outsideDays` and a wharf firm ID as `depot`. `path` is the real collection/delivery road between firm and pier, not an invented truck loop to the eastern highway. Water remains restricted to Greyhaven.
* Existing staged orders own stock until actual arrival/return. Imports pay invoice, tariff and carriage once. Exports remove owned stock and pay carriage now, but receive buyer cash and contract credit only at actual successful settlement. The ordinary claims/estate/default paths remain active.
* Paid dock handling comes from prepaid carriage through the existing outside account. Each actual processed unit earns the existing $0.10 fee once. New loads and old spot exports share the original 600 units/attending-worker capacity (with its existing scale factor). Daily counters reconstruct already-handled consignments before spot exports; fisheries retain original preparation after payroll rather than freezing yesterday's fishing crews.
* Water rate assumptions are explicit game coefficients: normal road collection $0.003/tile, existing-style river distance $0.0005/tile, $0.10 handling and $0.008/outside day. They are simulation assumptions, not empirically calibrated shipping prices.
* Optional river metadata is validated on active and retained recent records. Wharf IDs without river metadata, stray water fields, bad routes and invalid voyage dates reject atomically. Cleared historical ports may retain bounded recent records; active paid cargo already prevents land clearance.
* Paid queue transfer can switch water cargo to a road depot and clears water metadata. A closed dock cannot quote new loads. Interrupted existing cargo can return/recover through actual supplier cash/receivables. Capacity/claims do not mint money.

## Stable graphics/UI interfaces

`portCargoPoses()` returns `{id,port,good,qty,path,started,duration,inbound,stage}` for the **local river leg** of real outside-stage consignments. Sea-leg cargo is hidden beyond the outlet. IDs remain consignment IDs; graphics never settle stock/cash. New bounded actors use the existing boat painter, do not create duplicate legacy manifests, stop at far zoom/reduced motion and remain stable while paused.

`portFreightProspect(f,good,direction,wharfId)` returns current `water`, `road`, `units`, `reserve` and `handling` comparisons. Quote reads do not change the town; a regression compares all serialized town fields before/after. It is a current staffed-port comparison, not a promise about an unbuilt dock's future workforce or demand. Use existing wharf costs/receipts and actual new-site access when integrating replacement advice.

The Economy's existing logistics office adds “Prefer Greyhaven river freight”; automatic still compares quotes. A collapsed river office shows real competing docks, crews, receipts, expenses, break-even cargo, collection quotes, travel days and reviewed enterprise-paid loads. Larger dock receipts alone do not establish town-wide welfare; other markets can offer different commodity prices. Manual orders can compete with future local supply/agreement needs. The direct regional-exchange dialog preserves the existing transaction path; the generic council settlement path must not add a second commodity entry.

## Final-source checks and outcomes

The actual-control bulk test reviews eight real orders without grants, observes their river/sea/road stages and real arrival, and compares exact cold continuation. A first real archive round trip normalizes the existing empty Council list before this strict continuation check; no compared financial/physical field is removed. Cash/goods books pass throughout. One observed day uses the full 1,200-unit dock capacity, earns $120 handling against about $80 actual expenses, and is profitable; quieter sampled days lose money. This is not a guarantee of sustained profit or an instruction to order unwanted stock.

Controlled tests retain early cancellation, a starved-capacity queue, paid road transfer, closed-dock recovery, owned export/deferred settlement exactly once, malformed-voyage rejection and quote purity. Fault injection is labelled controlled; it is not claimed as an organically occurring congestion history. Existing logistics/recovery, 90-day trade, composite-save and core gates pass. Real boat presentation checks show zero distant actors, bounded near actors, exact paused poses and unchanged economic state. A current screenshot was inspected.

Two seeds then run both actual route-policy controls for six ordinary months, with no population/cash/stock grants and no forced wharf success. The standard step helper resolves Council letters through normal first-affordable choices. These are accelerated automated histories, not human six-month sessions or isolated causal estimates. All sampled records/cash/goods validate. Final-day results:

|Seed|Route policy|Wharf receipts/day|Actual costs/day|Net/day after tax|Wharf cash|
|---|---|---:|---:|---:|---:|
|42|interchange|$79.18|$91.69|$-12.51|$13722.55|
|42|river|$110.76|$91.69|$16.78|$14202.17|
|101|interchange|$87.66|$97.11|$-9.45|$18111.81|
|101|river|$110.26|$98.10|$10.70|$19237.19|

Endpoint profit is not cumulative profit. Seed42's river wharf still has less cash than its initial funding despite a profitable final sampled day. Older quiet-day losses and firms with cheaper road quotes are retained. A second port is not automatically justified; competition can still leave it underused.

The isolated 2,000-resident/21-deed/48-route evolving host profile measured near/far59.2x/65.2x at requested64x, draw P9528.2/21.7ms, RAF P9983.4/83.4ms and touch maxima156.8/195.2ms. These short observations do not supersede the ongoing negative full-session evidence or certify Android smoothness.

Source SHA256: `f7344d229358570ba03282cd42f910911989b7dc21ff697731e6f9a271848539`. Exact receipts are embedded in `reports/integration/8-connected-port-freight.json`. No new APK or final-quality claim. District-followthrough UI, native changes, migration/legacy tenancy and longer performance acceptance remain separately pending integration.
