# Cooperative mutation-entry review

Re-audited prototype `e68ff5fe2d4ced7396e4fa204930cf92dbe193a0`, not the production integration branch. No runtime fix or enablement in this branch. Reproducer: `python tests/test_cooperative_entry_audit.py`; source-bound results: `reports/cooperative-entry-audit.json`.

| Entry | Barrier / result | Remaining acceptance |
|---|---|---|
| DOM click, input, change, Escape | Window capture queues events; existing prototype policy/command tests cover replay ordering | Exact stale economic quotes require authoritative handlers to reject changed cost/capacity, beyond target resolution |
| Removed modal/control target | This audit queues a click then removes its control; replay explicitly declines | Reused IDs / changed dataset semantics need renewed-review tests |
| Pointer/touch road paint and map gestures | Capture queues gestures; beginning a day is prevented while a gesture is already active | Updated synthetic 500 pointer moves retain one coalesced command; the owner added a 256-command completion barrier. Test real drag/paint/pinch cancellation and ensure coalescing does not omit road tiles |
| Diagnostic `__townTest.get()` | **Reads working day while committed view remains preceding day** | Return committed diagnostics, explicitly reject while busy, or document/remove diagnostic API in production |
| Diagnostic `__townTest.set()` | **Changes minimum wage immediately while day is incomplete** | Queue through authoritative committed command or reject |
| Diagnostic `__townTest.step()` | **Runs another synchronous day inside suspended day; busy remains true** | Reject/finish explicitly before stepping; test exact continuation/RNG |
| Diagnostic `__townTest.reviewPetition()` | **Opens modal and sets pending event while incomplete** | Queue/reject this public entry; avoid modal state surviving failed continuation |
| Native export | Completes day synchronously, then exports; audit confirms no busy state remains | Original quote/lifecycle and physical input responsiveness still needed |
| Native restore / founding | Hydration and seed wrappers finish day, invalidate continuation token; existing barrier suite covers malformed import | New-town pending queued actions and failed replacement need independent adversarial coverage |
| Native Back / suspend / exit | Existing wrappers finish or wait for commit before returning actual state | Exact Android lifecycle/picker/process-death tests required; exceptional synchronous finish can block |
| Native resume | Audit retains busy day; audio refresh is effect-deferred | Does not establish audible trusted-gesture behavior |
| Pause | Immediate clock feedback, deferred save | Updated handler retains the SVG; audit confirms SVG markup |
| Music next/mute/volume | Trusted music gestures handled immediately; other ordinary clicks queued | Native audible activation and independent volume/lifecycle state remain acceptance requirements |
| Async storage callbacks | Save admission deferred; original epoch/town guards remain | Completion callbacks must not adopt a replaced town; retain save specialist's fault tests |

The `__townTest` failures are exposed diagnostic surfaces, not claims that normal button clicks bypass the fence. Other console/internal functions are lexical implementation details, not a safe command API. The supported explicit `__cooperativeSimulation.command()` interface queues mutations; arbitrary external direct calls are not automatically made safe by DOM capture.

The script records negative findings intentionally; its successful completion means the audit ran, not that every entry passed release acceptance. It uses controlled held-stage instrumentation and synthetic pointer stress, not a physical touch session. Do not enable the experiment on this evidence alone.

## Performance context

Parent's exact late-cache acceptance `0b24ea600a6339c97d362c19c7cba7ad00471e15` reports 16.08×→42.38×, row builds 97,306→1,759, zero evictions and 180-day exact model/RNG replay. RAF tail improves 467→333 ms, but touch 395→506 ms remains unresolved. Those are source-bound performance-owner results, not measurements produced by this entry audit and not proof of smoothness.

## Current rerun outcome

All nine cases reran on e68ff5f. Public diagnostic read/set/step/modal bypasses remain reproduced. Stale target rejection, native export/resume checks, pointer-move coalescing and SVG pause checks pass. No runtime changes made; forward the four diagnostic cases to the prototype owner before shared-code repair.
