# Exact urban spatial zero-contribution removal

The post-distance-cache late CPU attribution (performance owner b8e9fd9) places urbanRentMultiplier at 1,812.63 ms inclusive in a 30-second sample. Its spatial rebuild is also visible in the earlier exclusive profile. Scope is only that spatial builder; no scheduler, rent coefficients or cache lifetimes change.

Most houses contribute no jobs, industry or amenity. Previously every building still multiplied/stored zero into both Float32 housing/jobs arrays. The accepted change skips zero housing/job writes, preserving the original loops, contribution order, nonzero arithmetic and Float32 rounding. No new derived cache or mutable rollback state is introduced. Existing daily/town/topology/urban-revision invalidation remains authoritative.

The first candidate precomputed/froze a kernel and used an iterator; six alternating matched runs showed it slower despite exact replay. It is rejected and its source-bound result is retained as `rejected-precomputed-kernel.json`. The smaller zero-write-only candidate has reference/candidate median 221.15/194.30 ms per 100 forced rebuilds, five of six pairs favorable. This is about 12% lower isolated rebuild time on the retained 797-building town, not a whole-session FPS or input-latency claim.

`tests/test_urban_kernel.py` uses the exact synthetic terminal checkpoint, SHA ad6256fd85d4146fda9eeac0b16d5b182ed352c23bbd96af3b320553c29ce786. All four spatial arrays/block data match the old function after staffing/closure/income/condition/day/revision changes and explicit invalidation. The controlled mutation cleanup restores property presence and original numeric values exactly. Full canonical model/RNG continuation matches at each thirty-day checkpoint across 180 days. Receipt: `reports/integration/urban-kernel-8/receipt.json`.

Full integrated core/native/endurance acceptance remains separate. The observed hundreds-of-ms input stalls are not solved by this small inner-loop saving; the cooperative/performance owners retain those responsibilities. No repeated-presentation candidate was integrated.
