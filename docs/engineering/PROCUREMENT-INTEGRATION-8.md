# Integrated procurement checkpoint

The completed procurement implementation c11196f is integrated after brownfield art, precise compositor, locator, migration, native and first-save fixes. Main keeps cooperative scheduling disabled.

Authoritative APIs:
- `reviewRegionalProcurement({firmId,marketId,good,milestones:[{quantity,deadline},...]})` returns a pure town/state/RNG/spec-bound review for one or two stages.
- `authorizeRegionalProcurement(review)` preflights all stages and available history/slots before committing IDs and ordinary contract records once. Returns `{ok,contractIds}` or rejection.
- `cancelRegionalAgreement(id)` stops active siblings while preserving fulfilled outcomes and travelling cargo/liabilities.

`procurementGroup`, `procurementStage`, `dispatchFrom` are optional ordinary contract fields. Validation composes the existing regional validator; ungrouped legacy agreements remain supported. No parallel settlement ledger or persistent reliability score is added. Outcome cards use actual successful deliveries and do not grant a reward.

There is no new daily hook: existing `dispatchRegionalContracts()` enforces the second-stage opening. Sync/cooperative engines must call the current version through their existing freight/economy stage. New wrapper `validateRegionalTrade` must remain part of the candidate validation chain. Quotes and authorization belong at committed boundaries; direct external diagnostic entry remains subject to the prototype's API guards.

Exact-source five-gate receipt: `reports/integration/procurement-8/receipt.json`. Procurement, supplier controls, port faults, composite save and core release gates pass. The procurement test additionally performs thirty ordinary authorize/cancel cycles with whole-pair pruning, bounded history, validation and unchanged cash, followed by real paid two-stage fulfillment and exact replay. This does not certify every market/commodity combination or long-session performance. Future acceptance must include travelling-cargo-protected history saturation and final combined staged/native checks.
