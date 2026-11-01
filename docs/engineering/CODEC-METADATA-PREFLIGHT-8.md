# Early identity directory metadata rejection

This follow-up moves the existing household/firm header validation ahead of the canonical-byte traversal and all historical reconstruction. An invalid firm total previously scanned the entire wire and reconstructed households before rejecting. Person headers were already checked early. Both estate headers are now checked before either estate is reconstructed; missing/extra directories and unexpected v1 estate directories are also rejected before the value scan. The exact-key check short-circuits on an unexpected key without allocating/sorting all keys.

No limits, fields, record validators, node/cell/depth/byte charges, initialization, creator admission, or feature flags changed. Valid files use the same budget traversal and reconstruction order. The private decodeHistoricalEntity helper now expects the header preflight performed by its sole production caller, decodeInactiveEnvelope.

## Evidence

After `python tools/assemble.py`, run `python tools/test_codec_metadata_preflight.py`. The 6,101,949-byte synthetic boundary fixture includes actual constructor transitions to 3001 households/firms. Eighteen malformed cases (person total, missing/extra/v1 directories and seven header cases for each estate kind) reject with zero canonical budget calls and zero historical reconstructions. Each retains live state, RNG, chronology, and the caller object. Valid input still performs exactly one budget traversal and two reconstructions.

Also rerun `python tools/test_codec_canonical_budget.py` and `python tests/test_estate_firm_codec.py`: numeric guard/atomicity fixtures and the owner full-field, 13-malformed-case, v1 and 30-day exact replay suite pass. Source-bound host receipts are under docs/previews/codec-metadata-preflight.

This addresses avoidable work after JSON parsing for malformed headers, including directory-total errors. It does not eliminate initial JSON.parse/UTF8-size checks or establish a physical-device latency bound. Malformed inner rows and domain references still undergo their existing later validation. The parent's API30 software-emulator native timings predate this fix; a native retest is needed before quantifying improvement there.

Integrate this follow-up commit after 77a799d (canonical budget correction), then assemble. Keep the codec disabled pending independent capacity/normalization fixes and native acceptance. No production activation was performed.
