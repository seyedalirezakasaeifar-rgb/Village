# Session scheduler and interruption acceptance

Base: `525e47dd3967741fb59d2fd06921c1647a29a24a`. The scoped production change is in `70-interaction.js`: native suspension now parks the recurring presentation and autosave branch as well as simulation. A WebView can remain visible and receive RAF callbacks while the Android host is opening a picker or transitioning activities. The explicit suspend call already saves once.

## Reproduced defect and regression guard

Against the base bundle, `test_scheduler_idle.py` held a visible native-suspended town for 1.8 seconds, with an open economic report and an autosave due. Simulation correctly stayed on day 1, but eight header updates, one whole-panel rebuild, one dirty-map draw and one additional save still ran; chronology advanced from order 3 to 4. `scheduler-idle-before.json` preserves that negative result. The fixed test requires zero recurring calls and unchanged day/save order, then checks actual advancement after resume and preservation of an explicit user pause. It passes, together with existing host/audio lifecycle and older-WebView API checks.

No import validation, archive contents, economic rules, transit algorithms or renderer caches changed in this patch. The save specialist's strict-validation work and graphics specialist's `a9532b8` cache fix remain independent integration work. The latter's `VISUAL-CACHE-ACCEPTANCE-8.md` was read before interpreting renderer samples here.

## Whole-session method

`tools/profile_session.py` runs bounded host Chromium windows on a real loopback HTTP origin, serving the actual audio assets. It uses the existing synthetic 2,000-resident fixture and pays for 48 bus routes, six depots and all 21 deeds with transfers from existing regional funds. Two existing civic sites become funded private firms; cargo is actually paid and dispatched. This is a controlled load fixture, not an organically developed full 128-by-128 city. Every receipt includes its exact assembled-source hash.

The harness measures real RAF intervals, timer delivery, trusted pointer-down delivery to the next RAF, component durations, panel response, heap/backing storage, named cache bounds and cash/commodity conservation. Trusted input samples are few in the short windows; their maxima are useful observations, not calibrated percentile estimates. Next RAF is a presentation opportunity, not a claim of measured photon/display latency. Native audio decoder/GPU memory is outside V8 heap accounting.

Near, far, economic-report, paused and native-suspended states are sampled separately. The fixed near window also has a CDP sampling CPU trace; profiling overhead and normal host variation prevent treating before/after foreground timings as a measured speed improvement. The production fix's demonstrated improvement is the elimination of recurring suspended work. `profile-baseline.json` retains the earlier 15-second diagnostic windows too.

The additional bounded soak alternates near/far real-RAF windows, cycles genuine settings/music/save controls, rejects malformed imports without changing the active archive, repeatedly restores the paid 2,000-resident fixture and runs the founding path twice before restoring. Restoring each minute keeps the workload large while exercising interruption and stale-object release; this is not an uninterrupted multi-hour economic survival test. No forced GC occurs during play; collection is requested only at the initial and final boundaries.

## Ownership findings and limits

The sampling trace is kept as `cpu-fixed.cpuprofile.gz`. The profile attributes much of active frame cost to daily economy and passenger queries; those remain with their existing owners. The original baseline recorded a synchronous `save()` around 70 ms, with about 59 ms in `persistSnapshot()` and 11 ms in serialization. The second baseline recorded a suspended save episode around 184 ms. Queue/serialization follow-up belongs with the save owner; this patch avoids adding recurring native-suspended requests without modifying persistence correctness.

These are isolated host Chromium receipts. They do not certify Android frame rate, touch-to-display latency, media decoder residency, thermal behavior or subjective multi-hour fun. Final integrated schema/render/transit/music changes need a fresh immutable acceptance run on the assembled candidate and a real Android device.

## Receipts on the scoped bundle

Assembled source SHA-256: `24003acde9a84b719ab484e7df3827f10a1882baa50a0d1119a719050a4a8c28` (production commit `70b5218ef16bf9c91b232549abbdbe520c7adee5`). The corrected final harness counts simulated days inside the same RAF sampling interval. Final windows use trusted emulated touch events. Existing-provider fixtures hold autonomous building and new provider entry; the evolving supplement enables both and therefore includes the monthly investment scan.

| State | Window | Actual rate | RAF P95 / P99 | Longest touch to next RAF |
| --- | ---: | ---: | ---: | ---: |
| near | 12.0 s | 64.4× | 33.3 / 50.1 ms | 58.6 ms |
| far | 12.0 s | 63.7× | 16.8 / 33.4 ms | 66.1 ms |
| economy | 12.0 s | 64.0× | 33.3 / 33.4 ms | 52.6 ms |
| paused | 12.0 s | 0.0× | 16.8 / 16.8 ms | 31.0 ms |
| suspended | 12.0 s | 0.0× | 16.7 / 16.8 ms | 31.3 ms |
| Evolving near | 20.0 s | 63.2× | 33.4 / 83.3 ms | 122.1 ms |
| Evolving far | 20.0 s | 58.6× | 50.0 / 249.9 ms | 272.0 ms |

All cases retained 48 operating routes, paid cargo, four or more private-provider staff and real private clients, valid town records, conserved cash and commodity books, and no page errors. The final fixed-count private providers served about 212 client-equivalents/day. Economic/private/urban evolution increased clients and provider staffing in the evolving supplement.

The evolving far case remains a material foreground limitation: one monthly private-service investment call took 231.7 ms, a tick reached 282.2 ms, RAF P99 reached 249.9 ms (maximum 316.7 ms), and a trusted touch needed 272.0 ms to the next RAF. This is retained negative evidence, not an acceptance of smooth play. The economics/integration owner should optimize that scan with exact model/RNG/accounting equivalence and rerun the evolving case. Splitting an atomic economic day in this scheduler patch would require a broader design change and was not attempted.

The completed separate 300-second soak kept all 48 routes operating with 96 drivers in every snapshot, and both existing private firms open. All 30 windows explicitly asserted a requested 64× setting after imports/foundings. Peak named cache usage: 566 sprites / 45,552,640 atlas bytes, two service-access caches, 62 traffic actors, 240 history entries, 160 events and 800 transactions. Heap after requested boundary GC moved from 10,674,780 to 12,690,368 bytes; observed transient V8 peak was 106,561,084 bytes. These figures do not include all native canvas/decoder/GPU allocations. The final archive round trip took about 76 ms; the final/evolving short-session round trips took about 162/190 ms. No memory leak or physical-device smoothness certification follows from a five-minute controlled run.

Earlier receipts are preserved with their limitations. `profile-fixed.json` includes the CPU-sampled phase windows and an interrupted soak whose founding action reset speed to 1× after 120 seconds; later windows are explicitly excluded from 64× conclusions. The harness now reapplies and asserts 64× after replacement. The early soak's out-of-page day endpoints can slightly overstate its rate; `profile-final.json` and `profile-evolving.json` use corrected in-RAF counters. `profile-soak.json` is the completed memory/interruption/route-continuity receipt. This separates harness corrections from production changes without discarding inconvenient samples.

Reproduce the completed cases (run sequentially, with competing browser/benchmark processes stopped):

```sh
python tests/test_scheduler_idle.py
SESSION_SECONDS=12 SESSION_LABEL=final python tools/profile_session.py
SESSION_SECONDS=20 SESSION_MODES=near,far SESSION_EVOLVING=1 SESSION_LABEL=evolving python tools/profile_session.py
SESSION_MODES='' SESSION_SOAK_SECONDS=300 SESSION_LABEL=soak python tools/profile_session.py
```

The current harness includes the in-RAF rate correction for future soaks too. `SESSION_REF=525e47d` profiles the historical bundle in memory without replacing the working bundle; `SESSION_CPU=1` records an optional compressed CDP CPU trace during the near window.
