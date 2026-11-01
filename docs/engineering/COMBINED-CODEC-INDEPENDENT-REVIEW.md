# Independent inactive identity codec review

Status: **do not activate**. Production source and feature flags were not changed. Host Chromium evidence is not native memory or latency certification.

## Candidates and successful checks

Person candidate `f93a87ca331669c7a7907453799f009eb8adbfa0`; combined v2 `aecf8e3dbbd50cc60a67fb4063ef379170abbd48`; direct-validation optimization `d1f963afc24dc932e91c48bb72253583b3390429`. This review branch starts at the combined candidate and substitutes the optimized codec only inside isolated browser test pages. Optimized assembled-source SHA256: `b9f015806b20e5795bdb1814373b25a8786247c7c67f634ac9104c4c79d4f12f`.

The owner's combined boundary suite independently passed: actual constructor transitions past 3000 historical households/firms, full-field roundtrip, asset/title/claim/default-loan references, 30-day replay, 13 malformed cases, and v1 compatibility. Independent additional assertions passed on both combined versions: complete logical field equality before hydration, reordered active/historical directories without reindexing, own prototype/constructor fields, high-ID references, seven further atomic/domain rejects including shared UTF8 expansion, and exact 45-day canonical original-versus-second-decoded model/RNG continuation. Fixture preparation reuses the owner's synthetic historical-record generator; assertions and additional mutations are separate. Person-only evidence is in INACTIVE-CODEC-INDEPENDENT-REVIEW.md.

These are pinned-candidate results, not acceptance of later main changes.

## Activation blockers reproduced

1. **Raw numeric token expansion defeats the claimed 16 MiB logical bound (v1 and v2).** An allowed unknown payload array with 800000 finite `1e20` values passes node/depth limits. Raw JSON represents each number in four characters, whereas canonical JSON expands each to 21 digits. Person input is 4,135,509 bytes, combined input 4,135,613 bytes; both decode to 17,735,373 logical bytes, exceeding 16,777,216. Parsing and hydration succeed; immediate export fails the encoded-byte budget. The expansion estimate begins with raw encoded bytes and does not account for canonical numeric growth. Enforce a bounded canonical-size accounting pass, including all values and reconstructed keys, before adoption. Object-only malformed fixtures cannot reproduce this raw-token case.

2. **Initialization can make accepted input unsaveable without a player action.** On optimized v2, a valid 8,388,544-byte archive omits 26 optional firm unitCost maps. Hydration succeeds and ordinary initialization restores them. Immediate export fails; save returns false before any persistence write. Require post-normalization capacity validation with atomic refusal, in addition to mutation admission. Synthetic near-limit padding intentionally isolates the boundary.

3. **Known creator admission failure confirmed.** A valid 8,388,186-byte archive accepts three actual createFirm helper calls before export failure. Live firms become 29; restoring the last valid archive returns 28. Save returns false before writing. This is a helper-level capacity witness, not paid UI construction or a naturally evolved city. Mutations must reserve/check capacity safely before committing, or use an equally durable representation; an export-only error does not protect recent play.

## Remaining contracts and limitations

The wire schema is 9 but logical schema must stay 8 for these decoders. Raising RELEASE/G schema without adapting that contract prevents export. A permitted reserved format marker can also break a small archive after codec downgrade; see the person review witness. Ordinary oversized legacy raw archives remain rejected, so this is a forward encoding fix rather than demonstrated recovery for previously broken raw saves.

The synchronous production build can accept an independently sound codec without incorporating the failed cooperative simulation experiment. The presence-based cooperative guard refuses enabling in those experimental builds; preserve that separation. Direct validation of an already private JSON-derived candidate passed replay/atomicity checks and avoids a redundant parse, but does not prove a peak-memory bound. Initial JSON parsing occurs before traversal limits.

Native person-only measurements and whole-state restart discrepancies supplied by the parent remain separate gates: baseline also changes roadMetrics to null; regionalTrade initialization changes absent to object. Do not waive whole-state equality through ad hoc filters. Combined native memory/latency, latest-main normalization, and capacity-safe admission still require acceptance after fixes. Host heap samples are not peak or Android guarantees.

## Reproduction

On this branch run `python tools/assemble.py` first. The source flag remains off; scripts enable it only in disposable browser pages. Chromium and Playwright are required. Git objects d1f963a and 1d73dfda must be available.

- `python tools/review_combined_identity_codec.py`
- `CODEC_REVIEW_OPTIMIZED=1 python tools/review_combined_identity_codec.py`
- `python tools/review_codec_capacity_boundary.py`
- `python tools/review_codec_normalization_boundary.py`
- `python tools/review_codec_numeric_expansion.py`
- For pinned f93 assembled worktree: `CODEC_REVIEW_PERSON_ROOT=/path/to/f93-worktree python tools/review_codec_numeric_expansion.py`

Receipts are under docs/previews/codec-independent. Generated reports are intentionally outside the production source. No activation, native certification, release, or signing was performed.
