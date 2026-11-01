# Canonical decoded-byte accounting correction

The disabled identity codec previously seeded its decoded-size estimate with raw wire bytes. Short JSON numeric tokens such as `1e20` expand during canonical serialization, so valid input could exceed the existing 16 MiB logical-byte limit. This fix changes only the codec budget traversal; initialization and creator admission remain separately owned blockers.

The existing node/depth/finite-number traversal now counts canonical JSON bytes without building another full JSON string: exact numeric representation, UTF8 strings, escapes and lone surrogates, property names, array/object punctuation and scalar values. It stops at the unchanged logical-byte limit before historical directory reconstruction. Existing reconstructed-key and record-overhead charges remain. The initial allowance uses the larger of raw and canonical wire bytes, preserving the old conservative allowance for whitespace/escaped input as well. Initial bounded-wire JSON.parse still precedes this traversal; this is not a claim of a pre-parse heap bound.

The fix retains the original limits, fields, directory ordering, flags and domain validators. Both versions use the same corrected traversal. No initialization, persistence, admission or cooperative logic changed. Production remains disabled.

## Verification

Run `python tools/assemble.py`, then `python tools/test_codec_canonical_budget.py`. The receipt records the assembled source SHA256. It passes nine atomic raw-token attacks across v1/v2: flat, nested, mixed active records, historical person values, and mixed household/firm records. Every rejection preserves live archive, RNG and save chronology. Valid 16,415,367-byte logical inputs preserve all 740000 numeric values in both versions. Exact scanner fixtures cover 108 string/number cases including surrogate pairs, lone surrogates, controls, random UTF16 keys/values, negative zero and extreme finite numbers; exactly 16 MiB passes and one byte above fails.

The unchanged owner suite `python tests/test_estate_firm_codec.py` passes the actual 3000-to-3001 household/firm constructors, full logical field/reference equality, 13 atomic malformed cases, v1 isolation and 30-day replay. `python tools/review_combined_identity_codec.py` passes independent full-field and directory-reordering checks, seven additional atomic rejects, and 45-day deterministic continuation. Reports live under docs/previews/codec-canonical-budget. Host Chromium only; no native certification. The sampled owner encode/decode timings were 446/235 ms; these concurrent host test samples are not a controlled performance comparison or peak-memory measurement.

Integration: cherry-pick the fix commit, regenerate assets, and reconcile the small budget traversal/shared-expansion changes with any newer codec optimization. Do not replay the earlier reviewer commits merely to apply runtime logic. The parent's direct-validation optimization is compatible with this traversal; this branch retains the original candidate encoder for independent testing.

## Remaining activation blockers

A corrected 16 MiB decoded limit does not ensure an archive re-encodes below the separate 8 MiB wire limit. Valid near-logical-limit tests intentionally exercise parsing, not exportability. Capacity-safe admission and post-initialization capacity checks still require the save owner's fixes. Native latency/memory and whole-state restart acceptance also remain. This correction alone does not authorize activation.
