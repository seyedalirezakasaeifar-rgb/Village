# Disabled automatic-day admission candidate

Dependency: shared root API 4ee829c731da5f517ebb7a11277fa0691bed2bec. Neither experiment is assembled into the application. The import helper extraction preserves the existing hydration pipeline; it does not enable admission or the identity codec.

Inject root-capacity-api.js and then automatic-day-admission.js inside the game closure before instrumentation. Explicitly enable the identity codec, then call __automaticDayAdmission.enable(). Paid operations compose through __installPaidCommandLayer(__automaticDayAdmission), sharing the same controller, runtime journal, fences and certificate. The owner adapter exposes shared, metrics and registerRuntime. The composed test uses published paid checkpoint 455a12f1d01943bc9a8846b437146612e5f9bfd2; it does not copy or change that owner's files.

The real complete tick includes births, migration, automatic investment, procurement/project completion, histories and final RNG publication. Refusal restores the model/runtime graph directly, preserving identities and property order, discards pending saves/presentation, pauses frame retries and drains the accumulator. Explicit retry is required. Ordinary saves do not capture or certify the world. Delayed day requests must provide their original adoption epoch.

## Import capacity is measured, not guessed

prepareArchiveCandidate and initializeArchiveCandidate are extracted verbatim from hydrateSave's existing preparation and initialization. Hydration uses those same helpers. Certification serializes a private candidate without changing the live town, executes the real normalization/initialization against that private town, measures its strict wire and logical budgets, and restores the live graph directly in finally. It never calls hydrateSave for rollback, advances a save timeline, or opens a panel during projection. Both original and normalized representations must fit. The earlier per-entity default estimates have been removed. Existing malformed-import, runtime/epoch/UI atomicity and exact-replay regressions remain applicable.

## Visual reserve proof

Authoritative state remains G.freight, regionalTrade cargo/contracts, transit service/journey/fare records and transport financial counters. traffic vehicles are presentation samples of those obligations; no authoritative record is removed. beginVehicle refuses creation beyond 80 before consuming visual RNG. Activation rejects a preexisting fleet over 80 or nonfinite visual clocks/counters, nonfinite mutable numeric vehicle fields, invalid tile-index paths and invalid numeric junction gates. These additional checks apply only to the disabled experiment: the old archive validator itself does not provide these visual bounds.

Audited writers: beginVehicle and trafficUpdate in 60-renderer.js; setPurposeStyle, spawnPurposeTrip and detour in 67-transport.js; frameClock in the bounded frame loop; archivePayload's trafficState and visualState projection.

Every field which can be added or grow between committed roots is charged:

- Numeric vehicle fields: id, segment, fraction, speed, wait, age, from, to, person, shipment, rerouted, plannedStep. Each reserves 32 JSON bytes. A finite binary64 JSON token needs fewer than 32 characters: up to 17 significant decimal digits, decimal/sign/exponent formatting or at most 21 non-exponent integer digits; subnormal magnitudes use exponent notation.
- String/boolean fields: style (pedestrian/emergency maximum), color, emergency, finished, reason. Keys and separators are counted by serializing the complete field template. false is the larger Boolean token.
- Reasons reserve the maximum actual JSON UTF-8/escape width of person names, firm names and goods names plus the exact commuting/return/cargo separators and 32 cargo-quantity characters. Names are never truncated. Quotes, control characters and surrogate/Unicode encoding are included by JSON.stringify plus Blob.size. Mutating names must itself be inside the shared command root.
- Newly generated or detoured paths are simple BFS paths, at most the current road-node count. Tile indices are bounded by atlas length. Per path reserve is roadCount * (maxTileDigits + 1), conservatively including a final comma. Retained old paths/unknown imported fields remain charged in the measured existing archive; they are not discarded or assumed absent.
- Every future numeric junction key can be added once per road tile, with a finite 32-byte timestamp and array punctuation. Existing gates are already charged. frame clock, elapsed time, serial, visual RNG and enclosing headers have an additional 512-byte/32-node allowance.

Reserve the full possible future fleet and gates on top of current measured bytes/nodes, rather than subtracting current actors. This deliberately overcounts replacements. Finite elapsed/age/wait counters add at most the frame loop's 0.25 seconds per frame; numeric width stays bounded. New roads and identities are certified at their containing command/day root. A full-road atlas can exhaust this conservative reserve before its nominal archive limit; refusal is explicit and does not delete history or take payment.

## Automatic dialogs

Standalone automatic creation stages pendingEvent, correspondence and save requests inside the root. DOM/focus publication runs only after commit and does not execute choices. Caught failure poisons the root, restores pending correspondence and discards both presentation and queued saves. A pending dialog blocks subsequent days. In the paid composition the paid owner's already-separated showCustomEvent implementation is reused; the automatic wrapper does not duplicate it. Actual user choice application remains the paid-command owner's responsibility.

DOM opener references are restored as opaque references, not traversed as model graphs. Runtime registration is allowed only while disabled and idle.

## Evidence and remaining blockers

Tests cover exact synchronous replay, byte refusal, caught failures, queued saves, repeated/retried days, stale day requests, dialog publication/choice separation, actual import-normalization expansion, escaped long names, the full visual projection, and paid/day composition. Aggregate synthetic receipts are alongside this document. No user saves are published. To reproduce composition, first fetch codex/8-paid-shared-root so its immutable commit is available locally.

Run tools/assemble.py, tools/test_automatic_day_admission.py (ADMISSION_DAYS=360 for annual boundary), tools/test_automatic_dialog_admission.py, tools/test_composed_day_paid.py and tools/profile_automatic_day_admission.py. Tests use host Chromium, not Android performance certification.

Admission remains disabled. Full runtime/entry-point coverage, all paid choices with this normalization certificate, large-world heap, native latency and conservative reserve usability remain gates. The nested private projection and exact graph journal are expensive; measured guarded ticks substantially exceed ordinary ticks. Removing duplicate serialization alone did not establish a meaningful normal-case speed improvement. Keep that negative result. The adapter must not be promoted as smooth or production-ready from correctness results alone.

Terminal receipt: the final adapter passes the 360-day synchronous archive/RNG comparison, all 60 actual paid council choices with exact model/RNG and self-import, and composed construction/council/60-day continuation. Final host medians: ordinary tick 3.0 ms, guarded tick 335.05 ms, near-limit guarded tick 705.4 ms; refusal 897.6 ms. These are diagnostic host measurements, not native certification. The paid layer still explicitly refuses unintegrated road strokes and custom choices without transaction descriptors. Those paths, newer integration features and native lifecycle/I/O acceptance are not covered by this candidate's terminal pass.
