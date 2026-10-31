# Isolated explicit ownership: monthly outward migration

Branch `codex/8-owned-migration-phase`, based on `fb4b74c`. The experiment lives only in `experiments/owned-migration-phase.js`; it is not assembled, loaded, enabled or merged into production. No economic, renderer, persistence or native source files changed. The synchronous engine remains the fallback.

## Scope and input

The selected real phase, `outwardMigration()`, was a measured long task. The proof uses the actual retained terminal town from `833afee` and controls the monthly clock gate at41700, then eight successive monthly phase dates. It does **not** simulate the intervening whole days. A phase publication in this test is not a certified canonical end-of-day save; a full implementation must retain the previous completed-day view until every daily stage and effect has committed.

`createOwnedMigrationStore(initial, context, reviewedSource)` takes ownership of a canonical plain-data tree, audits/freezes it once, and exposes `current`, `context`, `run(day, options)` and `exportCommitted()`. The pinned reviewed function is in `experiments/owned-migration-reference.js.txt`; changes to the original function reject before execution. All other model sections remain shared and frozen. No per-read proxy is used in the phase. The initial audit reuses the isolated tree checker, without creating its proxy drafts.

The phase is split into the exact existing eligibility/filter/assessment/sort/random-choice order, followed by a narrowly owned apply section. Candidate order and RNG draws are preserved. The original function remains the independent oracle. This is reviewed duplication for the experiment, not a second production implementation to maintain indefinitely.

## Complete reviewed write boundary

| Target | Ownership / operation |
| --- | --- |
| Root | Shallow draft of every root property; clock gate and region are scalars. `recompute()` replaces stats and may replace road metrics. Unchanged fields are preserved. |
| People | Copy the outer index array and only departing person records; set `movedAway` and `job`. Other fields/nested containers stay shared/frozen. |
| Households | Copy the outer index array and selected household record; replace `people`, transfer cash to region, clear cash and tenancy address. Deposits, loans and titles remain recorded. |
| Firms | Copy the outer index array and only records whose worker lists contain a departing ID; the original filtering operation replaces their worker arrays. No payroll, stocks, prices or firm cash are settled by this phase. |
| Buildings | Copy the outer index array and the actual home record; tenancy cleanup may change `hh`, replace `units`, replace/delete `legacySharedTenants`. Geometry and ownership titles remain unchanged. |
| Events | Copy the bounded outer event array; the existing story helper prepends a fresh event and applies its existing limit. Old rows remain frozen. |
| RNG | Keep a transaction-local next RNG value, restore the live external RNG after every run, publish it with the phase context only on success. |
| Migration diagnostics | Own the recent-row array, counts and observation-day/owner binding. Preserve the original per-town reset semantics across new root identities. |

`freezeNew()` freezes newly owned containers at publication and immediately skips previously frozen sections. It does not traverse/copy the whole town on each phase. The initial tree audit/freezing is a one-time load cost. All fields are retained; the design does not declare mutable people/households static or omit data to improve timings.

## External references and cache boundary

The first attempt correctly failed on a frozen home record: `readBuild()` had cached a planning-phase building before the owned building array was installed. Its cache checks root identity/count, so replacing the array inside the same draft root was insufficient. The ownership barrier now invalidates the building index before tenancy helpers run. This is an explicit required cache transition, not permission to mutate the old published object.

The harness borrows/restores the global `G`, RNG and migration report bindings around a run. Road graph/building index and transit topology/routing caches are discarded at exit because they may refer to the temporary context. Other derived query caches retain their existing root/network ownership checks. Their identities are not persistence authority. A full design needs scoped/versioned caches and an audit of all retained entity references; it cannot assume that replacing `G` or an array automatically retires cached objects.

Shared model sections are frozen, so unexpected nested writes fail. A negative test replaces the recomputation helper with an unowned policy write after financial/tenancy changes have occurred in the draft: the write rejects and the entire phase publication/export remains unchanged. The experiment does not catch that failure and continue with a partly applied model.

## Read/export and rollback proof

Published root/context stay unchanged throughout planning and every apply boundary. `exportCommitted()` serializes the whole published model, including its committed RNG, and caches that text only while the immutable root/context version is unchanged. Commit invalidates the cache. An in-flight phase therefore cannot leak partial accounting into the export. Serialization is still a real cost when first requested; no actual persistence store or chronology protocol is replaced here.

Faults before/after planning, owned preparation, person mutation, worker unlinking, cash transfer, tenancy cleanup, report update, story, recomputation and pre-commit leave published data and the live external RNG/report state intact. Retrying matches a fresh oracle. The real terminal fixture covers eight exact model and external-state continuations, with88 observation boundaries. Ten fault boundaries are also exercised with a focused synthetic distress-history fixture using existing people, existing recorded employment, unchanged jobs/funds and occupancy lists derived from existing residents. That second fixture exercises real worker unlinking and optional tenancy-array cleanup; it is branch coverage, not an organically developed city or a gameplay performance claim.

## Cost result and decision

`counterbalanced-proof.json` binds game, prototype, audit, reviewed-function and fixture hashes. Eight phase rounds alternate control-first/owned-first. Host Chromium medians from that bounded run:

| Component | Time |
| --- | ---: |
| Full-state recovery copy control | 11.55ms |
| Ordinary graph preparation | 1.25ms |
| Ordinary phase after graph preparation | 20.10ms |
| Owned planning, including its query/cache work | 30.15ms |
| Owned preparation | 0.30ms |
| Owned apply | 0.70ms |
| Owned commit | 0.50ms |
| Full-copy rollback control total, median per round | 31.95ms |
| Owned total, median per round | 31.60ms |

The one-time audit cost is included separately in the receipt. The control models a recovery copy **for this isolated phase**; the production synchronous engine does not currently copy per phase. The whole-day cooperative backup would be amortized over all daily work, so this table is not evidence of a game-level speedup. Timings exclude the test's correctness serialization; export/save latency needs separate measurement. Eight samples do not establish calibrated tails or native behavior.

Earlier ordered diagnostic runs are retained: one was near parity, another favored ownership. The counterbalanced run does not establish a meaningful overall improvement. Ownership preparation/commit are cheap, but read/cache costs against the isolated state erase most savings. Further attribution is required before assigning that tax solely to freezing or to cache churn.

**Decision: keep this an isolated proof; do not expand or enable it as a full-day replacement yet.** It demonstrates a safe, low-copy write boundary without hot-path proxy traps, but not the required whole-game latency/throughput benefit. Extending it would require authoritative shared planning/apply code, scoped entity/cache ownership, a pure completed-day UI/read projection, queued command/version validation, canonical day publication, and the existing save/import/native epoch guarantees. Those are explicitly outside this first-phase proof. No unsafe alias exception or weaker rollback was added to make the benchmark pass.

Reproduce:

```sh
git fetch origin codex/8-session-soak
python tools/probe_owned_migration.py
```
