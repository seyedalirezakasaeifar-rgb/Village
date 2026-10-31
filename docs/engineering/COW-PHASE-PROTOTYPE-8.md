# Isolated transaction/read-model phase experiment

Branch `codex/8-transaction-read-model`, based on disabled cooperative checkpoint `2f5a73e`. No simulation, renderer, persistence, native or assembled-source file changes. `experiments/cow-phase.js` is not loaded by the game; only the research harness injects it. There is no production enable switch.

## Minimal proof

`createPhaseCowStore(initial)` audits a plain, unaliased archive-data tree once and freezes it as the completed read model. A rejected alias/cycle audit does not partially freeze caller data. `store.begin()` creates a draft with lazy proxy reads. First writes shallow-copy the affected container and ancestors. Commit publishes frozen copies only along modified paths; rollback discards the draft. Expired drafts throw. The initial ownership audit rejects shared containers, cycles and non-plain types rather than assuming them safe.

The first proof deliberately permits primitive writes/deletions in an existing tree. Container replacement and new alias ownership are **unsupported and rejected**, rather than falling back to unsafe mutation. This is not a general full-day transaction implementation. The input audit runs once per store; eight successive commits reuse its ownership metadata without re-auditing the full state.

`tools/probe_cow_phase.py` loads the actual retained terminal fixture from `833afee`, runs the real `maintainRoads()` function, and compares complete serialized model values with an independent ordinary execution. The harness proves eight consecutive exact phase commits, unchanged completed state during draft work, four faults at write counts1/3/25/100, exact continuation after those faults, expired-draft rejection, alias/cycle rejection and unchanged live game state. It preserves the original game `G` and resets phase-created graph/building caches afterwards. These are phase continuations, not eight complete simulated days. No fare, budget, quantity or policy rule was rewritten for the test.

The read model remains available while the working root differs. This synchronous phase proof does not claim a cooperative UI integration, queued-command protocol or native durability certification. Committed graphs are memory state, not a substitute for the existing persistent save chronology.

## Cost and rejection

Receipt `docs/previews/cow-phase/terminal-road-proof.json` binds game/prototype/fixture hashes. Eight host Chromium rounds, medians:

| Component | Ordinary phase | Proxy draft |
| --- | ---: | ---: |
| Graph preparation | 1.60ms | 25.75ms |
| Actual road-maintenance work | 1.25ms | 13.00ms |
| Draft creation | — | below0.1ms |
| Commit | — | 0.10ms |

The one-time tree audit/freezing cost12.10ms. Each measured draft phase made about180,543 proxy reads and5,894 writes;81 copied containers contained20,608 slots. Preparation/commit are cheap, but read interception and graph ownership/cache interaction overwhelm the saved snapshot cost. Graph preparation is reported separately and is not hidden in a warm-cache comparison. No Android performance conclusion follows from these host samples.

The broader real `dailyEconomy()` phase explicitly rejects its ordinary worker-array replacement (`Unsupported container replacement at workers`). This exposes the missing ownership protocol for array replacement, entity moves, newly allocated objects, local raw references and aliases. Silently accepting those writes would compromise the committed read model or alias semantics. The committed model also rejects `ensureSystems()` because that existing query/helper writes `climateSeasons`, even when setting the same value. Current UI/model helpers cannot simply point at a frozen read model without separating pure selectors from initialization and mutation.

**Reject this generic proxy approach as a drop-in pre-delivery optimization.** It preserves the limited phase's semantics and rollback, but performs substantially worse before the unsupported full-day behavior is implemented. It does not justify a sweeping rewrite or enabling either cooperative experiment. Keep the stable synchronous fallback.

## Narrower architecture worth designing separately

A lower-overhead alternative would require explicit ownership/write sets or phase reducers, not a proxy on every hot model read. Each phase would own its mutable domains, publish immutable read projections, preserve entity/alias semantics across references, and expose versioned geometry/query caches keyed to topology rather than transient root identity. Undo/rollback must also include non-`G` state and presentation/save effects. Inputs would validate against the authoritative completed version; persistence would retain its existing committed-snapshot/epoch protocol. Those obligations are not implemented or waived here.

Before any expansion, prove one explicitly owned phase with source-bound unexpected-write/fault checks and compare total preparation + model + commit + cache rebuild costs. Then demonstrate actual UI query purity, entity insertion/replacement, queued command ordering, import cancellation, persistent-save chronology and deterministic full-day replay. The present result supplies a rejection boundary and a working isolated test bed, not evidence that a whole-state transaction engine is ready.

Reproduce (requires the existing Chromium/Playwright tooling and retained fixture object):

```sh
git fetch origin codex/8-session-soak
python tools/probe_cow_phase.py
```
