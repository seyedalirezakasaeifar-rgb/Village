# Regional cargo timing and disruption guidance

## Scope

Reviewed public integration `848bf1bfb8fdddc3155ba5a7773348d28073ade4` and its existing regional-exchange and depot-operations panels. Contracts already showed estimated delivery windows, and logistics already tracked shipment stage, last status, stage checkpoint, road interruption, handling queue and buyer-liquidity wait. The gap was that the UI showed only a dated estimate plus a generic status, without the active stage/checkpoint or a next action when a paid shipment was blocked.

The update adds a read-only cargo readout to each depot-operations row and the existing trip inspector. It separates the overall estimated arrival day from the current logistics stage and next checkpoint, labels days past estimate, and explains the actual recorded blocker. A route interruption offers a “Show road access map” button; the advice updates if a road route returns before the next freight check. Existing depot-transfer and cancellation controls remain the choices for handling queues and export liquidity waits.

This does not create deliveries, alter quotes, reroute paid orders, guarantee an arrival time, or change cash/goods rules. Dates remain simulation estimates: later handling, route or buyer-cash disruptions can delay settlement. A route interruption follows the existing 30-day recovery rule and warns the mayor to restore access; the new interface performs no repair automatically.

## Evidence

`tests/test_regional_cargo_timing.py` creates one real, funded 12-unit import through `dispatchRegional`, confirms the inventory is recorded in transit with conserved cash/goods, then reads the actual order in the mobile Economy panel and trip inspector. A controlled road-cut fixture exercises the existing route-interruption state without adding cargo or changing shipment accounting. The test verifies overdue-day updates, the road-access map action, updated guidance after road access returns, archive validation, and unchanged simulation/RNG/cash/goods during projections. The deliberate road cut is a QA disruption, not a claim that players can remove a road beneath protected active cargo.

Screenshots show the actual shipment estimate, the delayed shipment and next step, and the road-access map: `regional-cargo-schedule-mobile.png`, `regional-cargo-delay-mobile.png`, and `regional-cargo-road-access-mobile.png`. The test-result record is `regional-cargo-timing.json`.

Passed `python tests/test_regional_cargo_timing.py`, `python tests/test_regional_trade.py`, `python tests/test_recent_trade_feedback.py`, assembly, Python compilation, JavaScript syntax validation and `git diff --check`. No renderer or simulation-worker source was edited.
