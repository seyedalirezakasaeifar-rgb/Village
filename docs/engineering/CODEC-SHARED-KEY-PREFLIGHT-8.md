# Shared reconstructed-key preflight

Runtime-only commit: `9932d34`. Apply after canonical-byte accounting 77a799d and early headers a964174; the prior review-only corpus commit f56d9a3 is not a runtime dependency. Source SHA256 after assembly: `d48e5ce2608c2d77db94ec271e1a0f0377657678308de73f5abc750f0a331eb6`.

A private preflight counter totals the unchanged record overhead, row-cell counts and repeated canonical UTF8 key charges across both estate directories and the person directory before reconstruction. It validates row shape and indices before using them. Only after all directories fit does reconstruction begin. The existing reconstruction checks remain; preflight uses its own counter copy so allowances are not charged twice. Computed key-byte arrays are reused during reconstruction, avoiding a second set of Blob/string measurements. No record values or fields are transformed, dropped or newly defaulted.

The key-expansion corpus attack previously entered two historical directory decoders and performed 48,903 field definitions before rejection. It now performs **one canonical budget traversal, zero historical reconstruction calls, and zero field definitions**. Malformed row metadata/indices also reject before record construction. Duplicate IDs and classification/domain checks remain in reconstruction. No limits, flags, initialization, admission, persistence or native source changed; the candidate remains disabled.

## Verification and native entrypoint

Assemble with `python tools/assemble.py`. To run only the changed rejection path:

`CODEC_CORPUS_KEYS_ONLY=reject python tools/test_codec_adversarial_corpus.py`

This creates a 692,926-byte synthetic shared-key input, checks the exact expansion error, asserts zero field definitions and zero reconstruction calls, and verifies unchanged live archive, RNG and save chronology. Output goes to reports/codec-shared-key-focused.json. Native harnesses may extract the script's probe and call `__codecCorpus('reject')`; it needs the existing game test instrumentation, and production flags are enabled only in the disposable test session. This mode does not run the rest of the corpus or claim its coverage.

Full `python tools/test_codec_adversarial_corpus.py` passes 2048 canonical-size comparisons, 350 valid-field cases and 177 atomic rejects. A separately computed conservative-charge oracle builds a valid archive at exactly **16,777,216** charged bytes: it decodes successfully with unchanged padding and directory lengths. One extra byte rejects before all field definitions and directory reconstruction. Each long-key directory alone still passes. Large shared node/depth cases also reject before reconstruction.

`python tools/test_codec_canonical_budget.py` passes both wire versions, nine numeric attacks, valid near-limit numeric values and exact scalar/string-byte fixtures. `python tests/test_estate_firm_codec.py` passes full logical field/reference fidelity, actual 3000-to-3001 constructors, 13 malformed atomic cases, v1 compatibility/isolation and 30-day exact replay. `python tools/review_combined_identity_codec.py` passes independent full-field/reordering checks, additional atomic rejects and 45-day deterministic continuation. Receipts are under docs/previews/codec-shared-key-preflight and share the assembled source hash above.

These are host Chromium results, not native elapsed-time or memory certification. The valid path gains a bounded row-index/cost pass while reusing key-byte computations; uncontrolled concurrent host timings are not used to claim a speedup. Native should retest this exact rejection path. Existing capacity/default/admission and rollout gates remain; this commit does not authorize enabling the codec.
