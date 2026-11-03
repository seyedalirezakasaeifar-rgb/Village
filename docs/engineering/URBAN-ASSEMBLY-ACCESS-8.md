# Land assembly: commuting, civic access and farm losses

The land-assembly review now selects an affordable vacant home only when each currently commuting tenant can still reach their existing job from that address using the live passenger/road access check. The review records the selected destination, marks a reserved municipal replacement as such, and reports the nearest public clinic and school road distance against their modeled range. This is a proximity disclosure, not a promise of staffed capacity or funded service; the dialog says coverage is assessed separately. If every affordable home would strand a current worker, clearance is refused with an actionable access explanation.

For active farms, the confirmation names the permanent closure, number of productive crop plots relinquished, tracked recent grain output when present, stored grain liquidation and jobs ending after severance. Clearing a farm building is not described as relocating the farm. The existing protected-title purchase and farm-renewal actions remain separate. Cancellation leaves the transaction's property, people, titles, inventories and accounts unchanged. Actual clearance preserves residents as residents, pays the quoted compensation/severance, and leaves road and transit networks intact.

## Real-control evidence

The seed-42 settlement was played through the map inspector and normal confirmation dialogs. First, an affordable farm with five productive plots was reviewed and cancelled; its buildings, firm, titles, accounts, inventories and resident records matched the pre-review transaction state. It was then cleared for its ordinary quoted cost. The farm closed, all five field titles were released, its workers remained resident (with jobs ending under the existing severance rules), road and transit networks remained byte-identical, and money/goods balances passed validation.

In a fresh run, the mayor paid for a municipal replacement dwelling through Public Works and let the ordinary simulation build it. The subsequent occupied-home review selected that reserved dwelling, showed two extant worker commutes as reachable, and reported clinic and school access at seven road segments each. Clearance moved the household without creating or losing residents; the reserve was consumed, road/transit state remained unchanged, and money balances validated. Both changed worlds passed exact 30-day archive/restore continuation (normalizing derived zero field counts and transient vehicle/render state).

The test's read-only-cancel check compares transaction-affected persistent records. Opening an inspector can lazily compute road metrics and derived approval values in the archive; those derived entries are not mistaken for a paid or destructive land transaction.

## Verification

```
python tools/assemble.py
node --check assets/game.js
TOWNLEDGER_USE_HTTP=1 PYTHONPATH=tools/browser_http_adapter:tests python tests/test_urban_assembly_disclosure.py
TOWNLEDGER_USE_HTTP=1 PYTHONPATH=tools/browser_http_adapter:tests python tests/test_transit_combined_redevelopment.py
TOWNLEDGER_USE_HTTP=1 PYTHONPATH=tools/browser_http_adapter:tests python tests/test_urban_evolution.py
```

The screenshot and machine-readable scenario result are in [`docs/previews/parcel-growth-outlook`](../previews/parcel-growth-outlook/).
