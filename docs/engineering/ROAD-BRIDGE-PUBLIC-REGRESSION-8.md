# Current-public bridge and road regression

Regression target: public `codex/townledger-7.0.1` commit `ecbc945c4aeeb99d27d0cf7b7cd8ee63651af785`. This is a current-source check, not a replay of the older bridge integration candidate. The test harness pins the assembled gameplay source SHA-256 recorded in `docs/previews/urban8/road-bridge-public-regression.json`.

The deterministic seed-42 East Meadow fixture uses the existing five-cell lake span. The live council and map controls were used to cancel and then authorize the $13,450 bridge quote ($12.50 daily upkeep). Cancellation preserves the economic/model state and RNG; the expected council decision, journal and inbox records are appended, and the lazily computed road-metrics cache is initialized. The separate road-retirement review was canceled with no model or ledger change beyond the same review-history/cache effects.

Current source rejects a span when its bank deed is absent, a waterway cargo manifest crosses the work zone, or a building footprint overlaps the deck. Reversible test fixtures were removed immediately after each check. The failed-tick recovery guard rejects new bridge work, repair, decommission and road retirement without changing the archive. With municipal cash moved into the regional reserve, 215 underfunded maintenance calls lower bridge condition to 24.75%, close the road surface and preserve water-network continuity without changing total money. The repair review can be canceled without game-state mutation; authorizing it without funds leaves the bridge closed. Reallocating reserve to municipal cash and approving the live repair restores condition to 100%, reopens the road graph and leaves total funds unchanged.

The paid East Meadow farm import was followed until day 4, when its shipment reached `delivering` with all five bridge tiles on its active path. The game refuses decommission while that paid consignment is crossing. Saving and loading the mid-delivery archive preserved the stage, path, bridge and money; the combined town validators remained clean.

Automated checks passed:

- `python3 tools/assemble.py` and `node --check assets/game.js`
- `PYTHONPATH=tests python3 tests/test_road_bridge_public_regression.py`
- `tests/test_road_bridge.py`, `tests/test_road_removal_network.py`, `tests/test_road_bridge_art.py`
- `tests/test_transit_network.py`, `tests/test_regional_trade.py`, `tests/test_save_composite.py`, `tests/test_cold_continue_canonical.py`

The canonical cold-continue check passed exact continuation equality with four traffic vehicles and stable legacy trade defaults. Bridge art/UI current-public tests passed. No production code or graphics were changed by this regression slice.

Limits: this covers the one naturally feasible East Meadow span and seeded simulated navigation/shipments, not a live externally controlled multiplayer environment or every possible map. The redundant-crossing survey rule remains as implemented in this public revision; this test did not alter its economics or siting policy.
