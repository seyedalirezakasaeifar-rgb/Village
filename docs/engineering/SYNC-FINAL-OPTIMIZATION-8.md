# Final synchronous performance investigation

Decision: **no runtime optimization promoted**. Isolated base87811c52cdb9aecd13cd23beebd52f6475c6dd9c remains the exact game/native source. BundleSHA256037c92b56d4b736f2c9c2bb96a950ae194bc815d1a393d36b3634f4272521d94. This branch adds attribution tools, aggregate evidence and a rejected laboratory patch only. No APK source, balance, actor quality, day-count/clock algorithm or requested-rate reporting change.

Retained generated778-person town: commit833afee35aa714919a38e420e74cee1f719315db, tests/fixtures/generated-late-31987fc/terminal.json.gz; decompressedSHA256ad6256fd85d4146fda9eeac0b16d5b182ed352c23bbd96af3b320553c29ce786. No whole town/save is added here. This is an existing synthetic late-city fixture, not a user's save. It starts day41681 with778 residents and total funds15493517.000209823. Classic Canvas, balanced original options,844×390 host Chromium, actual RAF and live Economy panel, audio stopped for measurement. Each speed reloads the exact same town; eight-second wall traces are diagnostic, not sustained device/FPS acceptance. One-speed1× windows contain only four completed days, so the~0.82× figure is strongly quantized.

## Actual live results

Times are inclusive wrapper means; nested functions must not be added together. Profiling overhead is present in both variants. Different wall admission counts can produce different endpoint populations; these are not economic counterfactual comparisons. Fixed-day equality is verified separately.

| Build | Request | Delivered rate | Model tick mean | Economy panel refresh mean |
|---|---:|---:|---:|---:|
|87811c baseline A|1×|0.82×|90.40ms|28.87ms|
|87811c baseline A|16×|15.07×|64.24ms|25.72ms|
|87811c baseline A|64×|21.93×|61.33ms|26.38ms|
|87811c repeat B|1×|0.82×|97.00ms|30.57ms|
|87811c repeat B|16×|15.01×|65.28ms|28.03ms|
|87811c repeat B|64×|22.18×|60.74ms|24.10ms|
|Rejected rent terms|1×|0.82×|89.12ms|27.22ms|
|Rejected rent terms|16×|15.14×|66.21ms|29.28ms|
|Rejected rent terms|64×|22.14×|60.17ms|29.67ms|

At16× the first baseline spends4754ms in74 model ticks,154ms across6 panel refreshes and1058ms across121 draws. At64× it spends6685ms in109 ticks,132ms across5 panel refreshes and923ms drawing. Monthly/cold model-day maxima reach~616–627ms. UI refresh can cause its own~25–31ms work, but it is not the dominant64× cost in this fixture. Repeated CPU samples put urbanSpatial first (987/970ms at16×;1287/1306ms at64×) and urbanDescriptor second (700/722ms;1016/1065ms). Those functions are nested under daily economy/rent/urban decisions. Canvas drawing is the largest recurring non-model work. Savings in panel refresh alone cannot make64× meet the requested rate here.

## Rejected prototype and exact semantics

The laboratory patch made urbanRentMultiplier read only numeric land/rent terms instead of allocating the full urbanDescriptor object. It added no cache, invalidation policy or economic coefficient. Candidate sourceSHA256 is recorded in rent-terms.json/equivalence.json. All128×128 grid-cell rent results were exactly equal in each of four fixtures. Complete180-day archives and RNG matched byte-value-for-byte-value (no excluded model/visual/traffic fields) across settlement42, regional91, regional909 and the retained778 town; candidate restore/replay matched too. Cash drift stayed below3.1e-6 and maximum goods error3.66e-8. Failed outcomes were not removed or injected away.

Despite exact semantics, live performance did not show a repeatable benefit. The prototype's16× mean tick worsened, and its22.14× delivered64× rate is below the untouched repeat's22.18×. The~1% variation in the first paired trace is ordinary measurement variation, not a demonstrated gain. The patch is retained under evidence/rejected-rent-terms.patch and is **not applied** to shipped source. No riskier spatial cache change was substituted: staffing, roads, household movement, topology and same-day actions require explicit invalidation guarantees.

## Reproduce and limits

Run python tools/profile_sync_final.py; SYNC_LABEL changes the aggregate output name and SYNC_PROFILE_MS the bounded window. SYNC_SOURCE_FILE can select an isolated assembled source. For the rejected lab only, apply docs/engineering/evidence/sync-final-optimization/rejected-rent-terms.patch in a separate checkout, assemble, then run python tools/test_sync_rent_terms_equivalence.py --candidate-source-file assets/game.js. The historical fixture object must exist; fetch its full commit above if missing. Do not apply the rejected patch to the fallback build.

Raw source-bound aggregates, repeat profile, prototype profile, fixed-day terminal model digests, cash/goods results and exact-equivalence log are in docs/engineering/evidence/sync-final-optimization/. No physical Android smoothness, sustained1× rate, worker performance or guaranteed64× is claimed. Existing clock admission/catchup caps remain unchanged and are not hidden by this diagnostic's separately computed delivered rate. Next work requires bounded, source-equivalent reduction of urban spatial/descriptor demand, with full invalidation and live paired measurement; this investigation does not justify a quick cache patch.
