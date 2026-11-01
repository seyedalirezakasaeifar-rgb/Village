# District observation cost review

Correct reference: `2e4ce5c8869a0483657ba3321d3e66e8954d780d`, assembled source SHA-256 `3af2f8355807bfa3c23482b25816f657ae618970dfeb4e38dc6c34aa3140115c`. Runtime remains byte-identical in this checkpoint.

The earlier paired public-versus-district host measurements found 5.7–11.8% more complete-step wall time. Those two sources evolve different economic towns after the initial checkpoint, so that percentage cannot all be attributed to profile code. The same-source phase probe uses the identical 765-person day-721 archive and explicit paused test clock, five repetitions of each 20/30-day window. External timers do not write the model; their overhead and Chromium timer resolution limit precision.

The corrected service population reduction runs only four times in the 20-day window and twelve in the 30-day window, consuming 0–0.2 ms per entire window. It is not an extra scan on each of the approximately fifteen thousand spatial reads. Fresh cold observations remain 21/35 builds per 20/30 days, rather than rebuilding per descriptor. Monthly transactional invalidations account for additional builds and must remain: the independently reproduced same-day bank-book and income failures otherwise return.

Median phase CPU milliseconds (timers add overhead):

| Window | Geometry and primitive facts | Retail reach | Medians and service profiles | Classification |
| --- | ---: | ---: | ---: | ---: |
| 20 days | 24.4 | 8.9 | 5.6 | 1.1 |
| 30 days | 38.4 | 13.5 | 11.6 | 1.4 |

A narrow alternative indexed grocers by block and captured household portals once per observation. Against the exact correct reference, seven alternating repetitions with identical initial town and clock reduced median cold-spatial CPU from 32.5 to 29.5 ms / 61.0 to 57.8 ms, but whole-step wall time worsened from 563.1 to 586.4 ms / 926.0 to 960.8 ms. This does not establish a useful total improvement. The patch is preserved as rejected experimental evidence and is **not applied**. It received timing and validity/conservation checks, not complete equivalence acceptance.

Recommendation: retain the known correct reference and accept the bounded host cost pending device measurement, rather than remove required freshness. A larger lazy-profile split needs an immutable observation snapshot and independent allocator/model/RNG acceptance; deferring mutable reads until renderer access could change economic decisions and stale observations. Do not claim smooth device performance from these host results. No renderer, worker, codec, admission, archive schema or native code changed.

Reproduce attribution with `PYTHONPATH=tools/browser_http_adapter TOWNLEDGER_USE_HTTP=1 python tools/attribute_district_cost.py`. The paired profiler now defaults to the correct reference, supports `TOWNLEDGER_PROFILE_BASE`, and uses seven alternating repetitions. Raw phase samples, rejected measurements and unapplied patch are in `evidence/district-cost-review/`.
