# Frozen hour result and current civic/renewal persistence checks

Frozen 662ec6f acceptance terminated PASSED after 3603.13 seconds: 2580 operations,
590 cold reloads, 151 exact replays, 336 malformed imports, 85 adoption faults,
107 quota recoveries, 100 corrupted-primary recoveries, 56 both-store denials and
105 stale callbacks. It reached day 7572 with zero recorded errors/replay failures.
Final cash drift is $0.000178. All 60 late sampled archives remain private with a
published hash-only manifest. Original source attribution is unchanged:
abe9c4bbdd86f8c2b9a3776d2996e2c32803f4dd0521791d25ba90cf6c398882.
The backend no longer retained the old process handle; terminal COMPLETE marker,
passed receipt and unchanged asset hashes were inspected, rather than inventing a
new observed exit code. This old checkpoint is not current-main acceptance.

Current-main read-only testing is on 6e8665e, assembled SHA-256
852b9950845a6563c600be5eced6188e11edeccda495ec778ca3f4ebe3e9ff61.
Existing civic-calendar, closed/active-industry compensated renewal/player path,
procurement-group/cancellation/arrival and legacy-tenancy tests pass. Source-bound
receipts are under docs/evidence/save-current8. No validation defect was found or
production code changed.

The new actual-HTTP test tests first save and paid scheduled/active/cancelled civic
states through real local/IDB save, document reload, Continue and injected failed
adoption. It retains the established hour harness's physical-cold comparator:
traffic/visual and service/road/stat reports are transient, while all physical and
financial records—including calendar paid cost and cancellation—must match. Its
failed-adoption check still compares the full exported archive and RNG exactly.

The initial diagnostic additionally compared all cached reports and recorded the
expected hydration nulling of service reports and road cache, plus cached
stats.townBalance refreshing after the paid preparation. Treasury/account records
were identical. This is not relabeled financial corruption or a full-cache cold
identity pass; no existing canonical/economic-replay assertion was weakened.
The calendar and procurement suites separately retain their existing exact replay
and no-payment-on-repeated/stale/cancelled action assertions. A future full-hour
combined acceptance is still needed for current main.
