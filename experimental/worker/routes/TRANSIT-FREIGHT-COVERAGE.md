# Transit/freight disabled worker family acceptance

Central hooks: 2c316f6; unchanged assembled economic source, exact hashes in each receipt. Original acceptance covered22 finite operations; the presentation follow-up adds3 for25 total; these are semantic operations, not a percentage of raw handlers. Every row below has a successful trusted actual UI journey against the same unmodified synchronous source, with complete committed model/RNG equality and original save barriers.

| Operation | Actual UI evidence |
|---|---|
| draft-start | ui: New Bus and second draft |
| draft-tap | ui: trusted canvas stop taps |
| draft-config | ui: level selects 2 then 1 |
| draft-map | ui: Pick Stops and panel closure |
| draft-undo | ui: Undo and replacement stop |
| draft-quote | ui: cost review and refreshed stale quote |
| draft-build | ui: paid bus build |
| draft-cancel | ui: cancel second draft |
| level | ui: suspend and resume |
| retire | ui: fleet retirement/salvage |
| remove-site | ui: unused paid depot salvage |
| remove-guideway | guideway: unused paid elevated track salvage |
| relief-review | ui: actual review and authorization |
| stop-relief | ui: stop authorization |
| priority | ui: essential dispatch |
| routing | ui: river preference |
| cargo-cancel-review | ui: paid import recall |
| procurement-review | commerce: day31 two-milestone timber order |
| agreement-cancel | commerce: grouped cancellation |
| offer-review | commerce: supplier agreement |
| port-review | commerce: actual paid river consignment |
| cargo-transfer-review | transfer: paid backlog transfer |
| report | ui: expanded real demand/funding report |
| hide-report | ui: report removed |
| overlay | ui: transit overlay toggled both ways |

Runners: `transit_freight_ui_test.py`, `transit_freight_commerce_test.py`, `transit_freight_transfer_test.py`, `transit_freight_guideway_test.py`. Their JSON receipts include source/worker hashes, exact checkpoints, town validation and money/goods checks. Separate direct DTO and parity runners retain malformed/no-op/absent target rollback.

No resource injections. Commerce fixture evolves seed42 through30 ordinary days. Transfer reuses the existing paid peak-arrival fixture, which dispatches actual inventories and advances freight time to create congestion; it is a controlled backlog, not ordinary-day history. Natural commerce continuation produced no transferable queue over20 days; that unavailable outcome is retained in prior diagnostic notes, never counted as a transfer pass. Guideway fixture buys depot/stations/elevated route from ordinary treasury and retires its fleet before testing actual unused-track removal.

The UI runner injects only writer failure: failed persistence leaves the actual economic retirement committed, explicitly unsaved, and the old stored envelope unchanged. Retry through actual Save acknowledges persistence without another model mutation. The commerce runner repeats the actual paid river choice token and asserts unchanged archive refusal. UI runner advances a real day after transit quote, attempts stale build (no payment), then refreshes and builds. Native durability is not certified.

Remaining limitation outside these25 registered operations: original Show Route needs a camera effect that preserves main zoom and uses zero vertical offset; current camera-grid forces a supplied zoom and adds25 screen units. Report/hide-report and overlay now use existing hooks and have exact no-authority-mutation checks; there is no completeness claim for every raw handler or overall worker release. Freight routing/priority refresh closes Depot Operations rather than preserving original open state; central owner has that confirmed presentation defect. Tests reopen through actual summary clicks. Completed river return/refund travel and exhaustive adversarial failure matrices are not implied by dispatch/recall parity. Production remains disabled.
