# Regional logistics: state and integration contract

This is an integrated economic state machine, not decorative vehicle queues. `src/26-logistics.js` owns the new behavior; existing regional goods ownership and cash accounts remain authoritative. Development release remains 8.0.0 / code 22 / schema 7.

## Shipment lifecycle and accounting

Trade-state version 2 upgrades version-1 consignments without rewriting already agreed ownership or invoices. New imports pass through origin preparation, outside travel, local collection, depot unloading and final delivery. Exports pass through company collection, depot loading, local departure, outside travel and buyer payment. Trucks are hidden during genuinely outside travel; stopped handling queues are visible at staging points. The visual API never settles money or goods.

A consignment is capped at 120 handling units. Named-market daily limits still apply, rechecked when accepting the order. Staffed connected warehouses provide 120 handling units per worker/day; interchange crews provide 500. Ready export and import queues share actual daily handling work. Carriage includes a handling allocation; only work performed earns a warehouse receipt, paid from the existing regional carriage account, not another charge to the enterprise.

Imports are paid at booking and remain town-owned in transit. Exports remain supplier-owned and receive payment only on successful outside delivery. Unfunded buyers wait; they do not mint receipts. Inventory reorder points now include quoted transit/handling lead time instead of using the old instant-import safety stock. Working capital still limits purchases.

Cancellation is a request at the next staging point, not an instant stock refill. Early imports recover invoice/duty with prepaid carriage retained. Later supplier returns recover 90% of invoice; duty is retained after actual border entry. An unfunded refund becomes an explicit financial receivable, freeing the physical order pool without inventing cash. Claims settle from actual regional/treasury cash. Export recall returns the same owned goods. A 30-day road failure uses a disclosed 70% reference-price recovery sale rather than teleporting supplies back to the company. Late estate receipts pay recorded defaulted creditors before the former shareholder; nonresident shareholders receive proceeds through the outside-region account.

## Mayor choices

The optional depot-operations disclosure in Economy exposes balanced, essential-input/food and agreement priorities. Routing can compare queues automatically, concentrate new orders at interchanges, or prefer staffed depots. Existing paid routes are not silently rewritten. A waiting consignment can be transferred to another connected depot with real extra enterprise carriage and transfer time.

A temporary extra interchange shift buys up to 300 handling units/day at $0.36 per unit actually needed, at most $108/day for 30 days. Empty queues cost nothing; future shifts can be stopped. This is a municipal reliability purchase, distinct from a privately staffed warehouse investment. Authorized reserve forecasts include the contingent commitment.

## APIs for gameplay and graphics

- `ensureRegionalTrade()` returns version-2 state, including `shipments`, bounded `recent`, `contracts`, `claims`, `priority`, `routePreference`, `handling`, `reliefUntil`, `delivered` and `cancelled`.
- An order retains `path` (full itinerary), `stage`, `activePath`, `stageStarted`, `stageDue`, `stageDays`, `depot`, `depotIndex`, `handled`, `principal`, `tariff`, `freight`, `cancelRequested` and optional `estateOwner`.
- `regionalShipmentVisualState(order)` returns visible/hidden, active road path, stage clock/duration and parked status. `shipmentVisualPose()` in the freight art module consumes this projection; do not revert it to the full order clock or paint outside travel on interior streets. Far LOD still exits before pose work.
- `regionalQuote(f, market, good, direction, forcedDepot = null)` includes depot routing, freight, estimated time and queue terms. `dispatchRegional` returns actual accepted quantity, at most 120 per call. Callers requesting a larger commitment must use multiple real orders over time, not assume the requested amount was accepted.
- `cancelRegionalShipment(id)` requests a valid recall; `rerouteRegionalShipment(id,depotId)` accepts only a waiting handling stage, a real connected alternative and sufficient enterprise cash.
- `regionalHandlingCapacity()`, `regionalLoadingLeft()`, `logisticsDepots()`, `logisticsQueue(depotId)` expose real operating limits. `G.cumulative.logisticsSupport` records actual extra-shift spending.
- **Arrival notification:** `settleRegionalArrival()` calls `civicProjectRecordArrival(order)` only after successful usable import delivery or paid export delivery. Cancelled, recalled, salvaged or merely removed orders must never count as project arrivals. Remove any older before/after-removal observer when integrating civic projects.

## Spatial and passenger-network integration

Urban expansion must remap tile IDs in **both `path` and `activePath`**, and the corresponding arrays in recent shipment history, using immutable copies from the old grid. `depotIndex` is an array index and must not be remapped. `depot`, `firm`, `contract` and claim beneficiary IDs refer to institutions/people, not tiles. The route caches belong to the current graph; invalidate roads/topology after changing dimensions. Do not keep cached geometry if the world projection changes without replacing path arrays.

Freight uses road routes and gateways. Passenger bus/rail accessibility must not make trucks traverse passenger-only links. Private service recruitment/access currently has a separate road-distance interface described in PRIVATE-SERVICES-8.md; integrate passenger access and actual fares explicitly rather than silently extending free coverage.

## Evidence

Targeted tests verify physical stages, early/late cancellation, unfunded refund recovery, export recall, defaulted-creditor estate recovery, exact cash/commodity conservation, archive validation, actual agreement controls and the mayor journey. A controlled, fully paid peak-arrival fixture compares real operations choices: the food consignment arrived on day 15 with balanced queues, day 13 with essential priority and day 14 with an extra shift. The intervention branch then ran six months with actual report visits, stopped extra shifts and restored automatic routing: zero unmet food, 100% employment, zero hardship, no pending refund claims and conserved cash at day 202. This is a controlled intervention test, not a claim that every player town or device performs identically.

Final integration still needs the new civic-project arrival observer replacement, the queued provider/night/district art commits, dense-city retiming and extended malformed/archive/active-play coverage. Existing 7.1.1 APK/source artifacts remain untouched.
