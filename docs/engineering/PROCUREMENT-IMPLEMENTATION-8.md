# Staged regional procurement

Implementation base: f26bbe0727ec686a1bc4f5d82bd39fb03120dc14 and its approved PROCUREMENT-GROUP-CONTRACT-8.md.

Economy now offers named regional development orders: 50 units arriving within fifteen days, followed by 100 within thirty days. The second dispatch window opens at the first deadline. Players can instead retain the existing single thirty-day agreement. Both use the same commodity-specific market price and existing premium; no new bonus, reward, escrow subsidy or simulated foreign wealth is added. The quote explains stock retained locally, shared freight outlay, uncertain production and capacity, and competing domestic buyers. Ineligible orders explain the blocked combined forecast rather than silently authorizing one stage.

`reviewRegionalProcurement(spec)` is read-only and returns a town/day/state/RNG-bound review plus an immutable-spec fingerprint. Shared stock, output, freight liquidity and a conservative common handling envelope are checked cumulatively. All outstanding commitments are deducted conservatively, including other producers/commodities: this may understate capacity rather than advertise independently usable capacity twice. Forecasts do not reserve real future production or loading capacity. Actual daily dispatch retains existing shared handling and market bounds.

`authorizeRegionalProcurement(review)` rechecks eligibility, available slots and the complete review before allocating both IDs/contracts together. It also serves ordinary single agreements. Failed/stale/repeated approvals leave state unchanged. Both ordinary contract records carry group/stage/window references, so no parallel financial ledger exists. Two milestones consume two of the existing three active slots. Whole completed groups are pruned together; groups referenced by travelling cargo cannot be pruned. Archive validation rejects orphaned or inconsistent groups while accepting legacy ungrouped agreements.

`cancelRegionalAgreement(id)` stops all active siblings. Fulfilled or missed outcomes remain truthful. Shipments, carriage charges, refund claims, assets, liabilities and eventual arrivals are preserved. Existing record cards show milestone outcomes from successful deliveries; there is no persistent reliability score or earned price/eligibility bonus inferred from prunable history.

Validation on the final assembled source:

- `tests/test_procurement.py`: pure review; invalid second stage and combined-slot rejection; stale and repeated approval rejection; delayed second-stage dispatch; group cancellation without cargo deletion; malformed orphan import rejected atomically; actual two-stage fulfillment; cash/goods conservation; exact archive continuation/replay.
- `tests/test_supplier_selection.py`: existing buyer/commodity/producer controls, stale review, cancellation and real food commitment remain working.
- `tests/test_port_freight_faults.py`: river closure/return, shared handling, paid road transfer and delayed buyer settlement remain working.

Evidence: docs/evidence/procurement8. Initial test expected cancellation to erase a fulfilled stage; that incorrect expectation was fixed and the failure retained. No release or Android performance claim. Broader large-city procurement balancing, all market/producer combinations, and a persistent buyer-reliability system remain outside this bounded implementation.
