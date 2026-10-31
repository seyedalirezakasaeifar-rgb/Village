# Pending paid-review handoffs

Paid confirmations now bind the displayed site, stage, quote and town to the action. If those records change before authorization, the action asks the mayor to review the current quote again. The land-assembly dialog rechecks its full compensation quote; neighbourhood plans recheck the target property, register entry and fee; brownfield steps recheck the current site, stage and displayed fee.

The reviews identify the actual parcel, neighbourhood or business and its map position. After a panel refresh, focus moves to the resulting district, planning section, or brownfield office. A successful archive restore now refreshes the open report, closes pending transient UI through the existing save hydration path, and puts focus on the panel close control.

`tests/test_pending_review_flows.py` exercises the actual controls at 844 × 390. It checks Back/cancel, a second parcel, a report/selection interruption, simulation ticks during the modal, exact ordinary-treasury debits, repeat authorization, plan/assessment targets, and loading another town during a pending deed review. The focused test plus `test_review_workflows.py`, `test_urban_planning_boundaries.py`, and `test_brownfield_player_path.py` pass. `node --check assets/game.js` and `git diff --check` pass.

`test_annexation.py` still has an outdated assertion that the current map contains 6,400 tiles. The integrated game now has 16,384 tiles (128 × 128); the rest of that run's deed purchase, payment, repeat, road, and home checks passed. This change does not alter the map or economic rules.
