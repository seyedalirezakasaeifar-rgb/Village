# Capacity admission: closure fix, executable frontiers, pending transaction contract

This disabled candidate depends on `1d73dfd`; it is not a completed capacity-safe admission coordinator. No paid-action guard is installed. Production remains OFF. The native Continue fix is independent on `codex/8-native-canonical`.

## Implemented: status-neutral identity bounds

Version 2 admitted up to 24,000 total people but only 16,000 historical people, and 9,000 household/firm IDs but only 6,000 historical entries per category. This was not closed under ordinary life transitions. A valid town containing 16,000 historical people became unexportable when one existing person died; a valid 6,000-estate town became unexportable when an existing household's remaining residents died. IDs and total money were unchanged in both executable reproductions.

Experimental wire version 3 retains version 2's exact representation and TOTAL identity ceilings, and permits historical rows up to that category's existing total ceiling. It does not admit additional total IDs. Versions 1/2 retain their original decoding restrictions and remain readable; old readers reject version 3 explicitly. The shared 8 MiB bytes, 16 MiB expansion, 1,000,000 nodes, 500,000 cells, depth 24, field dictionaries and active-count bounds are unchanged. The `limits.inactive` / `entityInactive` diagnostic values still describe old-version ceilings; current version-3 history is bounded by total / entityTotal.

This closes the demonstrated status-only count failure without deleting records, freezing deaths, releasing debts or increasing total directory allocation. It does NOT guarantee every future status transition fits shared bytes/cells/nodes: new fields and dictionary-index width changes still require future-growth reservation. Encoding/import remains strict and finite. No activation is implied.

## Executable evidence

Assembled version-3 source SHA-256 `7c1b88875d44ebfac4cbdc3e434d46b2e303e3e1052753e39df99f259b30645c`.

- `test_capacity_status_transition.py`: real `yearlyDemographics`, 16,000→16,001 historical people and 6,000→6,001 estates, unchanged total IDs and money. Version 2 failed; version 3 exports. Attempts to relabel those files as version 2 reject without adopting them. Earlier failure reports are retained.
- `test_capacity_budget_frontier.py`: exactly 8,388,607 / 8,388,608 / 8,388,609 UTF-8 bytes, and 999,999 / 1,000,000 / 1,000,001 nodes. Below/at limits accept, above reject without live model, RNG or save-epoch changes. Host valid import times were roughly 66–68 ms for byte cases and 123 ms for node cases; these are stress-import costs, not normal action overhead.
- `test_capacity_record_frontier.py`: 23,999 / 24,000 / 24,001 people, and 8,999 / 9,000 / 9,001 households or firms. Each below/at total accepts and remains self-exportable AFTER ordinary hydration defaults; above rejects atomically. Lean synthetic records exercise the independent record bounds; rich records can hit shared budgets earlier.
- Both codec regression suites pass exact 30-day model/RNG continuation, real 8,000→8,001 and 3,000→3,001 creator actions, every field/reference/asset, old formats 1/2, old release fixtures, regional creditor -1, invalid -2 and malformed summaries.

Reports contain aggregate facts and hashes only, no full saves. The record and node fixtures are synthetic boundary cases, not natural-growth trajectories or Android memory certification.

## Confirmed whole-command blocker

`test_capacity_paid_order.py` invokes the actual UI `construct('grocer', x, y)` at a valid near-byte-limit town. Its second paid construction becomes unexportable: treasury 96,498.782→92,448.782, region 14,648,572.741→14,640,622.741, firms 27→28, next building ID 106→107, RNG 1335636808→3735097094. The last valid archive is 8,388,041 bytes and reloads. This is expected NEGATIVE evidence, not an admission pass.

A guard solely in `createFirm` runs after the parent `construct` debit and regional investment debit. Returning null there also breaks the caller's immediate `newFirm.cash=12000`. A guard in `save` cannot undo all identity, wallet, goods, ownership, cache, queued UI and RNG effects safely. `startDevelopmentProject` records a worksite before financing, and paid construction can finish many days later. A generic "serialize after action, reload old town on failure" wrapper is therefore not installed or described as safe.

## Required synchronous transaction contract

This does not require cooperative simulation, Workers or a scheduler prototype. It requires complete mutation coverage in the ordinary synchronous runtime:

1. Prepare a typed action plan before the FIRST effect. It owns prospective field writes/appends, RNG advancement, money/goods/property transfers, history updates and a UI/save outbox. Plan construction must not run existing arbitrary mutator closures on live G and then attempt undo. UI quotes revalidate before planning.
2. Maintain certified usage plus reservations at a committed boundary. A trusted, audited per-action upper bound charges positive byte/node/cell growth, new IDs and dictionary-width changes. Never credit deletions from guesses. Include serialization of repeated references per path, optional fields and UTF-8 width. Unknown/unclassified growth takes exact preflight; it never receives a zero/default allowance.
3. If certified headroom covers the action plus all outstanding future obligations, admit without full serialization. Otherwise materialize a private prospective logical candidate and use the exact codec/validators BEFORE publishing any writes. Rescan exact usage after a conservative ledger saturates; conservative overcount must not become a false permanent refusal.
4. Commit the prepared write set only after capacity and economic validation. Preserve stable live entity references where existing UI callbacks rely on them, or update every stale-callback contract explicitly. Preallocate arrays/values; no callbacks, payment, save, toast or dialog runs between capacity validation and the atomic synchronous publish. Flush the outbox after final history/RNG are committed. Imports/new towns invalidate pending plans.
5. Reserve future materialization at project/contract acceptance: household/person/firm slots, full commissioned default fields, expected delivery/loan/claim records and bounded completion history. Completion converts an existing reservation; it must not discover a capacity shortage after taking payment. Cancelling a project releases only capacity, not debts/claims. Derive/persist reservation ownership deterministically so reload cannot forget it.
6. Existing identities reserve their worst supported death/departure/estate/demolition representation and bounded history growth. Do not prevent a natural death, discard its estate, or silently omit history to fit. Every authoritative day is admitted before it publishes. If a genuinely exhausted archive cannot support even the next complete day, leave the previous complete town and RNG intact, pause, and explain the format capacity. This is a real resource limit, not a universal cap on births or businesses by historical count.

Suggested user message on genuine refusal: "This town has reached the archive capacity supported by this version. No payment or changes were made. Your last complete town is intact. Export a backup before moving to a version that supports a larger archive." A denied discretionary project can leave other safe activity running; only inability to commit a complete day requires pausing simulation.

## Coverage that must be coordinated before implementation

| Whole mutation boundary | Existing paths requiring the same plan/outbox |
| --- | --- |
| Paid build/clear/upgrade | `70-interaction.construct`, road batches, land assembly, brownfields, transit purchases, civic events and calendar bookings; guard before their first debit |
| Deferred private construction | `40-development.startDevelopmentProject`, financing and completion, farms/fields, towers, airports, providers/malls; reserve at acceptance |
| Automatic population | `42-construction.birthsAndGenerations`, `40-development.addHouseholdAt`, `44-migration` family arrivals/departures, `80-civic.yearlyDemographics`; no live RNG roll before admission |
| Full day/history | `50-clock.tick`, monthly review, elections, journal/observations, loans/cargo/claims/calendar histories; intermediate dialog/save effects must remain queued until commit |
| Adoption and lifecycle | save/import/Continue/Back/suspend and pending confirmations; original epoch/entity references and all derived caches must remain coherent |

The main UI owner is already repairing a monthly-review partial-day save on a newer integration source. That committed-boundary contract must be shared rather than overwritten from this older isolated base. Installing a save-only transaction wrapper without that agreement would provide false safety. The current phase therefore implements the proven status-closure correction and supplies exact executable boundary/paid-order evidence; comprehensive admission, cheap-normal-case accounting benchmarks and all-command rollback tests remain OPEN. No claim is made that creators cannot exceed the shared budget. The candidate MUST stay disabled.
