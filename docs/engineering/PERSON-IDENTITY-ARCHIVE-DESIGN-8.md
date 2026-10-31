# Person identity history: proven boundary and safe-design gate

Read-only base 5c503015e9572329393f01242732b7ca0bed7708, assembled source
cc9f02a1c84a8e4aadc5df3d22bf8a9a382ed7c1ee5210742bff4cc5d31bfce6.
No model, creator guard, archive validator or scheduler is changed. Executable
proof is tests/test_person_identity_history.py; compact source-bound evidence is
under docs/evidence/person-history8. No whole checkpoints/person lists published.

## Confirmed mismatch, not a proposed birth freeze

An accepted 8,000-record history with synthetic deceased records and only 166
living residents admits one actual seeded birth through birthsAndGenerations.
After normal recompute/RNG publication there are 8,001 records and 167 living
residents. Structural membership validation passes; the same engine refuses its
export's record count. Existing wallets, addresses, titles and cash remain intact.
The previous accepted archive remains loadable. This is not an unassisted
8,000-person history or proof of a particular natural failure year.

A normal seed-42 twenty-year path separately confirms accumulation: year 2 has
215 identities / 209 living; year 20 has 376 identities / 331 living, including
17 deceased and 28 departed. Retirement is not disappearance: 34 retired records
remain at year 20. Death and departure do not shrink/reuse the array. Population's
2,000 admission ceiling therefore does not protect the 8,000 lifetime identity
cap. A blanket birth refusal based on dead history would change family behavior
rather than solve retention and is not implemented.

## Reference contract and unsafe shortcuts

| Reference | Meaning and preservation requirement |
| --- | --- |
| people[index].id | Dense stable identity equals index. Never filter/reindex historical records. |
| people[].hh | Stable household/estate identity, even after departure/death. |
| people[].job | Firm index or -1; preserve historical fields and current job semantics. |
| households[].people[] | Actual living family membership and heirs' household wallet. |
| firms[].workers[] / attendingWorkers[] | Employment/payroll and completed-day attendance; attendance can outlive a death until next settlement. |
| civicTraining[].person | Qualification obligation; a death may precede the next course cleanup. |
| transit.routes[].stats.staff[] | Published paid-service staffing; do not invalidate a completed-day record. |
| civicCalendar.events[].participants[] | Historical gathering participants can remain after death. |
| migration session person IDs | Transient diagnostics are also captured by cooperative rollback. |
| queued commands / cooperative snapshot | Old tokens/closures must not see renumbered identities or a half-decoded town. |

Property titles, bank claims/debts and the new loan-retention summary reference
households/firms rather than individual people. They are still relevant: person.hh
must keep resolving to the original estate; that household cannot be deleted just
because its living membership became empty. Loan summary keys from 8be6a943 must
be included in any later household/firm reachability analysis. That loan commit
is not present in this read-only base; it is explicitly a cross-branch contract.

Some loops mutate public-role/transit fields on *all* person records, including
inactive ones. Freezing runtime tombstones without auditing those writes can throw
or alter replay. Calendar/history references also make outright deletion unsafe.
Reducing G.people to living records would break IDs, initial achievement/count
semantics and direct indexing. No such shortcuts are proposed.

## Lossless encoding proof and proposed staged design

An offline dictionary/column-index representation round-trips every JSON field,
nested value, absent key distinction and original ID of all 376 measured records.
The complete person JSON is 115,062 bytes; its packed representation is 60,938
bytes (47% smaller). The decoded canonical SHA is retained. This is an executable
encoding experiment, NOT an accepted production archive format or runtime speed
proof. It does not by itself remove the existing 8,000-record guard.

The safest next candidate is a versioned **wire-only lossless inactive-identity
section**. Keep runtime G.people and every logical ID unchanged. Serialize inactive
full records through a shared field dictionary with original-index/presence/value
rows; do not discard biography, names, private-learning data or estate links to
save bytes. Decode to the same logical array before existing region/transit
migration and domain validation. Keep live/full-record limits separate from a
new explicitly bounded inactive-history allowance. A schema bump is required so
old builds reject the new layout rather than misread placeholders.

Required protections before any production patch:

1. Retain the existing legacy 8,000-record path and historical compatibility matrix.
   New allowance applies only to a validated new-format packed section, never a
   flag that bypasses old checks on an arbitrary oversized array.
2. Enforce encoded UTF-8 size, row/field/cell/depth/string budgets before expansion;
   reject duplicate IDs, active/inactive overlap, holes, malformed presence rows,
   unknown versions and unsafe property assignment. Preserve original dense index.
3. Determine a measured finite inactive allowance (for example test 16k/32k), not
   an unlimited-history claim. Measure decoded heap and all-person loop costs on
   older WebView/native before choosing it. The offline 47% saving does not certify
   that 32k runtime records are fast or memory-safe.
4. Centralize pack/unpack. Cooperative failure currently JSON.parse's its completed
   snapshot directly; changing archivePayload alone would break rollback. Agree a
   complete-runtime snapshot codec with its owner; do not duplicate its scheduler.
5. Round-trip authentic old archives and large mixed cargo/fare/provider/renewal/
   calendar histories; preserve every identity/reference, money/property/claim and
   exact RNG continuation. Attack malformed expansion and every cooperative yield.
6. Guard export against producing a layout the same build cannot import. If a
   true byte/identity budget is exhausted, communicate a specific capacity issue
   while preserving the previous checkpoint; never silently remove heirs/debts or
   freeze ordinary births merely because a smaller wire encoding is pending.

This reaches the requested design gate: there is a focused failing creator proof
and a fully lossless encoding proof, but safe comprehensive archival spans parser,
serializer, rollback, UI/reference and mobile-memory contracts. Shipping a larger
validator number alone would weaken protection and leave the performance problem.
Production work should begin only after those owner contracts and measured budgets
are agreed. Existing lifetime-cap risk remains explicitly unresolved by this branch.
