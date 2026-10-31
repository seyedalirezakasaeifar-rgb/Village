# Deferred presentation repeat: hold performance integration

Current base 6e8665e, SHA 852b9950845a6563c600be5eced6188e11edeccda495ec778ca3f4ebe3e9ff61. Current-base candidate 3b23377, SHA 432e00545fd63ee80979adec6ec2af277710f980733c40fd0f9434b3c71aeb0f. Exact generated late checkpoint ad6256fd85d4146fda9eeac0b16d5b182ed352c23bbd96af3b320553c29ce786.

Six isolated runs alternate base/candidate/candidate/base/base/candidate. All execute the same twelve touches, panel sequence, two explicit save actions and index-based zoom transition. Autonomous growth, audio, private entry and surviving transport remain enabled. No competing timing process ran.

| Variant | Actual rates | RAF P99 ms | Touch maximum ms | Touch median ms |
|---|---|---|---|---|
| Base |44.8,45.1,46.6|316.6,316.5,283.4|157.4,562.1,155.3|101.4,92.4,90.1|
| Deferred |44.6,45.3,45.0|316.6,316.6,316.6|396.4,179.4,151.7|98.2,87.6,87.8|

**Recommendation: hold/reject this candidate as a demonstrated performance improvement.** Small median differences are not accompanied by a consistent tail or throughput benefit. The earlier single 506-to-336 ms maximum was insufficient evidence. No additional presentation changes were made to manufacture a gain. Candidate source is preserved separately for architecture-hook review; no integration/merge performed.

Safety checks passed. Real calendar controls, brownfield renewal controls and procurement authorization/cancellation/stale/replay paths ran on both sources. Final complete model objects, including RNG, were exactly equal after excluding only trafficState and visualState. The periodic-task regression additionally passed immediate durable save, failed-storage retry, focused-input preservation, native suspend, unfinished-day and replaced-town guards. These tests do not prove future cooperative-stage compatibility: its committed-state/command barrier remains owned by that prototype.

Evidence: reports/presentation-repeat/timings.json, commands.json and the six repeat-* receipts under reports/integration/adaptive-road-distance-8/late. Full per-run latency and negative samples are preserved. Host Chromium only; no Android claim. Reproduce command equivalence with tools/check_presentation_commands_8.py. The timing driver retains fixed ordered actions; source selection is LATE_SOURCE_REF=6e8665e for baseline and empty for candidate.
