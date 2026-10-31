# Bounded shock acceptance

Production source: cc8631158cb004a8e4c26dead85df66f6b4468e8.
Game SHA-256: 3570ef6e14dbd08908232955768f355b198c1c869021289204825cd952d038ed.

Eight histories use settlement seeds 42 and 101, each with the same ordinary 240-day provider setup and 540 subsequent days. Private schools and fire providers enter through actual investment proposals, construction escrow, qualified workers, fees and vouchers. No skills, cash, stock or residents are granted. Treatments: baseline funded services; 20% benchmark/100 underwriting with one explicitly forced receivership, restoring opening credit policy after 180 days; six months without school/health/fire/police/road/voucher authorizations followed by funded recovery; or a synthetic landing-road interruption for 60 days followed by actual paid road construction. The road fixture dispatches paid river and road imports before cutting the approach. These are controlled disruptions, not forecasts of real disasters.

All eight histories complete with valid archives and round-trip, daily demographic identity, no missing/unregistered/overcapacity households, conserved cash and goods. Maximum endpoint cash drift is below 0.000017. No production changes or coefficient tuning were made.

| Seed | Arm | Final residents | Health | Education | Treasury |
| --- | --- | ---: | ---: | ---: | ---: |
| 42 | Baseline | 190 | 88.8 | 65.4 | 170687 |
| 42 | Bank / credit | 201 | 88.7 | 65.2 | 182911 |
| 42 | Service cut / restoration | 209 | 75.8 | 58.3 | 358937 |
| 42 | Road / paid repair | 202 | 88.7 | 65.2 | 204311 |
| 101 | Baseline | 218 | 88.6 | 65.2 | 136899 |
| 101 | Bank / credit | 218 | 88.6 | 65.1 | 147957 |
| 101 | Service cut / restoration | 215 | 75.9 | 58.2 | 256134 |
| 101 | Road / paid repair | 208 | 88.5 | 65.1 | 119847 |

The service cut has lasting human-service consequences even after restoration, while retaining more public cash. It does not induce mass departure in these already-funded households. Receivership pays all deposits in these solvent-bank fixtures: deposit losses and insurance payouts are zero. Therefore the bank arm proves closure, remaining-bank credit and continued growth; it does **not** prove recovery from deposit losses, a systemic bank failure, or a recession. No funds were replenished to obtain recovery.

Both interrupted-road runs record actual stranded-cargo recovery receivables, later deliveries and zero outstanding refund claims at the endpoint. Cargo is not counted as delivered merely because it was recovered financially. Repair purchases the missing Landing Lane road through `construct`, rather than restoring cash or directly granting a road. These histories do not isolate every effect of the extra paid imports from the road disruption.

Additional existing focused suites passed on this same source: `tests/test_logistics.py` checks early/late cancellation, finite unfunded refund claims, export recall, closed-firm estate recovery paying defaulted creditors before shareholders, cash/goods and malformed archive rejection. Its debtor-default fixture explicitly creates a funded synthetic loan and temporarily funds carriage; it is accounting evidence, not legitimate player recovery evidence. `tests/test_port_freight_faults.py` checks paid water-to-road transfer, shared handling limits, dock closure recovery, delayed export settlement exactly once and archive rejection. Its controlled dock reopening is not a player recapitalization claim.

Reproduce histories with `python tools/acceptance_shocks.py`. Evidence and retained negative policy outcomes are in `docs/evidence/shock-acceptance8/`. No serious correctness defect was reproduced. Limits: two modest city seeds, no all-bank failure or household deposit-loss crisis, no Android performance claim. Outside migration alternatives remain labelled founding-policy references, not simulated foreign cities.
