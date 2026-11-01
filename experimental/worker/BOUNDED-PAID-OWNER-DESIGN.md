# Proposed bounded paid-command owner (not implemented)

Decision requested: preserve the existing archive format and normal daily simulation; use the existing single shared root only for explicit admitted paid commands. Do not enable generic normalized byte/node certification, schema9, a proxy journal, or the reference test owner as production.

## Feasible ownership boundary

1. Keep corrected session/epoch/command admission and committed-day worker ownership. Only a finite typed whitelist may enter paid dispatch. Commands execute between complete days, synchronously in the worker; no callback or source crosses postMessage. Validation consumes a request ID before any attempt. Nested paid operations join the same shared root.
2. Introduce a separately named production paid-command adapter implementing the existing owner contract. It installs the existing shared fences and registers paid runtime and worker outbox/runtime on that one controller. It does not reuse the test-owner identity or report global capacity certification.
3. Preflight the requested kind against current source quotes, available cash and existing import record limits. For example: people8000, households3000, firms3000, banks12, loans10000, freight10000 and metro stations/lines120; remaining per-feature limits come from their actual current validators. Construction/project/contract DTOs declare their maximum newly created record counts. Unknown or unbounded growth kinds refuse. Check initial state plus that conservative delta before mutation; check actual final state before commit. Existing quote keys/creator results remain authoritative, not independently rewritten economics.
4. Capture one identity-preserving graph checkpoint for that paid command only, including G, RNG, pendingEvent/callback aliases, registered runtime/cache roots, logical view context and outbox/effect serial. The published graph checkpoint API already preserves aliases and function references without serializing callbacks. Add explicit traversal resource budgets to checkpoint construction, rejecting before model work if the budget cannot be satisfied; never call this a normalized archive reserve. Anti-replay IDs/epoch stay outside rollback. Restore the graph before runtime setters.
5. Execute the actual existing source function under `__rootAdmission.run`/serializable paid dispatcher. Any stale quote, insufficient funds, invalid return, creator refusal or exception refuses the whole command. Validate the actual resulting records and financial invariants before commit. This reuses existing bridge/removal/deed/construction/private-provider algorithms; it does not assume those functions alone provide universal rollback.
6. Produce and size one canonical existing-format export only for the paid commit certificate, reusing it for its save intent rather than serializing repeatedly. Native ArchiveIO currently has an8MiB input limit. Check the actual UTF8 bytes of the exact native export representation, including its wrapper, against that existing ceiling; do not invent a larger limit. A worker-side paid snapshot budget is a separate explicit resource policy and needs measured published thresholds, not a claim that8MiB JSON equals a heap bound. Existing validators plus an isolated hydrate/re-export fixed-point gate must pass for supported paid families before release; destructive hydrate never runs on the authoritative model. Per-command validation latency must be measured; no per-day whole-state certificate is added.
7. Commit once, drain the committed saver into the structured outbox, then acknowledge the command and publish the completed snapshot. A payment acknowledgement means model commit, not disk durability. The existing writer is the only persistence owner. Its verified write precedes token/checksum save ACK; failure retains a retriable save intent and clearly reports unsaved state. No financial rollback follows a presentation failure or a failed later disk write.

Ordinary `tick()` must be called directly by the adapter, with NO shared-root capture/certify on every day. The current experimental `workerTickCommittedDay` still wraps days when a reference owner is enabled: that is explicitly unsuitable for this production proposal and must change only in the isolated implementation after design agreement. Failed ordinary days remain fenced from export, paid commands and continued stepping; recover the last verified committed archive. This is fail-stop recovery, not rollback of every day.

## Guarantees and exclusions

| Guarantee | Proposed mechanism | Limit |
|---|---|---|
|No duplicate/stale user payment|Permanent command/epoch admission + current review ID|Already proven lifecycle scope; port must preserve it|
|Atomic supported paid operation|One bounded graph checkpoint and shared root|Requires complete runtime registration and fault injection for each family|
|No partial authoritative UI state|Completed snapshots + serial effect ACK|Snapshot/render cadence still needs performance work|
|Save/export consistency|Committed state token + original writer ACK|Native actual-picker/durability gates remain independent|
|No831ms/day generic certification tax|No daily graph capture or global normalization|Paid actions may still be expensive; measure them|
|Existing-format compatibility|Current validators, exact exports and supported-family reload gates|Not a universal future saveability guarantee|

This does NOT guarantee unlimited ordinary growth remains inside import/native limits. Automatic births, investment, cargo, histories and normalized defaults can grow without an explicit paid command. Cheap count checks at completed-day boundaries can stop further stepping and warn, but cannot retroactively roll back an oversized completed day. Guaranteeing every day stays within all normalized limits would require conservative family-specific daily reservations or another independently accepted design; it must not be silently claimed. Keep the last verified durable archive available.

Automatic investment is also outside the proposed paid-command root. If an ordinary-day creator can deduct funds then refuse, that source path requires its own local quote/commit or charge-after-success correction, with economic parity/failure tests. The paid owner does not make all automatic model activity atomic. Ordinary OOM/unsupported graph objects/irreversible descriptor changes remain fatal-fence cases, not a guaranteed graceful rollback under exhausted memory.

## Implementation and promotion gates

- Paid owner/reviewer agrees finite DTO families, conservative growth deltas and runtime roots before coding. No competing controller. Name status `paidCommandsProtected`, with `globalCapacityCertified:false`.
- Measure graph node/property/byte counts on fresh, dense778 and large near-limit towns to choose explicit checkpoint budgets. Publish refusal thresholds and before-work checks; do not guess memory guarantees.
- Reuse all12 independently reviewed lifecycle gates and actual council/provider/bridge/street/construction fixtures. Inject refusal/exception after payment, insertion, RNG use, queue mutation and creator-null; check full model/RNG, callback alias/retry, outbox and original reload semantics.
- Matched ordinary-day model/RNG equivalence and CPU with owner installed but no paid command must show no daily snapshot/certificate calls. Paid timing, main input, memory and save latency are separate measured gates.
- Native supported-runtime, async picker, load/new-town/session races, failed write/ACK retry and actual durable restore must pass on the composed source. Existing API30 arithmetic guard remains mandatory.

Feasible next implementation is this limited paid adapter plus changing worker day dispatch to the ordinary path, not enabling the present test owner. Full UI routing and renderer snapshot costs remain separate completion blockers. This document is a proposal, not approval or production acceptance.
