# Shore, parcel access and fixed late-city CPU checkpoint

Integrated c8a63c0 (actual paid transit/service parcel outlook) and verified full art commit 9f7f86d86f2e356e5136055713977abe799741df. Six source-matched gates pass: parcel outlook, district/world art, exact sprite envelopes, 36 camera cases and broad core release. Source `6326956a096ede9ae37bcfd1945b2133ee69a1a4f39d470786e385d24777e890`; receipt `reports/integration/shore-outlook-cpu-8/receipt.json`.

The original art capture has an opaque-origin save warning and is not suitable final media. A fresh real-HTTP-origin capture is retained here as `current-night-568.png` with save success and unchanged model recorded in `capture.json`; it was visually inspected. This is a small controlled paused capture, not native moving-scene acceptance.

## Current CPU attribution

`tools/profile_fixed_late_cpu_8.py` takes two 180-day sampling profiles from the exact retained terminal fixture. Both finish with canonical model/RNG hash `4a5787e476487a8d79a1e66574b4e6001079c3f01a35822a672ef8ddb7a7c985`, valid books and goods. Measured simulation steps are 5308.6 and 4897.7 ms with sampling enabled. Audio is paused to isolate simulation; these are not RAF/input/Android measurements.

Stable inclusive contributors over 180 days: private-service investment 547/511 ms; procurement lead-time quotes 530/403 ms; urban descriptors 473/446 ms; private-service operation 364/388 ms. `serviceAccess` itself consumes 195/318 ms exclusively, including repeated facility/household signature construction before cache hits. `dailyEconomy` remains the largest parent, 2922/2725 ms inclusive. Raw sampled profiles and source-bound totals are in `reports/integration/fixed-late-cpu-8/`.

Next safe targets are scope-local repeated quote inputs or service membership inside a proven immutable assessment phase, preserving live capacity/cash/worker checks. Do not infer a usable persistent per-day cache without mutation proofs. The rejected retail reuse experiment remains out: its full-model gain was not consistent. No new speed improvement is claimed here.

## Retention-candidate review

The once-missing UI branch is now published: f457b95c34710ab7271b303cb58034c87b1f66ce, 24478b16588380a76e67a99f92d3670898bacdba, 726d0a5a76512b6df8662d9c83f921b4a90d00b6. They are not integrated in this checkpoint.

Candidate-only negative `tests/test_retention_midday_save.py` confirms 726d0a5 calls save while `monthlyReview` is in progress: captured day30 has no day30 history and RNG1148058720; final day30 has history30 and RNG1031083423. The storage writer is intercepted; a controlled risk fixture is explicitly disclosed. This is evidence of an intermediate payload submission, not physical data-loss certification. Its passing negative test means reproduction succeeded, not release acceptance. Remove/defer automatic internal persistence to the committed boundary before activating the new dilemma; production main does not contain that candidate. See `reports/integration/retention-review-8/midday-save.json`.

Save owner must preserve the main regional-creditor correction: -1 is a legitimate external creditor after actual bank resolution, -2 is invalid; compacted lender summaries support the -1 bucket and validate aggregate owner/lender totals and monotonic ID metadata. Identity codecs stay disabled until reviewed/native-tested. No final packaging.
