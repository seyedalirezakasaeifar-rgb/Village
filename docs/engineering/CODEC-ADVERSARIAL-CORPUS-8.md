# Deterministic identity codec corpus

Review-only follow-up on a964174 (including canonical byte correction 77a799d). No runtime source, feature flag, initialization or admission changes. Assembled source SHA256: `96132c4a1efd8b05c0599c2aef4314aa0082940f600456f4e377618fa28666af`.

Run `python tools/assemble.py`, then `python tools/test_codec_adversarial_corpus.py`. Seed is `0x53a91c2d` / `1403591725`; fixture game seed is 42. Any assertion failure aborts and records the seed, source hash, named/indexed case, and reproduction command in reports/codec-adversarial-corpus-failure.json. Success receipt is docs/previews/codec-adversarial-corpus/result.json. Chromium/Playwright required. V8 old-space is capped at 384 MiB, generated random trees have depth at most four and bounded fanout/string lengths, and large shared-budget witnesses are generated once. Largest wire in this run: 4,406,102 bytes. This is a bounded test design, not a measured process/native peak-memory guarantee.

## Passed coverage

- 2048 seeded canonical-size comparisons against JSON.stringify UTF8 bytes.
- 350 valid wire/fidelity cases, including 256 random root values and 64 mixed active/historical person, household and firm extensions. Full base directories are independently compared against original record objects, rather than using a decoder output as the only reference.
- Unusual numeric spellings, exponents/underflow/extreme finite values, large unknown-field numbers, and negative zero. Negative zero survives decoding; ordinary subsequent JSON serialization canonicalizes it to zero, consistent with the existing JSON contract. Unsafe identity IDs reject separately.
- Unicode controls, UTF8 widths, actual and escaped surrogate pairs, lone surrogates, random UTF16 keys/values, own prototype/constructor keys, and missing-versus-null fields.
- 176 invalid atomic cases: invalid syntax including sparse/trailing-comma arrays, nonfinite exponents, duplicate identity IDs, malformed/null/sparse records and field-index arrays, missing required metadata/person fields, and 128 seeded invalid-header combinations. Every rejection retains live archive, RNG and save chronology.
- Raw duplicate JSON keys follow JSON.parse last-value-wins semantics. Tests explicitly verify both valid and invalid final metadata values and valid duplicate ID-property keys. Duplicate IDs across directory records reject. This does not add a new duplicate-key rejection policy.
- Each large household/firm directory independently fits the node budget, while the pair rejects the shared node limit. Separate long-UTF8-key directories independently fit decoded-byte charges, while the combined case rejects shared expansion. Existing canonical-budget suite separately covers exact/one-byte-over logical limits and short-token numeric expansion.

## Early-rejection work counts

Work instrumentation runs only in disposable test pages and counts canonical traversal calls, historical directory reconstruction calls, and Object.defineProperty calls. It is not elapsed-time profiling or a native speed claim.

142 malformed header cases and 10 syntax cases reject with zero budget traversals, zero directory reconstruction calls and zero property definitions. The combined node-budget and depth failures perform one budget traversal and zero reconstruction/property definitions.

Remaining late rejection is explicit: duplicate active person IDs still perform one budget traversal, two historical reconstruction calls and 96 field definitions in the small mixed fixture. Duplicate historical person IDs perform 114 field definitions; duplicate firm IDs 96. The shared long-key expansion case rejects atomically only after two directory calls and **48,903 field definitions**. These remain within the existing bounded private-candidate work; no acceptance or atomicity failure was found. A future narrow preflight of row indices/IDs and aggregate reconstructed-key charges could avoid that work before building objects, but would need a controlled valid-path overhead comparison. No such restructuring was included in this review commit.

All assertions passed. No new correctness blocker or budget bypass was discovered. Previously reported export-capacity, initialization/admission, and native acceptance gates are unchanged; this corpus does not authorize activation.
