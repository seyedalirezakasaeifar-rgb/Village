# District candidate review: held pending behavioral fixes

Production base remains `e3fae439e96b33bc3a62340f9a898029af674111`, source SHA-256 `dbbb77a80e54a8c02fa5d7da8af020ba6b8a24078270c39cd5d844bd236dd949`. No district feature, renderer, worker, admission or codec code is integrated by this review.

Reviewed candidate `b7a6039a799b2ceac38903f85da45933b61d4154` was ported locally without overwriting the accepted retail/bridge disclosures. That exact scratch assembly is SHA-256 `a6a1339050cbbe572ade5f430e1157fe88f37faf4ca1d1ed244566ee4cb1a9f6`. The reproducible review tool reconstructs those bytes from the two public commits in memory; it does not install or activate the candidate.

## Acceptance blockers

1. **The 90-day district transition commits the wrong character.** Review compares the new profile's `observed` character and queues it, but completion still assigns `old.character=b.character`, the older block classification. With a real regional seed-42 two-year downtown observation and a valid older residential classification, days 721/751/781 queue Downtown mixed-use. On day 811 the proposal is cleared and `changed` advances, but the archived character remains Residential neighbourhood. The one-line correction `old.character=observed` passes this lifecycle probe in memory. It is a proposed owner fix, not a production change in this commit.
2. **The new current-book/profile handoff inherits an intra-day stale cache.** After one ordinary regional day, block 3:3 reports bank deposits $23,858; invalidating only the derived cache reports the actual $23,859.5896, with the complete model unchanged. Income-band, income and rent observations change too. The accepted base already has intra-day staleness in its block income observations (76 changed block fields in this control); this is not attributed entirely to the candidate. The new profile adds stale bank-book/financial-activity fields and exposes those observations as current renderer/UI input (41 changed profile fields in the candidate). The one-line character correction does not fix this contract.

The owner needs a clear committed observation/invalidation contract for UI and renderer consumers. Do not fix it by blindly rebuilding shared economic spatial caches in every draw: rendering must remain model/RNG independent and repeated building descriptors must not trigger a whole-town rescan per building. Preserve actual paid service receipts and same-day transaction evidence. Candidate tests should compare profile readings with fresh authoritative inputs at completed-day and ordinary paid-command boundaries, including bank books and current household income/condition; independently measure any new projection cost.

## Missing historical fixture: equivalent coverage restored

The unchanged historical `tests/test_urban_kernel.py` fails before any product assertion because `833afee35aa714919a38e420e74cee1f719315db:tests/fixtures/generated-late-31987fc/terminal.json.gz` does not exist. The original failure is retained.

The test now uses the committed synthetic ordinary-resource regional seed-42 day-721 checkpoint (765 residents) introduced with the previous disclosure regression. It retains the original independent `bb02bbc` spatial reference and compares all four Float32 arrays, block metadata and median exactly. It tests jobs, closure, income, condition, day and revision mutations and checks that the audit leaves the model unchanged. Separate reference-cache ownership prevents the reference from simply returning the candidate's cached answer.

For model execution, the reference supplies its independently calculated core arrays/blocks while preserving any added candidate-only projection fields. Six 30-day intervals then compare complete canonical states, including traffic and visual state, with **zero exclusions**. This restored oracle passes on both the scratch district assembly and unchanged public source through day 901. It replaces the unavailable-fixture coverage rather than labeling that gate skipped.

## Other evidence and scope

- The candidate's own two natural six-year profile/UI/paid-plan/save-replay test passes on the composed source. It does not catch the transition or cache defects above. Natural downtown/suburban observations remain valid for their recorded samples; neither market nor financial district was produced, and no such gameplay claim is made.
- Eight scenario/seed comparisons over 180 days preserve every financial, identity, road, cargo and RNG field against the accepted public base. Only the intended district name/character/review metadata differs; those explicit metadata differences are recorded, not described as whole-model equality.
- The restored array/mutation/180-day oracle passes on candidate and public source. Candidate cold-kernel median was 129.65 ms per 100 uncached calculations versus 84.45 ms for the original reference on this host/fixture. These are diagnostic host timings with profiling overhead, not a device or sustained performance acceptance.
- The production runtime was restored byte-for-byte after review. Existing source-bound public evidence remains attached to its original bytes; no old pass is assigned to the scratch candidate. No Android/native, visual-fidelity, packaging, signing, release or integration promotion occurred.

[Manifest and retained evidence](evidence/district-review/manifest.json). `tools/review_district_candidate.py` exits successfully when it reproduces the immutable candidate's rejection and the proposed one-line correction; that is a diagnostic reproduction pass, **not candidate acceptance**. Integration is held for the behavioral reasons above, not because any tool denied the action.
