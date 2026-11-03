# Reviewable retail-centre proposals

The planning-office action **Invite a shopping centre proposal** first presents a read-only review. It names the vacant connected six-tile site, nearby grocers, resident catchment, a simplified, competition-weighted food-demand proxy before and after adding a centre, proposed staffing/wage, estimated net per day, and regional construction/working-capital commitment. The proxy counts existing centres double; it is a comparison aid, not actual customer orders or a profit guarantee. The review states that the centre redistributes current household food spending rather than creating new household demand. Actual household purchases still respond to price, travel, inventory and capacity.

Approval reruns the full site/market search against a review key covering the simulation day, regional funds, neighbourhood-plan revision, road graph, homes, existing grocers and proposed economics. A stale quote makes no commitment and asks the player to review again. Cancelling is byte-for-byte save-state read-only. The preview restores the simulation RNG consumed by the normal site-ranking tie-breakers; automatic monthly proposals keep their existing RNG sequence. Approval uses the existing regional-investment accounts: $44,000 construction and $28,000 escrowed operating capital, with no municipal charge.

The proposal remains confined to one vacant, connected 3 × 2 footprint permitted on every tile. It does not clear title-held homes, shops or productive farmland; protected plans reject the footprint. A centre remains a private, staffed grocer project with actual inventory, payroll, customer trips and receipts. The forecast gives no customers, new spending, free jobs or guaranteed operating profit.

The new no-site diagnosis counts candidate footprints through the actual gate sequence: vacant, permitted, connected, adequate/uncrowded catchment, reachable staff and expected return. It gives the first failed stage rather than prescribing a non-existent “mixed centre” zone. This was verified against the natural seed-42 regional city save at day 1081. After 40 unassisted days it had 868 residents, two existing centres, and 39 vacant, permitted, road-connected six-tile sites, but zero sites with 180 residents within 24 road steps and adequate uncrowded demand. It now recommends growing homes near an underserved district. The forecast did not mutate that save.

The confirmed UI path used a controlled demand fixture to reach the proposal threshold; it did not add money, goods or retailers. Before approval, no project or capital commitment existed. Approval opened a 65-workday private project with six footprint tiles, $28,000 operating escrow and an eight-worker/$28 daily wage offer. All four existing small grocers, resident addresses, existing titles and crop rights were unchanged; the surveyed centre site had 534 residents in its 24-road-step catchment, no existing grocer nearby, and all six tiles were road-connected, vacant and on market-plan ground. Town cash totals remained conserved and the following two days replayed exactly after save/restore. Existing natural retail labour validation separately checks actual staffing, payroll and operating receipts without double-counting public workers.

Verification:

```
python tools/assemble.py
node --check assets/game.js
python tests/test_retail_proposal_review.py
python tests/test_urban_planning_boundaries.py
python tests/test_retail_labour_viability.py
python tests/test_urban_trajectory_checkpoints.py
python tests/test_urban_evolution.py
```
